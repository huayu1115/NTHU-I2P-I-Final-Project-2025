from __future__ import annotations
import pygame
from enum import Enum
from typing import override
from .entity import Entity
from src.sprites import Sprite
from src.core import GameManager
from src.utils import GameSettings, Position, PositionCamera

class MerchantClassification(Enum):
    STATIONARY = "stationary"

class Merchant(Entity):
    goods: list[dict]
    sprite: Sprite
    interaction_range: float = 1.5 * GameSettings.TILE_SIZE

    def __init__(self, x: float, y: float, game_manager: GameManager, goods: list[dict]):
        super().__init__(x, y, game_manager)
        self.goods = goods
        self.sprite = Sprite("menu_sprites/menusprite1.png") 
        self.sprite.image = pygame.transform.scale(self.sprite.image, (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))
        self.sprite.update_pos(self.position)