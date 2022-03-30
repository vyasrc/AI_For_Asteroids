import pygame
import math
import random
import numpy as np
from sys import argv
from time import time

pygame.init()

sw = 800
sh = 800

bg = pygame.image.load('asteroidsPics/starbg.png')
alienImg = pygame.image.load('asteroidsPics/alienShip.png')
playerRocket = pygame.image.load('asteroidsPics/spaceRocket2.png')
star = pygame.image.load('asteroidsPics/star.png')
asteroid50 = pygame.image.load('asteroidsPics/asteroid50.png')
asteroid100 = pygame.image.load('asteroidsPics/asteroid100.png')
asteroid150 = pygame.image.load('asteroidsPics/asteroid150.png')

shoot = pygame.mixer.Sound('sounds/shoot.wav')
bangLargeSound = pygame.mixer.Sound('sounds/bangLarge.wav')
bangSmallSound = pygame.mixer.Sound('sounds/bangSmall.wav')
shoot.set_volume(.25)
bangLargeSound.set_volume(.25)
bangSmallSound.set_volume(.25)

pygame.display.set_caption('Asteroids')
win = pygame.display.set_mode((sw, sh))
clock = pygame.time.Clock()

gameover = False
lives = 1
score = 0
rapidFire = False
rfStart = -1
isSoundOn = True
highScore = 0


class Player(object):
    def __init__(self):
        self.img = playerRocket
        self.w = self.img.get_width()
        self.h = self.img.get_height()
        self.x = sw // 2
        self.y = sh // 2
        self.angle = 0
        self.rotatedSurf = pygame.transform.rotate(self.img, self.angle)
        self.rotatedRect = self.rotatedSurf.get_rect()
        self.rotatedRect.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w // 2, self.y - self.sine * self.h // 2)

    def draw(self, win):
        # win.blit(self.img, [self.x, self.y, self.w, self.h])
        win.blit(self.rotatedSurf, self.rotatedRect)

    def turnLeft(self):
        self.angle += 2
        self.rotatedSurf = pygame.transform.rotate(self.img, self.angle)
        self.rotatedRect = self.rotatedSurf.get_rect()
        self.rotatedRect.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w // 2, self.y - self.sine * self.h // 2)

    def turnRight(self):
        self.angle -= 2

        self.rotatedSurf = pygame.transform.rotate(self.img, self.angle)
        self.rotatedRect = self.rotatedSurf.get_rect()
        self.rotatedRect.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w // 2, self.y - self.sine * self.h // 2)

    def moveForward(self):
        self.x += self.cosine * 6
        self.y -= self.sine * 6
        self.rotatedSurf = pygame.transform.rotate(self.img, self.angle)
        self.rotatedRect = self.rotatedSurf.get_rect()
        self.rotatedRect.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w // 2, self.y - self.sine * self.h // 2)

    def moveBackward(self):
        self.x -= self.cosine * 6
        self.y += self.sine * 6
        self.rotatedSurf = pygame.transform.rotate(self.img, self.angle)
        self.rotatedRect = self.rotatedSurf.get_rect()
        self.rotatedRect.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w // 2, self.y - self.sine * self.h // 2)

    def updateLocation(self):
        if self.x > sw + 50:
            self.x = 0
        elif self.x < 0 - self.w:
            self.x = sw
        elif self.y < -50:
            self.y = sh
        elif self.y > sh + 50:
            self.y = 0

    def rotateShip(self, right, rangle):

        sign = 1 if right else -1
        # rot = math.pi * 2 / 180 * math.pi / 60 * sign
        rot = rangle * sign
        self.angle += rot
        self.angle = self.angle % 360
        # if self.angle < 0:
        #     self.angle += math.pi * 2
        # elif self.angle >= math.pi * 2:
        #     self.angle -= math.pi * 2
        # print(self.angle)
        self.rotatedSurf = pygame.transform.rotate(self.img, self.angle)
        self.rotatedRect = self.rotatedSurf.get_rect()
        self.rotatedRect.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w // 2, self.y - self.sine * self.h // 2)


