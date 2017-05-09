import random
import config


def have_ship_nearby(field, field_size, x, y):
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            n_x = x + i
            n_y = y + j
            if 0 <= n_x < field_size and 0 <= n_y < field_size and field[n_x][n_y]:
                return True
    return False


def can_place(field, field_size, ship_size, x, y, direction):
    v = (0, 1)
    if direction == 1:
        v = (1, 0)
    for i in range(ship_size):
        n_x = x + v[0] * i
        n_y = y + v[1] * i
        inside = 0 <= n_x < field_size and 0 <= n_y < field_size
        if not inside or field[n_x][n_y] or have_ship_nearby(field, field_size, n_x, n_y):
            return False
    for i in range(ship_size):
        n_x = x + v[0] * i
        n_y = y + v[1] * i
        field[n_x][n_y] = True
    return True


def find_place(field, field_size, ship_size):
    coordinates = []
    for i in range(field_size):
        for j in range(field_size):
            coordinates.append((i, j))
    random.shuffle(coordinates)
    for x, y in coordinates:
        d = random.randint(0, 1)
        for direction in [d, d ^ 1]:
            if can_place(field, field_size, ship_size, x, y, direction):
                return True
    return False


def try_random(field_size):
    field = [[0] * field_size for _ in range(field_size)]
    ships = list(config.battle_ships.keys())
    print(ships)
    for ship in ships:
        print(ship)
        print(config.battle_ships)
        for i in range(config.battle_ships[ship]):
            if not find_place(field, field_size, ship):
                return None
    return field


def generate_random_field(field_size):
    while 1:
        field = try_random(field_size)
        if field is not None:
            return field
