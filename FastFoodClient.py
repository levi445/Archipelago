from __future__ import annotations
import asyncio
from collections import deque
from typing import Dict, List, Optional, Set

import ModuleUpdate
ModuleUpdate.update()

import Utils
from NetUtils import ClientStatus
from CommonClient import (
    CommonContext, server_loop, gui_enabled,
    ClientCommandProcessor, logger, get_base_parser,
)
from Utils import async_start

DEFAULT_CALORIES = 450


class FastFoodCommandProcessor(ClientCommandProcessor):
    def _cmd_tracker(self) -> None:
        """Show current Fast Foodipelago progress and available items."""
        if isinstance(self.ctx, FastFoodContext):
            self.ctx.print_tracker_status()

    def _cmd_eat(self, number: str = "") -> None:
        """Check off an available item by number. Usage: /eat <number>"""
        if isinstance(self.ctx, FastFoodContext):
            self.ctx.eat_item(number)

    def _cmd_list(self) -> None:
        """List all eaten items so far."""
        if isinstance(self.ctx, FastFoodContext):
            self.ctx.list_eaten()


class FastFoodContext(CommonContext):
    game = "Fast Foodipelago"
    items_handling = 0b111
    command_processor = FastFoodCommandProcessor

    def __init__(self, server_address: Optional[str], password: Optional[str]) -> None:
        super().__init__(server_address, password)

        self._unlocked_restaurants: Set[str] = set()
        self._item_restaurants: Dict[str, Set[str]] = {}
        self._calorie_item_values: Dict[str, int] = {}
        self._bonus_calories: int = 0

        self._required_items: List[str] = []
        self._calorie_map: Dict[str, int] = {}
        self._calorie_goal: int = 2000
        self._item_goal: int = 10
        self._goal: str = "both"
        self._specificity: str = "specific"
        self._checked: List[str] = []
        self._check_queue: Dict[str, deque] = {}
        self._connected: bool = False
        self._finished: bool = False

    async def server_auth(self, password_requested: bool = False) -> None:
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict) -> None:
        super().on_package(cmd, args)

        if cmd == "ReceivedItems":
            bonus = 0
            for net_item in self.items_received:
                name = self.item_names[self.game].get(net_item.item, "")
                if name.endswith(" Access"):
                    self._unlocked_restaurants.add(name[:-7])
                elif name in self._calorie_item_values:
                    bonus += self._calorie_item_values[name]
            self._bonus_calories = bonus
            if self._connected:
                self.print_tracker_status()

        elif cmd == "Connected":
            self._connected = True
            # Reset derived state so reconnects don't accumulate duplicates.
            self._required_items = []
            self._check_queue = {}
            self._item_restaurants = {}
            self._calorie_map = {}
            sd = args.get("slot_data", {})

            self._specificity = "specific" if sd.get("item_specificity", 0) == 0 else "generic"
            self._calorie_item_values = sd.get("calorie_item_values", {})
            self._calorie_goal = sd.get("calorie_goal", 2000)
            self._item_goal = sd.get("number_of_items", 10)
            self._goal = {0: "calories", 1: "items", 2: "both"}.get(sd.get("goal", 2), "both")

            for r in sd.get("starting_restaurants", []):
                self._unlocked_restaurants.add(r)

            required_locs = sd.get("required_locations", [])
            name_to_id = {name: lid for lid, name in self.location_names[self.game].items()}
            id_to_display: Dict[int, str] = {}

            for loc in required_locs:
                specific_key = f"{loc['restaurant']}: {loc['name']}"
                display = (specific_key if self._specificity == "specific"
                           else loc.get("generic_name", loc["name"]))
                self._required_items.append(display)
                self._calorie_map[display] = loc["calories"]
                self._item_restaurants.setdefault(display, set()).add(loc["restaurant"])
                loc_id = name_to_id.get(specific_key)
                if loc_id is not None:
                    self._check_queue.setdefault(display, deque()).append(loc_id)
                    id_to_display[loc_id] = display

            already_checked = set(args.get("checked_locations", []))
            pending = self.locations_checked - already_checked
            if pending:
                async_start(self.check_locations(list(pending)))
            self._checked = [id_to_display[lid] for lid in already_checked if lid in id_to_display]

            mode = "Specific" if self._specificity == "specific" else "Generic"
            logger.info(f"Connected!  Goal={self._goal}  Items={self._item_goal}  Calories={self._calorie_goal}  Mode={mode}")
            logger.info("Commands: /eat <n>  /list  /tracker")

    def _is_accessible(self, display_name: str) -> bool:
        restaurants = self._item_restaurants.get(display_name, set())
        return any(r in self._unlocked_restaurants for r in restaurants)

    def _eaten_calories(self) -> int:
        return sum(self._calorie_map.get(i, DEFAULT_CALORIES) for i in self._checked) + self._bonus_calories

    def print_tracker_status(self) -> None:
        if not self._required_items:
            logger.info("Not connected to a game yet.")
            return

        eaten_cals = self._eaten_calories()
        unchecked = [i for i in self._required_items if i not in self._checked]
        available = [i for i in unchecked if self._is_accessible(i)]
        locked = [i for i in unchecked if not self._is_accessible(i)]

        logger.info(f"Eaten: {len(self._checked)}/{len(self._required_items)} items   Cals: {eaten_cals} kcal")

        if self._goal in ("calories", "both"):
            pct = min(100, int(eaten_cals / self._calorie_goal * 100))
            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
            logger.info(f"Calorie Goal  [{bar}] {pct:>3}%  ({eaten_cals}/{self._calorie_goal})")

        if self._goal in ("items", "both"):
            pct = min(100, int(len(self._checked) / self._item_goal * 100))
            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
            logger.info(f"Item Goal     [{bar}] {pct:>3}%  ({len(self._checked)}/{self._item_goal})")

        if available:
            logger.info(f"Available ({len(available)}):")
            for i, item in enumerate(available, 1):
                logger.info(f"  [{i:>2}]  {item}  (~{self._calorie_map.get(item, DEFAULT_CALORIES)} kcal)")
        if locked:
            logger.info(f"Locked ({len(locked)}):")
            for item in locked:
                logger.info(f"  [--]  {item}  (~{self._calorie_map.get(item, DEFAULT_CALORIES)} kcal)  [LOCKED]")

    def eat_item(self, number: str) -> None:
        if not self._required_items:
            logger.warning("Not connected to a game yet.")
            return

        unchecked = [i for i in self._required_items if i not in self._checked]
        available = [i for i in unchecked if self._is_accessible(i)]

        if not number.isdigit():
            logger.warning(f"Usage: /eat <number>  (1–{len(available)})")
            return

        idx = int(number) - 1
        if not (0 <= idx < len(available)):
            logger.warning(f"Invalid number (1–{len(available)}).")
            return

        item = available[idx]
        self._checked.append(item)
        logger.info(f"Checked off: {item}  (~{self._calorie_map.get(item, DEFAULT_CALORIES)} kcal)")

        queue = self._check_queue.get(item)
        if queue:
            async_start(self.check_locations([queue.popleft()]))

        self._check_win()
        self.print_tracker_status()

    def list_eaten(self) -> None:
        if not self._checked:
            logger.info("Nothing eaten yet.")
            return
        logger.info("Eaten so far:")
        for item in self._checked:
            logger.info(f"  {item}  (~{self._calorie_map.get(item, DEFAULT_CALORIES)} kcal)")

    def _check_win(self) -> None:
        if self._finished:
            return
        eaten_cals = self._eaten_calories()
        cal_done = self._goal in ("calories", "both") and eaten_cals >= self._calorie_goal
        item_done = self._goal in ("items", "both") and len(self._checked) >= self._item_goal
        won = (
            (self._goal == "both"     and cal_done and item_done) or
            (self._goal == "calories" and cal_done)               or
            (self._goal == "items"    and item_done)
        )
        if won:
            self._finished = True
            logger.info("GOAL COMPLETE! Fast Foodipelago run finished!")
            async_start(self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}]))

    def run_gui(self) -> None:
        from kvui import GameManager

        class FastFoodManager(GameManager):
            logging_pairs = [("Client", "Archipelago")]
            base_title = "Archipelago Fast Foodipelago Client"

        self.ui = FastFoodManager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")


def main() -> None:
    Utils.init_logging("FastFoodClient", exception_logger="Client")

    async def _main(args):
        ctx = FastFoodContext(args.connect, args.password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()
        await ctx.exit_event.wait()
        await ctx.shutdown()

    import colorama
    colorama.just_fix_windows_console()
    parser = get_base_parser(description="Fast Foodipelago Client")
    args, _ = parser.parse_known_args()
    asyncio.run(_main(args))
    colorama.deinit()


if __name__ == "__main__":
    main()
