# Fast Foodipelago Setup Guide

## What Is This?

Fast Foodipelago is a real-life Archipelago experience. You visit actual fast food restaurants,
order specific items, eat them, and check them off using the client. Your progress sends items
to other players in the multiworld.

**Note: This world is not recommended for synchronous games or races!**

## Requirements

- [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases/latest) (official installer is fine)
- `fast_foodipelago.apworld` and `FastFoodClient.py` from the [Fast Foodipelago release](https://github.com/levi445/fast-foodipelago/releases/latest)

## Installation

1. Open the Archipelago Launcher.
2. Click **Install APWorld** and select `fast_foodipelago.apworld`.
3. Drop `FastFoodClient.py` into your Archipelago install folder (the same folder as `ArchipelagoLauncher.exe`, typically `C:\ProgramData\Archipelago`).

The **Fast Foodipelago Client** button will then appear in the Archipelago Launcher.

## Configuring Your YAML

Download the template YAML from the release and adjust options to taste:

- **Goal** — `calories`, `items`, or `both` (default)
- **Calorie Goal** — total calories required when goal includes calories (default: 2000)
- **Number of Items** — how many items you must eat when goal includes items (default: 10)
- **Starting Restaurants** — how many restaurants are unlocked from the start (default: 2)
- **Max Restaurants** — cap on how many restaurants appear in your game (default: 4)
- **Excluded Restaurants** — restaurants you never want in your pool
- **Allowed Pizza Sizes** — which sizes are eligible for pizza restaurants (Small / Medium / Large)
- **Calorie Cap Per Item** — exclude items above this calorie count (0 = no cap)
- **Min Calories Per Item** — exclude items below this calorie count (0 = no minimum)
- **Excess Items** — extra locations beyond your goal, so you can skip some items

## Playing

1. After the multiworld is generated, open the **Fast Foodipelago Client** from the Archipelago Launcher, or run `python FastFoodClient.py` directly.
2. Connect to the server: `/connect <host>:<port>` then enter your slot name when prompted.
3. Run `/tracker` to see your available items and their numbers.
4. Go to the restaurant, order the item, eat it IRL, then run `/eat <number>` to check it off.
5. Run `/tracker` again at any time to see updated progress.

## Commands

| Command | Description |
|---------|-------------|
| `/tracker` | Show progress toward your goal and list available items with numbers |
| `/eat <n>` | Mark available item number `n` as eaten and send the check |
| `/list` | Show all items you have eaten so far |

## Notes

- Items are locked to specific restaurants in **Specific** mode (default). In **Generic** mode,
  items use a plain description and can be fulfilled at any restaurant carrying that item type.
- Starting restaurants are accessible immediately. Other restaurants unlock when you receive
  their `<Restaurant> Access` item from the multiworld.
- Locked items show as `[LOCKED]` in `/tracker` — you cannot eat them until the restaurant unlocks.
- You can reconnect at any time — the client resyncs your checked locations automatically.
