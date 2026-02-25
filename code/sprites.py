"""Module providing a function printing python version."""

import pygame
from const import *

class GeoGebraError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"GeoGebraError: {self.message}"

class GeoGebraObject(pygame.sprite.Sprite):
    '''
    所有geogebra对象的基础类
    '''
    def __init__(self,pos, groups, parents=None, z=DRAW_ORDER['Line']):
        super().__init__(groups)
        self.pos = pygame.Vector2(pos)
        self.parents = parents
        self.sons = []
        self.z = z
        self.appear = True
        self.rect = None

        self.selected_color = SELECTED_COLOR
        self.selected_width = SELECTED_WIDTH

        self.can_dragged = True
        self.can_moved = True
        self.dragged = False

    def set_pos(self, pos):
        '''
        用于更新对象的位置
        
        :param pos: 新的位置坐标
        '''
        self.pos = pos
        self.rect.center = self.pos
        if self.sons:
            for child in self.sons:
                child.set_pos(pos)

    def draw(self, screen, pos, select):
        """递归绘制自身和所有子对象"""
        if self.appear:
            if self.can_moved:
                blit_x = self.rect.x - pos.x
                blit_y = self.rect.y - pos.y
            else:
                blit_x = self.rect.x
                blit_y = self.rect.y
            screen.blit(self.image, (blit_x, blit_y))
            if self == select:
                border_rect = pygame.Rect(blit_x, blit_y, self.rect.width, self.rect.height)
                pygame.draw.rect(screen, self.selected_color, border_rect, self.selected_width)                    
            if self.sons:
                for child in self.sons:
                    child.draw(screen, pos, select)

    def delete(self):
        for son in self.sons:
            son.kill()    
        self.kill()

    def set_drag(self):
        '''
        更改是否被拖动的状态
        '''
        if self.can_dragged:
            self.dragged = not self.dragged
    
    def get_drag(self):
        '''
        获取当前是否被拖动的状态
        '''
        return self.dragged
    
    def add_son(self, other):
        self.sons.append(other)
    
    def get_rect(self):
        if self.rect:
            return self.rect
        else:
            raise GeoGebraError("you is cheat this system! you use a undefine object")
 
    def set_appear(self):
        for son in self.sons:
            if isinstance(son, Text):
                son.set_appear()
        self.appear = not self.appear

class GeoGebraUi(GeoGebraObject):
    '''
    GeoGebraUi类，继承自GeoGebraObject，表示界面元素
    '''
    def __init__(self,pos, groups, z=DRAW_ORDER['Bg']):
        '''
        初始化GeoGebraUi对象
        
        :param pos: 初始位置坐标
        :param groups: 所属的精灵组
        '''
        super().__init__(pos, groups)
        self.can_dragged = False
        self.can_moved = False

