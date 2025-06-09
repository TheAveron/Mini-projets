import random
from math import sqrt
from typing import TypedDict

size = 100
grid_size = size * size
grid_side = int(sqrt(grid_size))


assert grid_side * grid_side == grid_size, "Grid size must be a perfect square."
print(f"Size of the grid: {grid_side}x{grid_side}")


class Tile(TypedDict):
    name: str
    weight: float
    allowed_neighbors: set[int]


table: dict[int, int] = {i: 0 for i in range(size * size)}
queue: dict[int, set[int]] = {i: set() for i in range(1, 9)}

tiles: dict[int, Tile] = {
    0: {"name": "empty", "weight": 0, "allowed_neighbors": {0}},
    1: {"name": "grass", "weight": 0.26, "allowed_neighbors": {1, 3, 2, 4}},
    2: {"name": "water", "weight": 0.15, "allowed_neighbors": {2, 1, 8}},
    3: {"name": "forest", "weight": 0.20, "allowed_neighbors": {1, 3, 4}},
    4: {"name": "mountain", "weight": 0.10, "allowed_neighbors": {3, 4, 6}},
    5: {"name": "desert", "weight": 0.08, "allowed_neighbors": {1, 5}},
    6: {"name": "snow", "weight": 0.07, "allowed_neighbors": {4, 6}},
    7: {"name": "volcano", "weight": 0.01, "allowed_neighbors": {4, 7}},
    8: {"name": "swamp", "weight": 0.03, "allowed_neighbors": {2, 1, 8}},
}


def get_top(n: int) -> int | None:
    """Returns the number of the element in top on the table."""
    if n < grid_side:
        return None
    return n - grid_side


def get_bottom(n: int) -> int | None:
    """Returns the number of the element in bottom on the table."""
    if n >= len(table) - grid_side:
        return None
    return n + grid_side


def get_left(n: int) -> int | None:
    """Returns the number of the element in left on the table."""
    if n % grid_side == 0:
        return None
    return n - 1


def get_right(n: int) -> int | None:
    """Returns the number of the element in right on the table."""
    if (n + 1) % grid_side == 0:
        return None
    return n + 1


def get_neighbors(n: int) -> list[int]:
    """Returns the list of neighbors for the given element."""
    setted_elements = {
        get_top(n),
        get_bottom(n),
        get_left(n),
        get_right(n),
    }

    return [element for element in setted_elements if element is not None]


def possible_tiles(n: int) -> set[int]:
    """Returns the set of possible tiles for the given element."""
    possible = set(tiles.keys())

    for neighbor in get_neighbors(n):
        if neighbor is None or table[neighbor] == 0:
            continue
        possible &= tiles[table[neighbor]]["allowed_neighbors"]

    return possible


def resolve_impossible(n: int):
    """Resolve impossible tiles for the given element."""

    neighbors = get_neighbors(n)

    for neighbor in neighbors:
        if table[neighbor] != 0:
            table[neighbor] = 0

    queue[7].add(n)
    for neighbor in neighbors:
        queue[len(possible_tiles(neighbor))].add(neighbor)


def main():

    queue[8].add(random.randint(0, len(table) - 1))

    counter = 0

    while queue:
        counter += 1

        filter_result = list(filter(lambda x: len(queue[x]) > 0, queue))
        if not filter_result:
            print("No more elements in the queue to process.")
            break

        # print(f"###### Iteration {counter} ######\nQueue: {queue}\nfilter results: {filter_result}")
        i = min(list(filter_result))

        n = queue[i].pop()

        if table[n] != 0:
            continue

        possible_tiles_set = possible_tiles(n)

        if not possible_tiles_set:
            resolve_impossible(n)
            continue

        table[n] = random.choices(
            list(possible_tiles_set),
            weights=[
                tiles[tile]["weight"] for tile in tiles if tile in possible_tiles_set
            ],
            k=1,
        )[0]

        for neighbor in get_neighbors(n):
            if table[neighbor] != 0:
                continue

            possible = possible_tiles(neighbor)
            if not possible:
                resolve_impossible(neighbor)
                continue
            queue[len(possible)].add(neighbor)

    print(f"Final table after {counter} iterations:")


def print_table():
    for i in range(grid_side):
        print(
            " ".join(tiles[table[i * grid_side + j]]["name"] for j in range(grid_side))
        )
    print()


if __name__ == "__main__":
    main()

    print("Final table:")
    print_table()
    print("Final queue:")
    print(queue)
