import sys,os,pygame,json,logging
from typing import Callable

try:
    BASIC_PATH  = sys._MEIPASS
except AttributeError:
    BASIC_PATH  = os.path.abspath(".")
print(BASIC_PATH)

DEBUG = True

join_path : Callable[..., str] = os.path.join

GLOBAL_LOGS = logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=join_path(BASIC_PATH,"logs","app.log")
)


with open(join_path(BASIC_PATH, "settings", "ui.json"), "r") as f:
    js_data = json.loads(f.read())
    UI_TEXT = js_data["ui-text"]
    UI_NUM = len(UI_TEXT)
    UI_IMAGE = [join_path(BASIC_PATH, "img",f"{img}.png") for img in js_data["ui-image"]]


SELECT_BG_POS = pygame.Vector2()
SELECT_BG_COLOR= pygame.Color('lightgray')

WEIGH = 800
HEIGHT = 800

FPS = 60

DOT_RADIUS = 10

LINE_WIDTH = 4

DRAW_ORDER = {"Bg" : 3,"Line" : 0,"Dot": 1,"Text": 2}

TTF_PATH = join_path(BASIC_PATH, "ttf","WenJinMinchoP0-Regular.ttf")

SELECTED_COLOR = (0, 255, 255)
SELECTED_WIDTH = 3
SELECT_BG_HEIGHT = [0, 600, HEIGHT]

SUBSCRIPT_MAP = {'₀':'0','₁':'1','₂':'2','₃':'3','₄':'4','₅':'5','₆':'6','₇':'7','₈':'8','₉':'9'}

if __name__ == "__main__":
    print(DRAW_ORDER)
