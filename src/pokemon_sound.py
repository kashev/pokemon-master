import pyttsx
import vlc  # package python-vlc
import os

SOUND_PATH = os.path.join('res', 'sounds')

engine = pyttsx.init()
engine.setProperty('rate', 70)

p = vlc.MediaPlayer(os.path.join(SOUND_PATH, 'whos_that_pokemon.mp3'))
p.play()

engine.say("It's bulbasaur!")
engine.runAndWait()
