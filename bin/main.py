import pygame

import settings
import colors

from classes import Game, Snake, Message, Score

pygame.init()
pygame.display.set_caption('Snake')

gameDisplay = pygame.display.set_mode((settings.display_width, settings.display_height + settings.footer_height))
gameClock = pygame.time.Clock()


crashed = False

snake = Snake()
game = Game(gameDisplay, snake=snake)
score = Score()

while not crashed:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True

        if event.type == pygame.KEYDOWN:
            print("Changed direction to {}".format(event.key))
            if event.key == pygame.K_LEFT:
                snake.left()
            elif event.key == pygame.K_RIGHT:
                snake.right()
            elif event.key == pygame.K_DOWN:
                snake.down()
            elif event.key == pygame.K_UP:
                snake.up()

    gameDisplay.fill(colors.white)
    next_coordinates = snake.get_head_coordinates()

    if game.check_field(next_coordinates) and next_coordinates not in snake.get_body_coordinates():
        if game.check_fruit(next_coordinates):
            snake.grow()
            score.count()
            game.fruit = None
        else:
            snake.move()
        score.draw(gameDisplay)
        game.draw()
    else:
        Message('You Lost !!').draw(gameDisplay)


    pygame.display.update()
    gameClock.tick(60)
