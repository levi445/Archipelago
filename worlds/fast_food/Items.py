from typing import Dict, NamedTuple

from BaseClasses import ItemClassification, Item

class FastFoodItem(Item):
    game = "Fast Foodipelago"

class FastFoodItemData(NamedTuple):
    id: int
    type: ItemClassification


item_data_table: Dict[str, FastFoodItemData] = {
    # Restaurant access items (one per restaurant in RESTAURANT_DATA)
    "McDonald's Access":  FastFoodItemData(173, ItemClassification.progression),
    "Burger King Access": FastFoodItemData(174, ItemClassification.progression),
    "Wendy's Access":     FastFoodItemData(175, ItemClassification.progression),
    "Taco Bell Access":   FastFoodItemData(178, ItemClassification.progression),
    "Pizza Hut Access":   FastFoodItemData(179, ItemClassification.progression),
    "Sonic Access":       FastFoodItemData(180, ItemClassification.progression),
    "Arby's Access":      FastFoodItemData(181, ItemClassification.progression),
    "Hardee's Access":    FastFoodItemData(182, ItemClassification.progression),
    "Dairy Queen Access": FastFoodItemData(183, ItemClassification.progression),
    "KFC Access":         FastFoodItemData(184, ItemClassification.progression),
    "Domino's Access":    FastFoodItemData(185, ItemClassification.progression),
    "Papa John's Access": FastFoodItemData(186, ItemClassification.progression),
    "Chick-fil-A Access": FastFoodItemData(187, ItemClassification.progression),
    "Popeyes Access":     FastFoodItemData(188, ItemClassification.progression),
    "Subway Access":      FastFoodItemData(189, ItemClassification.progression),
    "Culver's Access":    FastFoodItemData(190, ItemClassification.progression),
    # Calorie bonus items (classification overridden at generation time based on goal)
    "50 Calories":        FastFoodItemData(176, ItemClassification.filler),
    "100 Calories":       FastFoodItemData(177, ItemClassification.filler),
    "200 Calories":       FastFoodItemData(191, ItemClassification.filler),
    "250 Calories":       FastFoodItemData(192, ItemClassification.filler),
    "300 Calories":             FastFoodItemData(193, ItemClassification.filler),
    "Fast Food Loyalty Points": FastFoodItemData(194, ItemClassification.filler),
}

item_table = {name: data.id for name, data in item_data_table.items()}
