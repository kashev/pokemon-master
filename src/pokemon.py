#!/usr/bin/env python
# pokemon-master

from __future__ import division
from __future__ import print_function

import os
import random
import json

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


def read_from_port(game):
    """ Threading function which reads data from the serial port. """
    # Open Serial Port

    ser = serial.Serial('/dev/ttyACM0', 9600)
    while True:

        game.data = ser.readline()
        game.consumed = False

        if game.over:
            return


class PokemonMaskWidget(Widget):
    """ The mask. """
    def __init__(self, **kwargs):
        super(PokemonMaskWidget, self).__init__(**kwargs)

        self.rect_size = 30
        self.num_rows = 20
        self.num_cols = 20
        self.num_rectangles_unmasked = 0

        with self.canvas:
            Color(0, 0, 1)
            self.mask = [[Rectangle(pos=(row * self.rect_size,
                                         col * self.rect_size),
                                    size=(self.rect_size, self.rect_size))
                          for row in range(self.num_rows)]
                         for col in range(self.num_cols)]

    def remove(self, x, y):
        with self.canvas:
            rect_x = int(x / self.rect_size)
            rect_y = int(y / self.rect_size)
            if rect_x < self.num_cols and rect_y < self.num_rows:
                self.canvas.remove(self.mask[rect_y][rect_x])
                self.num_rectangles_unmasked += 1


class PokemonMasterGame(BoxLayout):
    """ A box layout, which is the whole game. """
    answer = StringProperty(None)
    data = StringProperty(None)
    consumed = BooleanProperty(True)
    over = BooleanProperty(False)

    def run(self, dt):
        """ Run the game at certain intervals. """
        # Check for new data.
        if not self.consumed:
            if self.data[0] == '!':
                print('Broken!')
                # Check to see if the pokemon has been properly guessed.
                if self.answer == self.ids.guessbox.text.lower():
                    print('Winner!')
                    self.over = True
            else:
                touch_info = json.loads(self.data)
                print(touch_info['X'], touch_info['Y'], touch_info['P'])
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

        Clock.schedule_interval(game.run, 1.0 / 10.0)

        return game

    def on_stop(self):
        pass

    def on_pause(self):
        return True


if __name__ == '__main__':
    PokemonApp().run()
