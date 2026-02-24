import sys,os,pygame,json

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

with open(f"{BASIC_PATH}/setting.json", 'r', encoding='utf-8') as file:
    js_data = list(json.load(file).values())
    UI_TEXT = js_data[0]
    UI_NUM = len(UI_TEXT)
    DRAW_ORDER = js_data[2]
    UI_IMAGE = []
    for i in js_data[1]:
        UI_IMAGE.append(os.path.join(BASIC_PATH, f"img/{i}.png"))


TTF_PATH = "ttf/WenJinMinchoP0-Regular.ttf"

SELECTED_COLOR = (0, 255, 255)
SELECTED_WIDTH = 3
SELECT_BG_HEIGHT = [0, 600, HEIGHT]

if __name__ == "__main__":
    print(DRAW_ORDER, type(DRAW_ORDER))
