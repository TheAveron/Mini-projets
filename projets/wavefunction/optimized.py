import heapq
import random
from collections import deque
from functools import lru_cache
from time import perf_counter, perf_counter_ns
from typing import Dict, List, Tuple

from PIL import Image

from profiler import profile_with_memory

# --- Configuration ---
GRID_SIZE = 300
TILE_IDS = range(9)
choosen_distrib = "normal"  # Change this to select a distribution

COUNTER = 0


# --- Tile Definitions ---
class Tile:
    def __init__(self, name: str, weight: float, neighbors: set[int]):
        self.name: str = name
        self.weight: float = weight
        self.neighbors: set[int] = neighbors  # Set of valid adjacent tile IDs


distributions = {
    "uniform": [0.1 for _ in TILE_IDS] + [0.1],
    "normal": [0, 0.4, 0.25, 0.2, 0.05, 0.05, 0.03, 0.01, 0.01],
    "polarized": [0, 0.4, 0.2, 0.25, 0.05, 0.02, 0.02, 0.01, 0.05],
    "gradient": [0.05, 0.22, 0.15, 0.18, 0.1, 0.08, 0.1, 0.1, 0.02],
    "custom1": [0, 0.24, 0.2, 0.2, 0.14, 0.05, 0.1, 0.02, 0.05],
    "custom2": [0.01, 0.15, 0.01, 0.02, 0.1, 0.05, 0.1, 0.51, 0.05],
}


for key, value in distributions.items():
    assert (
        abs(sum(value) - 1.0) < 1e-6
    ), f"Probas must be equal to 1, not {sum(value)} for {key}"


TILES: Dict[int, Tile] = {
    0: Tile("empty", 0, {0}),
    1: Tile("grass", 0.45, {1, 3, 2, 4}),
    2: Tile("water", 0.18, {2, 1, 8}),
    3: Tile("forest", 0.2, {1, 3, 4}),
    4: Tile("mountain", 0.05, {3, 4, 6}),
    5: Tile("desert", 0.05, {1, 5}),
    6: Tile("snow", 0.05, {4, 6}),
    7: Tile("volcano", 0.01, {4, 7}),
    8: Tile("swamp", 0.01, {2, 1, 8}),
}  # default distribution, normal

for tile in TILE_IDS:
    value = distributions[choosen_distrib][tile]
    TILES[tile].weight = value
    # print(value)

print(sum(tile.weight for tile in TILES.values()))

TILE_COLOR_RGB = {
    0: (40, 40, 40),  # empty (dark grey)
    1: (34, 139, 34),  # grass (green)
    2: (30, 144, 255),  # water (dodger blue)
    3: (0, 100, 0),  # forest (dark green)
    4: (128, 128, 128),  # mountain (grey)
    5: (237, 201, 175),  # desert (light sand)
    6: (255, 250, 250),  # snow (white)
    7: (255, 69, 0),  # volcano (red-orange)
    8: (85, 107, 47),  # swamp (dark olive green)
}


DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]

BITMASK = (1 << len(TILES)) - 1


# --- Grid Cell Representation ---
class Cell:
    def __init__(self):
        self.domain = BITMASK  # Bitmask of possible tiles (all set)
        self.collapsed = False

    # def is_collapsed(self) -> bool:
    #    return bin(self.domain).count("1") == 1

    def entropy(self) -> int:
        return bin(self.domain).count("1")

    def get_possible_ids(self) -> List[int]:
        return [i for i in TILE_IDS if self.domain & (1 << i)]

    def collapse(self):
        options = self.get_possible_ids()
        weights = [TILES[t].weight for t in options]
        chosen = random.choices(options, weights=weights, k=1)[0]
        self.domain = 1 << chosen
        self.collapsed = True
        return chosen

    def collapse_with_bias(self, neighbor_counts: dict[int, int]) -> int:
        options = self.get_possible_ids()
        raw_weights = [TILES[t].weight for t in options]

        biased_weights = [
            raw_weights[i] + 0.3 * neighbor_counts.get(options[i], 0)
            for i in range(len(options))
        ]

        chosen = random.choices(options, weights=biased_weights, k=1)[0]
        self.domain = 1 << chosen
        self.collapsed = True
        return chosen


