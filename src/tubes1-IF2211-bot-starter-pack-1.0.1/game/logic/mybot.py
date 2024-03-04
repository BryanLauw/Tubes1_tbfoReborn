from typing import Optional, Tuple
from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import *


class MyBot(BaseLogic):
    def __init__(self):
        self.goal_position: Optional[Position] = None
        self.inside_portal: bool = False
    
    def next_move(self, board_bot: GameObject, board: Board) -> Tuple[int, int]:
        min_step = float('inf')
        n_portal = 0
        list_of_diamonds = []
        list_of_protal = [None, None]
        red_button = None

        props = board_bot.properties
        current_position = board_bot.position
        target = None
        closest_portal, farthest_portal = None, None

        if position_equals(current_position, props.base):
            self.goal_position = None

        # Kalo inventory penuh atau waktu tinggal dikit buat nyampe base, balik ke base
        if (self.goal_position and self.goal_position == props.base) or props.diamonds == props.inventory_size or (not position_equals(current_position, props.base) and 
            props.milliseconds_left / count_steps(current_position, props.base) <= 1250):
            
            self.goal_position = props.base
            
            # Cari portal, hitung jarak ke base lewat portal
            for object in board.game_objects:
                if object.type == "TeleportGameObject":
                    list_of_protal[n_portal] = object
                    n_portal += 1
                    
            min_step = count_steps(current_position, props.base)
            if count_steps(current_position, list_of_protal[0].position) < count_steps(current_position, list_of_protal[1].position):
                closest_portal = list_of_protal[0]
                farthest_portal = list_of_protal[1]
            else:
                closest_portal = list_of_protal[1]
                farthest_portal = list_of_protal[0]
            
            # Kalo lebih cepet lewat portal, ke portal
            if not self.inside_portal and count_steps(current_position, closest_portal.position) + count_steps(farthest_portal.position, props.base) < min_step:
                target = closest_portal
            
        else:
            # Cari semua diamond yang bisa diambil, red button, dan portal
            for object in board.game_objects:
                if object.type == "DiamondGameObject" and (object.properties.points == 1 or props.diamonds < 4):
                    list_of_diamonds.append(object)
                elif object.type == "DiamondButtonGameObject":
                    red_button = object 
                elif object.type == "TeleportGameObject":
                    list_of_protal[n_portal] = object
                    n_portal += 1
            
            # Cari diamond terdekat yang bisa diambil tanpa melewati portal
            for object in list_of_diamonds:
                if not target:
                    target = object
                    min_step = count_steps(current_position, object.position)
                elif target.properties.points == object.properties.points:
                    current_step = count_steps(current_position, object.position)
                    if min_step > current_step:
                        target = object
                        min_step = current_step
                else:
                    # Pilih diamond merah kalo jumlah step merah <= jumlah step biru + 2
                    current_step = count_steps(current_position, object.position)
                    diff = object.properties.points - target.properties.points
                    if min_step > current_step - (2 * diff):
                        target = object
                        min_step = current_step
            
            if count_steps(current_position, list_of_protal[0].position) < count_steps(current_position, list_of_protal[1].position):
                closest_portal = list_of_protal[0]
                farthest_portal = list_of_protal[1]
            else:
                closest_portal = list_of_protal[1]
                farthest_portal = list_of_protal[0]
            
            if not self.inside_portal:
                closest_portal_step = count_steps(current_position, closest_portal.position)
                target_portal = None
                
                if closest_portal_step < min_step:
                    # Cari jarak seluruh diamond melalui portal, bandingkan dengan hasil diamond terdekat sebelumnya
                    for diamond in list_of_diamonds:
                        current_step = count_steps(farthest_portal.position, diamond.position) + closest_portal_step
                        if diamond.properties.points == target.properties.points:
                            if current_step < min_step:
                                target_portal = closest_portal
                                target = diamond
                                min_step = current_step
                        elif diamond.properties.points == 1 or props.diamonds < 4:
                            diff = diamond.properties.points - target.properties.points
                            if min_step > current_step - diff*2:
                                target_portal = closest_portal
                                target = diamond
                                min_step = current_step
                
                if target_portal:
                    target = target_portal
            else:
                self.inside_portal = False
                            
            # Periksa red button, ambil kalo jarak ke diamond terdekat >= jarak button + 5
            if count_steps(red_button.position, current_position) + 5 <= min_step:
                target = red_button
        
        if not target and self.goal_position == props.base:
            return get_direction(current_position.x, current_position.y, props.base.x, props.base.y)

        delta_x, delta_y = get_direction(current_position.x, current_position.y, target.position.x, target.position.y)
        next_x, next_y = current_position.x + delta_x, current_position.y + delta_y
        
        # Cegah bot ga sengaja nabrak portal di jalan maupun stuck di portal
        if (position_equals_alt(next_x, next_y, closest_portal.position.x, closest_portal.position.y) or
            position_equals_alt(next_x, next_y, farthest_portal.position.x, farthest_portal.position.y)):
            if target.type != "TeleportGameObject":        
                return get_direction_alt(current_position.x, current_position.y, target.position.x, target.position.y)
            else:
                self.inside_portal = True
        
     
        return get_direction(current_position.x, current_position.y, target.position.x, target.position.y)
