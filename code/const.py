import sys,os,pygame

try:
    BASIC_PATH  = sys._MEIPASS
except AttributeError:
    BASIC_PATH  = os.path.abspath(".")

SELECT_BG_POS = pygame.Vector2()
SELECT_BG_COLOR= pygame.Color('lightgray')

WEIGH = 800
HEIGHT = 800

DOT_RADIUS = 10

LINE_WIDTH = 4

UI_TEXT = ['choose','Dot', 'Line']
UI_NUM = len(UI_TEXT)

SELECTED_COLOR = (0, 255, 255)
SELECTED_WIDTH = 3
SELECT_BG_HEIGHT = [0, 600, HEIGHT]

DRAW_ORDER = {
    'Bg': 0,
    'Line': 1,
    'Dot': 2,
    'Text': 3,
}