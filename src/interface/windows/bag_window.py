'''check point 2 - 3: Backpack Overlay'''
import pygame as pg
from src.interface.windows.window import Window 
from src.core import GameManager

class BagWindow(Window):
    def __init__(self, game_manager: GameManager, font_title: pg.font.Font, font_item: pg.font.Font):

        super().__init__(game_manager, 600, 500)
        
        self.font_title = font_title
        self.font_item = font_item

    def draw(self, screen: pg.Surface):
        self.draw_background(screen)
        
        if not self.is_open:
            return

        items = self.game_manager.bag._items_data
        monsters = self.game_manager.bag._monsters_data

        title_backpack = self.font_title.render("Backpack", True, (0, 0, 0))
        title_rect = title_backpack.get_rect(centerx=self.rect.centerx, y=self.rect.y + 30)
        screen.blit(title_backpack, title_rect)

        # 物品列表
        item_title = self.font_title.render("Items", True, (0, 0, 0))
        screen.blit(item_title, (self.rect.x + 50, self.rect.y + 100))

        current_y = self.rect.y + 150 # 列表起始 Y 座標
        for item in items:
            item_name = item.get("name", "Unknown Item")
            item_quantity = item.get("quantity", 1)
            
            text = f"{item_name} x{item_quantity}"
            item_text = self.font_item.render(text, True, (50, 50, 50))
            screen.blit(item_text, (self.rect.x + 60, current_y))
            current_y += 35 # 換行

        # 怪物列表
        monster_title = self.font_title.render("Monsters", True, (0, 0, 0))
        screen.blit(monster_title, (self.rect.centerx + 50, self.rect.y + 100))
        
        current_y = self.rect.y + 150 # 重置 Y 座標
        for monster in monsters:
            monster_name = monster.get("name", "Unknown Monster")
            monster_level = monster.get("level", 1)

            text = f"Lv.{monster_level} {monster_name}"
            monster_text = self.font_item.render(text, True, (50, 50, 50))
            screen.blit(monster_text, (self.rect.centerx + 60, current_y))
            current_y += 35 # 換行