#!/usr/bin/env python
# pokemon-master

from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.graphics import Canvas, Color, Ellipse, Rectangle
from kivy.properties import StringProperty

class PokemonImage(Image):
    source = StringProperty('../res/abra.png')


class PokemonMaskWidget(Widget):

    def __init__(self, **kwargs):
        super(PokemonMaskWidget, self).__init__(**kwargs)

        self.rect_size = 10
        self.num_rows = 50
        self.num_cols = 50
        self.num_rectangles_unmasked = 0

        with self.canvas:
            Color(0, 0, 1)
            self.mask = [[Rectangle(pos=(row * self.rect_size, 
                                         col * self.rect_size), 
                                    size = (self.rect_size, self.rect_size))
                          for row in range(self.num_rows)] 
                          for col in range(self.num_cols)]
    
    def on_touch_down(self, touch):
        with self.canvas:
            rect_x = int(touch.x / self.rect_size)
            rect_y = int(touch.y / self.rect_size)
            if rect_x < self.num_cols and rect_y < self.num_rows:
                self.canvas.remove(self.mask[rect_y][rect_x])
                self.num_rectangles_unmasked += 1


class PokemonApp(App):

    def build(self):
        parent = Builder.load_file('pokemon.kv')
        parent.add_widget(PokemonMaskWidget())        
        return parent

    def on_pause(self):
        return True


if __name__ == '__main__':
    PokemonApp().run()
