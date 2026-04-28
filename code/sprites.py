from __future__ import annotations
import pygame
from const import *
from typing import Optional, TypeVar, Sequence


class GeoGebraError(Exception):
    def __init__(self, message : str):
        self.message = message

    def __str__(self):
        return f"GeoGebraError: {self.message}"

class GeoGebraObject(pygame.sprite.Sprite):
    '''
    所有geogebra对象的基础类
    '''

    image: pygame.Surface
    rect: pygame.Rect
    pos: pygame.Vector2
    parents: Optional[GeoGebraObject]
    z: int
    groups: pygame.sprite.Group[GeoGebraObject]
    name:str

    def __init__(self,
                *groups,
                pos,
                name,
                parents: Optional[GeoGebraObject] = None,
                z:int = DRAW_ORDER['Line']):
        super().__init__(*groups)
        self.pos = pos
        self.parents = parents # type: ignore
        self.sons:list[GeoGebraObject] = []
        self.z = z
        self.appear = True
        self.image = pygame.Surface((0, 0))
        self.rect = self.image.get_rect(center=(pos.x, pos.y))
        self.name = name

        self.selected_color = SELECTED_COLOR
        self.selected_width = SELECTED_WIDTH

        self.can_dragged = True
        self.can_moved = True
        self.dragged = False

    def rebuild(self, pos:pygame.Vector2):
        '''
        用于更新对象的位置
        
        :param pos: 新的位置坐标
        '''
        self.pos = pos
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        if self.sons:
            for son in self.sons:
                son.rebuild(pos)

    def draw(self,
            screen:pygame.Surface,
            pos:pygame.Vector2,
            select:Optional[GeoGebraObject],
            hide_things_appear:bool) -> None:
        """递归绘制自身和所有子对象"""
        if self.can_moved:
            blit_x = self.rect.x - pos.x
            blit_y = self.rect.y - pos.y
        else:
            blit_x = self.rect.x
            blit_y = self.rect.y
        if DEBUG:
            pygame.draw.rect(screen, pygame.Color("red"), (blit_x, blit_y, self.rect.width, self.rect.height), width=2)
        if self.appear:
            screen.blit(self.image, (blit_x, blit_y))
        else:
            if hide_things_appear:
                alpha_image = self.image.copy()
                alpha_image.set_alpha(100)
                screen.blit(alpha_image, (blit_x, blit_y))
        if self == select:
            border_rect = pygame.Rect(blit_x, blit_y, self.rect.width, self.rect.height)
            pygame.draw.rect(screen, self.selected_color, border_rect, self.selected_width)                    
        if self.sons:
            for son in self.sons:
                son.draw(screen, pos, select, hide_things_appear)

    def delete(self, used_dot_names:list[str]) -> list[str]:
        deleted_names:list[str] = []
        for son in self.sons:
            son_names = son.delete(used_dot_names)
            deleted_names.extend(son_names)
        
        if isinstance(self, Dot):
            if self.text in used_dot_names:
                deleted_names.append(self.text)
        
        self.kill()
        return deleted_names

    def set_drag(self, b:bool):
        '''
        更改是否被拖动的状态
        '''
        if self.can_dragged:
            self.dragged = b
    
    def get_drag(self):
        '''
        获取当前是否被拖动的状态
        '''
        return self.dragged
    
    def add_son(self, other:GeoGebraObject):
        self.sons.append(other)
    
    def get_rect(self):
        if self.rect:
            return self.rect
        else:
            raise GeoGebraError("You are cheat this system! you use a undefine object")
 
    def set_appear(self):
        for son in self.sons:
            if isinstance(son, Text):
                son.set_appear()
        self.appear = not self.appear

    def cal_ana_exp(self):
        pass
        
    def get_distance(self, pos:pygame.Vector2):
        return self.rect.center - pos
    
