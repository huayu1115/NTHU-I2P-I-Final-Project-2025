import pygame as pg
from src.sprites import Sprite
from src.utils import GameSettings, Logger, Position, load_img

class Monster:
    def __init__(self, data: dict, is_player: bool):
        self.data = data
        self.name = data.get("name", "Unknown")
        self.hp = data.get("hp", 100)
        self.max_hp = data.get("max_hp", 100)
        self.level = data.get("level", 1)
        self.is_player = is_player
        self.sprite: Sprite | None = None

        self._setup_sprite(data.get("sprite_path", ""))

    ## 處理圖片
    def _setup_sprite(self, path: str):
        if not path: 
            return
        path = path.replace("menu_sprites/", "sprites/")
        path = path.replace("menusprite", "sprite")

        try:
            temp = Sprite(path)
            full_img = temp.image
            
            sheet_w = full_img.get_width()
            sheet_h = full_img.get_height()
            single_w = sheet_w // 2

            # 根據是否為玩家決定切左邊還是右邊
            start_x = single_w if self.is_player else 0
            crop_rect = pg.Rect(start_x, 0, single_w, sheet_h)
            cropped_img = full_img.subsurface(crop_rect)

            final_img = pg.transform.scale(cropped_img, (300, 300))

            # 建立 Sprite
            self.sprite = Sprite(path)
            self.sprite.image = final_img
            self.sprite.rect = final_img.get_rect()

            # 設定畫面位置
            if self.is_player:
                p_x = 50
                p_y = GameSettings.SCREEN_HEIGHT - 440 
                self.sprite.update_pos(Position(p_x, p_y))
            else:
                e_x = GameSettings.SCREEN_WIDTH - 350
                e_y = 80
                self.sprite.update_pos(Position(e_x, e_y))

        except Exception as e:
            Logger.error(f"Failed to load sprite for {self.name}: {e}")

    def draw(self, screen: pg.Surface):
        if self.sprite:
            self.sprite.draw(screen)

    def take_damage(self, amount: int):
        self.hp -= amount
        if self.hp < 0: self.hp = 0