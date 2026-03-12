# AGENTS.md

## Project Overview

WebSocket-based Python server that orchestrates a swarm of ComputerCraft turtles
in Minecraft. The server (`server.py`) accepts connections from Lua clients
(`minecraft/startup.lua`) running on in-game turtles, and the
`Master_Control_Program` coordinates their mining, movement, and refueling.

**Languages:** Python 3.10+ (server), Lua (turtle client)
**No web framework** -- pure `asyncio` + `websockets`.

## Repository Structure

```
start_server.py          # CLI entry point (argparse)
server.py                # WebSocket server, console, MCP loop
server_control/
  mcp.py                 # Master_Control_Program -- swarm orchestration
  turtle.py              # Turtle class -- per-turtle state machine & commands
  types.py               # Enums: Instruction_Status, Task_Status, Heading
worlds/
  json_manager.py        # JSON persistence for world & turtle data
minecraft/
  startup.lua            # Lua script deployed to each ComputerCraft turtle
config.json              # Game config: ore Y-levels, fuel values, thresholds
```

## Setup & Running

```bash
# Install dependencies
pip install -r requirements.txt   # aioconsole, websockets, argparse

# Start the server (default world "world", coords 0,0,0)
python3 start_server.py

# With options
python3 start_server.py -w myworld -c 100 64 200 -b z
```

Interactive console commands at runtime: `stop`, `save`, `stats`.

## Build / Lint / Test Commands

There is **no formal build system, linter config, or test framework** configured.
No `pyproject.toml`, `setup.py`, `Makefile`, or CI pipeline exists.

```bash
# Type checking (mypy is referenced in .gitignore but not configured)
# If adding mypy:
pip install mypy
mypy . --ignore-missing-imports

# Running a single ad-hoc test file (gitignored):
python3 test.py
```

If you add tests, use `pytest`:
```bash
pip install pytest pytest-asyncio
pytest tests/                     # run all tests
pytest tests/test_turtle.py       # run a single test file
pytest tests/test_turtle.py::test_step_to -v  # run a single test
```

## Code Style Guidelines

### General Formatting

- **Indentation:** 4 spaces (standard Python).
- **Line length:** No enforced limit; lines tend to stay under ~120 chars.
- **Blank lines:** One blank line between methods. Two blank lines before
  top-level class definitions. Extra blank lines are used liberally inside
  methods after logical sections.
- **Trailing whitespace / trailing newlines:** Not enforced. Some files end
  with extra blank lines.
- **Quotes:** Double quotes for strings throughout (both Python and JSON).

### Imports

- **Standard library** imports first, then **third-party**, then **local**.
- Separate groups with a blank line.
- Use `from X import Y` for specific items; use `import X` for modules
  used as namespaces (e.g., `import server_control.types as Types`).
- **Circular import pattern:** Use `TYPE_CHECKING` guard for forward
  references between `turtle.py` and `mcp.py`:
  ```python
  from typing import TYPE_CHECKING
  if TYPE_CHECKING: from server_control.mcp import Master_Control_Program
  ```
- String-quoted forward references for type annotations on class attributes:
  ```python
  master_control_program: 'Master_Control_Program'
  ```

### Naming Conventions

- **Classes:** `Pascal_Case` with underscores between words
  (e.g., `Master_Control_Program`, `Json_Manager`, `Instruction_Status`).
  This is a project-specific convention -- follow it consistently.
- **Methods and functions:** `snake_case` (e.g., `handle_connect`,
  `set_destination`, `go_to_destination`).
- **Instance variables:** `snake_case` (e.g., `startup_chores_complete`,
  `line_stepper`). Some use `camelCase` for game IDs (`gameID`, `parentID`)
  -- match the existing field names.
- **Constants:** `UPPER_SNAKE_CASE` at module level
  (e.g., `DISCONNECT_MESSAGE`, `TYPE_EXEC`).
- **Enums:** Class name is `Pascal_Case`; members are `UPPER_SNAKE_CASE`.
- **Type aliases module:** Imported as `Types`
  (`import server_control.types as Types`), referenced as
  `Types.Instruction_Status`, `Types.Heading`, etc.

