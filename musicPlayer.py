'''
Author: Seunghee Lee
Last modified: 11/01/2018

    - This module contains functions for playing music.
    - It plays a given music file by using the library 'pygame'
'''

import pygame

class MusicPlayer:

    def __init__(self):

        pygame.init()
        self.music = pygame.mixer.music

    def playMusic(self, musicFilePath):

        '''
        - code references: https://gist.github.com/guitarmanvt/3b6a91cefb2f5c3098ed

        :param musicFilePath: path for midifile
        :return:
        '''

        clock = pygame.time.Clock()
        try:
            self.music.load(musicFilePath)
            print("Music file %s loaded!" % musicFilePath)

        except pygame.error as e:

            print("File %s not found! (%s)" % (musicFilePath, pygame.get_error()))
            return

        self.music.play()

        while pygame.mixer.music.get_busy():

            # check if playback has finished
            clock.tick(30)

    def stopMusic(self):

        self.music.stop()