class InputBox(GeoGebraObject):
    """输入框类"""
    def __init__(self, pos, width, height, placeholder, groups, size=18, z=DRAW_ORDER['Text']):
        super().__init__(pos, groups, z=z)
        self.can_dragged = False
        self.can_moved = False
        self.appear = False
    
        # 位置和大小
        self.rect = pygame.Rect(pos.x, pos.y, width, height)
        # 样式
        path = os.path.join(BASIC_PATH, TTF_PATH)
        self.font = pygame.font.Font(path, size)
        self.placeholder = placeholder
        self.size = size
        
        # 状态
        self.text = ""  # 输入的文本
        self.active = False  # 是否获得焦点
        self.cursor_visible = True  # 光标是否可见
        self.cursor_timer = 0  # 光标闪烁计时器
    
    def get_active(self):
        return self.active
    
    def set_active(self, bool):
        self.active = bool
        
    def update(self):
        """更新状态（光标闪烁）"""
        # 每500ms切换光标可见状态
        self.cursor_timer += 1
        if self.cursor_timer >= FPS // 2:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, screen, pos, select):
        """绘制输入框"""
        if self.appear:
            self.update()
            border_color = pygame.Color("blue") if self.active else pygame.Color("grey")
            bg_color = pygame.Color("white") if self.active else pygame.Color("lightgrey")
        
            pygame.draw.rect(screen, bg_color, self.rect)
            pygame.draw.rect(screen, border_color, self.rect, 2)
            
            if self.text:
                text_surface = self.font.render(self.text, True, pygame.Color("black"))
            else:
                text_surface = self.font.render(self.placeholder, True, pygame.Color("grey"))
            
            text_rect = text_surface.get_rect(
                centerx=self.rect.centerx,
                centery=self.rect.centery,
                left=self.rect.left + 10
            )
            screen.blit(text_surface, text_rect)
            
            # 焦点状态下绘制闪烁光标
            if self.active and self.cursor_visible:
                # 光标位置在文本末尾
                cursor_x = text_rect.right + 2
                cursor_y = self.rect.top + 5
                cursor_height = self.rect.height - 10
                
                # 绘制光标（竖线）
                pygame.draw.line(screen, pygame.Color("black"), (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)

class SelectBg(GeoGebraUi):
    '''
    选择对象的背景
    '''
    def __init__(self,pos, height, groups, z=DRAW_ORDER['Bg']):
        '''
        初始化SelectBg对象
        
        :param pos: 初始位置坐标
        :param height: 背景高度
        :param groups: 所属的精灵组
        '''
        super().__init__(pos, groups, z=DRAW_ORDER['Bg'])
        self.image = pygame.Surface((WEIGH, 800 - height))
        self.image.fill(SELECT_BG_COLOR)
        self.rect = self.image.get_rect(topleft=pos)
        self.can_dragged = False
        self.sons = []
        self.create_son()

    def rebuild(self,height):
        '''
        选择背景的新高度
        
        :param height:新高度
        '''
        self.image = pygame.Surface((WEIGH, height))
        self.image.fill(SELECT_BG_COLOR)
        self.rect = self.image.get_rect(topleft=self.pos)
        for son in self.sons:
            son.kill()
        self.sons.clear()
        self.create_son()
    
    def create_son(self):
        '''
        生成子类
        
        '''
        for i in range(len(UI_TEXT)):
            text = UI_TEXT[i]
            image = UI_IMAGE[i]
            son_pos = (self.rect.topleft[0] + 75*i, self.rect.topleft[1] + 10)
            son = GeoGebraUi(son_pos, self.groups())
            basic_image = pygame.image.load(image).convert_alpha()
            son.image = pygame.transform.scale(basic_image, (50, 50))
            son.rect = son.image.get_rect(topleft=son.pos)
            son.text = text
            son.name = text
            son.get_name = lambda text=text: text


            text_pos = (son.rect.centerx, son.rect.bottom - 10)
            text_obj = Text(text, text_pos, pygame.Color("black"),15, self.groups(), parents=[son])
            text_obj.can_moved = False


            son.sons.append(text_obj)
            self.sons.append(son)

class Dot(GeoGebraObject):
    '''
    点
    '''
    def __init__(self,groups, text, pos, color = pygame.Color("blue"), z=DRAW_ORDER['Dot']):
        '''
        初始化
        
        :param self: 说明
        :param groups: 所属精灵组
        :param text: 点的文本标签
        :param pos: 点的初始位置坐标
        :param color: 点的颜色，默认为蓝色
        '''
        super().__init__(pos, groups, z=z)
        self.color = color
        self.radius = DOT_RADIUS
        self.image = pygame.Surface((self.radius*2,self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image,self.color, (self.radius, self.radius),self.radius)
        self.rect = self.image.get_rect(topleft=self.pos)

        text_pos = (self.rect.centerx, self.rect.bottom - 10)
        text_obj = Text(text, text_pos, self.color, 18, groups, parents=[self])
        self.sons.append(text_obj)

class Text(GeoGebraObject):
    def __init__(self, text, pos, color, size, groups, parents=None, z=DRAW_ORDER['Text']):
        super().__init__(pos, groups, parents=parents, z=z)
        self.text = str(text)
        path = os.path.join(BASIC_PATH, TTF_PATH)
        self.font = pygame.font.Font(path, size)
        self.image = self.font.render(self.text, True, color)
        self.rect = self.image.get_rect(topleft=pos)
        if parents:
            self.can_dragged = False

    def set_pos(self, pos):
        if len(self.parents) == 1:
            self.pos = (self.parents[0].rect.centerx, self.parents[0].rect.bottom - 10)
        else:
            self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)

class Line(GeoGebraObject):
    def __init__(self, groups, s_pos, e_pos , parents, color = pygame.Color("black"), z=DRAW_ORDER['Line']):
        super().__init__(s_pos, groups, parents, z=z)
        self.parent1 = parents[0]
        self.parent2 = parents[1]
        self.color = color
        self.width = LINE_WIDTH
        self.can_dragged = False

        self.rebuild()

    def rebuild(self):
        s_pos = pygame.Vector2(self.parent1.rect.center)
        e_pos = pygame.Vector2(self.parent2.rect.center)

        min_x = min(s_pos.x, e_pos.x)
        min_y = min(s_pos.y, e_pos.y)
        max_x = max(s_pos.x, e_pos.x)
        max_y = max(s_pos.y, e_pos.y)
        
        surface_width = max(int(max_x - min_x), 1)
        surface_height = max(int(max_y - min_y), 1)
        self.image = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)

        local_s = (s_pos.x - min_x, s_pos.y - min_y)
        local_e = (e_pos.x - min_x, e_pos.y - min_y)
        pygame.draw.line(self.image, self.color, local_s, local_e, self.width)
        
        self.rect = self.image.get_rect(topleft=(min_x, min_y))

    def draw(self, screen, pos, select):
        if self.appear:
            self.rebuild()
            super().draw(screen, pos, select)

class Circle(GeoGebraObject):
    def __init__(self, groups, center_pos, radius, parents, color = pygame.Color("black"), z=DRAW_ORDER['Line']):
        super().__init__(center_pos, groups, parents, z=z)
        self.center_parent = parents[0]
        self.radius_parent = parents[1]
        self.color = color
        self.width = LINE_WIDTH
        self.can_dragged = False

        self.rebuild()

    def rebuild(self):
        center_pos = pygame.Vector2(self.center_parent.rect.center)
        radius = int(pygame.Vector2(self.radius_parent.rect.center).distance_to(center_pos))
        
        surface_size = (radius * 2, radius * 2)
        self.image = pygame.Surface(surface_size, pygame.SRCALPHA)

        pygame.draw.circle(self.image, self.color, (radius, radius), radius, self.width)
        
        self.rect = self.image.get_rect(topleft=(center_pos.x - radius, center_pos.y - radius))

    def draw(self, screen, pos, select):
        if self.appear:
            self.rebuild()
            super().draw(screen, pos, select)