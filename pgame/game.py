import random

import pygame
import sys
import os

HERO = 'Pink_Monster_Walk_6.png'
pygame.init()
pygame.mixer.init()
BLACK = (0, 0, 0)
SIZE = width, height = 700, 700
FPS = 60
PLAYER_SPEED = 10  # Уменьшена скорость персонажа
WHITE = (255, 255, 255)
ground = 595  # уровень земли
JUMP_HEIGHT = 25  # сила прыжка
GRAVITY = 1  # сила гравитации
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Персонаж")
all_sprites = pygame.sprite.Group()  # создаем глобальную группу всех спрайтов
player_sprite = pygame.sprite.Group()
danger_sprite = pygame.sprite.Group()
COUNT = 0
danger_list = []

count_sound = pygame.mixer.Sound('music/Звук-достижения-сохранения.ogg')
pygame.mixer.music.load('music/laxity-crosswords-by-seraphic-music.mp3')
pygame.mixer.music.play(-1)
die_sound = pygame.mixer.Sound('music/dark-souls-you-died-sound-effect_hm5sYFG.ogg')

INIT_DELAY = 2500
spawn_delay = INIT_DELAY
DECREASE_BASE = 1.01
last_spawn_time = pygame.time.get_ticks()

font_path = 'PanterA.ttf'
font_large = pygame.font.Font(font_path, 48)
font_small = pygame.font.Font(font_path, 50)
font = pygame.font.Font('PanterA.ttf', 120)
font_but = pygame.font.Font('PanterA.ttf', 67)
play_but = (250, 480, 180, 70)
character_but = (240, 390, 340, 120)

