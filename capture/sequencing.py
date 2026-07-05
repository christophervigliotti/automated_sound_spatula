"""Reusable helper for the order in which a giblet works through a list of items."""

import random


def pop_by_direction(items: list, direction: str, last_side: str = None) -> tuple:
    """Pop the next item from `items` (mutated in place).

    `direction` is one of:
    - "forward": always pop from the front.
    - "backward": always pop from the end.
    - "alternating-random": pop from a randomly chosen end each call.
    - "alternating-toggle": strictly alternates ends, starting with the front.

    Returns (item, side_used); pass `side_used` back in as `last_side` on the
    next call so "alternating-toggle" keeps toggling correctly.
    """
    if direction == "forward":
        side = "front"
    elif direction == "backward":
        side = "back"
    elif direction == "alternating-random":
        side = random.choice(["front", "back"])
    elif direction == "alternating-toggle":
        side = "back" if last_side == "front" else "front"
    else:
        raise ValueError(f"unknown direction: {direction}")

    item = items.pop(0) if side == "front" else items.pop()
    return item, side
