from dataclasses import dataclass

from Options import Range, PerGameCommonOptions, Toggle, Choice, OptionSet
from worlds.fast_food.Locations import RESTAURANT_DATA, PIZZA_SIZES

class GoalChoice(Choice):
    """What the player must accomplish to finish the game."""
    display_name    = "Goal"
    option_calories = 0
    option_items    = 1
    option_both     = 2
    default         = 2


class CalorieGoal(Range):
    """Total calories the player must consume (used when goal includes calories)."""
    display_name = "Calorie Goal"
    range_start  = 500
    range_end    = 10000
    default      = 2000


class NumberOfItems(Range):
    """Number of food items the player must eat (used when goal includes items)."""
    display_name = "Number of Items Goal"
    range_start  = 1
    range_end    = 30
    default      = 10


class ItemSpecificity(Choice):
    """
    Specific: items are tied to a named restaurant (e.g. 'McDonalds: Big Mac').
    Generic:  items use a plain description and can be fulfilled at any
              restaurant that carries that type of item.
    """
    display_name    = "Item Specificity"
    option_specific = 0
    option_generic  = 1
    default         = 0


class ExcludeDrinks(Toggle):
    """Exclude drinks from the required item pool."""
    display_name = "Exclude Drinks"
    default      = 1   # excluded by default — drinks are largely interchangeable


class ExcludeDesserts(Toggle):
    """Exclude desserts from the required item pool."""
    display_name = "Exclude Desserts"
    default      = 0


class ExcludeFood(Toggle):
    """Exclude main food items from the required item pool."""
    display_name = "Exclude Food Items"
    default      = 0


class AttemptToCreateMeals(Toggle):
    """
    Try to build balanced meals by picking one Food, one Drink, and one Dessert
    per restaurant when selecting required items. Only takes effect when
    Exclude Food Items, Exclude Drinks, and Exclude Desserts are all disabled.
    """
    display_name = "Attempt to Create Meals"
    default      = 1


class NumberOfStartingRestaurants(Range):
    """How many restaurants are unlocked at the start."""
    display_name = "Starting Restaurants"
    range_start  = 1
    range_end    = 10
    default      = 2


class NumberOfStartingItems(Range):
    """
    How many item locations are accessible at the start.
    The actual count may be lower if the starting restaurants
    don't have enough eligible items after bans and exclusions,
    or if this value exceeds the Number of Items Goal.
    """
    display_name = "Starting Items"
    range_start  = 1
    range_end    = 10
    default      = 4


class MinItemsPerRestaurant(Range):
    """
    Minimum number of required items from each restaurant in the pool.
    If a restaurant cannot supply this many items after bans and exclusions,
    generation picks as many as available rather than failing.
    0 means no minimum enforced.
    """
    display_name = "Min Items Per Restaurant"
    range_start  = 0
    range_end    = 15
    default      = 0


class MaxItemsPerRestaurant(Range):
    """Maximum number of required items from a single restaurant."""
    display_name = "Max Items Per Restaurant"
    range_start  = 1
    range_end    = 15
    default      = 5


class AllowedPizzaSizes(OptionSet):
    """
    Which pizza sizes are eligible for pizza restaurant items.
    Only relevant when Pizza Hut, Domino's, or Papa John's are in the pool.
    At least one size must be selected; if empty, all sizes are allowed.
    """
    display_name = "Allowed Pizza Sizes"
    valid_keys   = PIZZA_SIZES
    default      = frozenset(PIZZA_SIZES)   # all sizes allowed by default


class BannedItems(OptionSet):
    """
    Items that will never be added to the required list.
    In specific mode use the full name (e.g. 'Big Mac').
    In generic mode use the generic name (e.g. 'Burger').
    Leave empty to ban nothing.
    """
    display_name = "Banned Items"
    valid_keys   = []   # accepts any string; unrecognised values are silently ignored
    default      = frozenset()


class AvailableRestaurants(OptionSet):
    """
    Which restaurants to draw items from.
    Leave empty to use all restaurants.
    Possible values: McDonald's, Burger King, Wendy's, Taco Bell, Pizza Hut, Papa John's
    Domino's, Sonic, Arby's, Hardee's, Dairy Queen, KFC, Chick-fil-A, Popeyes, Subway, Culver's
    """
    display_name = "Available Restaurants"
    valid_keys   = list(RESTAURANT_DATA.keys())
    default      = frozenset()


class ExcludedRestaurants(OptionSet):
    """
    Restaurants that will never appear in the pool.
    Takes priority over Available Restaurants — a restaurant in both lists is excluded.
    Leave empty to exclude nothing.
    Possible values: McDonald's, Burger King, Wendy's, Taco Bell, Pizza Hut, Papa John's
    Domino's, Sonic, Arby's, Hardee's, Dairy Queen, KFC, Chick-fil-A, Popeyes, Subway, Culver's
    """
    display_name = "Excluded Restaurants"
    valid_keys   = list(RESTAURANT_DATA.keys())
    default      = frozenset()


class MaxRestaurants(Range):
    """
    Maximum number of restaurants allowed. If more restaurants are available than this limit, randomly selects this many.
    """
    display_name = "Max Restaurants"
    range_start  = 1
    range_end    = 16
    default      = 4


class MinimumRestaurants(Range):
    """
    Minimum number of restaurants that must be available after all filtering.
    Generation fails if Available Restaurants, Excluded Restaurants, and Max Restaurants
    together leave fewer restaurants than this value.
    """
    display_name = "Minimum Restaurants"
    range_start  = 1
    range_end    = 16
    default      = 1


class ExcessItems(Range):
    """
    Number of extra item locations added beyond the goal count.
    With excess items the player has more locations than they need to check,
    giving flexibility in which items to eat. 0 means no excess.
    """
    display_name = "Excess Items"
    range_start  = 0
    range_end    = 20
    default      = 0


class CalorieCapPerItem(Range):
    """
    Maximum calories allowed for a single required item. Items above this threshold
    are excluded from the pool. 0 means no cap.
    Useful for preventing a 2000-cal brownie from dominating a calorie goal.
    """
    display_name = "Calorie Cap Per Item"
    range_start  = 0
    range_end    = 3000
    default      = 0


class MinCaloriesPerItem(Range):
    """
    Minimum calories required for a single item to be eligible.
    Items below this threshold are excluded from the pool. 0 means no minimum.
    Useful for filtering trivially low-calorie items like a 80-cal drink.
    """
    display_name = "Min Calories Per Item"
    range_start  = 0
    range_end    = 1000
    default      = 0


@dataclass
class FastFoodOptions(PerGameCommonOptions):
    goal:                      GoalChoice
    calorie_goal:              CalorieGoal
    number_of_items:           NumberOfItems
    item_specificity:          ItemSpecificity
    exclude_drinks:            ExcludeDrinks
    exclude_desserts:          ExcludeDesserts
    exclude_food:              ExcludeFood
    attempt_to_create_meals:   AttemptToCreateMeals
    starting_restaurants:      NumberOfStartingRestaurants
    starting_items:            NumberOfStartingItems
    min_items_per_restaurant:  MinItemsPerRestaurant
    max_items_per_restaurant:  MaxItemsPerRestaurant
    allowed_pizza_sizes:       AllowedPizzaSizes
    banned_items:              BannedItems
    available_restaurants:     AvailableRestaurants
    excluded_restaurants:      ExcludedRestaurants
    max_restaurants:           MaxRestaurants
    minimum_restaurants:       MinimumRestaurants
    excess_items:              ExcessItems
    calorie_cap_per_item:      CalorieCapPerItem
    min_calories_per_item:     MinCaloriesPerItem
