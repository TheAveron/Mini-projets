import heapq
import random
from collections import deque
from typing import Dict, List, Tuple

from PIL import Image

# --- Configuration ---
GRID_SIZE = 100
TILE_IDS = range(9)


# --- Tile Definitions ---
class Tile:
    def __init__(self, name: str, weight: float, neighbors: List[int]):
        self.name = name
        self.weight = weight
        self.neighbors = neighbors  # List of valid adjacent tile IDs


TILES: Dict[int, Tile] = {
    0: Tile("empty", 0.01, [0]),
    1: Tile("grass", 0.26, [1, 3, 2, 4]),
    2: Tile("water", 0.15, [2, 1, 8]),
    3: Tile("forest", 0.20, [1, 3, 4]),
    4: Tile("mountain", 0.10, [3, 4, 6]),
    5: Tile("desert", 0.08, [1, 5]),
    6: Tile("snow", 0.07, [4, 6]),
    7: Tile("volcano", 0.01, [4, 7]),
    8: Tile("swamp", 0.03, [2, 1, 8]),
}

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


# --- Grid Cell Representation ---
class Cell:
    def __init__(self):
        self.domain = (1 << len(TILES)) - 1  # Bitmask of possible tiles (all set)
        self.collapsed = False

    def is_collapsed(self) -> bool:
        return bin(self.domain).count("1") == 1

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


# --- World State ---
class World:
    def __init__(self, size: int):
        self.size = size
        self.grid = [[Cell() for _ in range(size)] for _ in range(size)]
        self.heap = []
        self.queue = deque()

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.size and 0 <= y < self.size

    def neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        return [
            (x + dx, y + dy) for dx, dy in DIRECTIONS if self.in_bounds(x + dx, y + dy)
        ]

    def run(self):
        # Start with one random seed
        sx, sy = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
        self.queue.append((sx, sy))

        # Initial heap population
        for y in range(self.size):
            for x in range(self.size):
                if not self.grid[y][x].is_collapsed():
                    entropy = self.grid[y][x].entropy()
                    heapq.heappush(self.heap, (entropy, random.random(), x, y))

        while self.heap:
            _, _, x, y = heapq.heappop(self.heap)
            cell = self.grid[y][x]

            if cell.is_collapsed():
                continue

            chosen_tile = cell.collapse()
            self.propagate(x, y, chosen_tile)

    def propagate(self, x: int, y: int, tile_id: int):
        queue = deque([(x, y)])

        while queue:
            cx, cy = queue.popleft()
            cell = self.grid[cy][cx]

            for nx, ny in self.neighbors(cx, cy):
                neighbor = self.grid[ny][nx]
                if neighbor.is_collapsed():
                    continue

                before = neighbor.domain
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
                    heapq.heappush(
                        self.heap, (neighbor.entropy(), random.random(), nx, ny)
                    )


# --- Output ---
def print_world(world: World):
    for row in world.grid:
        line = " ".join(
            TILES[cell.get_possible_ids()[0]].name[0] if cell.is_collapsed() else "?"
            for cell in row
        )
        print(line)


def export_image(world: World, pixel_size=10, filename="wfc_output.jpg"):
    size = world.size
    img = Image.new("RGB", (size * pixel_size, size * pixel_size))

    for y in range(size):
        for x in range(size):
            cell = world.grid[y][x]
            if cell.is_collapsed():
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
    world = World(GRID_SIZE)
    try:
        world.run()
        export_image(world, pixel_size=8, filename="wfc_map.jpg")
    except Exception as e:
        print(f"[ERROR] Generation failed: {e}")
