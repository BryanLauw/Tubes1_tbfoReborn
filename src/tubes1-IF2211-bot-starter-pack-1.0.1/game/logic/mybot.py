from typing import Optional, List, Tuple
from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import *

## ********** Helper Function ********** ##
def get_direction_alt(current_x, current_y, dest_x, dest_y):
    delta_x = clamp(dest_x - current_x, -1, 1)
    delta_y = clamp(dest_y - current_y, -1, 1)
    if delta_y != 0:
        delta_x = 0
    return delta_x, delta_y

def count_steps(a: Position, b: Position):
    return abs(a.x - b.x) + abs(a.y - b.y)

def coordinate_equals(x1: int, y1: int, x2: int, y2: int):
    return x1 == x2 and y1 == y2

## ********** Classes ********** ##
class Portals:
    closest_portal: GameObject
    farthest_portal: GameObject

    def __init__(self, portal_list: List[GameObject], current_position: Position):
        if count_steps(current_position, portal_list[0].position) < count_steps(current_position, portal_list[1].position):
            self.closest_portal = portal_list[0]
            self.farthest_portal = portal_list[1]
        else:
            self.closest_portal = portal_list[1]
            self.farthest_portal = portal_list[0]

    def count_steps_by_portal(self, current_position: Position, target_position: Position):
        return count_steps(current_position, self.closest_portal.position) + count_steps(self.farthest_portal.position, target_position)

    def is_closer_by_portal(self, current_position: Position, target_position: Position):
        return self.count_steps_by_portal(current_position, target_position) < count_steps(current_position, target_position)
    
class Player:
    current_position: Position
    target_position: Optional[Position]
    base_position: Position
    next_move: Tuple[int, int]
    current_target: Optional[GameObject]
    inventory_size: int
    diamonds_being_held: int
    entering_portal: bool
    
    def __init__(self, current_position: Position, base_position: Position, inventory_size: int, diamonds_being_held: int):
        self.current_position = current_position
        self.base_position = base_position
        self.inventory_size = inventory_size
        self.diamonds_being_held = diamonds_being_held
        self.entering_portal = False
    
    def is_inventory_full(self) -> bool:
        return self.diamonds_being_held == self.inventory_size
    
    def set_target(self, object: GameObject):
        self.current_target = object
        self.target_position = object.position

    def set_target_position(self, target_position: Position):
        self.target_position = target_position
        
    def avoid_obstacles(self, portals: Portals, red_button: GameObject):
        delta_x, delta_y = get_direction(self.current_position.x, self.current_position.y, self.target_position.x, self.target_position.y)
        next_x, next_y = self.current_position.x + delta_x, self.current_position.y + delta_y
        
        if (coordinate_equals(next_x, next_y, portals.closest_portal.position.x, portals.closest_portal.position.y) or
            coordinate_equals(next_x, next_y, portals.farthest_portal.position.x, portals.farthest_portal.position.y)):
            if self.current_target.type != "TeleportGameObject":
                delta_x, delta_y = get_direction_alt(self.current_position.x, self.current_position.y, self.target_position.x, self.target_position.y)
            else:
                self.entering_portal = True
        
        elif coordinate_equals(next_x, next_y, red_button.position.x, red_button.position.y):
            if self.current_target.type != "DiamondButtonGameObject":
                delta_x, delta_y = get_direction_alt(self.current_position.x, self.current_position.y, self.target_position.x, self.target_position.y)
        
        self.next_move = (delta_x, delta_y)
        
