#!/usr/bin/env python
# pokemon-master

from kivy.app import App
from kivy.uix.image import Image
from kivy.properties import StringProperty


class PokemonImage(Image):
    source = StringProperty('../res/1891631-016pidgey.png')


class PokemonApp(App):

    def build(self):
        pass

    def on_pause(self):
        return True


if __name__ == '__main__':
    PokemonApp().run()
