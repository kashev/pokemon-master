#!/usr/bin/env python
# pokemon-master

from __future__ import division
from __future__ import print_function

import os
import random
import json
import pyttsx
import vlc  # package python-vlc

import serial
from threading import Thread

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle


# CONSTANTS
POKEMON_DIR = os.path.join('res', 'images', 'pokemon')
SOUND_PATH = os.path.join('res', 'sounds')

# TOUCH PAD CONFIG
PAD_X_RANGE_MAX = 940
PAD_X_RANGE_MIN = 100
PAD_Y_RANGE_MAX = 900
PAD_Y_RANGE_MIN = 260

# Initialize Sound Engine
engine = pyttsx.init()
engine.setProperty('rate', 70)


def clamp(n, smallest, largest):
    """ Given n, clamp its value between smallest and largest. """
    return max(smallest, min(n, largest))


def maprange(a, b, s):
    """ http://rosettacode.org/wiki/Map_range#Python
        Maps s from tuple range a to range b.
    """
    (a1, a2), (b1, b2) = a, b
    return b1 + ((s - a1) * (b2 - b1) / (a2 - a1))


def touch_to_square(touch_x, touch_y, num_rows, num_cols):
    """ Given a touch x and y, convert it to a coordinate on the square. """
    x = clamp(maprange((PAD_Y_RANGE_MAX, PAD_Y_RANGE_MIN),
                       (0, num_rows),
                       touch_y) + random.randrange(-1, 2),
              0, num_rows - 1)

    y = clamp(maprange((PAD_X_RANGE_MAX, PAD_X_RANGE_MIN),
                       (0, num_cols),
                       touch_x) + random.randrange(-1, 2),
              0, num_cols - 1)

    return (int(x), int(y))


def read_from_port(game):
    """ Threading function which reads data from the serial port. """
    # Open Serial Port
    ser = serial.Serial('/dev/ttyACM0', 9600)
    while True:

        game.data = ser.readline()
        game.consumed = False

        if game.over:
            ser.close()
            return


class PokemonMaskWidget(Widget):
    """ The mask. """
    def __init__(self, **kwargs):
        super(PokemonMaskWidget, self).__init__(**kwargs)

        self.rect_size = 16
        self.num_rows = int(256 / self.rect_size) + 1
        self.num_cols = int(256 / self.rect_size) + 1
        self.num_rectangles_unmasked = 0

        self.offset_x = 125
        self.offset_y = 150

        with self.canvas:
            Color(0, 0, 1)
            self.mask = [[Rectangle(pos=(self.offset_x + row * self.rect_size,
                                         self.offset_y + col * self.rect_size),
                                    size=(self.rect_size, self.rect_size))
                          for row in range(self.num_rows)]
                         for col in range(self.num_cols)]

    def on_touch_down(self, touch):
        """ Handle mouse/touch events. """
        with self.canvas:
            rect_x = int((touch.x - self.offset_x) / self.rect_size)
            rect_y = int((touch.y - self.offset_y) / self.rect_size)
            if rect_x < self.num_cols and rect_y < self.num_rows:
                self.canvas.remove(self.mask[rect_y][rect_x])
                self.num_rectangles_unmasked += 1

    def remove(self, touch_x, touch_y):
        """ Handle touch events from the controller. """
        x, y = touch_to_square(touch_x, touch_y, self.num_rows, self.num_cols)
        with self.canvas:
            print("removing {}, {}".format(x, y))
            self.canvas.remove(self.mask[y][x])
            self.num_rectangles_unmasked += 1


class PokemonMasterGame(BoxLayout):
    """ A box layout, which is the whole game. """
    answer = StringProperty(None)
    data = StringProperty(None)
    consumed = BooleanProperty(True)
    over = BooleanProperty(False)

    def win(self, cena=False, khaled=False):
        """ Run winning tasks. """
        if self.over:
            return

        print('Winner!')
        self.over = True

        with self.ids.pokemask.canvas:
            self.ids.pokemask.canvas.clear()
            self.ids.pokemask.canvas.ask_update()

        if cena:
            p = vlc.MediaPlayer(os.path.join(SOUND_PATH, 'john_cena.mp3'))
            p.play()

            with self.ids.pokemask.canvas:
                Rectangle(source='res/images/john cena.png',
                          pos=self.pos, size=self.size)

        elif khaled:
            p = vlc.MediaPlayer(os.path.join(SOUND_PATH, 'dj_khaled.mp3'))
            p.play()

            with self.ids.pokemask.canvas:
                Rectangle(source='res/images/dj khaled.jpg',
                          pos=self.pos, size=self.size)

        else:
            engine.say("It's {}!".format(self.answer))
            engine.runAndWait()

            p = vlc.MediaPlayer(os.path.join(SOUND_PATH, 'pokemon_theme.mp3'))
            p.play()

    def on_enter(self):
        """ Enter key handler. Also called when controller is triggered. """
        # Check to see if the pokemon has been properly guessed.
        guess = self.ids.guessbox.text.lower()
        if guess == self.answer:
            self.win()
        elif guess == 'john cena':
            self.win(cena=True)
        elif guess == 'dj khaled':
            self.win(khaled=True)
        else:
            print('No')
            # engine.say("nah")
            # engine.runAndWait()

    def run(self, dt):
        """ Run the game at certain intervals. """
        # Check for new data.
        if not self.consumed:
            if self.data[0] == '!':
                print('Triggered!')
                self.on_enter()
            else:
                touch_info = json.loads(self.data)
                print(touch_info['X'], touch_info['Y'], touch_info['P'])
                self.ids.pokemask.remove(touch_info['X'], touch_info['Y'])

            self.consumed = True


class PokemonApp(App):
    """ The Pokemon Master Game! """
    def build(self):
        game = PokemonMasterGame()

        # Start data reading thread
        thread = Thread(target=read_from_port, args=(game,))
        thread.daemon = True
        thread.start()

        # Pick a random Pokemon, and set it as the source.
        pokemon_pic = random.choice(os.listdir(POKEMON_DIR))
        pokemon = os.path.splitext(pokemon_pic)[0]
        pokemon_path = os.path.join(POKEMON_DIR, pokemon_pic)

        game.ids.poke.source = pokemon_path
        game.answer = pokemon.lower()

        Clock.schedule_interval(game.run, 1.0 / 60.0)

        p = vlc.MediaPlayer(os.path.join(SOUND_PATH, 'whos_that_pokemon.mp3'))
        p.play()

        p = vlc.MediaPlayer(os.path.join(SOUND_PATH, 'crys',
                                         '{}.ogg'.format(pokemon)))
        p.play()

        return game

    def on_stop(self):
        pass

    def on_pause(self):
        return True


if __name__ == '__main__':
    PokemonApp().run()
