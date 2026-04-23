"""ASCII region-map renderer.

The engine's `map` command is a single-command entry point into this module.
The goal is a player can glance at the region they're in and see the
topology — what's visited, what's reachable, which exits still aren't
taken — without having to play dungeon-master in their head.

Rendering strategy is deliberately simple:
  * BFS from the player's current location (or the first visited location
    in the region if the player is elsewhere) using only cardinal exits
    (N/S/E/W) for grid placement.
  * Each placed location becomes a single-line box: ``[Name*]`` for the
    current, ``[Name]`` for visited, ``[Name?]`` for known-but-unvisited
    (an exit points at it from a visited neighbour).
  * Horizontal cardinal connections are drawn with ``─`` between boxes;
    vertical with ``│`` on a spacer row between box rows.
  * Non-cardinal exits (``up``/``down``/``in``/``out``/named portals like
    ``library`` or ``forge``) are collected per-cell and listed under the
    grid as an "Other connections" block — the grid stays a map, the
    annotations pick up the non-planar parts of the world graph.

The renderer is pure (world, player) → str; the engine call-site decides
what to print.
"""
from __future__ import annotations
from collections import deque
from typing import Dict, List, Optional, Tuple


# Grid directions. Cardinals map to one unit; up/down fold onto north/south
# because in practice the content treats vertical travel the same way on a
# terminal (a plateau north of a pass, a ridge above a cloister — both
# want to be "above" on the map). The renderer only uses this mapping for
# placement and for drawing connectors; the "Other connections" block
# keeps the original direction name, so no information is lost.
_DELTAS: Dict[str, Tuple[int, int]] = {
    "north": (0, -1),
    "south": (0, 1),
    "east":  (1, 0),
    "west":  (-1, 0),
    "up":    (0, -1),
    "down":  (0, 1),
}
_CARDINAL = set(_DELTAS)
# When we draw a connector, we check whether either side's exit matches
# this direction. Include up/down as valid vertical connectors.
_VERT_EXITS = {"north", "south", "up", "down"}
_HORIZ_EXITS = {"east", "west"}


def _region_of(world, loc_id: str) -> str:
    l = world["locations"].get(loc_id, {})
    return l.get("region") or ""


def _visited_in_region(world, player, region: str) -> List[str]:
    return [lid for lid in player.visited
            if _region_of(world, lid) == region]


def _compute_placement(world, player, region: str
                       ) -> Tuple[Dict[str, Tuple[int, int]], Dict[str, bool]]:
    """Run BFS over cardinal exits inside `region`. Returns:
      - positions: {loc_id: (col, row)}
      - visited_flag: {loc_id: True if in player.visited else False}
    Locations reachable by cardinal exit from a visited neighbour are
    placed even if unvisited; deeper unvisited chains are not followed
    (a single "you could go here next" row at the edge is enough).
    """
    all_locs = {lid: l for lid, l in world["locations"].items()
                if l.get("region") == region}

    # Pick a BFS start — prefer the player's current location if it's in
    # the region; otherwise the first visited location in the region.
    if region == _region_of(world, player.location):
        start = player.location
    else:
        vs = [lid for lid in all_locs if lid in player.visited]
        if not vs:
            return {}, {}
        start = vs[0]

    positions: Dict[str, Tuple[int, int]] = {start: (0, 0)}
    taken: set = {(0, 0)}
    visited_flag: Dict[str, bool] = {start: start in player.visited}

    # BFS only expands from locations the player has visited — unvisited
    # neighbours are placed but not stepped through (the map should not
    # spoil geography beyond one step from a visited edge).
    queue: deque = deque([start])
    seen: set = {start}
    while queue:
        cur = queue.popleft()
        if cur not in player.visited:
            continue
        cur_loc = all_locs.get(cur, world["locations"].get(cur, {}))
        cx, cy = positions[cur]
        for d, tgt in (cur_loc.get("exits") or {}).items():
            if d not in _CARDINAL:
                continue
            if tgt not in all_locs:
                continue  # cross-region exits aren't drawn on this grid
            if tgt in positions:
                continue  # already placed — keep the first position won
            dx, dy = _DELTAS[d]
            nx, ny = cx + dx, cy + dy
            if (nx, ny) in taken:
                continue  # grid collision — skip this placement
            positions[tgt] = (nx, ny)
            taken.add((nx, ny))
            visited_flag[tgt] = tgt in player.visited
            if tgt in player.visited and tgt not in seen:
                seen.add(tgt)
                queue.append(tgt)

    return positions, visited_flag


