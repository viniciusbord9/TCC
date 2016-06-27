#!/usr/bin/env python

import os.path
import random
import numpy as np
import cv2
from tracker import Tracker
from common import draw_str, RectSelector
from capture import Capture


#import basic pygame modules
import pygame
from pygame.locals import *
from player import Player
from alien import Alien
from bomb import Bomb
from explosion import Explosion
from shot import Shot
from score import Score

#see if we can load more than standard BMP
if not pygame.image.get_extended():
    raise SystemExit("Sorry, extended image module required")


#game constants
MAX_SHOTS      = 2      #most player bullets onscreen
ALIEN_ODDS     = 1     #chances a new alien appears
BOMB_ODDS      = 200    #chances a new bomb will drop
ALIEN_RELOAD   = 12     #frames between new aliens
SCREENRECT = Rect(0, 0, 640, 480)
eps = 1e-5

main_dir = os.path.split(os.path.abspath(__file__))[0]

def load_image(file):
    "loads an image, prepares it for play"
    file = os.path.join(main_dir, 'data', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
    return surface.convert()

def load_images(*files):
    imgs = []
    for file in files:
        imgs.append(load_image(file))
    return imgs


class dummysound:
    def play(self): pass

def load_sound(file):
    if not pygame.mixer: return dummysound()
    file = os.path.join(main_dir, 'data', file)
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print ('Warning, unable to load, %s' % file)
    return dummysound()

# each type of game object gets an init and an
# update function. the update function is called
# once per frame, and it is when each object should
# change it's current position and state. the Player
# object actually gets a "move" function instead of
# update, since it is passed extra information about
# the keyboard
  
def main(winstyle = 0):
    # Initialize pygame
    capture = Capture('0')
    pygame.init()
    if pygame.mixer and not pygame.mixer.get_init():
        print ('Warning, no sound')
        pygame.mixer = None

    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    #Load images, assign to sprite classes
    #(do this before the classes are used, after screen setup)
    img = load_image('player1.gif')
    Player.images = [img, pygame.transform.flip(img, 1, 0)]
    img = load_image('explosion1.gif')
    Explosion.images = [img, pygame.transform.flip(img, 1, 1)]
    Alien.images = load_images('alien1.gif', 'alien2.gif', 'alien3.gif')
    Bomb.images = [load_image('bomb.gif')]
    Shot.images = [load_image('shot.gif')]

    #decorate the game window
    icon = pygame.transform.scale(Alien.images[0], (32, 32))
    pygame.display.set_icon(icon)
    pygame.display.set_caption('Pygame Aliens')
    pygame.mouse.set_visible(0)

    #create the background, tile the bgd image
    bgdtile = load_image('background.gif')
    background = pygame.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    screen.blit(background, (0,0))
    pygame.display.flip()

    #load the sound effects
    boom_sound = load_sound('boom.wav')
    shoot_sound = load_sound('car_door.wav')
    if pygame.mixer:
        music = os.path.join(main_dir, 'data', 'house_lo.wav')
        pygame.mixer.music.load(music)
        pygame.mixer.music.play(-1)

    # Initialize Game Groups
    aliens = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()
    lastalien = pygame.sprite.GroupSingle()

    #assign default groups to each sprite class
    Player.containers = all
    Alien.containers = aliens, all, lastalien
    Shot.containers = shots, all
    Bomb.containers = bombs, all
    Explosion.containers = all
    Score.containers = all

    #Create Some Starting Values
    global score
    alienreload = ALIEN_RELOAD
    kills = 0
    clock = pygame.time.Clock()

    #initialize our starting sprites
    global SCORE
    player = Player()
    Alien() #note, this 'lives' because it goes into a sprite group
    if pygame.font:
        all.add(Score())

    current_pos = [0,0]
    while player.alive():
        capture.run();
        #get input
        
        if(len(capture.trackers) > 0):
            old_pos = current_pos;
            current_pos = capture.trackers[0].pos
            for event in pygame.event.get():
                if event.type == QUIT or \
                    (event.type == KEYDOWN and event.key == K_ESCAPE):
                        return
            keystate = pygame.key.get_pressed()
            
            if(old_pos[0] > current_pos[0]):
                direction = 1
            elif(old_pos[0] < current_pos[0]):
                direction = -1
            else:
                direction = 0
                
            
            
            # clear/erase the last drawn sprites
            all.clear(screen, background)

            #update all the sprites
            all.update()

            #handle player input
            #direction = keystate[K_RIGHT] - keystate[K_LEFT]
            player.move(direction)
            firing = keystate[K_SPACE]
            if not player.reloading and firing and len(shots) < MAX_SHOTS:
                Shot(player.gunpos())
                shoot_sound.play()
            player.reloading = firing


            # Drop bombs
            if lastalien and not int(random.random() * BOMB_ODDS):
                Bomb(lastalien.sprite)

            # Detect collisions
            for alien in pygame.sprite.spritecollide(player, aliens, 1):
                boom_sound.play()
                Explosion(alien)
                Explosion(player)
                SCORE = SCORE + 1
                player.kill()

            for alien in pygame.sprite.groupcollide(shots, aliens, 1, 1).keys():
                boom_sound.play()
                Explosion(alien)
                SCORE = SCORE + 1

            for bomb in pygame.sprite.spritecollide(player, bombs, 1):
                boom_sound.play()
                Explosion(player)
                Explosion(bomb)
                player.kill()

            #draw the scene
            dirty = all.draw(screen)
            pygame.display.update(dirty)

            #cap the framerate
            clock.tick(40)

    if pygame.mixer:
        pygame.mixer.music.fadeout(1000)
    pygame.time.wait(1000)
    pygame.quit()
    cv2.destroyWindow('frame')



#call the "main" function if running this script
if __name__ == '__main__': main()