class Bullet(object):
    def __init__(self):
        self.point = player.head
        self.x, self.y = self.point
        self.w = 6
        self.h = 6
        self.c = player.cosine
        self.s = player.sine
        self.xv = self.c * 10
        self.yv = self.s * 10

    def move(self):
        self.x += self.xv
        self.y -= self.yv

    def draw(self, win):
        pygame.draw.rect(win, (255, 255, 255), [self.x, self.y, self.w, self.h])

    def checkOffScreen(self):
        if self.x < -50 or self.x > sw or self.y > sh or self.y < -50:
            return True


class Asteroid(object):
    def __init__(self, rank):
        self.rank = rank
        if self.rank == 1:
            self.image = asteroid50
        elif self.rank == 2:
            self.image = asteroid100
        else:
            self.image = asteroid150
        self.w = 50 * rank
        self.h = 50 * rank
        self.ranPoint = random.choice([(random.randrange(0, sw - self.w), random.choice([-1 * self.h - 5, sh + 5])),
                                       (random.choice([-1 * self.w - 5, sw + 5]), random.randrange(0, sh - self.h))])
        self.x, self.y = self.ranPoint
        if self.x < sw // 2:
            self.xdir = 1
        else:
            self.xdir = -1
        if self.y < sh // 2:
            self.ydir = 1
        else:
            self.ydir = -1
        self.xv = self.xdir * random.randrange(1, 2)
        self.yv = self.ydir * random.randrange(1, 2)

    def draw(self, win):
        win.blit(self.image, (self.x, self.y))

    def checkLocation(self):
        if self.x > sw + 50:
            # self.x = 0
            return True
        elif self.x < 0 - self.w:
            # self.x = sw
            return True
        elif self.y < -50:
            return True
            # self.y = sh
        elif self.y > sh + 50:
            # self.y = 0
            return True

        return False


# class Star(object):
#     def __init__(self):
#         self.img = star
#         self.w = self.img.get_width()
#         self.h = self.img.get_height()
#         self.ranPoint = random.choice([(random.randrange(0, sw - self.w), random.choice([0, sh - self.h]))])
#         # print(self.ranPoint)
#         self.x, self.y = self.ranPoint
#         if self.x < sw // 2:
#             self.xdir = 1
#         else:
#             self.xdir = -1
#         if self.y < sh // 2:
#             self.ydir = 1
#         else:
#             self.ydir = -1
#         self.xv = self.xdir * 2
#         self.yv = self.ydir * 2
#
#     def draw(self, win):
#         win.blit(self.img, (self.x, self.y))


# class Alien(object):
#     def __init__(self):
#         self.img = alienImg
#         self.w = self.img.get_width()
#         self.h = self.img.get_height()
#         self.ranPoint = random.choice([(random.randrange(0, sw - self.w), random.choice([-1 * self.h - 5, sh + 5])),
#                                        (random.choice([-1 * self.w - 5, sw + 5]), random.randrange(0, sh - self.h))])
#         self.x, self.y = self.ranPoint
#         if self.x < sw // 2:
#             self.xdir = 1
#         else:
#             self.xdir = -1
#         if self.y < sh // 2:
#             self.ydir = 1
#         else:
#             self.ydir = -1
#         self.xv = self.xdir * 2
#         self.yv = self.ydir * 2
#
#     def draw(self, win):
#         win.blit(self.img, (self.x, self.y))
#
#
# class AlienBullet(object):
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y
#         self.w = 4
#         self.h = 4
#         self.dx, self.dy = player.x - self.x, player.y - self.y
#         self.dist = math.hypot(self.dx, self.dy)
#         self.dx, self.dy = self.dx / self.dist, self.dy / self.dist
#         self.xv = self.dx * 5
#         self.yv = self.dy * 5
#
#     def draw(self, win):
#         pygame.draw.rect(win, (255, 255, 255), [self.x, self.y, self.w, self.h])


