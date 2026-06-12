"""
Generation tests for Fast Foodipelago.
Each class with non-empty options automatically runs:
  - test_all_state_can_reach_everything
  - test_empty_state_can_reach_something
  - test_fill
"""
from collections import Counter

from . import FastFoodTestBase


class TestCaloriesGoal(FastFoodTestBase):
    options = {"goal": 0, "calorie_goal": 1500, "number_of_items": 5}


class TestItemsGoal(FastFoodTestBase):
    options = {"goal": 1, "number_of_items": 8}


class TestBothGoal(FastFoodTestBase):
    options = {"goal": 2, "calorie_goal": 2000, "number_of_items": 8}


class TestGenericMode(FastFoodTestBase):
    options = {"item_specificity": 1, "number_of_items": 8}

    def test_no_duplicate_generic_names(self):
        """In generic mode, the same generic name should not appear twice in required_locations."""
        names = [loc.generic_name for loc in self.world.required_locations]
        counts = Counter(names)
        duplicates = [name for name, count in counts.items() if count > 1]
        self.assertEqual(duplicates, [], f"Duplicate generic names: {duplicates}")


class TestExcessItems(FastFoodTestBase):
    options = {"excess_items": 5, "number_of_items": 8}

    def test_location_count_respects_excess(self):
        """required_locations should not exceed number_of_items + excess_items."""
        cap = (self.world.options.number_of_items.value
               + self.world.options.excess_items.value)
        self.assertLessEqual(len(self.world.required_locations), cap)


class TestExcludedRestaurants(FastFoodTestBase):
    options = {
        "excluded_restaurants": {"Pizza Hut", "Domino's", "Papa John's"},
        "number_of_items": 8,
    }

    def test_excluded_restaurants_not_in_pool(self):
        for restaurant in ("Pizza Hut", "Domino's", "Papa John's"):
            self.assertNotIn(restaurant, self.world.restaurant_pool,
                             f"{restaurant} should be excluded from pool")


class TestAllCategoriesWithMeals(FastFoodTestBase):
    options = {
        "exclude_drinks": 0,
        "exclude_desserts": 0,
        "exclude_food": 0,
        "attempt_to_create_meals": 1,
        "number_of_items": 12,
    }


class TestSmallOnlyPizzas(FastFoodTestBase):
    options = {
        "available_restaurants": {"Pizza Hut"},
        "allowed_pizza_sizes": {"Small"},
        "number_of_items": 5,
        "max_restaurants": 1,
        "minimum_restaurants": 1,
        "starting_restaurants": 1,
    }

    def test_only_small_pizza_sizes_in_pool(self):
        for loc in self.world.required_locations:
            if loc.is_pizza:
                self.assertEqual(loc.pizza_size, "Small",
                                 f"{loc.specific_name} should be Small only")


class TestMinItemsPerRestaurant(FastFoodTestBase):
    """With min_items=2 and ample items needed, every restaurant must contribute at least 2."""
    options = {
        "min_items_per_restaurant": 2,
        "number_of_items": 16,
        "max_restaurants": 4,
        "starting_restaurants": 2,
        "exclude_drinks": 0,
        "exclude_desserts": 0,
    }

    def test_each_restaurant_meets_minimum(self):
        min_per = self.world.options.min_items_per_restaurant.value
        counts = Counter(loc.restaurant for loc in self.world.required_locations)
        for restaurant in self.world.restaurant_pool:
            self.assertGreaterEqual(
                counts[restaurant], min_per,
                f"{restaurant} has {counts[restaurant]} items, expected >= {min_per}",
            )


class TestSingleStartingRestaurant(FastFoodTestBase):
    options = {
        "starting_restaurants": 1,
        "max_restaurants": 2,
        "number_of_items": 6,
        "max_items_per_restaurant": 3,
    }


class TestManyRestaurants(FastFoodTestBase):
    options = {
        "max_restaurants": 8,
        "number_of_items": 20,
        "starting_restaurants": 3,
        "excess_items": 4,
    }


class TestCalorieCapPerItem(FastFoodTestBase):
    """Items above calorie_cap_per_item must not appear in required_locations."""
    options = {
        "calorie_cap_per_item": 900,
        "number_of_items": 8,
        "max_restaurants": 4,
    }

    def test_no_items_exceed_calorie_cap(self):
        cap = self.world.options.calorie_cap_per_item.value
        for loc in self.world.required_locations:
            self.assertLessEqual(
                loc.calories, cap,
                f"{loc.restaurant}: {loc.specific_name} has {loc.calories} cal, cap is {cap}",
            )


class TestMinCaloriesPerItem(FastFoodTestBase):
    """Items below min_calories_per_item must not appear in required_locations."""
    options = {
        "min_calories_per_item": 300,
        "exclude_drinks": 0,
        "number_of_items": 8,
        "max_restaurants": 4,
    }

    def test_no_items_below_calorie_minimum(self):
        cal_min = self.world.options.min_calories_per_item.value
        for loc in self.world.required_locations:
            self.assertGreaterEqual(
                loc.calories, cal_min,
                f"{loc.restaurant}: {loc.specific_name} has {loc.calories} cal, min is {cal_min}",
            )


class TestCalorieRangeFilter(FastFoodTestBase):
    """Both calorie_cap_per_item and min_calories_per_item filter simultaneously."""
    options = {
        "calorie_cap_per_item": 800,
        "min_calories_per_item": 300,
        "exclude_drinks": 0,
        "number_of_items": 6,
        "max_restaurants": 4,
    }

    def test_all_items_within_calorie_range(self):
        cap = self.world.options.calorie_cap_per_item.value
        cal_min = self.world.options.min_calories_per_item.value
        for loc in self.world.required_locations:
            self.assertGreaterEqual(
                loc.calories, cal_min,
                f"{loc.restaurant}: {loc.specific_name} has {loc.calories} cal, below min {cal_min}",
            )
            self.assertLessEqual(
                loc.calories, cap,
                f"{loc.restaurant}: {loc.specific_name} has {loc.calories} cal, above cap {cap}",
            )
