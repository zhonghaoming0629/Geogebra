import pygame
from const import *
from geogebra import *

class Game:
    def __init__(self):
        pygame.init()
        self.icon = pygame.image.load(join_path(BASIC_PATH, "img","icon.jpg"))
        pygame.display.set_icon(self.icon)
        self.screen  = pygame.display.set_mode((WEIGH, HEIGHT))
        self.geogebra = GeoGebra(self.screen)
        pygame.display.set_caption('GeoGebra')
        self.clock = pygame.time.Clock()
                    
    def run(self):
        try: 
            logging.info("Game started")
            while True:
                for event in pygame.event.get():
                    # 处理退出事件
                    if event.type == pygame.QUIT:
                        logging.info("Game closed")
                        pygame.quit()
                        sys.exit()
                        
                    self.geogebra.run(event)
                self.screen.fill(pygame.Color("white"))
                self.geogebra.draw()
                self.clock.tick(FPS)
                pygame.display.update()
        except Exception as e:
            logging.error(str(e))
            raise e

if __name__ == '__main__':
    logging.info("Game init")
    if DEBUG:
        logging.debug("This run use debug")
    game = Game()
    game.run()
