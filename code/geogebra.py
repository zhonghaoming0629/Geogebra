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
        self.input_box = InputBox(pygame.Vector2(WEIGH/2, HEIGHT/2), 100, 30,"请输入长度", self.all_sprites)
        # 定义所有可选择的对象类型和界面元素类型
        self.all_selected = (Dot,Line,Circle)
        # 选择界面元素的类型
        self.choose_ui = tuple(type(son) for son in self.select_bg.sons)
        self.choose_obj = None
        # 当前选择的对象和选择历史记录
        self.select = None
        self.select_memory = []
        # 点的编号，用于生成点的名称
        self.dot_n = 0
        self.used_dot_names = set()
        self.free_dot_names = []
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
                self.get_input(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 鼠标左键按下
                    # 寻找鼠标点击最近的对象和ui
                    obj = self.search_nearest_object(pos, self.lb)
                    ui = self.search_nearest_object(pygame.mouse.get_pos(), self.ui)
                    log(f"Nearest obj {obj}, nearest ui {ui}")
                    if self.input_box.rect.collidepoint(pos):
                        self.input_box.set_active(True)
                    else:
                        self.input_box.set_active(False)
                    # 如果ui有值，设置选择对象为ui名称
                    if ui:
                        self.choose_obj = ui.get_name()
                        log(f"User choose obj {self.choose_obj}")
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
                        self.choose(pos)
            # 处理鼠标松开事件                                      
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: # 鼠标左键松开
                    # 如果当前选择的对象仍然是鼠标点击时的最近对象，并且存在选择，则取消拖动状态
                    if self.select==self.search_nearest_object(pos, self.lb) and self.select:
                        self.select.set_drag()
                        self.select = None
                    if self.move_background:    
                        self.move_background = False

        self.screen.fill(pygame.Color("white"))
        self.all_sprites.custom_draw(self.pos, self.select, self.get_mouse_pos())

        #print(self.choose_obj)

        # 如果正在拖动背景，更新位置
        if self.move_background:
            self.pos = self.drag_bg_pos + self.drag_mouse_screen_pos - pygame.Vector2(pygame.mouse.get_pos())

    def get_input(self, event):
        if self.input_box.get_active():
            if event.key == pygame.K_BACKSPACE:
                self.input_box.text= self.input_box.text[:-1]
            # 回车键 - 确认输入（这里仅打印，可自定义逻辑）
            elif event.key == pygame.K_RETURN:
                if self.choose_obj == "定长线段":
                    self.create_Line(self.pos)
            # 普通字符 - 过滤特殊键，只添加可打印字符
            elif event.unicode.isprintable():
            # 限制输入长度（可选）
                if len(self.input_box.text) < 20:
                    if event.unicode.isdigit():
                        self.input_box.text += event.unicode

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
                distance = (pos - pygame.Vector2(obj.get_rect().center)).length()

                if distance < min_distance and distance < 10:
                    min_distance = distance
                    nearest_obj = obj
        if nearest_obj:
            return nearest_obj
        else:
            return

    def sort_key(self, name):
        char_part = ''  # 字母部分
        num_part = ''

        for word in name:
            if word.isalpha():
                char_part = word
                break
        
        # 先把Unicode下标转为普通数字（₁→1，₂→2…₉→9，₀→0）
        name_normalized = name
        for sub, num in SUBSCRIPT_MAP.items():
            name_normalized = name_normalized.replace(sub, num)
        
        # 提取所有数字字符
        for num in name_normalized:
            if num.isdigit():
                num_part = num
        num = int(num_part) if num_part else 0
        
        first_char = char_part if char_part else ' '
        return (num, ord(first_char))
    
    def delete(self):
        deleted_names = self.select.delete(self.used_dot_names)
        
        if deleted_names:  # 只有存在被删除的名称时才处理
            unique_names = list(set(deleted_names))
            # 排序：按自定义规则排序，保证名称顺序符合直觉
            unique_names.sort(key=self.sort_key)
            
            # 3. 回收排序后的名称到闲置队列
            for name in unique_names:
                if name not in self.free_dot_names and name in self.used_dot_names:
                    self.free_dot_names.append(name)
                    self.used_dot_names.remove(name)
            self.free_dot_names.sort(key=self.sort_key)
            log(f"After sort the free_dot_names is {self.free_dot_names}")
        self.select = None

    def choose(self, pos):
        x, y = pygame.mouse.get_pos()
        if not self.select_bg.get_rect().collidepoint(x, y):
            if self.choose_obj == "选择":
                self.choose_obj = None
            elif self.choose_obj == "删除" and self.select:
                self.delete()
            elif self.choose_obj == "显示/隐藏对象" and self.select:
                self.select.set_appear()
                #self.select = "SH"
            elif self.choose_obj == "点":
                self.create_Dot(pos)
            elif self.choose_obj == "线":
                self.create_Line(pos)
            elif self.choose_obj == "圆(圆形与一点)":
                self.create_Circle(pos)
            elif self.choose_obj == "定长线段":
                self.input_box.set_appear()

    def dot_num(self):
        '''
        dot计数:优先复用已删除的名称，无闲置时生成新名称
        :return: 唯一的点名称
        '''
        if self.free_dot_names:
            text = self.free_dot_names.pop(0)
        else:
            if self.dot_n < 26:
                text = chr(65 + self.dot_n)
            else:
                base_char = chr(65 + self.dot_n % 26)
                num = self.dot_n // 26
                if unicodeit:
                    text = unicodeit.replace(f"{base_char}_{num}")
                else:
                    text = f"{base_char}_{num}"
            self.dot_n += 1  
        
        self.used_dot_names.add(text)
        log(f"Dot text{text}")
        return text
    
    def create_Dot(self, pos):
        '''
        创建一个点

        :param pos: 点的位置
        '''
        log('Create a dot')
        text = self.dot_num()
        lb1 = lambda obj : isinstance(obj, (Line, Circle))
        obj1 = self.search_nearest_object(pos, lb1)
        lb2 = lambda obj : lb1(obj) and obj != obj1
        obj2 = self.search_nearest_object(pos, lb2)
        if obj1:
            if obj2:
                dot = Dot(self.all_sprites, text, pos, "intersection", [obj1, obj2], color=pygame.Color("grey"))
            else:
                dot = Dot(self.all_sprites, text, pos, "plot",[obj1], color=pygame.Color("grey"))
        else:
            dot = Dot(self.all_sprites, text, pos, "normal", color=pygame.Color("blue"))

        return dot

    def create_LineFL(self, pos, long):
        '''
        创建一条线
        
        '''
        log('Create a lineFL')
        if isinstance(self.select, Dot):
            dot1 = self.select
        else:
            dot1 = self.create_Dot(pos)
        
        dot2 = self.create_Dot(pos+pygame.Vector2(long, 0))
        groups = list(set(dot1.groups()).union(dot2.groups()))
        line = Line(groups, dot1.get_rect().center, [dot1, dot2])

        return line

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
            start_pos = dot1.get_rect().center
            groups = list(set(dot1.groups()).union(dot2.groups()))
            line = Line(groups, start_pos, [dot1, dot2])
            dot1.add_son(line)
            dot2.add_son(line)
            return line

    def create_Circle(self, pos):
        log('Create a circle')
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
            center_pos = dot1.get_rect().center
            groups = list(set(dot1.groups()).union(dot2.groups()))
            circle = Circle(groups, center_pos, [dot1, dot2])
            dot1.add_son(circle)
            dot2.add_son(circle)
            return circle

    def get_mouse_pos(self):
        pos = pygame.Vector2(pygame.mouse.get_pos()) + self.pos
        return pos

class CameraGroup(pygame.sprite.Group):
    def __init__(self, screen):
        super().__init__()
        self.screen = screen

    def custom_draw(self, pos, select, mouse_pos):
        sorted_sprites = sorted(
            self.sprites(),
            key=lambda s: (s.z, s.rect.centery, s.rect.centerx)  # 补充x坐标，排序更稳定
        )
        for layer in range(4):
            for sprite in sorted_sprites:
                if sprite.z != layer:
                    continue
                if sprite.get_drag():
                    sprite.rebuild(mouse_pos)
                sprite.draw(self.screen, pos, select)

        pygame.display.flip()