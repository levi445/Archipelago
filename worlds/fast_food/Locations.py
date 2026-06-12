from typing import Set, Dict, List, Tuple, NamedTuple, Optional

from BaseClasses import Location

PIZZA_SIZES: List[str] = ["Small", "Medium", "Large"]

# Pizza restaurants and their pizza types (specific_name, generic_name, {size: calories})
# Sizes absent from cal_per_size (e.g. Stuffed Crust Large-only) are skipped at table build time.
PIZZA_TYPES: Dict[str, List[Tuple[str, str, Dict[str, int]]]] = {
    "Pizza Hut": [
        ("Pepperoni Pizza",               "Pepperoni Pizza",               {"Small": 1104, "Medium": 1888, "Large": 2584}),
        ("Cheese Pizza",                  "Cheese Pizza",                  {"Small":  944, "Medium": 1568, "Large": 2184}),
        ("Supreme Pizza",                 "Supreme Pizza",                 {"Small": 1584, "Medium": 2688, "Large": 3864}),
    ],
    "Domino's": [
        ("Pepperoni Pizza",               "Pepperoni Pizza",               {"Small": 1200, "Medium": 1680, "Large": 2360}),
        ("Cheese Pizza",                  "Cheese Pizza",                  {"Small": 1170, "Medium": 1600, "Large": 2280}),
        ("Philly Cheese Steak Pizza",     "Philly Cheese Steak Pizza",     {"Small": 1360, "Medium": 1850, "Large": 2480}),
        ("Chicken Bacon Ranch Pizza",     "Chicken Bacon Ranch Pizza",     {"Small": 1560, "Medium": 2400, "Large": 3280}),
        ("MeatZZa (Meat Lovers Pizza)",   "Meat Lovers Pizza",             {"Small": 1560, "Medium": 2100, "Large": 2960}),
        ("The People's Pizza (Deluxe)",   "Deluxe Pizza",                  {"Small": 1440, "Medium": 1950, "Large": 2720}),
    ],
    "Papa John's": [
        ("Pepperoni Pizza",               "Pepperoni Pizza",               {"Small": 1260, "Medium": 1840, "Large": 2560}),
        ("Cheese Pizza",                  "Cheese Pizza",                  {"Small": 1080, "Medium": 1520, "Large": 2160}),
        ("The Meat's Pizza",              "Meat Lovers Pizza",             {"Small": 1500, "Medium": 2080, "Large": 3040}),
        ("The Works Pizza",               "Deluxe Pizza",                  {"Small": 1380, "Medium": 1840, "Large": 2720}),
        ("Chicken Bacon Ranch Pizza",     "Chicken Bacon Ranch Pizza",     {"Small": 1440, "Medium": 2080, "Large": 2960}),
        ("Philly Cheese Steak Pizza",     "Philly Cheese Steak Pizza",     {"Small": 1440, "Medium": 2000, "Large": 2880}),
        ("Stuffed Crust Pepperoni Pizza", "Stuffed Crust Pepperoni Pizza", {"Large": 3040}),
    ],
}

