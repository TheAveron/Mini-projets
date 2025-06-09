import random
import heapq
from collections import deque
from typing import List, Dict, Tuple

# --- Configuration ---
GRID_SIZE = 50
TILE_IDS = range(9)

# --- Tile Definitions ---
class Tile:
    def __init__(self, name: str, weight: float, neighbors: List[int]):
        self.name = name
        self.weight = weight
        self.neighbors = neighbors  # List of valid adjacent tile IDs

TILES: Dict[int, Tile] = {
    0: Tile("empty",    0.01, [0]),
    1: Tile("grass",    0.26, [1, 3, 2, 4]),
    2: Tile("water",    0.15, [2, 1, 8]),
    3: Tile("forest",   0.20, [1, 3, 4]),
    4: Tile("mountain", 0.10, [3, 4, 6]),
    5: Tile("desert",   0.08, [1, 5]),
    6: Tile("snow",     0.07, [4, 6]),
    7: Tile("volcano",  0.01, [4, 7]),
    8: Tile("swamp",    0.03, [2, 1, 8]),
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
        return [(x + dx, y + dy) for dx, dy in DIRECTIONS if self.in_bounds(x + dx, y + dy)]

    def run(self):
        # Start with random seed
        sx, sy = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
        self.queue.append((sx, sy))

        while True:
            # Update heap from queue
            while self.queue:
                x, y = self.queue.popleft()
                if not self.grid[y][x].is_collapsed():
                    entropy = self.grid[y][x].entropy()
                    heapq.heappush(self.heap, (entropy, random.random(), x, y))

            if not self.heap:
                break  # Finished all collapses

            # Get cell with lowest entropy
            _, _, x, y = heapq.heappop(self.heap)
            cell = self.grid[y][x]

            if cell.is_collapsed():
                continue

            chosen_tile = cell.collapse()

            # Propagate constraints
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

                # Combine all valid neighbor tile options
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

# --- Output ---
def print_world(world: World):
    for row in world.grid:
        line = " ".join(
            TILES[cell.get_possible_ids()[0]].name[0] if cell.is_collapsed() else "?"
            for cell in row
        )
        print(line)

# --- Run the WFC ---
if __name__ == "__main__":
    world = World(GRID_SIZE)
    try:
        world.run()
        print_world(world)
    except Exception as e:
        print(f"[ERROR] Generation failed: {e}")
