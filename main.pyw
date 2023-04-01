from random import randint
from time import time as timer

from pygame import *
mixer.init()
font.init()

WIDTH = 1200
HEIGHT = 700

window = display.set_mode((WIDTH, HEIGHT), RESIZABLE)
display.set_caption("Shooter")

display.set_icon(image.load("images/asteroid.png"))
background = transform.scale(image.load("images/galaxy.jpg"), (WIDTH, HEIGHT))
clock = time.Clock()
fps = 60

mixer.music.load("sounds/space.ogg")
mixer.music.set_volume(0.1)
mixer.music.play()

shoot = mixer.Sound("sounds/fire.ogg")
shoot.set_volume(0.1)

current_size = window.get_size()
virtual_surface = Surface((WIDTH, HEIGHT))

font_interface = font.Font(None, 30)
font_finish = font.Font(None, 150)

lost = 0
text_lost = font_interface.render("Пропущено: " + str(lost), True, (255, 255, 255))

score = 0
text_score = font_interface.render("Рахунок: " + str(score), True, (255, 255, 255))

text_win = font_finish.render("You WIN!", True, (55, 255, 55))
text_lose = font_finish.render("You LOSE!", True, (255, 55, 55))


class GameSprite(sprite.Sprite):
    def __init__(self, sprite_image, x, y, width, height, speed):
        super().__init__()
        self.image = transform.scale(image.load(sprite_image), (width, height))
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        virtual_surface.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):
    def __init__(self, x, y):
        super().__init__("images/rocket.png", x, y, 100, 150, 10)
        self.kd = 0
        self.hp = 3
        self.clip = 10
        self.reload = False
        self.start_reloading = 0

    def update(self):
        global interface_clip
        global current_clip
        keys_pressed = key.get_pressed()

        if keys_pressed[K_a] and self.rect.x >= 5:
            self.rect.x -= self.speed
        if keys_pressed[K_d] and self.rect.x <= WIDTH - 105:
            self.rect.x += self.speed
        if (keys_pressed[K_SPACE] and self.kd <= 0) and not self.reload:
            self.fire()
            self.kd = 10
            current_clip = current_clip[:-1]
        else:
            self.kd -= 1

        if self.clip <= 0:
            self.reload = True
            self.start_reloading = timer()

        if self.reload:
            self.clip = 10
            current_time = timer()
            if current_time - self.start_reloading >= 1:
                self.reload = False
                current_clip = interface_clip

    def fire(self):
        shoot.play()
        self.clip -= 1
        bullet = Bullet(self.rect.centerx - 10, self.rect.top)
        bullets.add(bullet)


class Enemy(GameSprite):
    def __init__(self, width, height, damage, speed):
        self.damage = damage
        self.width = width
        self.height = height
        super().__init__("images/ufo.png", randint(0, WIDTH - self.width),
                         randint(-HEIGHT, - self.height), width, height, speed)

    def update(self):
        global lost
        global text_lost
        self.rect.y += self.speed
        if self.rect.y >= HEIGHT:
            self.spawn()
            lost += self.damage
            text_lost = font_interface.render("Пропущено: " + str(lost), True, (255, 255, 255))

    def spawn(self):
        self.rect.x = randint(0, WIDTH - self.width)
        self.rect.y = randint(-HEIGHT, - self.height)


class Ufo(Enemy):
    def __init__(self):
        super().__init__(150, 75, 1, 2)


class BossUfo(Enemy):
    def __init__(self):
        self.life = False
        self.hp = 7
        super().__init__(300, 150, 3, 1)

    def spawn(self):
        self.rect.x = randint(0, WIDTH - self.width)
        self.rect.y = -self.height


class Bullet(GameSprite):
    def __init__(self, x, y):
        super().__init__("images/bullet.png", x, y, 20, 40, 10)

    def update(self):
        self.rect.y -= self.speed
        if self.rect.y <= -40:
            self.kill()