class NeuralNetwork(object):

    def __init__(self, num_inputs, num_hidden, num_outputs):
        self.num_inputs = num_inputs
        self.num_hidden = num_hidden
        self.num_outputs = num_outputs
        self.bias0 = np.random.uniform(-1, 1, (1, self.num_hidden))
        self.bias1 = np.random.uniform(-1, 1, (1, self.num_outputs))
        self.weights0 = np.random.uniform(-1, 1, (self.num_inputs,self.num_hidden))
        self.weights1 = np.random.uniform(-1, 1, (self.num_hidden, self.num_outputs))
        self.hidden = []
        self.inputs = []

    def sigmoid(self, t):

        return 1 / (1 + np.exp(-t))

    def sigmoid_derivs(self, t):

        return t * (1 - t)

    def feedforward(self, arr):
        self.inputs = np.array(arr).reshape(1, np.array(arr).shape[0])

        # hidden = np.dot(inputs, self.weights0)
        # sigmoid = lambda t: 1 / (1 + math.exp(-t))
        temp = np.dot(self.inputs, self.weights0)
        vfunc = np.vectorize(self.sigmoid)
        temp = np.add(temp, self.bias0)
        self.hidden = vfunc(temp)

        # self.hidden = np.array([sigmoid(x) for x in np.dot(self.inputs, self.weights0)])
        temp = np.dot(self.hidden, self.weights1)
        temp = np.add(temp, self.bias1)
        outputs = vfunc(temp)
        # outputs = np.add(outputs, self.bias1)

        return outputs

    def train(self, arr, target):

        targets = np.array(target).reshape(1, np.array(target).shape[0])
        outputs = self.feedforward(arr)

        errors = np.subtract(targets, outputs)

        # derivs = lambda t: t * (1 - t)
        vfunc = np.vectorize(self.sigmoid_derivs)
        output_derivs = vfunc(outputs)
        output_deltas = np.multiply(errors, output_derivs)

        weights1_t = np.transpose(self.weights1)
        hidden_errors = np.dot(output_deltas, weights1_t)

        hidden_derivs = vfunc(self.hidden)
        hidden_deltas = np.multiply(hidden_errors, hidden_derivs)

        hidden_t = np.transpose(self.hidden)
        self.weights1 = np.add(self.weights1, np.dot(hidden_t, output_deltas))
        input_t = np.transpose(self.inputs)
        self.weights0 = np.add(self.weights0, np.dot(input_t, hidden_deltas))

        self.bias1 = np.add(self.bias1, output_deltas)
        self.bias0 = np.add(self.bias0, hidden_deltas)

    def save_model_weights(self):

        # with open('weights', 'wb') as f:
        np.savez('weights', self.bias0, self.bias1, self.weights0, self.weights1)

    def test_initialization(self):

        # with open('weights', 'rb') as f:
        #     self.bias0 = np.load(f)
        #     self.bias1 = np.laod(f)
        #     self.weights0 = np.load(f)
        #     self.weights1 = np.load(f)

        npzfile = np.load('weights.npz')
        # for arr in npzfile:
        self.bias0 = npzfile['arr_0']
        self.bias1 = npzfile['arr_1']
        self.weights0 = npzfile['arr_2']
        self.weights1 = npzfile['arr_3']


