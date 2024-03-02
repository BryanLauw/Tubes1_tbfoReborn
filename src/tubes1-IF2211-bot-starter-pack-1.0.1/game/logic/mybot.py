from typing import Optional, Tuple
from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import *


class MyBot(BaseLogic):
    def __init__(self):
        self.goal_position: Optional[Position] = None
    
    def next_move(self, board_bot: GameObject, board: Board) -> Tuple[int, int]:
        min_step_blue = float('inf')
        min_step_red = float('inf')
        n_portal = 0
        list_of_diamonds = []
        list_of_protal = [0, 0]
        list_of_bots = []

        props = board_bot.properties
        current_position = board_bot.position
        target = None

        for object in board.game_objects:
            if object.type == "DiamondGameObject":
                list_of_diamonds.append(object)
                if (object.properties.points == 2 and props.inventory_size < 4):
                    min_step_red = min(min_step_red,count_steps(current_position, object.position))
                elif (object.properties.points == 1):
                    min_step_blue = min(min_step_blue,count_steps(current_position, object.position))
            elif object.type == "DiamondButtonGameObject":
                red_button_step = count_steps(current_position, object.position)
            elif object.type == "BotGameObject":
                list_of_bots.append(object) 
                # untuk di bawah
                # if (count_steps(object.position,current_position) <= 3): 
                #     return get_direction(current_position.x, current_position.y, )
            elif object.type == "TeleportGameObject":
                list_of_protal[n_portal] = object
                n_portal += 1

        if props.diamonds == props.inventory_size: # tambahin cek bot dan portal di sekitar
            self.goal_position = props.base
        
        if (not position_equals(current_position, props.base) and 
              props.milliseconds_left / count_steps(current_position, props.base) <= 1250):
            self.goal_position = props.base

        if not position_equals(current_position, props.base) and self.goal_position == props.base:
            return get_direction(current_position.x, current_position.y, props.base.x, props.base.y)
        elif position_equals(current_position, props.base):
            self.goal_position = None

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
            # next_step, next_position = Position, Position
            # next_step.x, next_step.y = get_direction(current_position.x, current_position.y, target.position.x, target.position.y)
            # next_position.x, next_position.y = current_position.x + next_step.x, current_position.y + next_step.y
            
            # if position_equals(next_position, portal1) or position_equals(next_position, portal2):
            #     return get_direction_alt(current_position.x, current_position.y, target.position.x, target.position.y)
        
        # return get_direction(current_position.x, current_position.y, target.position.x, target.position.y)