# fmt: off
# Each tuple: (specific_name, generic_name, calories)
RESTAURANT_DATA: Dict[str, Dict[str, List[Tuple[str, str, int]]]] = {
    "McDonald's": {
        "food": [
            ("Big Mac",                          "Burger",                           580),
            ("10 Piece McNuggets",               "Chicken Nuggets",                  410),
            ("Filet-O-Fish",                     "Fish Sandwich",                    380),
            ("McChicken",                        "Chicken Sandwich",                 390),
            ("McDouble",                         "Burger",                           390),
            ("Quarter Pounder with Cheese",      "Burger",                           520),
        ],
        "dessert": [
            ("Oreo McFlurry",                    "Ice Cream",                        410),
            ("M&M McFlurry",                     "Ice Cream",                        570),
            ("Hot Fudge Sundae",                 "Sundae",                           330),
        ],
        "drink": [
            ("Sprite Berry Blast",               "Soda",                             390),
            ("Dirty Dr Pepper",                  "Soda",                             410),
            ("Orange Dream",                     "Soda",                             430),
        ],
    },
    "Burger King": {
        "food": [
            ("Whopper",                          "Burger",                           710),
            ("8 Piece Crown Nuggets",            "Chicken Nuggets",                  440),
            ("Double Cheeseburger",              "Burger",                           460),
            ("Bacon Double Cheeseburger",        "Burger",                           500),
            ("Chicken Fries",                    "Chicken Fries",                    220),
            ("Original Chicken Sandwich",        "Chicken Sandwich",                 680),
            ("Royal Crispy Chicken",             "Chicken Sandwich",                 600),
        ],
        "dessert": [
            ("Oreo Sundae",                      "Sundae",                           310),
            ("Hershey's Sundae",                 "Sundae",                           230),
            ("BK Cinnamon Apple Pie",            "Pie",                              270),
        ],
        "drink": [
            ("Signature Strawberry Lemonade",    "Lemonade",                         500),
            ("Signature Watermelon Lemonade",    "Lemonade",                         380),
        ],
    },
    "Taco Bell": {
        "food": [
            ("Crunchwrap Supreme",               "Wrap",                             530),
            ("Doritos Locos Taco",               "Taco",                             170),
            ("Cheesy Gordita Crunch",            "Gordita",                          480),
            ("Soft Taco",                        "Taco",                             180),
            ("Chalupa Supreme",                  "Chalupa",                          350),
        ],
        "dessert": [
            ("Cinnabon Delights",                "Cinnamon Bites",                   170),
            ("Cinnamon Twists",                  "Cinnamon Twists",                  170),
        ],
        "drink": [
            ("Baja Blast",                       "Slushie",                          420),
            ("Baja Midnight",                    "Slushie",                          420),
            ("Strawberry Passionfruit Agua Refresca", "Agua Fresca",                 170),
        ],
    },
    "Pizza Hut": {
        "food": [
            ("8 Piece Boneless Wings",           "Wings",                            800),
            ("6 Piece Traditional Wings",        "Wings",                            642),
            ("Buffalo Chicken Melt",             "Flatbread",                        1185),
        ],
        "dessert": [
            ("Triple Chocolate Brownie",         "Brownie",                          2070),
            ("Cinnabon Mini Rolls",              "Cinnamon Roll",                    800),
            ("Ultimate Chocolate Chip Cookie",   "Cookie",                           1520),
        ],
        "drink": [],
    },
    "Sonic": {
        "food": [
            ("Tots",                             "Tots",                             360),
            ("Sonic Cheeseburger",               "Burger",                           700),
            ("All American Sonic Smasher",       "Burger",                           610),
            ("SuperSonic Double Cheeseburger",   "Burger",                           1040),
            ("Corn Dog",                         "Corn Dog",                         230),
            ("Chili Cheese Coney",               "Hot Dog",                          470),
        ],
        "dessert": [
            ("Sonic Blast with Oreo",            "Ice Cream",                        770),
            ("Sonic Blast with Reese's",         "Ice Cream",                        890),
            ("Strawberry Classic Shake",         "Milkshake",                        690),
            ("Chocolate Classic Shake",          "Milkshake",                        720),
        ],
        "drink": [
            ("Watermelon Peach Refresher",       "Slushie",                          80),
            ("Strawberry Passionfruit Refresher","Slushie",                          100),
            ("Cherry Limeade",                   "Limeade",                          240),
            ("Cranberry Limeade",                "Limeade",                          240),
        ],
    },
    "Wendy's": {
        "food": [
            ("Baconator",                        "Burger",                           890),
            ("Dave's Double",                    "Burger",                           810),
            ("Son of Baconator",                 "Burger",                           590),
            ("Big Bacon Classic Double",         "Burger",                           860),
            ("Jr. Bacon Cheeseburger",           "Burger",                           350),
            ("10 Piece Nuggets",                 "Chicken Nuggets",                  430),
            ("Classic Asiago Ranch Club Sandwich","Chicken Sandwich",                670),
            ("10 Piece Spicy Nuggets",           "Spicy Chicken Nuggets",            470),
        ],
        "dessert": [
            ("Frosty",                           "Milkshake",                        510),
        ],
        "drink": [
            ("Watermelon Lemonade",              "Lemonade",                         260),
            ("Pineapple Mango Lemonade",         "Lemonade",                         420),
            ("Strawberry Lemonade",              "Lemonade",                         220),
        ],
    },
    "Arby's": {
        "food": [
            ("Classic Roast Beef",               "Sandwich",                         360),
            ("Beef 'n Cheddar",                  "Sandwich",                         450),
            ("Mozzarella Sticks",                "Mozzarella Sticks",                440),
            ("Ham & Swiss Melt",                 "Sandwich",                         380),
            ("Chicken Cordon Bleu",              "Chicken Sandwich",                 650),
            ("Potato Cakes",                     "Potato Cakes",                     250),
        ],
        "dessert": [
            ("Orange Cream Shake",               "Milkshake",                        550),
            ("Peach Cobbler Rolls",              "Pastry",                           350),
            ("Apple Turnover",                   "Pastry",                           430),
        ],
        "drink": [
            ("Lemonade",                         "Lemonade",                         110),
            ("Strawberry Lemonade",              "Lemonade",                         220),
        ],
    },
    "Hardee's": {
        "food": [
            ("Mushroom & Swiss Burger (Hardee's)", "Burger",                         580),
            ("Superstar Burger",                 "Burger",                           850),
            ("Double Hardee's Frisco Burger",    "Burger",                           1020),
            ("Double Bacon Cheeseburger",        "Burger",                           910),
            ("Hand-Breaded Chicken Sandwich",    "Chicken Sandwich",                 560),
            ("5 Piece Hand-Breaded Chicken Tenders", "Chicken Tenders",             440),
        ],
        "dessert": [
            ("Mocha Coffee Freeze",              "Milkshake",                        690),
            ("Triple Berry Ice Cream Shake",     "Milkshake",                        750),
            ("Apple Turnover",                   "Pastry",                           430),
            ("Cinnamon Roll",                    "Cinnamon Roll",                    520),
        ],
        "drink": [
            ("Triple Berry Tea",                 "Iced Tea",                         270),
            ("Iced Coffee",                      "Iced Coffee",                      280),
            ("Lemonade",                         "Lemonade",                         110),
        ],
    },
    "Dairy Queen": {
        "food": [
            ("Cheese Deluxe Stackburger",        "Burger",                           620),
            ("Chicken Strip Basket",             "Chicken Tenders",                  1020),
            ("Honey BBQ Chicken Strip Basket",   "Chicken Tenders",                  1140),
            ("Hot Dog",                          "Hot Dog",                          330),
        ],
        "dessert": [
            ("Choco Brownie Extreme Blizzard",   "Blizzard",                         1120),
            ("Dilly Bar",                        "Ice Cream",                        220),
            ("Chocolate Chip Cookie Dough Blizzard", "Blizzard",                    1340),
            ("M&M Milk Chocolate Blizzard",      "Blizzard",                         1100),
            ("Royal Ultimate Choco Brownie Blizzard", "Blizzard",                   1340),
        ],
        "drink": [
            ("Orange Julius",                    "Fruit Drink",                      400),
            ("Fruity Pebbles Shake",             "Milkshake",                        980),
            ("Chocolate Shake",                  "Milkshake",                        920),
            ("Misty Freeze",                     "Slushie",                          340),
            ("Lemonade Sparkler",                "Lemonade",                         320),
        ],
    },
    "KFC": {
        "food": [
            ("Famous Bowl",                      "Bowl",                             590),
            ("2 Piece Chicken Fill Up",          "Fried Chicken",                    810),
            ("Mac and Cheese Bowl",              "Bowl",                             660),
            ("Pot Pie",                          "Pot Pie",                          720),
            ("10 Piece Nuggets",                 "Chicken Nuggets",                  590),
        ],
        "dessert": [
            ("Pie Poppers",                      "Pie",                              340),
        ],
        "drink": [
            ("Lemonade",                         "Lemonade",                         110),
            ("Mountain Dew Sweet Lightning",     "Soda",                             210),
        ],
    },
    "Domino's": {
        "food": [
            ("Garlic Bread Bites",               "Bread",                            210),
            ("5-Cheese Mac and Cheese",          "Mac and Cheese",                   830),
        ],
        "dessert": [
            ("Chocolate Lava Crunch Cake",       "Cake",                             350),
            ("Cinnamon Bread Bites",             "Cinnamon Bites",                   230),
        ],
        "drink": [],
    },
    "Papa John's": {
        "food": [
            ("Chicken Bacon Ranch Sandwich",     "Sandwich",                         780),
            ("Philly Cheesesteak Sandwich",      "Sandwich",                         790),
            ("BBQ Wings",                        "Wings",                            880),
            ("BBQ Boneless Wings",               "Wings",                            640),
        ],
        "dessert": [
            ("Cinnamon Pull Aparts",             "Cinnamon Roll",                    1960),
            ("Chocolate Chip Cookie",            "Cookie",                           1520),
            ("Double Chocolate Chip Brownie",    "Brownie",                          2160),
        ],
        "drink": [],
    },
    "Chick-fil-A": {
        "food": [
            ("Chicken Sandwich",                 "Chicken Sandwich",                 420),
            ("8 Piece Nuggets",                  "Chicken Nuggets",                  250),
            ("Spicy Chicken Sandwich",           "Chicken Sandwich",                 450),
            ("Grilled Chicken Sandwich",         "Chicken Sandwich",                 390),
        ],
        "dessert": [
            ("Chocolate Fudge Brownie",          "Brownie",                          370),
            ("Peach Milkshake",                  "Milkshake",                        600),
            ("Cookies and Cream Milkshake",      "Milkshake",                        630),
        ],
        "drink": [
            ("Pineapple Dragonfruit Sunjoy",     "Soda",                             240),
            ("Pineapple Dragonfruit Lemonade",   "Lemonade",                         290),
            ("Lemonade",                         "Lemonade",                         260),
        ],
    },
    "Popeyes": {
        "food": [
            ("Chicken Sandwich",                 "Chicken Sandwich",                 700),
            ("Spicy Chicken Sandwich",           "Chicken Sandwich",                 700),
            ("3 Piece Signature Chicken",        "Fried Chicken",                    600),
            ("5 Piece Tenders",                  "Chicken Tenders",                  650),
            ("6 Piece Bone-In Wings",            "Wings",                            650),
            ("6 Piece Boneless Wings",           "Wings",                            480),
        ],
        "dessert": [
            ("Cinnamon Apple Pie",               "Pie",                              280),
            ("Strawberry Cream Cheese Pie",      "Pie",                              300),
        ],
        "drink": [
            ("Sweet Tea",                        "Sweet Tea",                        180),
            ("Purple Cane Lemonade",             "Lemonade",                         270),
            ("Mango Sweet Lemonade",             "Lemonade",                         270),
            ("Strawberry Cane Lemonade",         "Lemonade",                         270),
        ],
    },
    "Subway": {
        "food": [
            ("BMT Sub",                          "Sub",                              590),
            ("All-American Club Sub",            "Sub",                              540),
            ("Chicken Bacon Ranch Sub",          "Sub",                              580),
            ("Ham and Turkey Stacker Sub",       "Sub",                              290),
            ("Grilled Chicken Wrap",             "Wrap",                             680),
        ],
        "dessert": [
            ("Chocolate Chip Cookie",            "Cookie",                           210),
            ("Double Chocolate Cookie",          "Cookie",                           210),
            ("White Chip Macadamia Nut Cookie",  "Cookie",                           220),
        ],
        "drink": [],
    },
    "Culver's": {
        "food": [
            ("ButterBurger with Cheese",         "Burger",                           700),
            ("Culver's Deluxe Burger",           "Burger",                           820),
            ("Mushroom & Swiss Burger",          "Burger",                           780),
            ("4 Piece Chicken Tenders",          "Chicken Tenders",                  520),
            ("Crispy Chicken Sandwich",          "Chicken Sandwich",                 690),
        ],
        "dessert": [
            ("Root Beer Float",                  "Float",                            490),
            ("Chocolate Custard",                "Ice Cream",                        280),
            ("Concrete Mixer",                   "Ice Cream",                        820),
            ("Turtle Sundae",                    "Sundae",                           1050),
        ],
        "drink": [
            ("Root Beer",                        "Soda",                             430),
        ],
    },
}
# fmt: on


