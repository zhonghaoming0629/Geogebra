import sys,os,pygame,json

js_data = data = load_json_file(f"{BASIC_PATH}/setting.json")

def load_json_file(file_path):
    """
    安全地加载JSON文件,包含完整的错误处理
    """
    # 1. 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在：{file_path}")
    
    # 2. 检查文件是否为空
    if os.path.getsize(file_path) == 0:
        raise ValueError(f"JSON文件为空:{file_path}")
    
    # 3. 读取并解析JSON文件
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # 先读取内容并打印，方便调试
            file_content = file.read()
            
            # 解析JSON
            json_data = json.loads(file_content)
            return json_data
    except UnicodeDecodeError:
        # 如果UTF-8解码失败，尝试GBK编码
        with open(file_path, 'r', encoding='gbk') as file:
            json_data = json.load(file)
            return json_data
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON格式错误:{e}")
    except Exception as e:
        raise Exception(f"读取JSON文件时出错:{e}")

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

UI_TEXT = js_data["ui-text"]
UI_NUM = len(UI_TEXT)
UI_IMAGE = [os.path.join(BASIC_PATH, f"img/{img}.png") for img in js_data["ui-image"]]

DRAW_ORDER = js_data["draw-order"]

TTF_PATH = js_data["ttf-path"]

SELECTED_COLOR = (0, 255, 255)
SELECTED_WIDTH = 3
SELECT_BG_HEIGHT = [0, 600, HEIGHT]

if __name__ == "__main__":
    print(js_data)