# --- World State ---
class World:
    def __init__(self, size: int = 100):
        self.size = GRID_SIZE
        self.grid = [[Cell() for _ in range(self.size)] for _ in range(self.size)]
        self.heap = []  # Min-heap for cells by entropy
        # self.queue = deque() # Queue for propagation
        # self.in_heap = [[False for _ in range(self.size)] for _ in range(self.size)]
        self.counter = 0

    @lru_cache(maxsize=GRID_SIZE * GRID_SIZE)
    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.size and 0 <= y < self.size

    @lru_cache(maxsize=GRID_SIZE * GRID_SIZE)
    def neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        return [
            (x + dx, y + dy) for dx, dy in DIRECTIONS if self.in_bounds(x + dx, y + dy)
        ]

    # @profile_with_memory
    def run(self):
        # Start with one random seed
        sx, sy = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
        # self.queue.append((sx, sy))

        # Initial heap population
        for y in range(self.size):
            for x in range(self.size):
                if not self.grid[y][x].collapsed:
                    entropy = self.grid[y][x].entropy()
                    heapq.heappush(self.heap, (entropy, random.random(), x, y))

        while self.heap:
            _, _, x, y = heapq.heappop(self.heap)
            cell: Cell = self.grid[y][x]

            if cell.collapsed:
                continue

            neighbor_counts = None  # self.count_tile_types_around(x, y)
            if not neighbor_counts:
                chosen_tile = cell.collapse()
                self.counter += 1
            else:
                chosen_tile = cell.collapse_with_bias(neighbor_counts)

            self.propagate(x, y, chosen_tile)

    def propagate(self, x: int, y: int, tile_id: int):
        queue = deque([(x, y)])

        while queue:
            cx, cy = queue.popleft()
            cell = self.grid[cy][cx]

            for nx, ny in self.neighbors(cx, cy):
                neighbor = self.grid[ny][nx]
                if neighbor.collapsed:
                    continue

                new_domain = 0

                for t in cell.get_possible_ids():
                    allowed = TILES[t].neighbors
                    for nt in neighbor.get_possible_ids():
                        if nt in allowed:
                            new_domain |= 1 << nt

                if new_domain != neighbor.domain:
                    neighbor.domain = new_domain
                    if neighbor.domain == 0:
                        raise Exception(f"Contradiction at ({nx}, {ny})")
                    queue.append((nx, ny))
                    # enqueue updated entropy
                    # if not self.in_heap[ny][nx]:
                    #   self.in_heap[ny][nx] = True
                    heapq.heappush(
                        self.heap, (neighbor.entropy(), random.random(), nx, ny)
                    )

    def count_tile_types_around(self, x: int, y: int) -> dict[int, int]:
        counts = {}
        for nx, ny in self.neighbors(x, y):
            cell = self.grid[ny][nx]
            if cell.collapsed:
                tid = cell.get_possible_ids()[0]
                counts[tid] = counts.get(tid, 0) + 1
        return counts