game_over = False
retry_text = font_small.render('YOU DIED', True, (255, 255, 255))
retry_rect = retry_text.get_rect()
retry_rect.midtop = (width // 2, height // 2)


def load_image_no(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image_l = pygame.image.load(fullname).convert_alpha()  # Используем convert_alpha()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    if color_key is not None:
        if color_key == -1:
            color_key = image_l.get_at((0, 0))
        image_l.set_colorkey(color_key)
    return image_l


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


class Player(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, scale_factor=2, frame_rate=10):
        super().__init__()
        self.frames = []
        self.cut_sheet(sheet, columns, rows, scale_factor)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x = 250
        self.rect.y = ground
        self.speed_x = 0
        self.speed_y = 0
        self.onGround = True
        self.facing_left = False
        self.frame_rate = frame_rate
        self.frame_timer = 0
        self.is_moving = False
        self.player_out = False

    def cut_sheet(self, sheet, columns, rows, scale_factor):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frame = sheet.subsurface(pygame.Rect(frame_location, self.rect.size))
                frame = pygame.transform.scale(frame,
                                               (frame.get_width() * scale_factor, frame.get_height() * scale_factor))
                self.frames.append(frame)

    def move(self, dx):
        self.speed_x += dx
        self.rect.x += self.speed_x
        self.speed_x = 0

    def update(self):
        if self.is_moving:
            self.frame_timer += 1
            if self.frame_timer >= self.frame_rate:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
                self.frame_timer = 0
            if self.facing_left:
                self.image = pygame.transform.flip(self.frames[self.cur_frame], True, False)
        else:
            self.image = self.frames[0]
            if self.facing_left:
                self.image = pygame.transform.flip(self.frames[0], True, False)

        if not self.onGround:
            self.speed_y += GRAVITY
        if self.rect.y + self.speed_y >= ground:
            self.rect.y = ground
            self.onGround = True
            self.speed_y = 0
        else:
            self.rect.y += self.speed_y

    def jump(self):
        if self.onGround:
            self.speed_y = -JUMP_HEIGHT
            self.onGround = False


class Danger(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, scale_factor=2, frame_rate=10):
        super().__init__()
        self.frames = []
        self.cut_sheet(sheet, columns, rows, scale_factor)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.y = height - self.rect.height
        self.frame_rate = frame_rate
        self.speed_x = 4
        self.facing_left = True
        self.player_out = True
        direction = random.randint(0, 1)
        if direction == 0:
            # Справа внизу
            self.rect.x = width - self.rect.width
            self.rect.y = height - self.rect.height
            self.speed_x = -self.speed_x  # Двигаемся влево
            self.facing_left = False
        else:
            # Слева внизу
            self.rect.x = 0
            self.rect.y = height - self.rect.height
            self.speed_x = self.speed_x  # Двигаемся вправо
            self.facing_left = True
        self.frame_timer = 0
        self.danger_life = True

    def cut_sheet(self, sheet, columns, rows, scale_factor):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frame = sheet.subsurface(pygame.Rect(frame_location, self.rect.size))
                frame = pygame.transform.scale(frame,
                                               (frame.get_width() * scale_factor, frame.get_height() * scale_factor))
                self.frames.append(frame)

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.x < -self.rect.width or self.rect.x > width:
            self.kill()
        self.frame_timer += 1
        if self.frame_timer >= self.frame_rate:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            if self.facing_left:
                self.image = pygame.transform.flip(self.image, True, False)
            self.frame_timer = 0


class Danger1(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, scale_factor=2, frame_rate=10):
        super().__init__()
        self.frames = []
        self.cut_sheet(sheet, columns, rows, scale_factor)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.y = height - self.rect.height
        self.frame_rate = frame_rate
        self.speed_x = 4
        self.facing_left = True
        self.player_out = True
        direction = random.randint(0, 1)
        if direction == 0:
            # Справа внизу
            self.rect.x = width - self.rect.width
            self.rect.y = (height - self.rect.height) + 33
            self.speed_x = -self.speed_x  # Двигаемся влево
            self.facing_left = False
        else:
            # Слева внизу
            self.rect.x = 0
            self.rect.y = (height - self.rect.height) + 33
            self.speed_x = self.speed_x  # Двигаемся вправо
            self.facing_left = True
        self.frame_timer = 0
        self.danger_life = True

    def cut_sheet(self, sheet, columns, rows, scale_factor):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frame = sheet.subsurface(pygame.Rect(frame_location, self.rect.size))
                frame = pygame.transform.scale(frame,
                                               (frame.get_width() * scale_factor, frame.get_height() * scale_factor))
                self.frames.append(frame)

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.x < -self.rect.width or self.rect.x > width:
            self.kill()
        self.frame_timer += 1
        if self.frame_timer >= self.frame_rate:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            if self.facing_left:
                self.image = pygame.transform.flip(self.image, True, False)
            self.frame_timer = 0


class Danger2(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, scale_factor=2, frame_rate=10):
        super().__init__()
        self.frames = []
        self.cut_sheet(sheet, columns, rows, scale_factor)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.y = height - self.rect.height
        self.frame_rate = frame_rate
        self.speed_x = 4
        self.facing_left = True
        self.player_out = True
        direction = random.randint(0, 1)
        if direction == 0:
            # Справа внизу
            self.rect.x = width - self.rect.width
            self.rect.y = height - self.rect.height
            self.speed_x = -self.speed_x  # Двигаемся влево
            self.facing_left = False
        else:
            # Слева внизу
            self.rect.x = 0
            self.rect.y = height - self.rect.height
            self.speed_x = self.speed_x  # Двигаемся вправо
            self.facing_left = True
        self.frame_timer = 0
        self.danger_life = True

    def cut_sheet(self, sheet, columns, rows, scale_factor):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frame = sheet.subsurface(pygame.Rect(frame_location, self.rect.size))
                frame = pygame.transform.scale(frame,
                                               (frame.get_width() * scale_factor, frame.get_height() * scale_factor))
                self.frames.append(frame)

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.x < -self.rect.width or self.rect.x > width:
            self.kill()
        self.frame_timer += 1
        if self.frame_timer >= self.frame_rate:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            if self.facing_left:
                self.image = pygame.transform.flip(self.image, True, False)
            self.frame_timer = 0


class DangerShow(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, scale_factor=2, frame_rate=10):
        super().__init__()
        self.frames = []
        self.cut_sheet(sheet, columns, rows, scale_factor)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.y = height - self.rect.height
        self.frame_rate = frame_rate
        self.speed_x = 0
        self.facing_left = True
        self.player_out = True
        self.rect.x = 350
        self.rect.y = 350
        self.frame_timer = 0
        self.danger_life = True

    def cut_sheet(self, sheet, columns, rows, scale_factor):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frame = sheet.subsurface(pygame.Rect(frame_location, self.rect.size))
                frame = pygame.transform.scale(frame,
                                               (frame.get_width() * scale_factor, frame.get_height() * scale_factor))
                self.frames.append(frame)

    def update(self):
        self.frame_timer += 1
        if self.frame_timer >= self.frame_rate:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.frame_timer = 0


class BackgroundChoosing(pygame.sprite.Sprite):
    def __init__(self, image_file, w, h):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (w, h))


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (width, height))


