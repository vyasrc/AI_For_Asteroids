import pygame
import math
import random
import pygame.math as pymath
from time import time
from sys import argv

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


class SteeringData(object):
    def __init__(self):
        self.linear = pymath.Vector2()
        self.angular = float()


class Kinematic(object):
    maxVel = 30.0
    maxRot = 50.0

    def __init__(self, position, orientation):
        self.position = position
        self.velocity = pymath.Vector2(0, 0)
        self.orientation = orientation
        self.rotation = 0.0
    
    def update(self, steering, time):
        self.position += self.velocity * time
        self.orientation += self.rotation * time

        self.velocity = steering.linear
        self.rotation = steering.angular
    #
    # def move(self, time):
    #     self.pos *= self.vel * time
    #     self.orientation *= self.rot * time


class SteeringBehavior(object):

    def calculate_acceleration(self, character, goal):
        pass


class Position(SteeringBehavior):

    def __init__(self):
        self.speed = 1.0
        self.acc = 1.0
        self.radius = 0.3
        self.targetSpeed = 0.0
        self.direction = pymath.Vector2()
        self.targetVelocity = pymath.Vector2()

    def calculate_acceleration(self, character, goal):

        result = SteeringData()

        self.direction = goal.position - character.position

        distance = self.direction.length()

        if distance > self.radius:
            self.targetSpeed = self.speed
        else:
            self.targetSpeed = self.speed * distance / self.radius

        self.targetVelocity = self.direction
        self.targetVelocity.normalize()
        self.targetVelocity *= self.speed

        result.linear = self.targetVelocity - character.velocity

        if result.linear.length() > self.acc:
            result.linear.normalize()
            result.linear *= self.acc

        result.angular = 0

        return result


class Orientation(SteeringBehavior):

    def __init__(self):
        self.acc = 100.0
        self.radius = 5.0
        self.targetRotation = 0.0
        self.rotationSize = 0.0
        self.rotationSize = 0.0
        self.maxRotation = 180.0

    def calculate_acceleration(self, character, goal):

        result = SteeringData()

        rotation = goal.orientation - character.orientation

        r = int(rotation) % 360

        if abs(r) <= 180:
            rotation = r
        elif r > 180:
            rotation = 360 - r
        else:
            rotation = r + 180

        self.rotationSize = abs(rotation)

        if self.rotationSize > self.radius:
            self.targetRotation = self.maxRotation
        else:
            self.targetRotation = self.maxRotation * self.rotationSize / self.radius

        if self.rotationSize == 0:
            self.targetRotation += rotation
        else:
            self.targetRotation += rotation / self.rotationSize

        result.angular = self.targetRotation - character.orientation

        if abs(result.angular) > self.acc:
            result.angular /= abs(result.angular)
            result.angular *= self.acc

        result.linear = pymath.Vector2(0, 0)

        return result


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
        # print(self.angle)
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
        if self.x > sw:
            self.x = 0
        elif self.x < 0:
            self.x = sw
        elif self.y < 0:
            self.y = sh
        elif self.y > sh:
            self.y = 0

    def updateValues(self, values):

        self.angle = values.orientation
        self.x = values.position.x
        self.y = values.position.y


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
        self.xv = self.xdir * random.randrange(1, 3)
        self.yv = self.ydir * random.randrange(1, 3)

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


class Star(object):
    def __init__(self):
        self.img = star
        self.w = self.img.get_width()
        self.h = self.img.get_height()
        self.ranPoint = random.choice([(random.randrange(0, sw - self.w), random.randrange(0, sh - self.h))])
        # print(self.ranPoint)
        self.x, self.y = self.ranPoint
        # if self.x < sw // 2:
        #     self.xdir = 1
        # else:
        #     self.xdir = -1
        # if self.y < sh // 2:
        #     self.ydir = 1
        # else:
        #     self.ydir = -1
        # self.xv = self.xdir * 2
        # self.yv = self.ydir * 2

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))


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
    for s in stars:
        s.draw(win)
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


def collision_distance(px, py, ax, ay):

    return math.sqrt(math.pow(ax - px, 2) + math.pow(py - ay, 2))


def collision_avoidance():
    # print(len(asteroids))
    # print(player.x, player.y)

    collision = False

    for asteroid in asteroids:
        # print(distance(player.x, player.y, asteroid.x, asteroid.y))
        if collision_distance(player.x, player.y, asteroid.x, asteroid.y) < 100:
            # print("Asteroid Nearby")
            if asteroid.xv > 0 and asteroid.yv > 0:
                player.turnRight()
                player.moveForward()
            elif asteroid.xv > 0 and asteroid.yv < 0:
                player.turnLeft()
                player.moveForward()
            elif asteroid.xv < 0 and asteroid.yv > 0:
                player.turnLeft()
                player.moveForward()
            else:
                player.turnRight()
                player.moveForward()

            collision = True

    return collision