class FastFoodLocation(Location):
    game = "Fast Foodipelago"


class FastFoodLocationData(NamedTuple):
    specific_name: str
    restaurant: str
    calories: int
    generic_name: str
    category: str
    address: int
    is_pizza:   bool          = False
    pizza_size: Optional[str] = None


def _build_location_table() -> List[FastFoodLocationData]:
    entries = []
    next_id = 198600
    for restaurant, categories in RESTAURANT_DATA.items():
        for cat_key, cat_label in [("food", "Food"), ("dessert", "Dessert"), ("drink", "Drink")]:
            for specific, generic, calories in categories.get(cat_key, []):
                entries.append(FastFoodLocationData(
                    specific_name=specific,
                    restaurant=restaurant,
                    calories=calories,
                    generic_name=generic,
                    category=cat_label,
                    address=next_id,
                ))
                next_id += 1
    # Expand pizza size variants; build_pool() filters by allowed_pizza_sizes at generation time.
    for restaurant, pizza_list in PIZZA_TYPES.items():
        for specific_base, generic_base, cal_per_size in pizza_list:
            for size in PIZZA_SIZES:
                if size not in cal_per_size:
                    continue
                entries.append(FastFoodLocationData(
                    specific_name=f"{specific_base} ({size})",
                    restaurant=restaurant,
                    calories=cal_per_size[size],
                    generic_name=f"{generic_base} ({size})",
                    category="Food",
                    address=next_id,
                    is_pizza=True,
                    pizza_size=size,
                ))
                next_id += 1
    return entries


location_table: List[FastFoodLocationData] = _build_location_table()

# Location names are "{Restaurant}: {specific_name}" to guarantee uniqueness
# (multiple restaurants share the same item name, e.g. "Lemonade", "10 Piece Nuggets").
location_name_to_id: Dict[str, int] = {
    f"{loc.restaurant}: {loc.specific_name}": loc.address
    for loc in location_table
}
