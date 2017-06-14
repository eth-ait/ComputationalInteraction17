from __future__ import division
import os, sys, socket, struct, time
from math import sqrt

import pyglet
from pyglet.gl import *

# screen width, pixels
SCREEN_WIDTH = 1000
# screen height, pixels
SCREEN_HEIGHT = 300
# framerate for the pyglet window
FPS = 60
# port to listen for incoming data
LISTEN_PORT = 12334

# cursor size, pixels
CURSOR_SIZE = 6

# colour of the targets when inactive
INACTIVE_COLOUR = (0.35, 0.35, 0.35)
# colour of targets when hit
ACTIVE_COLOUR = (0.2, 0.9, 0.2)

# soace to toggle
MOUSE_VISIBLE = True

X_POSITION = 200
TARGET_WIDTH = 15
TARGET_HEIGHT = 100
TARGETS = \
        [ 
            # id, x position, y position, width, height, activation distance
            (0, X_POSITION, SCREEN_HEIGHT / 2, TARGET_WIDTH, TARGET_HEIGHT, TARGET_WIDTH),
            (1, SCREEN_WIDTH - X_POSITION, SCREEN_HEIGHT / 2, TARGET_WIDTH, TARGET_HEIGHT, TARGET_WIDTH),
        ]

class Logger(object):

    def __init__(self, basename):
        self.log = None
        for i in range(10000):
            tmp = '%s_%04d_log.csv' % (basename, i)
            if not os.path.exists(tmp):
                self.log = open(tmp, 'w')
                break

        if not self.log:
            print('Failed to create a log file!')
            sys.exit(-1)

        print('Logging data to: %s\n' % self.log.name)

        self.start_time = time.clock()

    def name(self):
        return self.log.name

    def close(self):
        self.log.close()

    def do_log(self, data):
        # add timestamp to each set of data
        self.log.write('%f,%s\n' % (time.clock() - self.start_time, data))

class Target(object):

    def __init__(self, id, x, y, sx, sy, d, b=3):
        self.id = id
        self.x = x
        self.y = y
        self.sx = sx
        self.sy = sy
        self.d = d
        self.b = b
        self.outer_data = ('v2f', (self.x - self.sx, self.y - self.sy, 
                                    self.x - self.sx, self.y + self.sy,
                                    self.x + self.sx, self.y + self.sy,
                                    self.x + self.sx, self.y - self.sy))
        self.inner_data = ('v2f', ((self.x - self.sx) + self.b, (self.y - self.sy) + self.b, 
                                    (self.x - self.sx) + self.b, (self.y + self.sy) - self.b,
                                    (self.x + self.sx) - self.b, (self.y + self.sy) - self.b,
                                    (self.x + self.sx) - self.b, (self.y - self.sy) + self.b))

    def is_hit(self, cx):
        return (self.d >= abs(cx - self.x))

    def dist(self, cx):
        return (cx - self.x)

    def draw(self, cx):
        glColor3f(*INACTIVE_COLOUR)
        pyglet.graphics.draw(4, GL_QUADS, self.outer_data)

        if self.is_hit(cx):
            glColor3f(*ACTIVE_COLOUR)

        pyglet.graphics.draw(4, GL_QUADS, self.inner_data)

class FittsLaw(pyglet.window.Window):

    def __init__(self):
        super(FittsLaw, self).__init__(SCREEN_WIDTH, SCREEN_HEIGHT, vsync=False)

        self.mx = self.width / 2
        self.my = self.height / 2

        self.cx = self.mx
        self.cy = self.my

        self.targets = [Target(*t) for t in TARGETS]

        self.line_data = ('v2f', (self.targets[0].x, self.targets[0].y, self.targets[1].x, self.targets[1].y))

        self.log = Logger('fitts_law')
        self.set_caption('Fitt\'s Law [%s]' % (self.log.name()))

        self.mouse_visible = MOUSE_VISIBLE
        self.set_mouse_visible(self.mouse_visible)

    def update_cursor(self, dt):
        # update cursor pos based on mouse pos...
        self.cx = self.mx

    def update(self, dt):
        self.update_cursor(dt)

        # log format: mouse x, cursor x, target 0 distance, target 1 distance, ???
        self.log.do_log('%d,%d,%d,%d' % (self.mx, self.cx, self.targets[0].dist(self.cx), self.targets[1].dist(self.cx)))

        self.draw()

    def draw(self):
        self.clear()

        self.draw_targets()
        self.draw_cursor()

    def draw_targets(self):
        glColor3f(0.2, 0.2, 0.2)
        pyglet.graphics.draw(2, GL_LINES, self.line_data)
        for t in self.targets:
            t.draw(self.cx)

    def draw_cursor(self):
        glColor3f(1, 1, 1)
        pyglet.graphics.draw(4, GL_QUADS, ('v2f', (   self.cx, self.cy - CURSOR_SIZE / 2,
                                        self.cx + CURSOR_SIZE / 2, self.cy,
                                        self.cx, self.cy + CURSOR_SIZE / 2,
                                        self.cx - CURSOR_SIZE / 2, self.cy)))

    def on_mouse_motion(self, x, y, dx, dy):
        if x >= 0 and x <= SCREEN_WIDTH: #self.targets[0].x and x <= self.targets[1].x:
            self.mx = x
        elif x < 0: #self.targets[0].x:
            self.mx = 0 #self.targets[0].x
        elif x > SCREEN_WIDTH: #self.targets[1].x:
            self.mx = SCREEN_WIDTH #self.targets[1].x

    def on_key_release(self, symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            self.mouse_visible = not self.mouse_visible
            self.set_mouse_visible(self.mouse_visible)

    def run(self):
        pyglet.clock.schedule_interval(self.update, 1.0/FPS)
        pyglet.app.run()
        self.log.close()

if __name__ == "__main__":
    FittsLaw().run()
