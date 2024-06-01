import pygame
import os
import sys

pygame.init()
FPS = 50
size = WIDTH, HEIGHT = 900, 500
size = [pygame.display.Info().current_w, pygame.display.Info().current_h - 30]
WIDTH, HEIGHT = size[0], size[1]
all_sprites = pygame.sprite.Group()
screen = pygame.display.set_mode(size)
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
player = None


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


tile_width = tile_height = 400
tile_images = {
    'road': pygame.transform.scale(load_image('road.jpg'), (tile_width, tile_height)),
    'empty': pygame.transform.scale(load_image('grass.png'), (tile_width, tile_height)),
    'road_l': pygame.transform.scale(load_image('grass_l.jpg'), (tile_width, tile_height)),
    'road_r': pygame.transform.flip(pygame.transform.scale(load_image('grass_l.jpg'), (tile_width, tile_height)), True,
                                    False),
    "wall": pygame.transform.scale(load_image('box.png'), (tile_width, tile_height)),
}
player_image = pygame.transform.scale(load_image('car1.png'), (50, 100))


def terminate():
    pygame.quit()
    sys.exit()


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, wall=False):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.is_wall = wall

    def my_eq(self, other):
        if self.is_wall:
            if pygame.sprite.collide_mask(self, other):
                return True
        return False


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.mask = pygame.mask.from_surface(self.image)
        self.x = self.rect.x
        self.y = self.rect.y
        self.speed = 50
        self.speed_a = 10
        self.drawing_x = False
        self.drawing_y = False
        self.delta_x = 1
        self.delta_y = 1
        self.alfa = 0

    def up(self, d):
        self.speed += d * self.speed_a

        if self.drawing_y:
            sm = d * self.speed * self.delta_y
            self.y += sm
            self.rect.y = int(self.y)
            for el in tiles_group:
                el: Tile
                if el.my_eq(player):
                    self.y -= d * self.speed * self.delta_y
                    self.rect.y = int(self.y)
                    break
            if self.drawing_x:
                sm = d * self.speed * self.delta_x
                self.x += sm
                self.rect.x = int(self.x)
                for el in tiles_group:
                    el: Tile
                    if el.my_eq(player):
                        self.x -= d * self.speed * self.delta_x
                        self.rect.x = int(self.x)
                        break

    def update(self, event, d):
        if event.key == 1073741904:
            self.image = pygame.transform.rotate(self.image, 45)
            self.delta_x = -1
            self.drawing_x = True
        if event.key == 1073741903:
            self.image = pygame.transform.rotate(self.image, 315)
            self.delta_x = 1
            self.drawing_x = True
        elif 1073741905 == event.key:
            self.drawing_y = True
            self.delta_y = +1
        elif 1073741906 == event.key:
            self.drawing_y = True
            self.delta_y = -1

    def del_a(self, event):
        if event.key == 1073741906 or event.key == 1073741905:
            self.drawing_y = False
            self.delta_y = 0
            self.speed = 50
        if event.key == 1073741903 or event.key == 1073741904:
            self.drawing_x = False
            self.delta_x = 0
            self.image = player_image


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy
        if obj == player:
            obj.x += self.dx
            obj.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -int(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -int(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


camera = Camera()


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('road', x, y)
            elif level[y][x] == '/':
                Tile('road_l', x, y)
            elif level[y][x] == '\\':
                Tile('road_r', x, y)
            elif level[y][x] == '*':
                Tile('wall', x, y, wall=True)
            elif level[y][x] == '@':
                Tile('road', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def start_screen():
    global player
    clock = pygame.time.Clock()
    intro_text = ["Mario", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",

                  "приходится выводить их построчно"]
    screen.fill("white")
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                main()
                return
        # обновляем положение всех спрайтов
        pygame.display.flip()
        clock.tick(FPS)


def main():
    clock = pygame.time.Clock()
    global player
    player, level_x, level_y = generate_level(load_level('map.txt'))
    running = True
    while running:
        d = clock.tick() / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == 768:
                player.update(event, d)
            elif event.type == 769:
                player.del_a(event)
        screen.fill("black")
        player.up(d)
        # изменяем ракурс камеры
        camera.update(player)
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            camera.apply(sprite)
        tiles_group.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    start_screen()
