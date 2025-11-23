'''check point 2 - 3: Backpack Overlay'''
import pygame as pg
from src.interface.windows.window import Window 
from src.core import GameManager
from src.utils import load_img, Logger

class BagWindow(Window):
    def __init__(self, game_manager: GameManager, font_title: pg.font.Font, font_item: pg.font.Font):

        super().__init__(game_manager, 600, 500)
        
        self.font_title = font_title
        self.font_item = font_item

        # 圖片快取字典
        self.sprite_cache = {}


    # 輔助函式：獲取快取圖片
    def get_cached_sprite(self, path: str, size: int):
        if path not in self.sprite_cache:
            try:
                img = load_img(path)
                img = pg.transform.scale(img, (size, size))
                self.sprite_cache[path] = img
            except Exception as e:
                Logger.warning(f"Failed to load sprite {path}: {e}")
                surf = pg.Surface((size, size)) # 產生一個替代用的色塊
                surf.fill((150, 150, 150))
                self.sprite_cache[path] = surf
        
        return self.sprite_cache[path]
    
    def update(self, dt: float):
        super().update(dt)
    

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
        item_title = self.font_item.render("Items", True, (0, 0, 0))
        screen.blit(item_title, (self.rect.x + 50, self.rect.y + 90))

        current_y = self.rect.y + 120 # 列表起始 Y 座標
        for item in items:
            item_name = item.get("name", "Unknown Item")
            item_quantity = item.get("count", item.get("quantity", 1))
            
            text = f"{item_name} x{item_quantity}"
            item_text = self.font_item.render(text, True, (50, 50, 50))
            screen.blit(item_text, (self.rect.x + 60, current_y))
            current_y += 45 # 換行

        # 怪物列表
        monster_title = self.font_item.render("Monsters", True, (0, 0, 0))
        screen.blit(monster_title, (self.rect.centerx + 50, self.rect.y + 90))
        
        current_y = self.rect.y + 120 # 重置 Y 座標
        for monster in monsters:
            monster_name = monster.get("name", "Unknown Monster")
            monster_level = monster.get("level", 1)
            monster_hp = monster.get("hp", 0)
            monster_max_hp = monster.get("max_hp", 100)
            sprite_path = monster.get("sprite_path", None)

            # 載入並縮放圖片
            icon_size = 35
            icon_x = self.rect.centerx + 20

            if sprite_path:
                image = self.get_cached_sprite(sprite_path, icon_size)
                screen.blit(image, (icon_x, current_y))
            else:
                pg.draw.rect(screen, (150, 150, 150), (icon_x, current_y, icon_size, icon_size))

            # 怪獸文字資訊
            text_x = icon_x + icon_size + 10

            name_text = f"Lv.{monster_level} {monster_name}"
            name_surface = self.font_item.render(name_text, True, (50, 50, 50))
            screen.blit(name_surface, (text_x, current_y))

            hp_text = f"HP: {monster_hp}/{monster_max_hp}"
            hp_color = (200, 50, 50) if monster_hp < monster_max_hp * 0.2 else (50, 50, 50)
            hp_surface = self.font_item.render(hp_text, True, hp_color)
            screen.blit(hp_surface, (text_x, current_y + 20))

            current_y += 45