def text_about(intro_text, screen_ch):
    font_ch = 'data/ofont.ru_Driagwa.ttf'
    font_ch = pygame.font.Font(font_ch, 23)
    text_coord = 350
    for line in intro_text:
        string_rendered = font_ch.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 120
        text_coord += intro_rect.height
        screen_ch.blit(string_rendered, intro_rect)


def choosing():
    global HERO, PLAYER_SPEED, JUMP_HEIGHT
    pygame.init()
    size_ch = width_ch, height_ch = 800, 800
    screen_ch = pygame.display.set_mode(size_ch)
    font_path_ch = 'data/ofont.ru_Wolgadeutsche.ttf'
    font_name = pygame.font.Font(font_path_ch, 48)
    font_buti = pygame.font.Font(font_path_ch, 20)
    all_sprites_ch = pygame.sprite.Group()
    new_danger_spisok = pygame.sprite.Group()
    back_ground_ch = BackgroundChoosing('data/img.png', width_ch, height_ch)
    running_ch = True
    text = 'Pink'
    text_evil = font_name.render('Злодеи', True, (255, 255, 255))
    text_hero = font_name.render('Герои', True, (255, 255, 255))
    text_buti = font_buti.render('Выбрать', True, (255, 255, 255))
    text_choose = font_name.render('Ваш выбор', True, (255, 255, 255))
    choose_pic = load_image('Pink.стоит.png', color_key=-1)
    new_danger_ch = DangerShow(load_image_no("Pink_Monster_Attack2_6.png"), 6, 1, scale_factor=7, frame_rate=7)
    new_danger_spisok.add(new_danger_ch)
    with open('data/Pinki.txt', 'r', encoding='utf-8') as t:
        intro_text = t.readlines()
        intro_text = [ll[:-1] for ll in intro_text[:-1]] + [intro_text[-1]]
    while running_ch:
        text_surface_ch = font_name.render(text, True, (80, 0, 100))
        name_rect = (140, 310)
        screen_ch.fill([255, 255, 255])
        screen_ch.blit(back_ground_ch.image, back_ground_ch.rect)
        image_p = load_image('Pink.стоит.png', color_key=-1)
        image_d = load_image('Dude.стоит.png', color_key=-1)
        image_o = load_image('Owlet.стоит.png', color_key=-1)
        image_fl = load_image('FLYING_стоит.png', color_key=-1)
        image_sk = load_image('Скилет.png', color_key=-1)
        image_n = load_image('ниндзя.jpg', (255, 255, 255))
        image_svitok = load_image('свиток.dark.png', color_key=-1)
        image_buti = load_image('кнопки.jpg', color_key=-1)
        image_p = pygame.transform.scale(image_p, (50, 50))
        image_d = pygame.transform.scale(image_d, (50, 50))
        image_o = pygame.transform.scale(image_o, (50, 50))
        image_fl = pygame.transform.scale(image_fl, (50, 50))
        image_sk = pygame.transform.scale(image_sk, (50, 50))
        image_n = pygame.transform.scale(image_n, (50, 50))
        choose_pic = pygame.transform.scale(choose_pic, (50, 50))
        image_buti = pygame.transform.scale(image_buti, (90, 50))
        image_svitok = pygame.transform.scale(image_svitok, (350, 400))
        screen_ch.blit(image_p, (700, 420))
        screen_ch.blit(image_d, (700, 500))
        screen_ch.blit(image_o, (700, 580))
        screen_ch.blit(image_fl, (700, 160))
        screen_ch.blit(image_sk, (700, 240))
        screen_ch.blit(image_n, (700, 320))
        screen_ch.blit(image_svitok, (30, 260))
        screen_ch.blit(image_buti, (610, 428))
        screen_ch.blit(image_buti, (610, 508))
        screen_ch.blit(image_buti, (610, 588))
        screen_ch.blit(text_surface_ch, name_rect)
        screen_ch.blit(text_evil, (640, 100))
        screen_ch.blit(text_hero, (650, 360))
        screen_ch.blit(text_buti, (620, 440))
        screen_ch.blit(text_buti, (620, 520))
        screen_ch.blit(text_buti, (620, 600))
        screen_ch.blit(text_choose, (50, 200))
        screen_ch.blit(choose_pic, (250, 200))
        for event_ch in pygame.event.get():
            if event_ch.type == pygame.QUIT:
                running_ch = False
            if event_ch.type == pygame.MOUSEBUTTONDOWN:
                mouse_x_ch, mouse_y_ch = event_ch.pos
                if 610 <= mouse_x_ch <= 700 and 428 <= mouse_y_ch <= 478:
                    choose_pic = load_image('Pink.стоит.png', color_key=-1)
                    HERO = 'Pink_Monster_Walk_6.png'
                    PLAYER_SPEED = 10
                    JUMP_HEIGHT = 25
                if 610 <= mouse_x_ch <= 700 and 508 <= mouse_y_ch <= 558:
                    choose_pic = load_image('Dude.стоит.png', color_key=-1)
                    HERO = 'Dude_Monster_Run_6.png'
                    PLAYER_SPEED = 5
                    JUMP_HEIGHT = 30
                if 610 <= mouse_x_ch <= 700 and 588 <= mouse_y_ch <= 638:
                    choose_pic = load_image('Owlet.стоит.png', color_key=-1)
                    HERO = 'Owlet_Monster_Run_6.png'
                    PLAYER_SPEED = 15
                    JUMP_HEIGHT = 15
                if 700 <= mouse_x_ch <= 750 and 420 <= mouse_y_ch <= 470:
                    text = 'Pink'
                    with open('data/Pinki.txt', 'r', encoding='utf-8') as t:
                        intro_text = t.readlines()
                        intro_text = [ll[:-1] for ll in intro_text[:-1]] + [intro_text[-1]]
                    new_spisok = pygame.sprite.Group()
                    new = DangerShow(load_image_no("Pink_Monster_Attack2_6.png"), 6, 1, scale_factor=7, frame_rate=7)
                    new_spisok.add(new)
                    new_danger_spisok = new_spisok
                elif 700 <= mouse_x_ch <= 750 and 500 <= mouse_y_ch <= 550:
                    text = 'Редскарф'
                    with open('data/Редскарф.txt', 'r', encoding='utf-8') as t:
                        intro_text = t.readlines()
                        intro_text = [ll[:-1] for ll in intro_text[:-1]] + [intro_text[-1]]
                    new_spisok = pygame.sprite.Group()
                    new = DangerShow(load_image_no("Dude_Monster_Attack2_6.png"), 6, 1, scale_factor=7, frame_rate=7)
                    new_spisok.add(new)
                    new_danger_spisok = new_spisok
                elif 700 <= mouse_x_ch <= 750 and 580 <= mouse_y_ch <= 630:
                    text = 'Бяша'
                    with open('data/Бяша.txt', 'r', encoding='utf-8') as t:
                        intro_text = t.readlines()
                        intro_text = [ll[:-1] for ll in intro_text[:-1]] + [intro_text[-1]]
                    new_spisok = pygame.sprite.Group()
                    new = DangerShow(load_image_no("Owlet_Monster_Run_6.png"), 6, 1, scale_factor=7, frame_rate=7)
                    new_spisok.add(new)
                    new_danger_spisok = new_spisok
                elif 700 <= mouse_x_ch <= 750 and 160 <= mouse_y_ch <= 210:
                    text = 'Чёрт'
                    with open('data/Чёрт.txt', 'r', encoding='utf-8') as t:
                        intro_text = t.readlines()
                        intro_text = [ll[:-1] for ll in intro_text[:-1]] + [intro_text[-1]]
                    new_spisok = pygame.sprite.Group()
                    new = DangerShow(load_image_no("FLYING.png"), 4, 1, scale_factor=4, frame_rate=7)
                    new_spisok.add(new)
                    new_danger_spisok = new_spisok
                elif 700 <= mouse_x_ch <= 750 and 240 <= mouse_y_ch <= 290:
                    text = 'Скелет'
                    with open('data/Скелет.txt', 'r', encoding='utf-8') as t:
                        intro_text = t.readlines()
                        intro_text = [ll[:-1] for ll in intro_text[:-1]] + [intro_text[-1]]
                    new_spisok = pygame.sprite.Group()
                    new = DangerShow(load_image_no("Skeleton_01_Yellow_Walk (1).png"), 10, 1, scale_factor=4,
                                     frame_rate=4)
                    new_spisok.add(new)
                    new_danger_spisok = new_spisok
                elif 700 <= mouse_x_ch <= 750 and 320 <= mouse_y_ch <= 370:
                    text = 'Ниндзя'
                    with open('data/Ниндзя.txt', 'r', encoding='utf-8') as t:
                        intro_text = t.readlines()
                        intro_text = [ll[:-1] for ll in intro_text[:-1]] + [intro_text[-1]]
                    new_spisok = pygame.sprite.Group()
                    new = DangerShow(load_image_no("NightBorne.png"), 6, 1, scale_factor=4, frame_rate=7)
                    new_spisok.add(new)
                    new_danger_spisok = new_spisok
        text_about(intro_text, screen_ch)
        new_danger_spisok.update()
        new_danger_spisok.draw(screen_ch)
        all_sprites_ch.draw(screen_ch)
        all_sprites_ch.update()
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    # Уменьшаем размер и скорость анимации
    text_surface = font.render('Shabash', True, (255, 255, 255))
    clock = pygame.time.Clock()
    BackGround_m = Background('data/стратовый фон.jpg')
    last_spawn_time = pygame.time.get_ticks()
    running_m = True
    INIT_DELAY = 2000
    txt_surf = ''
    while running_m:
        screen.fill([255, 255, 255])
        screen.blit(BackGround_m.image, BackGround_m.rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_m = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if 230 <= mouse_x <= 450 and 400 <= mouse_y <= 480:
                    choosing()
                    screen = pygame.display.set_mode(SIZE)
                if play_but[0] <= mouse_x <= play_but[0] + play_but[2] and play_but[1] <= mouse_y <= play_but[3] + \
                        play_but[1]:
                    BackGround = Background('data/фон.png')
                    grass = Background('data/трава.png')
                    # Загрузка спрайт-листа для анимации
                    player_animation = Player(load_image_no(HERO), 6, 1, scale_factor=1.8, frame_rate=7)
                    all_sprites = pygame.sprite.Group()
                    player_sprite = pygame.sprite.Group()
                    danger_sprite = pygame.sprite.Group()
                    player_sprite.add(player_animation)
                    all_sprites.add(player_animation)
                    running = True
                    while running:
                        screen.fill([255, 255, 255])
                        screen.blit(BackGround.image, BackGround.rect)
                        screen.blit(grass.image, grass.rect)
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running = False
                                pygame.mixer.music.stop()
                        # Получаем нажатые клавиши
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LEFT]:
                            player_animation.move(-PLAYER_SPEED)  # движение влево
                            player_animation.facing_left = True  # Устанавливаем флаг для зеркалирования
                            player_animation.is_moving = True  # Устанавливаем флаг движения
                        elif keys[pygame.K_RIGHT]:
                            player_animation.move(PLAYER_SPEED)  # движение вправо
                            player_animation.facing_left = False  # Сбрасываем флаг зеркалирования
                            player_animation.is_moving = True  # Устанавливаем флаг движения
                        else:
                            player_animation.is_moving = False  # Персонаж стоит, прекращаем анимацию

                        if keys[pygame.K_UP]:
                            player_animation.jump()  # прыжок

                        now = pygame.time.get_ticks()
                        if now - last_spawn_time > INIT_DELAY:
                            last_spawn_time = now
                            if COUNT == 5:
                                BackGround = Background('data/лес_2.webp')
                            if COUNT == 10:
                                BackGround = Background('data/лес_3.png')
                            if COUNT > 10:
                                third_danger = Danger2(load_image_no("Skeleton_01_Yellow_Walk (1).png"),
                                                       10, 1, scale_factor=1.8, frame_rate=7)
                                danger_sprite.add(third_danger)
                            if COUNT > 5:
                                second_danger = Danger1(load_image_no("NightBorne.png"), 6, 1,
                                                        scale_factor=1.8, frame_rate=7)
                                danger_sprite.add(second_danger)
                            new_danger = Danger(load_image_no("FLYING.png"), 4, 1, scale_factor=1.8,
                                                frame_rate=7)
                            if not player_animation.player_out:
                                danger_sprite.add(new_danger)

                        score_text = font_but.render((str(COUNT)), True, (255, 255, 255))
                        score_rect = score_text.get_rect()

                        player_animation.update()
                        danger_sprite.update()

                        for goomba in danger_sprite:
                            if player_animation.rect.colliderect(goomba.rect):
                                if player_animation.rect.bottom - player_animation.speed_y < goomba.rect.top:
                                    count_sound.play()
                                    goomba.kill()
                                    player_animation.speed_y = -JUMP_HEIGHT // 2  # Отскок вверх
                                    COUNT += 1
                                    print(COUNT)
                                else:
                                    pygame.mixer_music.stop()
                                    player_animation.kill()
                                    if not player_animation.player_out:
                                        die_sound.play(0)
                                    player_animation.player_out = True
                        if player_animation.player_out:
                            image = load_image_no('смерть.jpg')
                            image = pygame.transform.scale(image, (800, 800))
                            screen.blit(image, (0, 0))
                            score_rect.midbottom = (width // 2, height // 2)
                            screen.blit(retry_text, retry_rect)

                        #     # Обновление состояния игрок
                        score_rect.midtop = (width // 2, 5)
                        player_sprite.draw(screen)
                        danger_sprite.draw(screen)
                        screen.blit(score_text, score_rect)
                        pygame.display.flip()
        screen.blit(text_surface, (190, 580))  # Обновление дисплея
        image_play = load_image_no('кнопка главная.png')
        image_ch = load_image_no('кнопка главная.png')
        image_play = pygame.transform.scale(image_play, (play_but[2], play_but[3]))
        image_ch = pygame.transform.scale(image_ch, (220, 80))
        text_surf = font_but.render("play", True, 'white')
        text_ch = font_but.render("choose", True, 'white')
        screen.blit(image_play, (play_but[0], play_but[1]))
        screen.blit(image_ch, (230, 400))
        screen.blit(text_surf, (play_but[0] + 50, play_but[1] + 20))
        screen.blit(text_ch, (275, 425))
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