def _collect_other_exits(world, player, region: str,
                         positions: Dict[str, Tuple[int, int]]
                         ) -> List[Tuple[str, str, str]]:
    """Non-grid exits from placed-and-visited cells. An up/down that was
    actually used for grid placement is skipped here (avoids duplicating
    the grid's visual with a text line). Returns (from, direction, to)."""
    out: List[Tuple[str, str, str]] = []
    for lid in positions:
        if lid not in player.visited:
            continue
        l = world["locations"].get(lid, {})
        lpos = positions[lid]
        for d, tgt in (l.get("exits") or {}).items():
            if d in _CARDINAL:
                # Skip only if the direction matches how the neighbour sits
                # on the grid (otherwise it's an exit that happens to share
                # a name but points elsewhere).
                if tgt in positions:
                    dx, dy = _DELTAS[d]
                    tpos = positions[tgt]
                    if (tpos[0] - lpos[0], tpos[1] - lpos[1]) == (dx, dy):
                        continue
            out.append((lid, d, tgt))
    out.sort()
    return out


def _label_for(world, loc_id: str, player, is_current: bool,
               is_visited: bool) -> str:
    """Short cell label. Name trimmed to <= 14 chars so the grid stays
    compact on a typical terminal."""
    name = world["locations"].get(loc_id, {}).get("name", loc_id)
    # Strip common prefix words for tighter cells on the grid — the region
    # name supplies the context. 'Azure Cloud Library' -> 'Library'.
    trimmed = name
    for prefix in ("Azure Cloud ", "Willowmere ", "Thousand Venom Valley ",
                   "Scarlet Lotus Hidden ", "The Drowned Willow ",
                   "The Old Hermit's ", "Willow and Moon ",
                   "Elder Baixu's ", "Hanging Terraces of "):
        if trimmed.startswith(prefix):
            trimmed = trimmed[len(prefix):]
            break
    if len(trimmed) > 14:
        trimmed = trimmed[:13] + "…"
    # Current-location marker is a trailing asterisk; unvisited is a trailing
    # question-mark; plain visited is nothing extra.
    if is_current:
        return f"{trimmed}*"
    if not is_visited:
        return f"{trimmed}?"
    return trimmed