class Asteroid(GameSprite):
    def __init__(self):
        self.width = randint(30, 70)

        super().__init__("images/asteroid.png", randint(0, WIDTH - self.width),
                         randint(-HEIGHT, - self.width), self.width, self.width, 3)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y >= HEIGHT:
            self.spawn()

    def spawn(self):
        self.change_width()
        self.rect.x = randint(0, WIDTH - self.width)
        self.rect.y = randint(-HEIGHT, - self.width)

    def change_width(self):
        self.width = randint(40, 80)
        self.image = transform.scale(image.load("images/asteroid.png"), (self.width, self.width))
        self.rect = self.image.get_rect()



player = Player(550, HEIGHT - 170)

monsters = sprite.Group()
for i in range(10):
    monster = Ufo()
    monsters.add(monster)

health = []
heart_x = 20
for i in range(player.hp):
    heart = GameSprite("images/heart.png", heart_x, 20, 40, 40, 0)
    health.append(heart)
    heart_x += 45

asteroids = sprite.Group()
for i in range(3):
    asteroid = Asteroid()
    asteroids.add(asteroid)

interface_clip = []
ammo_x = 20
for i in range(player.clip):
    ammo = GameSprite("images/bullet.png", ammo_x, HEIGHT - 100, 20, 40, 0)
    interface_clip.append(ammo)
    ammo_x += 20
current_clip = interface_clip

boss = BossUfo()

bullets = sprite.Group()

game = True
finish = False

while game:
    for e in event.get():
        if e.type == QUIT:
            game = False
        if e.type == VIDEORESIZE:
            current_size = e.size
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                game = False
            if e.key == K_r:
                player.clip = 0

    if not finish:
        virtual_surface.blit(background, (0, 0))
        player.update()
        player.reset()

        monsters.update()
        monsters.draw(virtual_surface)

        bullets.update()
        bullets.draw(virtual_surface)

        asteroids.update()
        asteroids.draw(virtual_surface)

        if boss.life:
            boss.update()
            boss.reset()
            if sprite.collide_rect(boss, player):
                boss.rect.x = -400
                boss.life = False
                player.hp -= 2
                health = health[:-2]

            hits_boss = sprite.spritecollide(boss, bullets, True)

            if len(hits_boss) != 0:
                for hit in hits_boss:
                    boss.hp -= 1
                    if boss.hp <= 0:
                        boss.life = False
                        player.hp += 1
                        heart_x = 20 + 45 * (player.hp - 1)
                        heart = GameSprite("images/heart.png", heart_x, 20, 40, 40, 0)
                        health.append(heart)
                        heart_x += 45
                        score += 3
                        text_score = font_interface.render("Рахунок: " + str(score), True, (255, 255, 255))
        elif score % 20 == 0 and score != 0:
            boss.spawn()
            boss.hp = 7
            boss.life = True

        crush_list = sprite.spritecollide(player, monsters, False)
        dead_monsters = sprite.groupcollide(monsters, bullets, False, True)
        crush_list_asteroids = sprite.spritecollide(player, asteroids, False)
        sprite.groupcollide(asteroids, bullets, False, True)

        if len(crush_list_asteroids) != 0:
            for asteroid in crush_list_asteroids:
                asteroid.spawn()
                player.hp -= 2
                health = health[:-2]

        if len(dead_monsters) != 0:
            for monster in dead_monsters:
                monster.spawn()
                score += 1
                text_score = font_interface.render("Рахунок: " + str(score), True, (255, 255, 255))

        if len(crush_list) != 0:
            for monster in crush_list:
                monster.spawn()
                player.hp -= 1
                health = health[:-1]

        if score >= 100:
            virtual_surface.blit(text_win, (380, 300))
            finish = True

        if player.hp <= 0 or lost >= 20:
            finish = True
            virtual_surface.blit(text_lose, (380, 300))

        virtual_surface.blit(text_lost, (1000, 20))
        virtual_surface.blit(text_score, (1000, 50))

        for heart in health:
            heart.reset()

        for ammo in current_clip:
            ammo.reset()

        scaled_surface = transform.scale(virtual_surface, current_size)
        window.blit(scaled_surface, (0, 0))

    display.update()
    clock.tick(fps)
