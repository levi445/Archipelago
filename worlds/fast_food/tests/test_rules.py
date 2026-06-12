"""
Access rule and completion condition tests for Fast Foodipelago.
"""
from BaseClasses import CollectionState

from . import FastFoodTestBase


class TestAccessRules(FastFoodTestBase):
    """Verify region locking/unlocking with Access items."""
    options = {
        "starting_restaurants": 1,
        "max_restaurants": 3,
        "number_of_items": 8,
        "max_items_per_restaurant": 3,
    }

    def test_starting_restaurants_reachable_from_start(self):
        state = CollectionState(self.multiworld)
        for restaurant in self.world.starting_restaurants:
            with self.subTest(restaurant=restaurant):
                self.assertTrue(state.can_reach(restaurant, "Region", self.player),
                                f"{restaurant} should be accessible without any items")

    def test_non_starting_restaurants_locked_without_access(self):
        state = CollectionState(self.multiworld)
        non_starting = [r for r in self.world.restaurant_pool
                        if r not in self.world.starting_restaurants]
        for restaurant in non_starting:
            with self.subTest(restaurant=restaurant):
                self.assertFalse(state.can_reach(restaurant, "Region", self.player),
                                 f"{restaurant} should require its Access item")

    def test_non_starting_restaurants_unlock_with_access(self):
        non_starting = [r for r in self.world.restaurant_pool
                        if r not in self.world.starting_restaurants]
        for restaurant in non_starting:
            with self.subTest(restaurant=restaurant):
                state = CollectionState(self.multiworld)
                for item in self.multiworld.itempool:
                    if item.name == f"{restaurant} Access" and item.player == self.player:
                        state.collect(item)
                        break
                self.assertTrue(state.can_reach(restaurant, "Region", self.player),
                                f"{restaurant} should be accessible with its Access item")

    def test_starting_locations_reachable_at_game_start(self):
        """At least one non-event location must be reachable with no items."""
        state = CollectionState(self.multiworld)
        reachable = [loc for loc in self.multiworld.get_reachable_locations(state, self.player)
                     if loc.address is not None]
        self.assertGreater(len(reachable), 0,
                           "No food locations are accessible from game start")


class TestCompletionCondition(FastFoodTestBase):
    """Verify the Victory event and goal conditions."""
    options = {
        "starting_restaurants": 1,
        "max_restaurants": 3,
        "number_of_items": 8,
        "max_items_per_restaurant": 3,
    }

    def test_game_not_won_with_empty_state(self):
        state = CollectionState(self.multiworld)
        self.assertFalse(self.multiworld.completion_condition[self.player](state),
                         "Game should not be won from empty state")

    def test_game_won_with_all_state(self):
        state = self.multiworld.get_all_state()
        self.assertTrue(self.multiworld.completion_condition[self.player](state),
                        "Game should be winnable with all items")

    def test_victory_location_exists(self):
        location = self.multiworld.get_location("Finish the Meal", self.player)
        self.assertIsNotNone(location)
        self.assertIsNone(location.address, "Finish the Meal should be an event location")
        self.assertIsNotNone(location.item)
        self.assertEqual(location.item.name, "Fast Foodipelago Victory")


class TestCalorieItemClassification(FastFoodTestBase):
    """Calorie items should be progression when goal includes calories."""
    options = {"goal": 0}

    def test_calorie_items_are_progression(self):
        calorie_items = [item for item in self.multiworld.itempool
                         if "Calories" in item.name and item.player == self.player]
        self.assertGreater(len(calorie_items), 0, "Expected calorie items in pool")
        for item in calorie_items:
            self.assertTrue(item.advancement,
                            f"{item.name} should be progression for a calories goal")


class TestItemsGoalCalorieClassification(FastFoodTestBase):
    """Calorie items should NOT be progression when goal is items-only."""
    options = {"goal": 1}

    def test_calorie_items_are_not_progression(self):
        calorie_items = [item for item in self.multiworld.itempool
                         if "Calories" in item.name and item.player == self.player]
        for item in calorie_items:
            self.assertFalse(item.advancement,
                             f"{item.name} should not be progression for an items-only goal")


class TestItemLocationBalance(FastFoodTestBase):
    """Item pool size must equal non-event location count."""
    options = {"number_of_items": 10, "excess_items": 3}

    def test_item_count_equals_location_count(self):
        locations = [loc for loc in self.multiworld.get_locations(self.player)
                     if loc.address is not None]
        pool_items = [item for item in self.multiworld.itempool
                      if item.player == self.player]
        self.assertEqual(
            len(pool_items), len(locations),
            f"Pool has {len(pool_items)} items but {len(locations)} locations",
        )


class TestAccessItemsAreProgression(FastFoodTestBase):
    """All restaurant Access items must always be progression."""
    options = {"max_restaurants": 6, "number_of_items": 12}

    def test_access_items_classified_progression(self):
        access_items = [item for item in self.multiworld.itempool
                        if item.name.endswith(" Access") and item.player == self.player]
        self.assertGreater(len(access_items), 0, "Expected Access items in pool")
        for item in access_items:
            self.assertTrue(item.advancement,
                            f"{item.name} should always be progression")
