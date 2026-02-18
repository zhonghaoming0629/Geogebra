import sys,pygame
from log import *
from const import *
from sprites import *
import unicodeit

class GeoGebra:
    '''
    GeoGebra 的 Docstring
    '''
    def __init__(self, screen):
        # 初始化 GeoGebra 对象
        self.screen = screen
        # 初始化位置和状态变量
        self.pos = pygame.Vector2(0,0)
        # 拖动背景相关变量
        self.drag_bg_pos = pygame.Vector2(0,0)
        # 鼠标在屏幕上的位置，用于计算拖动背景时的偏移
        self.drag_mouse_screen_pos = pygame.Vector2(0, 0)
        # 是否正在拖动背景的标志
        self.move_background = False
        # 创建一个精灵组来管理所有的精灵对象
        self.all_sprites = CameraGroup(self.screen)
        # 选择背景相关变量
        self.select_height = SELECT_BG_HEIGHT[1]
        # 创建选择背景对象，并将其添加到精灵组中
        self.select_bg = SelectBg((0,self.select_height),self.select_height, self.all_sprites)
        # 定义所有可选择的对象类型和界面元素类型
        self.all_selected = (Dot,Line)
        # 选择界面元素的类型
        self.choose_ui = tuple(type(son) for son in self.select_bg.sons)
        self.choose_obj = None
        print(self.choose_ui)
        # 当前选择的对象和选择历史记录
        self.select = None
        self.select_memory = []
        # 点的编号，用于生成点的名称
        self.dot_n = 0
        # 定义用于判断对象类型的 lambda 函数，分别用于判断是否是可选择的对象和界面元素
        self.lb = lambda obj: isinstance(obj, self.all_selected)
        self.ui = lambda ui: isinstance(ui, self.choose_ui)

        self.all_sprites.add(self.select_bg)

    def run(self):
        # 获取鼠标位置
        pos = self.get_mouse_pos()
        # 处理事件循环
        for event in pygame.event.get():
            # 处理退出事件
            if event.type == pygame.QUIT:
                log("Game closed")
                pygame.quit()
                sys.exit()
            # 处理键盘按下事件
            elif event.type == pygame.KEYDOWN:
                log(f"Key pressed: {event.key}")
                pos = self.get_mouse_pos()
                # 根据按下的键执行相应的操作，例如创建点或线
                #if event.key == pygame.K_c:
                #    self.create_Dot(pos)
                #if event.key == pygame.K_x:
                #    self.create_Line()
            # 处理鼠标按下事件
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 鼠标左键按下
                    # 寻找鼠标点击最近的对象和ui
                    obj = self.search_nearest_object(pos, self.lb)
                    ui = self.search_nearest_object(pos, self.ui)
                    # 如果ui有值，设置选择对象为ui名称
                    if ui:
                        self.choose_obj = ui.get_name()
                    # 如果当前已经有选择对象，并且点击的对象是当前选择对象，则取消选择并准备拖动背景
                    if self.select:
                        if self.select == obj:
                            self.select.set_drag()
                        self.select = None
                    else:
                        # 如果点击了一个可选择的对象，设置为当前选择，并将其添加到选择历史记录中
                        if obj:
                            if  obj not in self.select_memory:
                                self.select_memory.append(obj)
                                self.select = obj
                                self.select.set_drag()
                            # 如果没有点击到任何可选择的对象，清空选择历史记录，并准备拖动背景
                        else: 
                            self.select_memory.clear()
                            self.drag_bg_pos = self.pos.copy()
                            self.drag_mouse_screen_pos = pygame.Vector2(pygame.mouse.get_pos())
                            self.move_background = True 
                    # 如果当前有选择对象，并且点击的对象不是当前选择对象，则根据当前选择的界面元素类型执行相应的操作，例如创建点或线
                    if self.choose_obj:
                        x, y = pygame.mouse.get_pos()
                        if not self.select_bg.rect.collidepoint(x, y):
                            if self.choose_obj == "choose":
                                self.choose_obj = None
                            elif self.choose_obj == Dot.__name__:
                                self.create_Dot(pos)
                            elif self.choose_obj == Line.__name__:
                                self.create_Line(pos)
            # 处理鼠标松开事件                                      
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: # 鼠标左键松开
                    # 如果当前选择的对象仍然是鼠标点击时的最近对象，并且存在选择，则取消拖动状态
                    if self.select==self.search_nearest_object(pos, self.lb) and self.select:
                        self.select.set_drag()
                        self.select = None
                    if self.move_background:    
                        self.move_background = False
        self.all_sprites.custom_draw(self.pos, self.select, self.get_mouse_pos())

        # 如果正在拖动背景，更新位置
        if self.move_background:
            self.pos = self.drag_bg_pos + self.drag_mouse_screen_pos - pygame.Vector2(pygame.mouse.get_pos())

        pygame.display.flip()

    def search_nearest_object(self, pos, match_condition):
        '''
        查找最近的对象
        
        :param pos: 位置
        :param match_condition: 匹配条件函数
        :return: 最近的对象或 None
        '''
        min_distance = float('inf')
        nearest_obj = None
        for obj in self.all_sprites:
            if match_condition(obj):
                distance = (pos - pygame.Vector2(obj.rect.center)).length()

                if distance < min_distance and distance < 10:
                    min_distance = distance
                    nearest_obj = obj
        if nearest_obj:
            return nearest_obj
        else:
            return

    def dot_num(self):
        '''
        dot计数
        :return: 点的名称
        '''
        if self.dot_n < 26:
            text = chr(65 + self.dot_n)
        else:
            text = unicodeit.replace(chr(65 + self.dot_n % 26) + "_" + str(self.dot_n // 26))
        self.dot_n += 1
        return text
    

    def create_Dot(self, pos):
        '''
        创建一个点

        :param pos: 点的位置
        '''
        log('Create a dot')
        text = self.dot_num()
        dot = Dot(self.all_sprites, text, pos, pygame.Color("blue"))

        return dot
    
    def create_Line(self, pos):
        '''
        创建一条线
        
        '''
        log('Create a line')
        if isinstance(self.select, Dot):
            dot1 = self.select
        else:
            dot1 = self.create_Dot(pos)
        

        dot2 = None
        for idx in reversed(range(len(self.select_memory))):
            obj = self.select_memory[idx]
            if isinstance(obj, Dot) and obj != self.select:
                if not dot2:
                    dot2 = obj
                self.select_memory.remove(obj)
        if dot2:
            dot1.connect(dot2)

    def get_mouse_pos(self):
        pos = pygame.Vector2(pygame.mouse.get_pos()) + self.pos
        return pos

class CameraGroup(pygame.sprite.Group):
    def __init__(self, screen):
        super().__init__()
        self.screen = screen

    def custom_draw(self, pos, select, mouse_pos):
        for layer in DRAW_ORDER.values():
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    if sprite.get_drag():
                        sprite.set_pos(mouse_pos)
                    sprite.draw(self.screen, pos, select)