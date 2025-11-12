import pygame as pg
import threading
import time

from src.scenes.scene import Scene
from src.core import GameManager, OnlineManager
from src.utils import Logger, PositionCamera, GameSettings, Position
from src.core.services import sound_manager
from src.sprites import Sprite
from typing import override
from src.interface.components import Button

class GameScene(Scene):
    game_manager: GameManager
    online_manager: OnlineManager | None
    sprite_online: Sprite

    menu_button: Button
    is_menu_open: bool
    menu_box: pg.Rect
    close_menu_button: Button

    bag_button: Button
    is_bag_open: bool
    bag_box: pg.Rect
    close_bag_button: Button
    
    def __init__(self):
        super().__init__()
        # Game Manager
        manager = GameManager.load("saves/game0.json")
        if manager is None:
            Logger.error("Failed to load game manager")
            exit(1)
        self.game_manager = manager
        
        # Online Manager
        if GameSettings.IS_ONLINE:
            self.online_manager = OnlineManager()
        else:
            self.online_manager = None
        self.sprite_online = Sprite("ingame_ui/options1.png", (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))

        self.font_title = pg.font.Font("././assets/fonts/Pokemon Solid.ttf", 30)
        self.font_item = pg.font.Font("././assets/fonts/Minecraft.ttf", 20)
        px, py = GameSettings.SCREEN_WIDTH , GameSettings.SCREEN_HEIGHT

        ## 初始化 menu ##
        self.is_menu_open = False

        self.menu_button = Button(
            "UI/button_setting.png",
            "UI/button_setting_hover.png",
            px - 50, py - 50,
            35, 35,
            on_click = self.toggle_menu
        ) 

        menu_box_width, menu_box_height = 600, 500
        self.menu_box = pg.Rect(
            (GameSettings.SCREEN_WIDTH - menu_box_width) // 2,
            (GameSettings.SCREEN_HEIGHT - menu_box_height) // 2,
            menu_box_width,
            menu_box_height
        )

        self.close_menu_button = Button(
            "UI/button_x.png",
            "UI/button_x_hover.png",
            self.menu_box.right - 45,
            self.menu_box.y + 10,
            35, 35,
            on_click = self.toggle_menu
        )

        ## 初始化 bag ##
        self.is_bag_open = False

        self.bag_button = Button(
            "UI/button_backpack.png",
            "UI/button_backpack_hover.png",
            px - 50, py - 100,
            35, 35,
            on_click = self.toggle_bag
        ) 

        bag_box_width, bag_box_height = 600, 500
        self.bag_box = pg.Rect(
            (GameSettings.SCREEN_WIDTH - bag_box_width) // 2,
            (GameSettings.SCREEN_HEIGHT - bag_box_height) // 2,
            bag_box_width,
            bag_box_height
        )

        self.close_bag_button = Button(
            "UI/button_x.png",
            "UI/button_x_hover.png",
            self.bag_box.right - 45,
            self.bag_box.y + 10,
            35, 35,
            on_click = self.toggle_bag
        )
        
    ## 切換 menu 開啟或關閉 ##
    def toggle_menu(self):      
        self.is_menu_open = not self.is_menu_open

    ## 切換 bag 開啟或關閉 ##
    def toggle_bag(self):      
        self.is_bag_open = not self.is_bag_open

    ## 黑色遮罩 ## 
    def draw_overlay(self, screen: pg.Surface):
        overlay = pg.Surface(screen.get_size(), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) # RGBA, 150 代表透明度
        screen.blit(overlay, (0, 0))


    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 103 Pallet Town.ogg")
        if self.online_manager:
            self.online_manager.enter()
        
    @override
    def exit(self) -> None:
        if self.online_manager:
            self.online_manager.exit()
        
    @override
    def update(self, dt: float):

        self.menu_button.update(dt)
        self.bag_button.update(dt)

        ## menu 開啟時 ##
        if self.is_menu_open: 
            self.close_menu_button.update(dt)
        ## bag 開啟時 ##
        elif self.is_bag_open:
            self.close_bag_button.update(dt)
        else: ## 正常遊戲 ##
            # Check if there is assigned next scene
            self.game_manager.try_switch_map()
            
            # Update player and other data
            if self.game_manager.player:
                self.game_manager.player.update(dt)
            for enemy in self.game_manager.current_enemy_trainers:
                enemy.update(dt)
                
            # Update others
            self.game_manager.bag.update(dt)
            
            if self.game_manager.player is not None and self.online_manager is not None:
                _ = self.online_manager.update(
                    self.game_manager.player.position.x, 
                    self.game_manager.player.position.y,
                    self.game_manager.current_map.path_name
                )

    
            
            

        
        
    @override
    def draw(self, screen: pg.Surface):        
        if self.game_manager.player:
            '''
            [TODO HACKATHON 3]
            Implement the camera algorithm logic here
            Right now it's hard coded, you need to follow the player's positions
            you may use the below example, but the function still incorrect, you may trace the entity.py
            camera = self.game_manager.player.camera
            '''
            # 使用玩家在中央的相機
            camera = self.game_manager.player.camera
            self.game_manager.current_map.draw(screen, camera)
            self.game_manager.player.draw(screen, camera)
        else:
            camera = PositionCamera(0, 0)
            self.game_manager.current_map.draw(screen, camera)

        for enemy in self.game_manager.current_enemy_trainers:
            enemy.draw(screen, camera)

        self.game_manager.bag.draw(screen)
        
        if self.online_manager and self.game_manager.player:
            list_online = self.online_manager.get_list_players()
            for player in list_online:
                if player["map"] == self.game_manager.current_map.path_name:
                    camera = self.game_manager.player.camera
                    pos = camera.transform_position_as_position(Position(player["x"], player["y"]))
                    self.sprite_online.update_pos(pos)
                    self.sprite_online.draw(screen)

        ## menu ##
        if self.is_menu_open:
            self.draw_overlay(screen) #背景變暗
            pg.draw.rect(screen, (255, 153, 51), self.menu_box)
            pg.draw.rect(screen, (255, 178, 102), self.menu_box, 10) 
            self.close_menu_button.draw(screen)

        ## bag ##
        if self.is_bag_open:
            self.draw_overlay(screen)
            pg.draw.rect(screen, (255, 153, 51), self.bag_box)
            pg.draw.rect(screen, (255, 178, 102), self.bag_box, 10) 
            self.close_bag_button.draw(screen)

            ## 取得背包資料: 怪物和物品列表 ##
            items = self.game_manager.bag._items_data
            monsters = self.game_manager.bag._monsters_data

            title_Backpack = self.font_title.render("Backpack", True, (0, 0, 0)) # render 渲染文字圖片(Surface)
            title_rect = title_Backpack.get_rect(centerx=self.bag_box.centerx, y=self.bag_box.y + 30) # 定位
            screen.blit(title_Backpack, title_rect) # blit: Pygame 用來複製貼上一個 Surface 到另一個 Surface

            # 繪製物品列表
            item_title = self.font_title.render("Items", True, (0, 0, 0))
            screen.blit(item_title, (self.bag_box.x + 50, self.bag_box.y + 100))

            current_y = self.bag_box.y + 150 # 列表起始 Y 座標
            for item in items:
                item_name = item.get("name", "Unknown Item")
                item_quantity = item.get("quantity", 1)
                
                text = f"{item_name} x{item_quantity}"
                item_text = self.font_item.render(text, True, (50, 50, 50))
                screen.blit(item_text, (self.bag_box.x + 60, current_y))
                current_y += 35 # 換行

            # 繪製怪物列表
            monster_title = self.font_title.render("Monsters", True, (0, 0, 0))
            screen.blit(monster_title, (self.bag_box.centerx + 50, self.bag_box.y + 100))
            
            current_y = self.bag_box.y + 150 # 重置 Y 座標
            for monster in monsters:
                monster_name = monster.get("name", "Unknown Monster")
                monster_level = monster.get("level", 1)

                text = f"Lv.{monster_level} {monster_name}"
                monster_text = self.font_item.render(text, True, (50, 50, 50))
                screen.blit(monster_text, (self.bag_box.centerx + 60, current_y))
                current_y += 35 # 換行

        
        self.menu_button.draw(screen)
        self.bag_button.draw(screen)