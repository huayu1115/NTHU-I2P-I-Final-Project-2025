'''check point 2 - 5: Enemy Interaction'''
import pygame as pg
import random
from src.scenes.scene import Scene
from src.core import GameManager
from src.utils import GameSettings, Logger, Position
from src.interface.components import Button
from src.core.services import scene_manager
from src.sprites import BackgroundSprite, Sprite

class BattleScene(Scene):
    background: BackgroundSprite

    ## 儀表板
    dashboard_rect: pg.Rect
    btn_fight: Button
    btn_run: Button

    ## 怪獸
    player_sprite: Sprite | None 
    enemy_sprite: Sprite | None 

    def __init__(self):
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background1.png")
        self.font = pg.font.Font("./assets/fonts/Minecraft.ttf", 24)
        self.game_manager = None 

        ## 初始化儀表板 ##
        dashboard_height = 140
        self.dashboard_rect = pg.Rect(
            0, 
            GameSettings.SCREEN_HEIGHT - dashboard_height, 
            GameSettings.SCREEN_WIDTH, 
            dashboard_height
        )

        ## 初始化按鈕 ##
        btn_width, btn_height = 150, 50
        btn_y = self.dashboard_rect.centery - (btn_height // 2)
        
        # 戰鬥按鈕
        self.btn_fight = Button(
            "UI/raw/UI_Flat_Button02a_3.png", "UI/raw/UI_Flat_Button02a_1.png", 
            100, btn_y, 
            btn_width, btn_height,
            on_click=self.player_attack
        )
        
        # 逃跑按鈕
        self.btn_run = Button(
            "UI/raw/UI_Flat_Button02a_3.png", "UI/raw/UI_Flat_Button02a_1.png", 
            300, btn_y, 
            btn_width, btn_height,
            on_click=self.run_away
        )


    ## 攻擊邏輯 ##    
    def player_attack(self):
        Logger.info("Player chose to Fight!")
        pass

    ## 逃跑邏輯 ##
    def run_away(self):
        Logger.info("Player chose to Run!")
        scene_manager.change_scene("game")

    ## 繪製血條的函式 ##
    def draw_hp_bar(self, screen, x, y, hp, max_hp, name="Unknown"):
        bar_width = 200
        bar_height = 20
        
        # 計算血量百分比
        ratio = hp / max_hp if max_hp > 0 else 0
        fill_width = int(bar_width * ratio)
        
        # 血條
        pg.draw.rect(screen, (60, 60, 60), (x, y, bar_width, bar_height))
        color = (0, 255, 0) # 依照血量呈現: 綠色, 黃色, 紅色
        if ratio < 0.5: color = (255, 255, 0) 
        if ratio < 0.2: color = (255, 0, 0)   
        pg.draw.rect(screen, color, (x, y, fill_width, bar_height))
        pg.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)
        
        # 文字: name, HP
        name_text = self.font.render(f"{name}", True, (0, 0, 0))
        hp_text = self.font.render(f"{hp}/{max_hp}", True, (0, 0, 0))
        screen.blit(name_text, (x, y - 30))
        screen.blit(hp_text, (x + bar_width + 10, y))


    def enter(self):
       
        self.game_manager = GameManager.load("saves/game0.json") # 讀取最新檔案
        
        self.player_hp = 100
        self.player_max_hp = 100
        self.player_name = "Player"
        self.enemy_hp = 100
        self.enemy_name = "Wild Pokemon"

        if self.game_manager and self.game_manager.bag:
            monsters = getattr(self.game_manager.bag, "_monsters_data", [])
        
        ## 設定玩家第一隻怪獸
        if monsters:
                p_data = monsters[0] 
                self.player_hp = p_data.get("hp", 100)
                self.player_max_hp = p_data.get("max_hp", 100)
                self.player_name = p_data.get("name", "Unknown")
                
                path = p_data.get("sprite_path", "")
                if path:
                    path = path.replace("menu_sprites/", "sprites/")
                    path = path.replace("menusprite", "sprite")
                    try:
                        self.player_sprite = self._create_battle_sprite(
                        path, 
                        Position(100, self.dashboard_rect.top - 300), 
                        is_player=True
                        )
                    except Exception as e:
                        Logger.error(f"Failed to load player sprite: {e}")

                # 設定敵人，從背包隨機挑一隻當對手
                e_data = random.choice(monsters) 
                self.enemy_name = e_data.get("name", "Wild Pokemon")
                
                path = e_data.get("sprite_path", "")
                if path:
                    path = path.replace("menu_sprites/", "sprites/")
                    path = path.replace("menusprite", "sprite")
                    try:
                       self.enemy_sprite = self._create_battle_sprite(
                        path, 
                        Position(GameSettings.SCREEN_WIDTH - 450, 80), 
                        is_player=False
                        )      
                    except Exception as e:
                        Logger.error(f"Failed to load enemy sprite: {e}")

        # 設置狀態
        self.state = "PLAYER_TURN"
        self.log_text = f"A wild {self.enemy_name} appeared!"

    def update(self, dt: float):
        if self.state == "PLAYER_TURN":
            self.btn_fight.update(dt)
            self.btn_run.update(dt)
       
    def draw(self, screen: pg.Surface):
        self.background.draw(screen)
        
        ## 繪製儀錶板 ##
        pg.draw.rect(screen, (40, 40, 40), self.dashboard_rect)
        pg.draw.rect(screen, (255, 255, 255), self.dashboard_rect, 3)

        if self.state == "PLAYER_TURN":
            self.btn_fight.draw(screen)
            self.btn_run.draw(screen)

            txt_fight = self.font.render("Fight", True, (0, 0, 0))
            txt_rect = txt_fight.get_rect(center=self.btn_fight.hitbox.center)
            screen.blit(txt_fight, txt_rect)

            txt_run = self.font.render("Run", True, (0, 0, 0))
            txt_rect = txt_run.get_rect(center=self.btn_run.hitbox.center)
            screen.blit(txt_run, txt_rect)
         
        ## 繪製對手 ##
        self.enemy_sprite.draw(screen)
        self.draw_hp_bar(screen, self.enemy_sprite.rect.x + 10, 70, self.enemy_hp, 100, "Wild Trainer")

        ## 繪製玩家 ##
        self.player_sprite.draw(screen)
        self.draw_hp_bar(screen, self.player_sprite.rect.x + 50, self.player_sprite.rect.top + 80, self.player_hp, self.player_max_hp, "My Pokemon")

    ## 切割 sprite 的輔助函式
    def _create_battle_sprite(self, path: str, pos: Position, is_player: bool) -> Sprite | None:
        try:
            temp_sprite = Sprite(path) 
            full_img = temp_sprite.image
            sheet_w = full_img.get_width()
            sheet_h = full_img.get_height()
            single_w = sheet_w // 2

            ## 對手取左半部圖片，玩家取右半部圖片
            start_x = single_w if is_player else 0
            crop_rect = pg.Rect(start_x, 0, single_w, sheet_h)
            
            cropped_img = full_img.subsurface(crop_rect)

            final_img = pg.transform.scale(cropped_img, (300, 300))
            sprite = Sprite(path)
            sprite.image = final_img
            sprite.rect = final_img.get_rect()
            sprite.update_pos(pos)
            return sprite

        except Exception as e:
            Logger.error(f"Failed to create battle sprite from {path}: {e}")
            return None