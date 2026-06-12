
def set_completion_rules(world, player) -> None:
    world.multiworld.completion_condition[player] = (
        lambda state: state.has("Fast Foodipelago Victory", player)
    )

    goal_location = world.multiworld.get_location("Finish the Meal", player)
    goal = world.options.goal.value

    if goal == 0:
        goal_location.access_rule = lambda state: _calories_met(state, world, player)
    elif goal == 1:
        goal_location.access_rule = lambda state: _items_met(state, world, player)
    else:
        goal_location.access_rule = lambda state: (
            _calories_met(state, world, player) and _items_met(state, world, player)
        )


def _items_met(state, world, player) -> bool:
    needed = world.options.number_of_items.value
    reachable = sum(
        1 for loc in world.required_locations
        if state.can_reach(f"{loc.restaurant}: {loc.specific_name}", "Location", player)
    )
    return reachable >= needed


def _calories_met(state, world, player) -> bool:
    food_cals = sum(
        loc.calories for loc in world.required_locations
        if state.can_reach(f"{loc.restaurant}: {loc.specific_name}", "Location", player)
    )
    cal_items = sum(
        state.count(f"{d} Calories", player) * d
        for d in world._CALORIE_DENOMS
    )
    return (food_cals + cal_items) >= world.effective_cal_goal