def post_process_cleaner(world, iterations=3):
    size = world.size

    for _ in range(iterations):
        # Make a copy of current states to avoid influencing this iteration
        new_domains = [[cell.domain for cell in row] for row in world.grid]

        for y in range(size):
            for x in range(size):
                cell: Cell = world.grid[y][x]
                if not cell.collapsed:
                    continue

                neighbors = [
                    (nx, ny)
                    for nx, ny in world.neighbors(x, y)
                    if world.grid[ny][nx].collapsed
                ]

                if not neighbors:
                    continue

                # Count neighbors' tile types
                neighbor_tiles = [
                    world.grid[ny][nx].get_possible_ids()[0] for nx, ny in neighbors
                ]
                tile_counts = {}
                for t in neighbor_tiles:
                    tile_counts[t] = tile_counts.get(t, 0) + 1

                majority_tile = max(tile_counts, key=tile_counts.get)  # type: ignore
                current_tile = cell.get_possible_ids()[0]

                # If current tile differs from majority and majority is strong enough, flip it
                if (
                    current_tile != majority_tile
                    and tile_counts[majority_tile] >= len(neighbors) // 2 + 1
                ):
                    new_domains[y][x] = 1 << majority_tile

        # Apply changes after checking whole grid
        for y in range(size):
            for x in range(size):
                world.grid[y][x].domain = new_domains[y][x]


def post_process_cleaner_respecting_rules(world, iterations=3):
    size = world.size

    for _ in range(iterations):
        # Copy current domains to allow batch updates
        new_domains = [[cell.domain for cell in row] for row in world.grid]

        for y in range(size):
            for x in range(size):
                cell: Cell = world.grid[y][x]
                if not cell.collapsed:
                    continue

                current_tile = cell.get_possible_ids()[0]

                # Get collapsed neighbors
                neighbor_coords = [
                    (nx, ny)
                    for nx, ny in world.neighbors(x, y)
                    if world.grid[ny][nx].collapsed
                ]

                if not neighbor_coords:
                    continue

                neighbor_tiles = [
                    world.grid[ny][nx].get_possible_ids()[0]
                    for nx, ny in neighbor_coords
                ]

                # Count tile types around
                tile_counts = {}
                for tid in neighbor_tiles:
                    tile_counts[tid] = tile_counts.get(tid, 0) + 1

                # Most common neighbor tile
                majority_tile = max(tile_counts, key=tile_counts.get)  # type: ignore
                if majority_tile == current_tile:
                    continue  # already matches

                # Check if this majority tile can validly replace current one
                majority_allowed = True
                for nx, ny in neighbor_coords:
                    neighbor_tile = world.grid[ny][nx].get_possible_ids()[0]
                    if (
                        majority_tile not in TILES[neighbor_tile].neighbors
                        or neighbor_tile not in TILES[majority_tile].neighbors
                    ):
                        majority_allowed = False
                        break

                if (
                    majority_allowed
                    and tile_counts[majority_tile] >= len(neighbor_tiles) // 2 + 1
                ):
                    new_domains[y][x] = 1 << majority_tile

        # Apply new domains
        for y in range(size):
            for x in range(size):
                world.grid[y][x].domain = new_domains[y][x]


# --- Output ---
def print_world(world: World):
    for row in world.grid:
        line = " ".join(
            TILES[cell.get_possible_ids()[0]].name[0] if cell.collapsed else "?"
            for cell in row
        )
        print(line)


def export_image(world: World, pixel_size=10, filename="wfc_output.jpg"):
    size = world.size
    img = Image.new("RGB", (size * pixel_size, size * pixel_size))

    for y in range(size):
        for x in range(size):
            cell = world.grid[y][x]
            if cell.collapsed:
                tile_id = cell.get_possible_ids()[0]
                color = TILE_COLOR_RGB[tile_id]
            else:
                color = (0, 0, 0)  # Uncollapsed cells are black

            for dy in range(pixel_size):
                for dx in range(pixel_size):
                    img.putpixel((x * pixel_size + dx, y * pixel_size + dy), color)

    img.save(filename)
    print(f"[\u2714] Exported WFC output to {filename}")


# --- Run the WFC ---
if __name__ == "__main__":
    world = World()
    try:
        t1 = perf_counter()
        world.run()
        t2 = perf_counter()
        print(t2 - t1)
        post_process_cleaner_respecting_rules(world, iterations=5)
        export_image(world, pixel_size=8, filename="wfc_map.jpg")
        print(world.counter)
    except Exception as e:
        print(f"[ERROR] Generation failed: {e}")
