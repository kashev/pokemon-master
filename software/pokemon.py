#!/usr/bin/env python
# pokemon-master

from kivy.app import App


class PokemonApp(App):

    def build(self):
        pass

    def on_pause(self):
        return True


if __name__ == '__main__':
    PokemonApp().run()
