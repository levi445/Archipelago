"""
Multi-seed stress tests for Fast Foodipelago.

For each option profile, generates N seeds and asserts:
  1. Starting restaurants: empty state reaches >= 1 location
  2. Item goal: all-state satisfies _items_met (enough locations reachable)
  3. Calorie goal: all-state satisfies _calories_met (food + calorie items >= goal)
  4. Beatable: fill succeeds and game can be completed
"""
import typing
import unittest
from argparse import Namespace

from Generate import get_seed_name
from BaseClasses import MultiWorld, CollectionState
from worlds import AutoWorld
from worlds.AutoWorld import call_all
from worlds.fast_food.Rules import _calories_met, _items_met
import random

from test.general import gen_steps


PROFILES: typing.List[typing.Dict[str, typing.Any]] = [
    # --- defaults ---
    {"label": "defaults"},
    # --- goal variations ---
    {"label": "goal=calories", "goal": 0, "calorie_goal": 1500},
    {"label": "goal=items",    "goal": 1, "number_of_items": 8},
    {"label": "goal=both",     "goal": 2, "calorie_goal": 2000, "number_of_items": 8},
    # --- starting restaurant counts ---
    {"label": "start=1", "starting_restaurants": 1, "max_restaurants": 3, "number_of_items": 6},
    {"label": "start=3", "starting_restaurants": 3, "max_restaurants": 5, "number_of_items": 10},
    # --- excess items ---
    {"label": "excess=5", "excess_items": 5, "number_of_items": 8},
    # --- calorie cap/min filters ---
    {"label": "cal_cap=900",  "calorie_cap_per_item": 900,  "number_of_items": 8, "max_restaurants": 4},
    {"label": "cal_min=300",  "min_calories_per_item": 300, "number_of_items": 8, "max_restaurants": 4, "exclude_drinks": 0},
    {"label": "cal_range",    "calorie_cap_per_item": 800, "min_calories_per_item": 300,
                               "number_of_items": 6, "max_restaurants": 4, "exclude_drinks": 0},
    # --- high calorie goal, tight item count (stresses calorie-item generation) ---
    {"label": "high_cal_goal", "goal": 0, "calorie_goal": 5000, "number_of_items": 5, "max_restaurants": 3},
    # --- meals mode ---
    {"label": "meals", "exclude_drinks": 0, "exclude_desserts": 0, "exclude_food": 0,
                        "attempt_to_create_meals": 1, "number_of_items": 12},
    # --- generic mode ---
    {"label": "generic", "item_specificity": 1, "number_of_items": 8},
    # --- many restaurants ---
    {"label": "many_restaurants", "max_restaurants": 8, "number_of_items": 20,
                                   "starting_restaurants": 3, "excess_items": 4},
    # --- pizza only ---
    {"label": "pizza_small_only", "available_restaurants": {"Pizza Hut"}, "allowed_pizza_sizes": {"Small"},
                                   "number_of_items": 4, "max_restaurants": 1,
                                   "minimum_restaurants": 1, "starting_restaurants": 1},
]

SEEDS_PER_PROFILE = 20
GAME = "Fast Foodipelago"


def build_world(options: typing.Dict[str, typing.Any], seed: int) -> typing.Tuple[MultiWorld, AutoWorld.World]:
    mw = MultiWorld(1)
    mw.game[1] = GAME
    mw.player_name = {1: "Tester"}
    mw.set_seed(seed)
    random.seed(mw.seed)
    mw.seed_name = get_seed_name(random)

    args = Namespace()
    world_cls = AutoWorld.AutoWorldRegister.world_types[GAME]
    for name, option in world_cls.options_dataclass.type_hints.items():
        setattr(args, name, {1: option.from_any(options.get(name, option.default))})
    mw.set_options(args)
    mw.state = CollectionState(mw)
    world = mw.worlds[1]
    for step in gen_steps:
        call_all(mw, step)
    return mw, world


class TestMultiSeed(unittest.TestCase):
    """Runs SEEDS_PER_PROFILE seeds for each option profile."""

    def _run_profile(self, label: str, options: typing.Dict[str, typing.Any]) -> None:
        base_seed = abs(hash(label)) % (2 ** 31)
        for i in range(SEEDS_PER_PROFILE):
            seed = base_seed + i
            with self.subTest(profile=label, seed=seed):
                try:
                    mw, world = build_world(options, seed)
                except Exception as exc:
                    self.fail(f"Generation failed: {exc}")

                player = 1
                all_state = mw.get_all_state(False)

                # 1. Starting restaurants: empty state reaches >= 1 location.
                empty_state = CollectionState(mw)
                reachable_from_start = mw.get_reachable_locations(empty_state, player)
                self.assertGreater(
                    len(reachable_from_start), 0,
                    f"Empty state reached 0 locations — starting restaurants have no accessible locations. "
                    f"Starting: {world.starting_restaurants}",
                )

                goal = world.options.goal.value

                # 2. Item goal achievable (goal 1 or 2).
                if goal != 0:
                    self.assertTrue(
                        _items_met(all_state, world, player),
                        f"Item goal not met with all items. "
                        f"needed={world.options.number_of_items.value}, "
                        f"locations={[f'{l.restaurant}: {l.specific_name}' for l in world.required_locations]}",
                    )

                # 3. Calorie goal achievable (goal 0 or 2).
                if goal != 1:
                    self.assertTrue(
                        _calories_met(all_state, world, player),
                        f"Calorie goal not met with all items. "
                        f"goal={world.options.calorie_goal.value}, "
                        f"food_cals={world.total_food_calories}, "
                        f"calorie_items={world.calorie_item_names}",
                    )

                # 4. Beatable (completion condition satisfied).
                self.assertTrue(
                    mw.can_beat_game(all_state),
                    "Game not beatable with all items collected.",
                )


# Dynamically generate one test method per profile so failures report
# which profile broke, not just a generic TestMultiSeed.
def _make_test(label: str, options: typing.Dict[str, typing.Any]):
    def test_method(self):
        self._run_profile(label, options)
    test_method.__name__ = f"test_profile_{label.replace('=', '_').replace(' ', '_')}"
    return test_method


for _profile in PROFILES:
    _label = _profile.pop("label")
    _opts = dict(_profile)
    _method = _make_test(_label, _opts)
    setattr(TestMultiSeed, _method.__name__, _method)