class GeoGebraUi(GeoGebraObject):

    '''
    GeoGebraUi类,继承自GeoGebraObject.表示界面元素
    '''
    def __init__(self,
                *groups:pygame.sprite.Group[GeoGebraObject],
                pos:pygame.Vector2,
                name,
                z :int =DRAW_ORDER['Bg']):
        '''
        初始化GeoGebraUi对象
        
        :param pos: 初始位置坐标
        :param groups: 所属的精灵组
        '''
        super().__init__(*groups,pos=pos,z=z)
        self.can_dragged = False
        self.can_moved = False

class InputBox(GeoGebraObject):
    """输入框类"""
    def __init__(self, 
                *groups : Optional[pygame.sprite.Group[GeoGebraObject]],
                pos : pygame.Vector2,
                width : float,
                height : float,
                placeholder : str,
                size : int = 18,
                z : int = DRAW_ORDER['Text']):
        super().__init__(*groups,pos=pos, z=z, name="InputBox")
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
    
    def draw(self, screen, pos, select, hide_things_appear:bool):
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
    def __init__(self,*groups,pos, height, z=DRAW_ORDER['Bg']):
        '''
        初始化SelectBg对象
        
        :param pos: 初始位置坐标
        :param height: 背景高度
        :param groups: 所属的精灵组
        '''
        super().__init__(*groups, pos=pos,z=z, name="SelectBg")
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
            son_pos = pygame.Vector2(self.rect.topleft[0] + 75*i, self.rect.topleft[1] + 10)
            basic_image = pygame.image.load(UI_IMAGE[i]).convert_alpha()
            image = pygame.transform.scale(basic_image, (50, 50))
            son = GeoGebraUi(self.groups(), pos=son_pos, image=image, name=text)
            son.text = text


            text_pos = pygame.Vector2(son.rect.centerx, son.rect.bottom - 10)
            text_lb = lambda obj: (obj.rect.centerx, obj.rect.bottom - 10) 
            text_obj = Text(self.groups(),
                            text=text,
                            pos=text_pos,
                            color=pygame.Color("black"),
                            size=15,
                            func=text_lb,
                            parents=[son])
            text_obj.can_moved = False


            son.add_son(text_obj)
            self.add_son(son)

class Dot(GeoGebraObject):
    '''
    点
    '''
    def __init__(self,*groups, text:str, pos, type , parents = [], color = pygame.Color("blue"), z=DRAW_ORDER['Dot']):
        '''
        初始化
        
        :param self: 说明
        :param groups: 所属精灵组
        :param text: 点的文本标签
        :param pos: 点的初始位置坐标
        :param color: 点的颜色，默认为蓝色
        '''
        super().__init__(*groups,pos=pos-pygame.Vector2(DOT_RADIUS, DOT_RADIUS),  z=z, name=text)
        if type == "intersection":
            self.can_dragged = False
        self.type = type
        self.parents = parents
        self.color = color
        self.radius = DOT_RADIUS
        self.text = text
        self.image = pygame.Surface((self.radius*2,self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image,self.color, (self.radius, self.radius),self.radius)
        self.rect = self.image.get_rect(topleft=self.pos)

        text_pos = pygame.Vector2(self.rect.centerx, self.rect.bottom - 10)
        text_lb = lambda obj: (obj.rect.centerx, obj.rect.bottom - 10) 
        text_obj = Text(groups,
                        text=self.text,
                        pos=text_pos,
                        color=self.color,
                        size=18,
                        func=text_lb, 
                        parents=[self])
        self.sons.append(text_obj)

    def rebuild(self, pos):
        if self.appear:
            if self.type == "intersection":
                parent1_k ,parent1_b = self.parents[0].get_exp()
                parent2_k ,parent2_b = self.parents[1].get_exp()
                if isinstance(self.parents[0], Line):
                    if isinstance(self.parents[1], Line):
                        if parent1_k - parent2_k == 0:
                            self.pos.x = 0
                        else:
                            self.pos.x = (parent2_b - parent1_b) // (parent1_k - parent2_k)
                        self.pos.y = parent1_k*self.pos.x + parent1_b
                    else:
                        pass
                else:
                    pass
                for son in self.sons:
                    son.rebuild(pos)
            elif self.type == "plot":
                parent_k, parent_b = self.parents[0].get_exp()
                new_y = parent_k*pos.x + parent_b
                if parent_k == 0:
                    new_x = 0
                else :
                    new_x = (pos.y-parent_b) // parent_k
                if min(new_x, new_y) == new_x:
                    new_y = parent_k*new_x + parent_b
                else:
                    if parent_k == 0:
                        new_x = 0
                    else:
                        new_x = (new_y-parent_b) // parent_k
                for son in self.sons:
                    son.rebuild(pos)
            else:
                super().rebuild(pos)

class Text(GeoGebraObject):
    def __init__(self,*groups, text, pos, color, size, func, parents=None, z=DRAW_ORDER['Text']):
        super().__init__(*groups,pos=pos,parents=parents,z=z, name=text)
        self.text = str(text)
        path = os.path.join(BASIC_PATH, TTF_PATH)
        self.font = pygame.font.Font(path, size)
        self.image = self.font.render(self.text, True, color)
        self.rect = self.image.get_rect(topleft=pos)
        self.func = func
        if parents:
            self.can_dragged = False

    def rebuild(self, pos):
        if len(self.parents) == 1:
            self.pos = (self.parents[0].rect.centerx, self.parents[0].rect.bottom - 10)
            self.pos = self.func(self.parents[0])
        else:
            self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)

