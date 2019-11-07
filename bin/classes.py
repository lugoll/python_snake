import settings as s
import random

from pathlib import Path
from pygame import image
from pygame.font import Font


class ImageWrapper():
    image_object = None
    x = None
    y = None

    def __init__(self,display,x,y):
        self.x = x
        self.y = y
        self.display = display

    def draw(self):
        self.display.blit(self.image_object, (self.x, self.y))


class Field(ImageWrapper):
    solid = None


class Block(Field):
    solid = True
    image_object = image.load(str(Path(s.image_directory + 'block.png')))


class Ground(Field):
    solid = False
    image_object = image.load(str(Path(s.image_directory + 'ground.png')))


class Fruit(ImageWrapper):
    image_object = image.load(str(Path(s.image_directory + 'pineapple.png')))

    def __init__(self,display):
        x = random.randrange(1,s.game_width-1)
        y = random.randrange(1,s.game_height-1)
        super().__init__(
            display,
            x*s.block_size,
            y*s.block_size
        )
        self.map_x = x
        self.map_y = y


class SnakeSegment(ImageWrapper):
    head = False
    image_object = image.load(str(Path(s.image_directory + 'snake.png')))
    direction = None  # up / down / right / left

    def __init__(self,display,x,y,direction='down',head=False,):
        super().__init__(display,x*s.block_size,y*s.block_size,)
        self.direction = direction
        self.head = head
        self.map_x = x
        self.map_y = y

    def draw(self,display=None):
        self.display = display
        super().draw()

    def update_coordinates(self):
        self.map_x = self.x // s.block_size
        self.map_y = self.y // s.block_size

    def get_coordinates(self):
        return (self.map_x,self.map_y)

    def __str__(self):
        return "<Segment head={} x={} y ={}>".format(self.head, self.map_x, self.map_y)


class Snake():
    length = 2
    speed = 1  # affects the velocity of the snake 1 - 16
    change = {
        "state" : False,
        "direction": "",
    }

    move_change = {
        "down": (0,1*s.block_size),
        "up": (0,-1*s.block_size),
        "right": (1*s.block_size,0),
        "left": (-1*s.block_size,0),
    }

    def __init__(self):
        self.move_count = 0
        self.fields = [
            SnakeSegment(None,1,2,head=True),
            SnakeSegment(None,1,1),
        ]

    def grow(self):
        x = self.fields[-1].x
        y = self.fields[-1].y
        direction = self.fields[-1].direction
        self.move()
        self.fields.append(SnakeSegment(None,x,y,direction=direction))
        self.length += 1

    def left(self):
        if self.fields[0].direction is not "right" and self.change["state"] is False:
            self.change["state"] = True
            self.change["direction"] = "left"

    def right(self):
        if self.fields[0].direction is not "left" and self.change["state"] is False:
            self.change["state"] = True
            self.change["direction"] = "right"

    def down(self):
        if self.fields[0].direction is not "up" and self.change["state"] is False:
            self.change["state"] = True
            self.change["direction"] = "down"

    def up(self):
        if self.fields[0].direction is not "down" and self.change["state"] is False:
            self.change["state"] = True
            self.change["direction"] = "up"

    def check_move(self):
        return not self.move_count % s.block_size and not self.move_count == 0

    def move(self):
        # only move if move count is multiple of block_size to slow things down
        if self.check_move():
            x, y, direction = [], [], []
            x.append(self.fields[0].x)
            y.append(self.fields[0].y)
            direction.append(self.fields[0].direction)

            if self.change["state"] is True:
                self.fields[0].direction = self.change["direction"]
                self.change["state"] = False

            self.fields[0].x += Snake.move_change[self.fields[0].direction][0]
            self.fields[0].y += Snake.move_change[self.fields[0].direction][1]
            self.fields[0].update_coordinates()

            for i in range(1,len(self.fields)):
                x.append(self.fields[i].x)
                y.append(self.fields[i].y)
                direction.append(self.fields[i].direction)
                self.fields[i].x = x.pop(0)
                self.fields[i].y = y.pop(0)
                self.fields[i].direction = direction.pop(0)
                self.fields[i].update_coordinates()
            self.move_count = 0
        else:
            self.move_count += self.speed
            #print("{} = {} + {}*{}".format(self.move_count,self.move_count,self.speed,1000))

    def draw(self,display):
        for segment in self.fields:
            #print("drawing segment: ",str(segment))
            segment.draw(display)

    def get_head_coordinates(self):
        if self.change['state']:
            direction = self.change['direction']
        else:
            direction = self.fields[0].direction
        x = self.fields[0].map_x + Snake.move_change[direction][0] // s.block_size
        y = self.fields[0].map_y + Snake.move_change[direction][1] // s.block_size
        return x, y

    def get_body_coordinates(self):
        return [seg.get_coordinates() for seg in self.fields if not seg.head]


class Map():
    pattern = []

    def __init__(self,display):
        self.display = display
        self.pattern.append([
            Block(
                self.display,
                s.block_size*x,
                s.block_size*0
            ) for x in range(0,s.game_width)
        ])

        for y in range(1, s.game_height-1):
            row = []
            # Add first of row
            row.append(Block(
                self.display,
                s.block_size*0,
                s.block_size*y
            ))
            # Add fields between the edge blocks
            for x in range(1, s.game_width-1):
                row.append(Ground(
                    self.display,
                    s.block_size*x,
                    s.block_size*y,
                ))
            # Add last block of row
            row.append(Block(
                self.display,
                s.block_size*(s.game_width-1),
                s.block_size*y
            ))
            # Finally add row to pattern
            self.pattern.append(row)

        self.pattern.append([
            Block(
                self.display,
                s.block_size*x,
                s.block_size*(s.game_height-1)
            ) for x in range(0,s.game_width)
        ])


class Game(Map):
    fruit = None

    def __init__(self,display,snake=Snake()):
        super().__init__(display)
        self.fruit = Fruit(display)
        self.snake = snake

    def draw(self):
        for row in self.pattern:
            for field in row:
                field.draw()

        self.add_fruit()

        if type(self.fruit) is Fruit:
            self.fruit.draw()

        self.snake.draw(self.display)

    def add_fruit(self):
        if self.fruit is None:
            self.fruit = Fruit(self.display)

    def check_field(self,field_tuple):
        if self.snake.check_move():
            return not self.pattern[field_tuple[0]][field_tuple[1]].solid
        else:
            return True

    def check_fruit(self,field_tuple):
        return self.fruit.map_x == field_tuple[0] and self.fruit.map_y == field_tuple[1]


class Message():
    message = ""

    def __init__(self,message):
        self.message = message
        self.font = Font('freesansbold.ttf',50)

    def draw(self,display):
        text_surface = self.font.render(self.message, True, s.black)
        text_rect = text_surface.get_rect()
        text_rect.center = ((s.display_width/2),(s.display_height/2))
        display.blit(text_surface, text_rect)


class Score():
    score = 0

    def __init__(self):
        self.text = "Score: {}"
        self.font = Font('freesansbold.ttf',12)

    def draw(self,display):
        text_surface = self.font.render(self.text.format(self.score), True, s.black)
        text_rect = text_surface.get_rect()
        text_rect.center = (s.block_size*2,s.display_height+s.block_size/2)
        display.blit(text_surface, text_rect)

    def count(self):
        self.score += 1
