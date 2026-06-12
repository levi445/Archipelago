# Fast Foodipelago Setup Guide

## What Is This?

Fast Foodipelago is a real-life Archipelago experience. You visit actual fast food restaurants,
order specific items, eat them, and check them off using the client. Your progress sends items
to other players in the multiworld.

**Note: This world is not recommended for synchronous games or races!** 

## Installation

Save the `.apworld` file into the `custom_worlds` folder inside your Archipelago installation.

## Configuring Your YAML

Generate a template YAML from the Archipelago website or Launcher, then adjust options such as:

- **Goal** — calories, item count, or both
- **Number of Items** — how many items you must eat to win
- **Calorie Goal** — total calories required (if goal includes calories)
- **Starting Restaurants** — how many restaurants are unlocked from the start
- **Excluded Restaurants** — restaurants you want removed from the pool
- **Allowed Pizza Sizes** — which pizza sizes are eligible (Small / Medium / Large)
- **Calorie Cap Per Item** — exclude items above a calorie threshold (e.g. 2000 to skip giant brownies)
- **Min Calories Per Item** — exclude items below a calorie threshold (e.g. 200 to skip trivial drinks)

## Playing

1. After the multiworld is generated, open the **Fast Foodipelago Client** from the Archipelago Launcher.
2. Connect to the server: `/connect <host>:<port>` then enter your slot name when prompted.
3. Run `/list` to see all your required items and their numbers.
4. Go to the restaurant, order the item, eat it IRL, then run `/eat <number>` to check it off.
5. Run `/tracker` at any time to see your progress toward the goal.

## Commands

| Command | Description |
|---------|-------------|
| `/list` | Show all required items with their check numbers |
| `/eat <n>` | Mark item number `n` as eaten and send the check |
| `/tracker` | Display current progress toward your goal |

## Notes

- Items are locked to specific restaurants in **Specific** mode (default). In **Generic** mode,
  items use a plain description and can be fulfilled at any restaurant carrying that item type.
- Starting restaurants are accessible immediately. Other restaurants unlock when you receive
  their Access item from the multiworld.
- You can reconnect at any time — the client will resync your checked locations automatically.