def collision_avoidance():
    # print(len(asteroids))
    # print(player.x, player.y)

    collision = False

    for asteroid in asteroids:
        # print(distance(player.x, player.y, asteroid.x, asteroid.y))
        if collision_distance(player.x, player.y, asteroid.x, asteroid.y) < 100:
            # print("Asteroid Nearby")
            if asteroid.xv > 0 and asteroid.yv > 0:
                player.turnRight()
                player.moveForward()
            elif asteroid.xv > 0 and asteroid.yv < 0:
                player.turnLeft()
                player.moveForward()
            elif asteroid.xv < 0 and asteroid.yv > 0:
                player.turnLeft()
                player.moveForward()
            else:
                player.turnRight()
                player.moveForward()

            collision = True

    return collision


def collect_powerup(time_elapsed):
    # result_position = SteeringData()
    # result_orientation = SteeringData()

    result_position = pos.calculate_acceleration(player_kinematic, star_kinematic)
    result_orientation = orient.calculate_acceleration(player_kinematic, star_kinematic)
    # print(resultPosition.linear)

    if time_elapsed == 0:
        time_elapsed = clock.get_rawtime()
    if 0 < clock.get_rawtime() < 20:
        time_elapsed = clock.get_rawtime()

    player_kinematic.update(result_position, time_elapsed / 1000)
    player_kinematic.update(result_orientation, time_elapsed / 1000)

    if math.isnan(player_kinematic.orientation):
        player_kinematic.orientation = 0
    # print(player_kinematic.position)
    player.updateValues(player_kinematic)


player = Player()
player_kinematic = Kinematic(pymath.Vector2(player.x, player.y), player.angle)
pos = Position()
orient = Orientation()
playerBullets = []
asteroids = []
count = 0
stars = []
rand_dir = random.choice([True, False])
# aliens = []
# alienBullets = []
# collect_star = False
timeElapsed = 0
run = True
start = time()
time_list = []
score_list = []
destroyed_asteroids = {}
while run:
    clock.tick(100)

    if not gameover:
        if count % 50 == 0:
            ran = random.choice([1, 1, 1, 2, 2, 3])
            asteroids.append(Asteroid(ran))
        if count % 1000 == 0 and stars == [] and not rapidFire:
            stars.append(Star())
            # collect_star = True
            theta = math.atan2(stars[-1].y - player.y, stars[-1].x - player.x)
            deg = theta * 180 / 3.141592
            # print(deg)
            star_kinematic = Kinematic(pymath.Vector2(stars[-1].x, stars[-1].y), deg)
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

        collision_flag = collision_avoidance()

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

        for s in stars:
            # s.x += s.xv
            # s.y += s.yv
            # if s.x < -100 - s.w or s.x > sw + 100 or s.y > sh + 100 or s.y < -100 - s.h:
            #     stars.pop(stars.index(s))
            #     break
            # for b in playerBullets:
            #     if (s.x <= b.x <= s.x + s.w) or s.x <= b.x + b.w <= s.x + s.w:
            #         if (s.y <= b.y <= s.y + s.h) or s.y <= b.y + b.h <= s.y + s.h:

            if argv[1] == 'ARBITRATION' and not collision_flag:
                collect_powerup(timeElapsed)
            elif argv[1] == 'BLENDING':
                collect_powerup(timeElapsed)

            # if count == 101:
            #     gameover = True
            if (player.x - player.w // 2 <= s.x <= player.x + player.w // 2) or (
                    player.x + player.w // 2 >= s.x + s.w >= player.x - player.w // 2):
                if (player.y - player.h // 2 <= s.y <= player.y + player.h // 2) or (
                        player.y - player.h // 2 <= s.y + s.h <= player.y + player.h // 2):
                    rapidFire = True
                    rfStart = count
                    stars.pop(stars.index(s))
                    # playerBullets.pop(playerBullets.index(b))
                    break

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

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.turnLeft()
        if keys[pygame.K_RIGHT]:
            player.turnRight()
        if keys[pygame.K_UP]:
            player.moveForward()
        if keys[pygame.K_DOWN]:
            player.moveBackward()
        # if keys[pygame.K_SPACE]:
        #     if rapidFire:
        #         playerBullets.append(Bullet())
        #         if isSoundOn:
        #             shoot.play()

        if not gameover:
            if count % 180 == 0:
                rand_dir = not rand_dir
            if rand_dir:
                player.turnLeft()
            else:
                player.turnRight()
            if rapidFire:
                if count % 11 == 0:
                    playerBullets.append(Bullet())
                    # print(clock.get_time())
                    if isSoundOn:
                        shoot.play()
            else:
                if count % 22 == 0:
                    playerBullets.append(Bullet())
                    if isSoundOn:
                        shoot.play()

    count += 1

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
                    stars.clear()
                    if score > highScore:
                        highScore = score
                    score = 0
                    count = 0
                    start = time()
                    rapidFire = False
                    rfStart = -1

    redrawGameWindow()
pygame.quit()
