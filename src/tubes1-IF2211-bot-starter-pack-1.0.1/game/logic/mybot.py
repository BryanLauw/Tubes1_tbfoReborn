from typing import Optional, Tuple, List
from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import *


class MyBot(BaseLogic):
    def __init__(self):
        self.goal_position: Optional[Position] = None
    
    def next_move(self, board_bot: GameObject, board: Board) -> Tuple[int, int]:
        min_step = float('inf')
        n_portal = 0
        list_of_diamonds = [GameObject]
        list_of_protal = [GameObject, GameObject]
        list_of_bots = []
        red_button = None

        props = board_bot.properties
        current_position = board_bot.position
        target = None
        closest_portal, farthest_portal = GameObject, GameObject

        # if not position_equals(current_position, props.base) and self.goal_position == props.base:
        #         return get_direction(current_position.x, current_position.y, props.base.x, props.base.y)
        #     elif position_equals(current_position, props.base):
        #         self.goal_position = None

        # 1. Simpan seluruh objek pada masing-masing list
        if position_equals(current_position, props.base):
            self.goal_position = None
        
        if self.goal_position == props.base or props.diamonds == props.inventory_size or (not position_equals(current_position, props.base) and 
                props.milliseconds_left / count_steps(current_position, props.base) <= 1250):
            for object in board.game_objects:
                if object.type == "BotGameObject":
                    list_of_bots.append(object) 

                elif object.type == "TeleportGameObject":
                    list_of_protal[n_portal] = object
                    n_portal += 1
            
            min_step = count_steps(current_position, props.base)
            if (count_steps(current_position, list_of_protal[0]) < count_steps(current_position, list_of_protal[1])):
                closest_portal = list_of_protal[0]
                farthest_portal = list_of_protal[1]
            else:
                closest_portal = list_of_protal[1]
                farthest_portal = list_of_protal[0]
            
            if (count_steps(current_position, closest_portal) + count_steps(farthest_portal, props.base) < min_step):
                target = closest_portal

            # strategi base
        else:
            for object in board.game_objects:
                if object.type == "DiamondGameObject" and object.properties.points == 1 or props.diamonds < 4:
                    list_of_diamonds.append(object)
                        
                elif object.type == "DiamondButtonGameObject":
                    red_button = object
                        
                elif object.type == "BotGameObject":
                    list_of_bots.append(object) 

                elif object.type == "TeleportGameObject":
                    list_of_protal[n_portal] = object
                    n_portal += 1
                    
            # 2. Cari diamond terdekat yang bisa diambil
            for diamond in list_of_diamonds:
                if target == None:
                    target = object
                    min_step = count_steps(current_position, object.position)
                    
                elif target.properties.points == object.properties.points:
                    current_step = count_steps(current_position, object.position)
                    if min_step > current_step:
                        target = object
                        min_step = current_step
                
                else:
                    current_step = count_steps(current_position, object.position)
                    selisih = object.properties.points - target.properties.points
                    if min_step > current_step - 2 * selisih:
                        target = object
                        min_step = current_step
                
            # 3. Cari jarak seluruh diamond yang valid melalui portal dan bandingkan dengan hasil nomor 2
            if count_steps(current_position, list_of_protal[0]) < count_steps(current_position, list_of_protal[1]):
                closest_portal = list_of_protal[0]
                farthest_portal = list_of_protal[1]
            else:
                closest_portal = list_of_protal[1]
                farthest_portal = list_of_protal[0]
                
            closest_portal_step = count_steps(current_position, closest_portal.position)
            
            if (closest_portal_step < min_step):
                for diamond_object in list_of_diamonds:
                    current_step = count_steps(farthest_portal, diamond_object) + closest_portal_step
                    if (diamond_object.properties.points == target.properties.points):
                        if (current_step < min_step):
                            target = closest_portal
                            min_step = current_step
                    elif (diamond_object.properties.points == 1 or props.diamonds < 4):
                        selisih = diamond_object.properties.points - target.properties.points
                        if (min_step > current_step - 2 * selisih):
                            target = closest_portal
                            min_step = current_step
                            
            # 4. Periksa red button, ambil jika jaraknya <= 5 + jarak ke diamond terdekat
            if (min_step >= 5 + count_steps(red_button.position, current_position)):
                target = red_button
                
        if target != closest_portal:
            next_step, next_position = Position, Position
            next_step.x, next_step.y = get_direction(current_position.x, current_position.y, target.position.x, target.position.y)
            next_position.x, next_position.y = current_position.x + next_step.x, current_position.y + next_step.y
            
            if position_equals(next_position, closest_portal) or position_equals(next_position, farthest_portal):
                return get_direction_alt(current_position.x, current_position.y, target.position.x, target.position.y)
            
            if props.diamonds == props.inventory_size: # tambahin cek bot dan portal di sekitar
                self.goal_position = props.base
            
        return get_direction(current_position.x, current_position.y, target.position.x, target.position.y)

            

        # props = board_bot.properties
        # current_position = board_bot.position
        # target = None
        
        # # Strategy 1: Self-Defense
        # # If an enemy is one step away from the player, tackle
        # bots_list = board.bots
        # for bot in bots_list:
        #     if (bot.position.x == current_position.x - 1 and bot.position.y == current_position.y or 
        #         bot.position.x == current_position.x + 1 and bot.position.y == current_position.y or
        #         bot.position.x == current_position.x and bot.position.y == current_position.y + 1 or
        #         bot.position.x == current_position.x and bot.position.y == current_position.y - 1):
                
        #         target = bot
        #         break
            
        # if target:
        #     return (target.position.x - current_position.x, target.position.y - current_position.y)
        
        # # Strategy 2: Hoarder
        # # If inventory is full, go home
        # if props.diamonds >= props.inventory_size:
        #     return get_direction(current_position.x, current_position.y, props.base.x, props.base.y)
        
        # # Strategy 3: Last Minute
        # # If there's barely enough time to go home, go home
        # if (not position_equals(current_position, props.base) and
        #     props.milliseconds_left / count_steps(current_position, props.base) <= 1250):
        #     self.goal_position = props.base
        
        # if not position_equals(current_position, props.base) and self.goal_position == props.base:
        #     return get_direction(current_position.x, current_position.y, props.base.x, props.base.y)
        # elif position_equals(current_position, props.base):
        #     self.goal_position = None
        
        # # Strategy 4 (default): Nearest Diamond --> ntar ganti jadi prioritas
        # # Go to the nearest diamond
        # diamond = board.diamonds
        # '''
        # # pakai for loop
        # n_portal = 0
        # for item in board:
        #     if item == diamond
        #         #append array diamond
        #     if item == red block
        #         coor_red_block = ...
        #     if item == portal
        #         list_portal[n_portal] = ..
        #         n_portal += 1
        # '''
        # min_steps = float('inf')
        
        # for d in diamond:
        #     steps = count_steps(current_position, d.position)
        #     if steps < min_steps:
        #         target = d
        #         min_steps = steps
        
        # next_step = Position
        # next_step.x, next_step.y = get_direction(current_position.x, current_position.y, target.position.x, target.position.y)
        
        # # Strategy 5: Teleport
        # # If a portal helps you get to your goal faster, use it
        # portals = []
        # i = 0
        # while i < len(board.game_objects) and len(portals) < 2:     
        #     if board.game_objects[i].type == "TeleportGameObject":
        #         portals.append(board.game_objects[i].position)
        #     i += 1
        
        # portal1, portal2 = portals[0], portals[1]
        # if count_steps(current_position, portal1) + count_steps(portal2, target.position) < min_steps:
        #     target = portal1
        #     min_steps = steps
        # elif count_steps(current_position, portal2) + count_steps(portal1, target.position) < min_steps:
        #     target = portal2
        #     min_steps = steps
        # else:
        #     # Avoid portals if not beneficial
            
        
        # return get_direction(current_position.x, current_position.y, target.position.x, target.position.y)