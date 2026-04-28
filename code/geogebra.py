import pygame, logging
from const import *
from sprites import *
import unicodeit
from typing import Iterable, Any, NoReturn

class GeoGebra:
    '''
    GeoGebra 的 Docstring
    '''
    def __init__(self, screen:pygame.Surface):
        self.screen = screen
        self.pos = pygame.Vector2(0,0)
        self.moved_bg = False
        self.all_sprites = CameraGroup(self.screen)
        self.select_height = SELECT_BG_HEIGHT[1]
        self.select_bg = SelectBg(self.all_sprites,
                                  pos=pygame.Vector2(0,self.select_height),
                                  height=self.select_height)
        self.input_box = InputBox(self.all_sprites,
                                  pos=pygame.Vector2(WEIGH/2, HEIGHT/2),
                                  width=100,
                                  height=30,
                                  placeholder="请输入长度")
        self.choice : Optional[GeoGebraObject] = None
        self.select = None
        self.select_memory = []
        self.dot_n = 0
        self.used_dot_names : set[str] = set()
        self.free_dot_names = []
        self.choose_obj_func : Callable[[GeoGebraObject], bool] = lambda obj: isinstance(obj, (Dot,Line,Circle))
        self.choose_ui_func = lambda ui: isinstance(ui, tuple(type(son) for son in self.select_bg.sons))

        self.all_sprites.add(self.select_bg)

    def run(self, event) -> None:
        pos = self.get_mouse_pos()
        if event.type == pygame.KEYDOWN:
            logging.info(f"Key pressed: {event.key}")
            self.get_input(event)
        self.choose_obj(pos, event)
        self.move_bg(pos, event)
        self.choose(pos, event)

    def draw(self):
        self.all_sprites.custom_draw(self.pos, self.select, self.get_mouse_pos())
    
    def choose_obj(self,
                   pos: pygame.Vector2,
                   event: list[pygame.event.Event]) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            nearest_obj = self.search_nearest_object(pos, self.lb)
            nearest_ui = self.search_nearest_object(pos ,self.ui)
            logging.debug(f"Choose obj and ui is {nearest_obj}, {nearest_ui}")
            if nearest_ui:
                self.choice = nearest_ui.name
            if nearest_obj:
                if self.select == nearest_obj:
                    self.select.set_drag(False)
                    self.select = None
                    self.select_memory.pop()
                else:
                    self.select = nearest_obj
                    nearest_obj.set_drag(True)
                    self.select_memory.append(nearest_obj)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.select:
                self.select.set_drag(False)
                self.select = None

    def move_bg(self,pos:pygame.Vector2, event:list[pygame.event.Event]) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hasattr(self.select, "set_drag"):
                if self.select.get_drag():
                    return
                    
            if not self.search_nearest_object(pos, self.choose_obj_func):
                self.moved_bg = True
                self.start_pos = pygame.Vector2(pygame.mouse.get_pos())
                self.start_offest_pos = self.pos
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.moved_bg:
            self.moved_bg = False

        if self.moved_bg:
            offest_pos = pygame.Vector2(pygame.mouse.get_pos()) - self.start_pos
            self.pos = self.start_offest_pos - offest_pos

    def get_input(self, event:pygame.event.Event):
        if self.input_box.get_active():
            if event.key == pygame.K_BACKSPACE:
                self.input_box.text= self.input_box.text[:-1]
            
            elif event.key == pygame.K_RETURN:
                if self.choice == "定长线段":
                    self.create_Line(self.pos)
            
            elif event.unicode.isprintable():
            
                if len(self.input_box.text) < 20:
                    if event.unicode.isdigit():
                        self.input_box.text += event.unicode

    def search_nearest_object(self, pos : pygame.Vector2,
                            match_condition : Callable[GeoGebraObject, bool]) -> Optional[GeoGebraObject]:
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
                if isinstance(obj, Line):
                    if obj.type == "up":
                        x = obj.pos.x
                        y = pos.y
                    else:
                        k = obj.k
                        b = obj.b
                        x = (pos.x + k * pos.y - k * b) // k**2 +1
                        y = k *x + b
                    if x >= max(obj.parent1.pos.x, obj.parent2.pos.x) or x <= min(obj.parent1.pos.x, obj.parent2.pos.x) or y >= max(obj.parent1.pos.y, obj.parent2.pos.y) or x <= min(obj.parent1.pos.y, obj.parent2.pos.y):
                        distance = min((pos - obj.parent1.pos).length, (pos - obj.parent2.pos).length)
                    else:
                        distance = (pos - pygame.Vector2(x, y)).length
                else:
                 distance = (pos - pygame.Vector2(obj.get_rect().center)).length()

                if distance < min_distance and distance < 10:
                    min_distance = distance
                    nearest_obj = obj
        return nearest_obj
        
    def sort_key(self, name):
        char_part = ''  
        num_part = ''

        for word in name:
            if word.isalpha():
                char_part = word
                break
        
        
        name_normalized = name
        for sub, num in SUBSCRIPT_MAP.items():
            name_normalized = name_normalized.replace(sub, num)
        
        
        for num in name_normalized:
            if num.isdigit():
                num_part = num
        num = int(num_part) if num_part else 0
        
        first_char = char_part if char_part else ' '
        return (num, ord(first_char))
    
    def delete(self):
        deleted_names = self.select.delete(self.used_dot_names)
        
        if deleted_names:  
            unique_names = list(set(deleted_names))
            
            unique_names.sort(key=self.sort_key)
            
            for name in unique_names:
                if name not in self.free_dot_names and name in self.used_dot_names:
                    self.free_dot_names.append(name)
                    self.used_dot_names.remove(name)
            self.free_dot_names.sort(key=self.sort_key)
            logging.debug(f"After sort the free_dot_names is {self.free_dot_names}")
        self.select = None

    def choose(self, pos, event):
        x, y = pygame.mouse.get_pos()
        if not self.select_bg.get_rect().collidepoint(x, y) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.choice == "选择":
                self.choice = None
            elif self.choice == "删除" and self.select:
                self.delete()
            elif self.choice == "显示/隐藏对象" and self.select:
                self.select.set_appear()
            elif self.choice == "点":
                obj = self.create_Dot(pos)
            elif self.choice == "线":
                obj = self.create_Line(pos)
            elif self.choice == "圆(圆形与一点)":
                obj = self.create_Circle(pos)
            
            elif self.choice == "定长线段":
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
        logging.debug(f"Dot text{text}")
        return text
    
    def create_Dot(self, pos):
        '''
        创建一个点

        :param pos: 点的位置
        '''
        logging.info('Create a dot')
        text = self.dot_num()
        lb1 = lambda obj : isinstance(obj, (Line, Circle))
        obj1 = self.search_nearest_object(pos, lb1)
        lb2 = lambda obj : lb1(obj) and obj != obj1
        obj2 = self.search_nearest_object(pos, lb2)
        if obj1:
            if obj2:
                dot = Dot(self.all_sprites,
                          text=text,
                          pos=pos,
                          type="intersection",
                          parents=[obj1, obj2],
                          color=pygame.Color("grey"))
            else:
                dot = Dot(self.all_sprites,
                          text=text,
                          pos=pos, 
                          type="plot",
                          parents=[obj1],
                          color=pygame.Color("grey"))
        else:
            dot = Dot(self.all_sprites,
                      text=text,
                      pos=pos, 
                      type="normal",
                      color=pygame.Color("blue"))

        return dot
    
    def create_LineFL(self, pos, long):
        '''
        创建一条线
        
        '''
        logging.info('Create a lineFL')
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
        logging.info('Create a line')
        if isinstance(self.select, Dot):
            dot1 = self.select
        else:
            dot1 = self.create_Dot(pos)
        
        if len(self.select_memory) > 1 and isinstance(self.select_memory[-2], Dot):
            dot2 = self.select_memory[-2]
            self.select_memory.pop(-2)
        else:
            dot2 = None

        if dot2:
            self.select_memory.pop()
            start_pos = dot1.get_rect().center
            groups = list(set(dot1.groups()).union(dot2.groups()))
            line = Line(groups,
                        pos=start_pos,
                        parents=[dot1, dot2])
            dot1.add_son(line)
            dot2.add_son(line)
            return line

    def create_Circle(self, pos):
        logging.info('Create a circle')
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

    def get_mouse_pos(self) -> pygame.Vector2:
        pos = pygame.Vector2(pygame.mouse.get_pos()) + self.pos
        return pos

class CameraGroup(pygame.sprite.Group):
    def __init__(self, screen : pygame.Surface):
        super().__init__()
        self.screen = screen

    def custom_draw(self, pos:pygame.Vector2, select:GeoGebraObject, mouse_pos:pygame.Vector2):
        sorted_sprites : list[GeoGebraObject] = sorted(
            self.sprites(),
            key=lambda s: (s.z, s.rect.centery, s.rect.centerx)  
        )
        for layer in range(4):
            for sprite in sorted_sprites:
                if sprite.z != layer:
                    continue
                if sprite.get_drag():
                    sprite.rebuild(mouse_pos)
                sprite.draw(self.screen, pos, select, False)

        pygame.display.flip()