def render_region(world, player, region: Optional[str] = None) -> str:
    """Render the visual ASCII map of one region. If `region` is None, use
    the player's current region."""
    if region is None:
        region = _region_of(world, player.location)
    if not region:
        return "(You are nowhere any region claims.)"

    positions, visited_flag = _compute_placement(world, player, region)
    if not positions:
        return f"~~ {region} ~~\n  (You have not visited any location in this region yet.)"

    # Normalise coordinates so the top-left cell is at (0,0).
    min_c = min(c for c, _ in positions.values())
    min_r = min(r for _, r in positions.values())
    norm: Dict[str, Tuple[int, int]] = {
        lid: (c - min_c, r - min_r) for lid, (c, r) in positions.items()
    }

    # Grid dimensions.
    max_c = max(c for c, _ in norm.values())
    max_r = max(r for _, r in norm.values())

    # Build cell labels and pick a per-column width (widest label in column).
    labels: Dict[str, str] = {
        lid: _label_for(world, lid, player,
                        is_current=(lid == player.location),
                        is_visited=visited_flag.get(lid, False))
        for lid in norm
    }
    col_labels: Dict[int, List[str]] = {}
    for lid, (c, _) in norm.items():
        col_labels.setdefault(c, []).append(labels[lid])
    col_width: Dict[int, int] = {
        c: max(len(lbl) for lbl in col_labels[c]) + 2  # +2 for `[` `]`
        for c in col_labels
    }

    # For each column, compute its left-edge X in the output canvas.
    # Between columns we leave a 4-char gap for horizontal connectors.
    gap = 4
    col_x: Dict[int, int] = {}
    x = 0
    for c in range(max_c + 1):
        col_x[c] = x
        x += col_width.get(c, 0) + gap

    # Row 2 rows per grid row: a cell row and a spacer for vertical connectors.
    # Output lines as a list of mutable chars.
    def blank(width: int) -> List[str]:
        return [" "] * width

    total_w = x
    total_h = (max_r + 1) * 2 + 1
    canvas: List[List[str]] = [blank(total_w) for _ in range(total_h)]

    # Build cell -> center-row; row 0 cells live on canvas row 1, row 1 on 3, etc.
    # We use: cell_row = r*2 + 1. Spacer rows = r*2 + 2 (between).
    def cell_row(r: int) -> int:
        return r * 2 + 1

    # Place labels as [Label] at (col_x, cell_row).
    cell_span: Dict[Tuple[int, int], Tuple[int, int]] = {}
    # cell_span maps (c, r) -> (start_x, end_x_inclusive) on the canvas.
    for lid, (c, r) in norm.items():
        lbl = labels[lid]
        text = f"[{lbl}]"
        start = col_x[c]
        end = start + len(text) - 1
        for i, ch in enumerate(text):
            if start + i < total_w:
                canvas[cell_row(r)][start + i] = ch
        cell_span[(c, r)] = (start, end)

    # Draw connectors only when an actual cardinal exit exists between the
    # two cells. Proximity on the grid is not enough — BFS can place two
    # unrelated locations in adjacent cells (e.g. Pale Lake west of Hermit's
    # Hut because both pivot off a shared ancestor), and a line between
    # them would lie.
    pos_by_coord: Dict[Tuple[int, int], str] = {v: k for k, v in norm.items()}

    def _exit_to(src_lid: str, tgt_lid: str, allowed: set) -> bool:
        """True if `src_lid` has any exit in `allowed` pointing at `tgt_lid`."""
        l = world["locations"].get(src_lid, {})
        for d, t in (l.get("exits") or {}).items():
            if d in allowed and t == tgt_lid:
                return True
        return False

    for (c, r), lid in pos_by_coord.items():
        # East neighbour.
        if (c + 1, r) in pos_by_coord:
            east_lid = pos_by_coord[(c + 1, r)]
            if (_exit_to(lid, east_lid, _HORIZ_EXITS) or
                _exit_to(east_lid, lid, _HORIZ_EXITS)):
                _, end_x = cell_span[(c, r)]
                start_x, _ = cell_span[(c + 1, r)]
                for x_ in range(end_x + 1, start_x):
                    canvas[cell_row(r)][x_] = "─"
        # South neighbour.
        if (c, r + 1) in pos_by_coord:
            south_lid = pos_by_coord[(c, r + 1)]
            if (_exit_to(lid, south_lid, _VERT_EXITS) or
                _exit_to(south_lid, lid, _VERT_EXITS)):
                start_x, end_x = cell_span[(c, r)]
                mid = (start_x + end_x) // 2
                canvas[cell_row(r) + 1][mid] = "│"

    # Trim trailing whitespace per line and assemble.
    grid_lines: List[str] = []
    for row in canvas:
        grid_lines.append("".join(row).rstrip())
    # Drop purely-empty trailing lines.
    while grid_lines and not grid_lines[-1]:
        grid_lines.pop()
    while grid_lines and not grid_lines[0]:
        grid_lines.pop(0)

    # Compose final output.
    out: List[str] = []
    out.append(f"~~ {region} ~~")
    out.append("")
    out.extend(grid_lines)

    # Detached-but-visited block: locations in the region the player has
    # visited that cardinal BFS couldn't place (typical for sect hubs
    # whose interior is navigated by named portals — library, forge,
    # elder, in/out). These aren't lost to the map; they get a sibling
    # list.
    detached = [lid for lid in player.visited
                if _region_of(world, lid) == region and lid not in positions]
    if detached:
        out.append("")
        out.append("  Also in this region (non-cardinal):")
        for lid in sorted(detached):
            lname = world["locations"].get(lid, {}).get("name", lid)
            marker = "  *" if lid == player.location else ""
            out.append(f"    {lname}{marker}")

    # Other-connections block: non-cardinal exits from placed-and-visited
    # cells AND from detached-visited cells. Group by source location.
    other = _collect_other_exits(world, player, region, positions)
    # Also pull from detached cells.
    for lid in detached:
        for d, tgt in (world["locations"].get(lid, {}).get("exits") or {}).items():
            if d in _CARDINAL:
                continue
            other.append((lid, d, tgt))
    other.sort()
    if other:
        out.append("")
        out.append("  Other connections:")
        last_src = None
        for src, d, tgt in other:
            src_name = world["locations"].get(src, {}).get("name", src)
            tgt_loc = world["locations"].get(tgt, {})
            tgt_name = tgt_loc.get("name", tgt)
            tgt_region = tgt_loc.get("region") or ""
            marker = "" if tgt in player.visited else "  (unexplored)"
            if tgt_region and tgt_region != region:
                marker = f"  [→ {tgt_region}]" + (
                    "" if tgt in player.visited else "  (unexplored)"
                )
            if src != last_src:
                out.append(f"    {src_name}:")
                last_src = src
            out.append(f"      {d:10s} → {tgt_name}{marker}")

    # Legend.
    out.append("")
    out.append("  Legend: [Name*] = you are here   "
               "[Name] = visited   [Name?] = seen, not entered")
    return "\n".join(out)


def render_all_visited(world, player) -> str:
    """Render every region the player has set foot in, top-to-bottom."""
    regions_seen: List[str] = []
    for lid in player.visited:
        r = _region_of(world, lid)
        if r and r not in regions_seen:
            regions_seen.append(r)
    if not regions_seen:
        return "(You have not yet walked anywhere worth remembering.)"
    parts: List[str] = []
    for r in regions_seen:
        parts.append(render_region(world, player, r))
        parts.append("")
    return "\n".join(parts).rstrip()