class Diamonds:
    diamonds_list: List[GameObject]
    chosen_diamond: GameObject
    chosen_diamond_distance: int
    red_button: GameObject
    
    def __init__(self, diamonds_list: List[GameObject], red_button: GameObject, diamonds_being_held: int):
        self.diamonds_list = [d for d in diamonds_list if d.properties.points == 1 or diamonds_being_held < 4]
        self.chosen_diamond = diamonds_list[0]
        self.chosen_diamond_distance = float('inf')
        self.red_button = red_button
    
    def choose_diamond(self, player: Player, portals: Portals, inside_portal: bool) -> GameObject:
        for diamond in self.diamonds_list:
            diamond_distance = count_steps(player.current_position, diamond.position)
            diff = diamond.properties.points - self.chosen_diamond.properties.points
            if self.chosen_diamond_distance > diamond_distance - (diff * 2):
                self.chosen_diamond = diamond
                self.chosen_diamond_distance = diamond_distance    
        
        if not inside_portal and count_steps(player.current_position, portals.closest_portal) < self.chosen_diamond_distance:
            diamond_distance = portals.count_steps_by_portal(player.current_position, diamond.position)
            diff = diamond.properties.points - self.chosen_diamond.properties.points
            if self.chosen_diamond_distance > diamond_distance - (diff * 2):
                self.chosen_diamond = diamond
                self.chosen_diamond_distance = diamond_distance
                player.set_target(portals.closest_portal)
                
        player.set_target(self.chosen_diamond)
    
    def check_red_button(self, player: Player, portals: Portals, inside_portal: bool):
        if not inside_portal:
            red_button_distance = min(count_steps(player.current_position, self.red_button.position), portals.count_steps_by_portal(player.current_position, self.red_button.position))
        else:
            red_button_distance = count_steps(player.current_position, self.red_button.position)
        
        if red_button_distance + 5 <= self.chosen_diamond_distance:
            player.set_target(self.red_button)
        
        if portals.is_closer_by_portal(player.current_position, self.red_button.position):
            player.set_target(portals.closest_portal)
    
class GameState:
    board: Board
    player_bot: GameObject
    
    def __init__(self, board_bot: GameObject, board: Board):
        self.board = board
        self.player_bot = board_bot
    
    def initialize(self):
        list_of_diamonds = []
        list_of_portals = []
        red_button = None
        
        for object in self.board.game_objects:
            if object.type == "DiamondGameObject":
                list_of_diamonds.append(object)
            elif object.type == "DiamondButtonGameObject":
                red_button = object 
            elif object.type == "TeleportGameObject":
                list_of_portals.append(object)
        
        return (Player(self.player_bot.position, self.player_bot.properties.base, self.player_bot.properties.inventory_size, self.player_bot.properties.diamonds),
                Diamonds(list_of_diamonds, red_button, self.player_bot.properties.diamonds),
                Portals(list_of_portals, self.player_bot.position))
    
    def no_time_left(self, current_position: Position, base_position: Position):
        return (not position_equals(current_position, base_position) and
                self.player_bot.properties.milliseconds_left / count_steps(current_position, base_position) <= 1250)


## ********** Main Logic ********** ##
class MyBot(BaseLogic):
    def __init__(self):
        self.back_to_base: bool = False
        self.inside_portal: bool = False
    
    def next_move(self, board_bot: GameObject, board: Board) -> Tuple[int, int]:
        game_state = GameState(board_bot, board)
        player, diamonds, portals = game_state.initialize()
        
        if position_equals(player.current_position, player.base_position):
            self.back_to_base = False
        elif not position_equals(player.current_position, portals.closest_portal.position):
            self.inside_portal = False
        
        if self.back_to_base or player.is_inventory_full() or game_state.no_time_left(player.current_position, player.base_position):
            player.set_target_position(player.base_position)
            self.back_to_base = True
            
            if not self.inside_portal and portals.is_closer_by_portal(player.current_position, player.base_position):
                player.set_target(portals.closest_portal)

        else:            
            diamonds.choose_diamond(player, portals, self.inside_portal)
            diamonds.check_red_button(player, portals, self.inside_portal)
        
        player.avoid_obstacles(portals, diamonds.red_button)
        if player.entering_portal:
            self.inside_portal = True

        return player.next_move