class Line(GeoGebraObject):
    def __init__(self, *groups, pos, parents : list[Dot], color = pygame.Color("black"), z=DRAW_ORDER['Line']):
        self.parent1 = parents[0]
        self.parent2 = parents[1]
        super().__init__(*groups,pos=pos,parents=parents, z=z, name=self.parent1.name + self.parent2.name)
        self.color = color
        self.width = LINE_WIDTH
        self.can_dragged = False
        self.type, self.k, self.b = self.cal_ana_exp(self.parent1.rect, self.parent2.rect)

        self.rebuild(pos)

    def rebuild(self, pos):
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
    
    def get_distance(self, pos):
        if self.k == 0:
            k = float("inf")
            b = 0
        else:
            k = -1 // self.k
            b = pos.y - k*pos.x

    def cal_ana_exp(self,
                    pos1:pygame.Vector2,
                    pos2:pygame.Vector2):
        if pos1.x == pos2.x:
            type = "level"
            k = 0
            b = pos1.y
        elif pos1.y == pos2.y:
            type = "up"
            k = float("inf")
            b = float("inf")
        else:
            k = (pos1.y - pos2.y) // (pos1.x - pos2.x)
            b = pos1.y - k * pos1.x
        return type, k, b 

    def get_exp(self):
        return self.k ,self.b

class Circle(GeoGebraObject):
    def __init__(self, groups, pos, parents, color = pygame.Color("black"), z=DRAW_ORDER['Line']):
        self.center_parent = parents[0]
        self.radius_parent = parents[1]
        super().__init__(pos=pos, groups=groups, parents=parents, z=z, name=self.center_parent.name+self.radius_parent.name)
        self.color = color
        self.width = LINE_WIDTH
        self.can_dragged = False

        self.rebuild(pos)

    def rebuild(self, pos):
        center_pos = pygame.Vector2(self.center_parent.rect.center)
        radius = int(pygame.Vector2(self.radius_parent.rect.center).distance_to(center_pos))
        
        surface_size = (radius * 2, radius * 2)
        self.image = pygame.Surface(surface_size, pygame.SRCALPHA)

        pygame.draw.circle(self.image, self.color, (radius, radius), radius, self.width)
        
        self.rect = self.image.get_rect(topleft=(center_pos.x - radius, center_pos.y - radius))

    def cal_ana_exp(self):
        pass