### Type Annotations

- Type hints are used on class-level attribute declarations and constructor
  parameters but often omitted on method return types and local variables.
- Use `# type: ignore` for websocket API calls that have union return types.
- Use `'ClassName'` string annotations for forward references.
- Union types use `X | None` syntax (Python 3.10+).

### Classes and Architecture

- Classes declare instance attributes as class-level type annotations
  (without default values), then initialize them in `__init__`.
- Constructor uses keyword arguments with defaults for optional params.
- `match`/`case` statements are used for dispatching on enum values.
- Methods are grouped with section comment banners:
  ```python
  ###########################
  ##### MAIN CODE START #####
  ###########################
  ```

### Error Handling

- Errors are printed to stdout with `[ERROR]` prefix -- no exceptions raised,
  no logging framework.
  ```python
  print("[ERROR] Requested world block does not exist yet.")
  ```
- Functions return sentinel values on failure (`None`, `"unknown"`, `-1`)
  rather than raising exceptions.
- `None` returns are typed as `'Turtle | None'` but often use
  `# type: ignore` to suppress warnings.

### Async Patterns

- The server uses `asyncio` with `websockets.server.serve`.
- `async def` for WebSocket handlers; sync `def` for pure logic/queue ops.
- Turtle commands are queued as strings and sent one at a time per 0.25s tick.
- `aioconsole.ainput` for non-blocking console input.

### Data and Persistence

- World state: flat dict with `"x,y,z"` string keys mapping to block names.
- Turtle state: serialized to/from JSON via `Json_Manager`.
- All JSON files use 4-space indent (`json.dumps(data, indent=4)`).
- Config values in `config.json` use `kebab-case` keys.
- World data lives in `worlds/<name>/` (gitignored except manager code).

### Lua Client

- Single file: `minecraft/startup.lua`.
- Communicates with the Python server over WebSocket.
- Trust handshake: sends `"shake-my-hand-bro"` on connect.
- Sends JSON payloads with inventory, fuel, block detection, and command
  return status.

### Key Domain Concepts

- **Task** (big picture): Assigned by MCP via a priority-based decision tree.
  `IDLE`, `MINE`, `REFUEL`, `DEPOSIT`, `MINE_FUEL`, `MINE_RESOURCES`,
  `SMELT`, `CRAFT`, `REPRODUCE`.
  Priority order (highest first):
  `REFUEL > DEPOSIT > MINE_FUEL > MINE_RESOURCES > SMELT > CRAFT > REPRODUCE`.
  Each task has a `should_*` helper method in `mcp.py` that returns `bool`.
- **Instruction** (immediate): `IDLE`, `GOTO`, `MANUAL`, `STARTUP_CHORES`,
  `TUNNLING` -- executed by Turtle via command queue.
- **Heading:** `NORTH(0)`, `EAST(1)`, `SOUTH(2)`, `WEST(3)`.
- **Bounding box:** Virtual mining region with left/right tunnel walls,
  an "infinite dimension" axis (x or z).
- Turtle types: `"M"` (master, crafty turtle), `"U"` (underling/child).
- **Smelting:** Fixed base furnace at deposit area. Turtle drops raw ore
  from above (input slot), drops fuel from side, collects output from side.
- **Crafting:** Master turtle only (crafty turtle peripheral). Crafts
  computer, chest, then turtle from raw materials.
- **Reproduction:** MCP-driven based on `max-swarm-size` config. Master
  turtle clones using disk drive + disk (reusable) + crafted turtle item.

### Things to Watch Out For

- The enum value is `TUNNLING` (not `TUNNELING`) -- match the existing typo.
- `ammount` is used instead of `amount` in several places -- match existing
  spelling in variable names (`refuel_ammount`, etc.).
- `gameID` and `parentID` use camelCase -- do not rename to snake_case.
- `gameID` and `parentID` use camelCase -- do not rename to snake_case
  in the `place()` method signature or elsewhere.
- World data keys are comma-separated coordinate strings: `"x,y,z"`.
