import pygame, sys
from log import log
from const import *
from geogebra import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WEIGH, HEIGHT))
        self.geogebra = GeoGebra(self.screen)
        pygame.display.set_caption('GeoGebra')
        self.clock = pygame.time.Clock()
                    
    def run(self):
        try: 
            log("Game started")
            while True:
                self.geogebra.run()
                pygame.display.update()
                self.screen.fill(pygame.Color("white"))
                self.clock.tick(60)
        except Exception as e:
            log(f"{e}", "Error")
            raise e

if __name__ == '__main__':
    log("game init")
    game = Game()
    game.run()