def redrawGameWindow():
    win.blit(bg, (0, 0))
    font = pygame.font.SysFont('arial', 30)
    livesText = font.render('Lives: ' + str(lives), 1, (255, 255, 255))
    playAgainText = font.render('Press Tab to Play Again', 1, (255, 255, 255))
    scoreText = font.render('Score: ' + str(score), 1, (255, 255, 255))
    highScoreText = font.render('High Score: ' + str(highScore), 1, (255, 255, 255))

    player.draw(win)
    for a in asteroids:
        a.draw(win)
    for b in playerBullets:
        b.draw(win)
    # for s in stars:
    #     s.draw(win)
    # for a in aliens:
    #     a.draw(win)
    # for b in alienBullets:
    #     b.draw(win)

    if rapidFire:
        pygame.draw.rect(win, (0, 0, 0), [sw // 2 - 51, 19, 102, 22])
        pygame.draw.rect(win, (255, 255, 255), [sw // 2 - 50, 20, 100 - 100 * (count - rfStart) / 500, 20])

    if gameover:
        win.blit(playAgainText, (sw // 2 - playAgainText.get_width() // 2, sh // 2 - playAgainText.get_height() // 2))
    win.blit(scoreText, (sw - scoreText.get_width() - 25, 25))
    win.blit(livesText, (25, 25))
    win.blit(highScoreText, (sw - highScoreText.get_width() - 25, 35 + scoreText.get_height()))
    pygame.display.update()


def distance(px, py, ax, ay):
    return math.sqrt(math.pow(ax - px, 2) + math.pow(py - ay, 2))


# def collision_avoidance():
#     # print(len(asteroids))
#     # print(player.x, player.y)
#     for asteroid in asteroids:
#         # print(distance(player.x, player.y, asteroid.x, asteroid.y))
#         if distance(player.x, player.y, asteroid.x, asteroid.y) < 100:
#             print("Asteroid Nearby")
#             if asteroid.xv > 0 and asteroid.yv > 0:
#                 player.turnRight()
#                 player.moveForward()
#             elif asteroid.xv > 0 and asteroid.yv < 0:
#                 player.turnLeft()
#                 player.moveForward()
#             elif asteroid.xv < 0 and asteroid.yv > 0:
#                 player.turnLeft()
#                 player.moveForward()
#             else:
#                 player.turnRight()
#                 player.moveForward()


def angle_to_point(x, y, bearing, targetx, targety):

    angle = math.atan2(-targety + y, targetx - x)
    diff = bearing - angle
    return (diff + math.pi * 2) % (math.pi * 2)


def normalise_input(ax, ay, sa, angle, ran):

    arr = [((ax + (50 * ran)) / 2) / (sw + (50 * ran)),
           ((ay + (50 * ran)) / 2) / (sh + (50 * ran)),
           angle / (math.pi * 2), sa / (math.pi * 2)]

    return arr


player = Player()
nn = NeuralNetwork(4, 20, 1)
rangle = 30
mode = argv[1]
if mode == "TRAIN":
    for i in range(100000):
        for j in range(1, 4):
            # ran = random.choice([1, 2, 3])
            ran = j
            ax = np.random.rand() * (sw + 50 * ran) - 50 * ran / 2
            ay = np.random.rand() * (sh + 50 * ran) - 50 * ran / 2

            sa = np.random.rand() * math.pi * 2
            angle = angle_to_point(player.x, player.y, sa, ax, ay)
            direction = 0 if angle > math.pi else 1

            nn.train(normalise_input(ax, ay, sa, angle, ran), [direction])
    nn.save_model_weights()
elif mode == "TEST":
    nn.test_initialization()

playerBullets = []
asteroids = []
count = 0
# stars = []
rand_dir = random.choice([True, False])
# aliens = []
# alienBullets = []
run = True
# d_left = d_right = 0
start = time()
time_list = []
score_list = []
destroyed_asteroids = {}
# stats = True
while run:
    clock.tick(60)
    count += 1
    if not gameover:
        if count % 50 == 0:
            ran = random.choice([1, 1, 1, 2, 2, 3])
            asteroids.append(Asteroid(ran))
        # if count % 1000 == 0:
        #     stars.append(Star())
        # if count % 750 == 0:
        #     aliens.append(Alien())
        # for i, a in enumerate(aliens):
        #     a.x += a.xv
        #     a.y += a.yv
        #     if a.x > sw + 150 or a.x + a.w < -100 or a.y > sh + 150 or a.y + a.h < -100:
        #         aliens.pop(i)
        #     if count % 60 == 0:
        #         alienBullets.append(AlienBullet(a.x + a.w // 2, a.y + a.h // 2))
        #
        #     for b in playerBullets:
        #         if (a.x <= b.x <= a.x + a.w) or a.x <= b.x + b.w <= a.x + a.w:
        #             if (a.y <= b.y <= a.y + a.h) or a.y <= b.y + b.h <= a.y + a.h:
        #                 aliens.pop(i)
        #                 if isSoundOn:
        #                     bangLargeSound.play()
        #                 score += 50
        #                 break
        #
        # for i, b in enumerate(alienBullets):
        #     b.x += b.xv
        #     b.y += b.yv
        #     if (
        #             player.x - player.w // 2 <= b.x <= player.x + player.w // 2) or player.x - player.w // 2 <= b.x + b.w <= player.x + player.w // 2:
        #         if (
        #                 player.y - player.h // 2 <= b.y <= player.y + player.h // 2) or player.y - player.h // 2 <= b.y + b.h <= player.y + player.h // 2:
        #             lives -= 1
        #             alienBullets.pop(i)
        #             break

        # collision_avoidance()
        player.updateLocation()

        for b in playerBullets:
            b.move()
            if b.checkOffScreen():
                playerBullets.pop(playerBullets.index(b))
        # print(len(asteroids))
        for a in asteroids:
            a.x += a.xv
            a.y += a.yv
            # print(a.xv, a.yv)
            if (player.x - player.w // 2 <= a.x <= player.x + player.w // 2) or (
                    player.x + player.w // 2 >= a.x + a.w >= player.x - player.w // 2):
                if (player.y - player.h // 2 <= a.y <= player.y + player.h // 2) or (
                        player.y - player.h // 2 <= a.y + a.h <= player.y + player.h // 2):
                    lives -= 1
                    asteroids.pop(asteroids.index(a))
                    if isSoundOn:
                        bangLargeSound.play()
                    break

            # bullet collision
            for b in playerBullets:
                if (a.x <= b.x <= a.x + a.w) or a.x <= b.x + b.w <= a.x + a.w:
                    if (a.y <= b.y <= a.y + a.h) or a.y <= b.y + b.h <= a.y + a.h:
                        if a.rank == 3:
                            if isSoundOn:
                                bangLargeSound.play()
                            score += 10
                            if 3 in destroyed_asteroids:
                                destroyed_asteroids[3] += 1
                            else:
                                destroyed_asteroids[3] = 1
                            na1 = Asteroid(2)
                            na2 = Asteroid(2)
                            na1.x = a.x
                            na2.x = a.x
                            na1.y = a.y
                            na2.y = a.y
                            asteroids.append(na1)
                            asteroids.append(na2)
                        elif a.rank == 2:
                            if isSoundOn:
                                bangSmallSound.play()
                            score += 20
                            if 2 in destroyed_asteroids:
                                destroyed_asteroids[2] += 1
                            else:
                                destroyed_asteroids[2] = 1
                            na1 = Asteroid(1)
                            na2 = Asteroid(1)
                            na1.x = a.x
                            na2.x = a.x
                            na1.y = a.y
                            na2.y = a.y
                            asteroids.append(na1)
                            asteroids.append(na2)
                        else:
                            score += 30
                            if 1 in destroyed_asteroids:
                                destroyed_asteroids[1] += 1
                            else:
                                destroyed_asteroids[1] = 1
                            if isSoundOn:
                                bangSmallSound.play()
                        asteroids.pop(asteroids.index(a))
                        playerBullets.pop(playerBullets.index(b))
                        break

        # for s in stars:
            # s.x += s.xv
            # s.y += s.yv
            # if s.x < -100 - s.w or s.x > sw + 100 or s.y > sh + 100 or s.y < -100 - s.h:
            #     stars.pop(stars.index(s))
            #     break
            # for b in playerBullets:
            #     if (s.x <= b.x <= s.x + s.w) or s.x <= b.x + b.w <= s.x + s.w:
            #         if (s.y <= b.y <= s.y + s.h) or s.y <= b.y + b.h <= s.y + s.h:
            # if (player.x - player.w // 2 <= s.x <= player.x + player.w // 2) or (
            #         player.x + player.w // 2 >= s.x + s.w >= player.x - player.w // 2):
            #     if (player.y - player.h // 2 <= s.y <= player.y + player.h // 2) or (
            #             player.y - player.h // 2 <= s.y + s.h <= player.y + player.h // 2):
            #         rapidFire = True
            #         rfStart = count
            #         stars.pop(stars.index(s))
                    # playerBullets.pop(playerBullets.index(b))
                    # break

        if lives <= 0:
            gameover = True
            end = time()
            time_list.append(end - start)
            score_list.append(score)
            print(f'Average Time over {len(time_list)} iterations: {sum(time_list) / len(time_list)}')
            print(f'Average Score over {len(score_list)} iterations: {sum(score_list) / len(score_list)}')
            print(f'Average Asteroids over {len(score_list)} iterations:')
            for key in destroyed_asteroids.keys():
                print(f'Rank {key} Asteroids: {round(destroyed_asteroids[key] / len(score_list))}')

        if rfStart != -1:
            if count - rfStart > 500:
                rapidFire = False
                rfStart = -1

        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_LEFT]:
        #     player.turnLeft()
        # if keys[pygame.K_RIGHT]:
        #     player.turnRight()
        # if keys[pygame.K_UP]:
        #     player.moveForward()
        # if keys[pygame.K_DOWN]:
        #     player.moveBackward()
        # if keys[pygame.K_SPACE]:
        #     if rapidFire:
        #         playerBullets.append(Bullet())
        #         if isSoundOn:
        #             shoot.play()

        if not gameover:

            # if count % 180 == 0:
            #     rand_dir = not rand_dir
            # if rand_dir:
            #     player.turnLeft()
            # else:
            #     player.turnRight()
            if asteroids:

                # if count % 50 == 0:
                c = 0
                dist0 = distance(player.x, player.y, asteroids[0].x, asteroids[0].y)
                if len(asteroids) > 1:
                    for i in range(1, len(asteroids)):
                        dist1 = distance(player.x, player.y, asteroids[i].x, asteroids[i].y)
                        if dist1 < dist0:
                            dist0 = dist1
                            c = i
                ax = asteroids[c].x
                ay = asteroids[c].y
                ar = asteroids[c].rank
                sa = player.angle
                angle = angle_to_point(player.x, player.y, sa, ax, ay)
                predict = nn.feedforward(normalise_input(ax, ay, sa, angle, ar))[0][0]

                d_left = abs(predict - 0)
                d_right = abs(predict - 1)
                # print(d_left, d_right)
                if d_left < 0.1:
                    player.rotateShip(False, rangle)
                    if count % 12 == 0:
                        playerBullets.append(Bullet())
                        if isSoundOn:
                            shoot.play()
                elif d_right < 0.1:
                    player.rotateShip(True, rangle)
                    if count % 12 == 0:
                        playerBullets.append(Bullet())
                        if isSoundOn:
                            shoot.play()

            # if rapidFire:
            #     if count % 12 == 0:
            #         playerBullets.append(Bullet())
            #         # print(clock.get_time())
            #         if isSoundOn:
            #             shoot.play()
            # else:
            #     if count % 24 == 0:
            #         playerBullets.append(Bullet())
            #         if isSoundOn:
            #             shoot.play()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_SPACE:
            #         if not gameover:
            #             if not rapidFire:
            #                 playerBullets.append(Bullet())
            #                 if isSoundOn:
            #                     shoot.play()
            if event.key == pygame.K_m:
                isSoundOn = not isSoundOn
            if event.key == pygame.K_TAB:
                if gameover:
                    gameover = False
                    lives = 1
                    asteroids.clear()
                    # aliens.clear()
                    # alienBullets.clear()
                    # stars.clear()
                    if score > highScore:
                        highScore = score
                    score = 0
                    start = time()

    redrawGameWindow()
pygame.quit()
