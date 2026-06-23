from worlds.AutoWorld import WebWorld, World
from BaseClasses import Region, ItemClassification, Tutorial
from typing import Dict, List, Any, Optional, Set

from worlds.fast_food.Items import FastFoodItem, item_table, item_data_table, FastFoodItemData
from worlds.fast_food.Locations import (
    PIZZA_SIZES, RESTAURANT_DATA, FastFoodLocation,
    location_table, location_name_to_id, FastFoodLocationData,
)
from worlds.fast_food.Options import FastFoodOptions
from worlds.fast_food.Rules import set_completion_rules
from worlds.LauncherComponents import Component, components, Type

components.append(Component(
    "Fast Foodipelago Client",
    script_name="FastFoodClient",
    component_type=Type.CLIENT,
    game_name="Fast Foodipelago",
    description="Manual client for tracking Fast Foodipelago progress.",
))


class FastFoodWebWorld(WebWorld):
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Fast Foodipelago for Archipelago.",
        "English",
        "setup_en.md",
        "setup/en",
        ["levi445"],
    )]


class FastFoodWorld(World):
    """
    Fast Foodipelago – an IRL Archipelago experience where the player visits
    real fast food restaurants, orders specific items, and tracks progress
    toward calorie and/or item-count goals.
    """

    web = FastFoodWebWorld()

    game              = "Fast Foodipelago"
    options_dataclass = FastFoodOptions
    options: FastFoodOptions

    item_name_to_id     = item_table
    location_name_to_id = location_name_to_id

    required_locations:   List[FastFoodLocationData]
    restaurant_pool:      List[str]
    starting_restaurants: List[str]
    menu_locations:       List[FastFoodLocationData]
    total_food_calories:  int
    calorie_item_names:   List[str]
    effective_cal_goal:   int

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def get_filler_item_name(self) -> str:
        return "Fast Food Loyalty Points"

    def create_item(self, name: str) -> "FastFoodItem":
        return FastFoodItem(name, item_data_table[name].type, item_data_table[name].id, player=self.player)

    # Greedy denomination selection: largest first, then fill remainder with 50s.
    _CALORIE_DENOMS = [300, 250, 200, 100, 50]

    def create_items(self) -> None:
        # Starting restaurant Access items are precollected, not placed in the pool.
        for r in self.starting_restaurants:
            self.multiworld.push_precollected(self.create_item(f"{r} Access"))

        available    = list(set(self.restaurant_pool) - set(self.starting_restaurants))
        access_items = [f"{r} Access" for r in available]

        n_filler      = max(0, len(self.required_locations) - len(access_items))
        remaining_gap = max(0, self.options.calorie_goal.value - self.total_food_calories)

        calorie_names: List[str] = []
        for _ in range(n_filler):
            if remaining_gap <= 0:
                calorie_names.append("50 Calories")
            else:
                pick = next((d for d in self._CALORIE_DENOMS if d <= remaining_gap),
                            self._CALORIE_DENOMS[-1])  # smallest if gap < 50
                calorie_names.append(f"{pick} Calories")
                remaining_gap -= pick

        self.calorie_item_names = calorie_names
        self.calorie_item_values = {f"{d} Calories": d for d in self._CALORIE_DENOMS}
        total_cal_items = sum(self.calorie_item_values.get(n, 0) for n in calorie_names)
        self.effective_cal_goal = min(
            self.options.calorie_goal.value,
            self.total_food_calories + total_cal_items,
        )

        # Classify calorie items based on whether the goal uses calories.
        goal_uses_calories = self.options.goal.value != 1  # 0=calories, 2=both → progression
        cal_classification = (
            ItemClassification.progression if goal_uses_calories else ItemClassification.filler
        )

        item_objects = [self.create_item(name) for name in access_items]
        for name in calorie_names:
            obj = self.create_item(name)
            obj.classification = cal_classification
            item_objects.append(obj)

        self.multiworld.itempool += item_objects

    def use_specific(self) -> bool:
        return self.options.item_specificity.value == 0

    def allowed_pizza_sizes(self) -> List[str]:
        sizes = self.options.allowed_pizza_sizes.value
        ordered = [s for s in PIZZA_SIZES if s in sizes]
        return ordered if ordered else PIZZA_SIZES

    def build_pool(self) -> List[FastFoodLocationData]:
        opts = self.options
        banned: Set[str] = set(opts.banned_items.value)

        restaurants = (
            list(opts.available_restaurants.value)
            if opts.available_restaurants.value
            else list(RESTAURANT_DATA.keys())
        )

        excluded = set(opts.excluded_restaurants.value)
        restaurants = [r for r in restaurants if r not in excluded]

        # User-specified hard cap on total restaurants.
        max_total = opts.max_restaurants.value
        if len(restaurants) > max_total:
            restaurants = self.random.sample(restaurants, max_total)

        # Structural cap: non-starters can't usefully exceed total item slots.
        n_start = min(opts.starting_restaurants.value, len(restaurants))
        max_non_starting = opts.number_of_items.value + opts.excess_items.value
        if len(restaurants) - n_start > max_non_starting:
            restaurants = self.random.sample(restaurants, n_start + max_non_starting)

        # Check minimum after all reductions so the guarantee reflects the final pool.
        min_total = opts.minimum_restaurants.value
        if len(restaurants) < min_total:
            raise Exception(
                f"Fast Foodipelago: only {len(restaurants)} restaurant(s) available after filtering "
                f"but minimum_restaurants is {min_total}. "
                f"Reduce minimum_restaurants or adjust your restaurant settings."
            )

        self.restaurant_pool = restaurants
        self.starting_restaurants = self.random.sample(restaurants, n_start)

        categories: List[str] = []
        if not opts.exclude_food.value:
            categories.append("Food")
        if not opts.exclude_desserts.value:
            categories.append("Dessert")
        if not opts.exclude_drinks.value:
            categories.append("Drink")

        cal_cap = opts.calorie_cap_per_item.value
        cal_min = opts.min_calories_per_item.value

        pool: List[FastFoodLocationData] = []
        for location in location_table:
            if location.category not in categories:
                continue
            if location.restaurant not in self.restaurant_pool:
                continue
            ban_key = location.specific_name if self.use_specific() else location.generic_name
            if ban_key in banned:
                continue
            if location.is_pizza and location.pizza_size not in self.allowed_pizza_sizes():
                continue
            if cal_cap > 0 and location.calories > cal_cap:
                continue
            if cal_min > 0 and location.calories < cal_min:
                continue
            pool.append(location)

        return pool

    def pick_required(
        self,
        pool: List[FastFoodLocationData],
        prioritize: Optional[List[str]] = None,
    ) -> List[FastFoodLocationData]:
        opts    = self.options
        needed  = opts.number_of_items.value + opts.excess_items.value
        max_per      = opts.max_items_per_restaurant.value
        generic_mode = not self.use_specific()

        shuffled = pool.copy()
        self.random.shuffle(shuffled)

        chosen:     List[FastFoodLocationData] = []
        per_rest:   Dict[str, int] = {}
        name_count: Dict[str, int] = {}
        chosen_ids: Set[int] = set()

        def can_add(loc: FastFoodLocationData) -> bool:
            if per_rest.get(loc.restaurant, 0) >= max_per:
                return False
            if generic_mode and name_count.get(loc.generic_name, 0) > 0:
                return False
            return True

        def add(loc: FastFoodLocationData) -> None:
            chosen.append(loc)
            per_rest[loc.restaurant]     = per_rest.get(loc.restaurant, 0) + 1
            name_count[loc.generic_name] = name_count.get(loc.generic_name, 0) + 1
            chosen_ids.add(id(loc))

        # Guarantee minimum items per restaurant FIRST so later phases can't consume those slots.
        min_per = self.options.min_items_per_restaurant.value
        if min_per > 0:
            for restaurant in self.restaurant_pool:
                if len(chosen) >= needed:
                    break
                for loc in shuffled:
                    if per_rest.get(restaurant, 0) >= min_per:
                        break
                    if len(chosen) >= needed:
                        break
                    if loc.restaurant == restaurant and id(loc) not in chosen_ids and can_add(loc):
                        add(loc)

        use_meals = (
            self.options.attempt_to_create_meals.value
            and not self.options.exclude_food.value
            and not self.options.exclude_drinks.value
            and not self.options.exclude_desserts.value
        )

        if use_meals:
            # Starting restaurants first so they claim budget before non-starters.
            ordered = list(prioritize or []) + [r for r in self.restaurant_pool if r not in (prioritize or [])]
            by_rest_cat: Dict[str, Dict[str, List[FastFoodLocationData]]] = {}
            for loc in shuffled:
                by_rest_cat.setdefault(loc.restaurant, {}).setdefault(loc.category, []).append(loc)

            for restaurant in ordered:
                if len(chosen) >= needed:
                    break
                for category in ("Food", "Drink", "Dessert"):
                    if len(chosen) >= needed:
                        break
                    for loc in by_rest_cat.get(restaurant, {}).get(category, []):
                        if id(loc) not in chosen_ids and can_add(loc):
                            add(loc)
                            break
        else:
            # Reserve at least one slot per starting restaurant so they're always visible.
            if prioritize:
                for restaurant in prioritize:
                    if len(chosen) >= needed:
                        break
                    for loc in shuffled:
                        if loc.restaurant == restaurant and can_add(loc):
                            add(loc)
                            break

        # Ensure at least starting_items total come from starting restaurants.
        if prioritize:
            starter_set = set(prioritize)
            target_starters = min(self.options.starting_items.value, needed)
            starter_count = sum(1 for c in chosen if c.restaurant in starter_set)
            for loc in shuffled:
                if starter_count >= target_starters or len(chosen) >= needed:
                    break
                if loc.restaurant in starter_set and id(loc) not in chosen_ids and can_add(loc):
                    add(loc)
                    starter_count += 1

        # Fill remaining slots from the full pool.
        for loc in shuffled:
            if len(chosen) >= needed:
                break
            if id(loc) in chosen_ids:
                continue
            if can_add(loc):
                add(loc)

        return chosen

    # ------------------------------------------------------------------
    # Archipelago lifecycle
    # ------------------------------------------------------------------

    def generate_early(self) -> None:
        self.required_locations   = []
        self.restaurant_pool      = []
        self.starting_restaurants = []
        self.menu_locations       = []
        self.total_food_calories  = 0
        self.calorie_item_names   = []
        self.effective_cal_goal   = 0

        pool = self.build_pool()
        if not pool:
            raise Exception(
                "Fast Foodipelago: item pool is empty — check your exclusion/banned settings."
            )

        min_per = self.options.min_items_per_restaurant.value
        needed  = self.options.number_of_items.value + self.options.excess_items.value
        if min_per > 0 and needed < len(self.restaurant_pool) * min_per:
            raise Exception(
                f"Fast Foodipelago: number_of_items + excess_items ({needed}) is too low to guarantee "
                f"min_items_per_restaurant ({min_per}) across all {len(self.restaurant_pool)} restaurants "
                f"(need at least {len(self.restaurant_pool) * min_per}). "
                f"Raise number_of_items, lower min_items_per_restaurant, or reduce max_restaurants."
            )

        chosen = self.pick_required(pool, prioritize=self.starting_restaurants)
        if not chosen:
            raise Exception(
                "Fast Foodipelago: could not select enough required items from the available pool."
            )

        self.required_locations = chosen

        starting_pool = [loc for loc in chosen if loc.restaurant in self.starting_restaurants]
        if not starting_pool:
            raise Exception(
                "Fast Foodipelago: no items are accessible from the start — "
                "all items from your starting restaurants were banned or excluded. "
                "Reduce banned_items or check your exclusion settings."
            )
        n_menu = min(self.options.starting_items.value, len(starting_pool))
        self.random.shuffle(starting_pool)
        self.menu_locations = starting_pool[:n_menu]

        self.total_food_calories = sum(loc.calories for loc in chosen)

    def create_regions(self) -> None:
        menu_region = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu_region)

        goal_location = FastFoodLocation(self.player, "Finish the Meal", None, menu_region)
        goal_location.place_locked_item(
            FastFoodItem("Fast Foodipelago Victory", ItemClassification.progression, None, self.player)
        )
        menu_region.locations.append(goal_location)

        menu_loc_names: Set[str] = {
            f"{loc.restaurant}: {loc.specific_name}" for loc in self.menu_locations
        }
        for loc in self.menu_locations:
            loc_name = f"{loc.restaurant}: {loc.specific_name}"
            loc_id   = self.location_name_to_id[loc_name]
            menu_region.locations.append(
                FastFoodLocation(self.player, loc_name, loc_id, menu_region)
            )

        for restaurant in self.restaurant_pool:
            region = Region(restaurant, self.player, self.multiworld)
            self.multiworld.regions.append(region)

            for loc in self.required_locations:
                if loc.restaurant == restaurant:
                    loc_name = f"{restaurant}: {loc.specific_name}"
                    if loc_name not in menu_loc_names:
                        loc_id = self.location_name_to_id[loc_name]
                        region.locations.append(
                            FastFoodLocation(self.player, loc_name, loc_id, region)
                        )

            if restaurant in self.starting_restaurants:
                menu_region.connect(region)
            else:
                menu_region.connect(
                    region,
                    rule=lambda state, r=restaurant: state.has(f"{r} Access", self.player),
                )

    def set_rules(self) -> None:
        set_completion_rules(self, self.player)

    # ------------------------------------------------------------------
    # Slot data
    # ------------------------------------------------------------------

    def fill_slot_data(self) -> Dict[str, Any]:
        return {
            "goal":             self.options.goal.value,
            "calorie_goal":     self.effective_cal_goal,
            "number_of_items":  min(self.options.number_of_items.value, len(self.required_locations)),
            "item_specificity": self.options.item_specificity.value,
            "required_locations": [
                {
                    "name":         loc.specific_name,
                    "generic_name": loc.generic_name,
                    "restaurant":   loc.restaurant,
                    "calories":     loc.calories,
                }
                for loc in self.required_locations
            ],
            "calorie_item_values":  self.calorie_item_values,
            "restaurants":          self.restaurant_pool,
            "starting_restaurants": self.starting_restaurants,
        }
