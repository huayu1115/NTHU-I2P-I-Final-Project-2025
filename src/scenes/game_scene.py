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

    '''check point 2 - 1: Overlay'''
    menu_button: Button
    is_menu_open: bool
    menu_box: pg.Rect
    close_menu_button: Button

    '''check point 2 - 4: Setting Overlay'''
    setting_button: Button
    is_setting_open: bool
    setting_box: pg.Rect
    close_setting_button: Button

    volume_bar_rect: pg.Rect
    volume_handle_rect: pg.Rect
    volume: float

    '''check point 2 - 3: Backpack Overlay'''
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

        ## 字型
        self.font_title = pg.font.Font("././assets/fonts/Pokemon Solid.ttf", 30)
        self.font_item = pg.font.Font("././assets/fonts/Minecraft.ttf", 20)
        px, py = GameSettings.SCREEN_WIDTH , GameSettings.SCREEN_HEIGHT

        '''check point 2 - 1: Overlay 初始化 menu'''
        self.is_menu_open = False

        self.menu_button = Button(
            "UI/button_load.png",
            "UI/button_load_hover.png",
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

        '''check point 2 - 4: Setting Overlay 初始化 setting'''
        self.is_setting_open = False
        self.is_muted = False

        self.setting_button = Button(
            "UI/button_setting.png",
            "UI/button_setting_hover.png",
            px - 50, py - 100,
            35, 35,
            on_click = self.toggle_setting
        ) 

        setting_box_width, setting_box_height = 600, 500
        self.setting_box = pg.Rect(
            (GameSettings.SCREEN_WIDTH - setting_box_width) // 2,
            (GameSettings.SCREEN_HEIGHT - setting_box_height) // 2,
            setting_box_width,
            setting_box_height
        )

        
        self.text_title = self.font_title.render("Settings", True, (0, 0, 0))
        self.text_volume_label = self.font_item.render("Volume", True, (0, 0, 0))

        self.close_setting_button = Button(
            "UI/button_x.png",
            "UI/button_x_hover.png",
            self.setting_box.right - 45,
            self.setting_box.y + 10,
            35, 35,
            on_click = self.toggle_setting
        )

        ## 靜音按鈕 
        btn_x = self.setting_box.centerx - 60
        btn_y = self.setting_box.centery - 50
        btn_w, btn_h = 40, 25

        self.mute_button_off = Button(
            "UI/raw/UI_Flat_ToggleRightOff01a.png",
            "UI/raw/UI_Flat_ToggleRightOff01a.png",
            btn_x, btn_y, btn_w, btn_h,
            on_click=self.toggle_mute
        )

        self.mute_button_on = Button(
            "UI/raw/UI_Flat_ToggleRightOn01a.png",
            "UI/raw/UI_Flat_ToggleRightOn01a.png",   
            btn_x, btn_y, btn_w, btn_h,
            on_click=self.toggle_mute
        )

        ## 音量條
        bar_width, bar_height = 300, 20
        bar_x = self.setting_box.centerx - bar_width // 2
        bar_y = (self.setting_box.centery) - 100
        self.volume_bar_rect = pg.Rect(bar_x, bar_y, bar_width, bar_height)

        ## 音量滑桿
        handle_size = 20
        handle_x = bar_x + int(GameSettings.AUDIO_VOLUME * bar_width) - handle_size // 2
        handle_y = bar_y + bar_height // 2 - handle_size // 2
        self.volume_handle_rect = pg.Rect(handle_x, handle_y, handle_size, handle_size)

        '''check point 2 - 3: Backpack Overlay 初始化 bag'''
        self.is_bag_open = False

        self.bag_button = Button(
            "UI/button_backpack.png",
            "UI/button_backpack_hover.png",
            px - 50, py - 150,
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


    '''check point 2: function'''      
    ## 切換 menu 開啟或關閉 ##
    def toggle_menu(self):      
        self.is_menu_open = not self.is_menu_open

    ## 切換 setting 開啟或關閉 ##
    def toggle_setting(self):      
        self.is_setting_open = not self.is_setting_open

    ## 切換 bag 開啟或關閉 ##
    def toggle_bag(self):      
        self.is_bag_open = not self.is_bag_open

    ## 黑色遮罩 ## 
    def draw_overlay(self, screen: pg.Surface):
        overlay = pg.Surface(screen.get_size(), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) # RGBA, 150 代表透明度
        screen.blit(overlay, (0, 0))

    def toggle_mute(self):
        # 恢復播放
        if self.is_muted:
            self.is_muted = False
            sound_manager.resume_all()  
        # 暫停所有聲音
        else:
            self.is_muted = True
            sound_manager.pause_all()   

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
        self.setting_button.update(dt)
        self.bag_button.update(dt)

        ## menu 開啟時 ##
        if self.is_menu_open: 
            self.close_menu_button.update(dt)
        ## setting 開啟時 ##
        elif self.is_setting_open:
            self.close_setting_button.update(dt)

            ## 音量條 ##
            if pg.mouse.get_pressed()[0]:  
                mx, my = pg.mouse.get_pos()
                if self.volume_bar_rect.collidepoint(mx, my):
                    # 計算音量比例
                    ratio = (mx - self.volume_bar_rect.x) / self.volume_bar_rect.width
                    ratio = max(0, min(1, ratio))
                    GameSettings.AUDIO_VOLUME = ratio
                    # 設定音量
                    if sound_manager.current_bgm:
                        sound_manager.current_bgm.set_volume(ratio)
            ## 靜音按鈕 ##
            if self.is_muted:
                self.mute_button_on.update(dt)
            else:
                self.mute_button_off.update(dt)

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

        ## setting ##
        if self.is_setting_open:
            self.draw_overlay(screen) #背景變暗
            pg.draw.rect(screen, (255, 153, 51), self.setting_box)
            pg.draw.rect(screen, (255, 178, 102), self.setting_box, 10) 
            self.close_setting_button.draw(screen)

            # 標題
            text_surface = self.font_title.render("Setting", True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(self.setting_box.centerx, self.setting_box.top + 80))
            screen.blit(text_surface, text_rect)

            # 畫音量條
            pg.draw.rect(screen, (204, 102, 0), self.volume_bar_rect)  

            # 根據音量比例畫出目前音量大小
            fill_width = int(self.volume_bar_rect.width * GameSettings.AUDIO_VOLUME)
            pg.draw.rect(screen, (255, 178, 102), (self.volume_bar_rect.x, self.volume_bar_rect.y, fill_width, self.volume_bar_rect.height))

            # 更新滑桿位置
            self.volume_handle_rect.x = (
                self.volume_bar_rect.x + int(GameSettings.AUDIO_VOLUME * self.volume_bar_rect.width) - self.volume_handle_rect.width // 2
            )
            # 畫滑桿
            pg.draw.rect(screen, (255, 255, 255), self.volume_handle_rect)
            pg.draw.rect(screen, (0, 0, 0), self.volume_handle_rect, 2)

            # 文字 -- 音量條
            text_rect = self.text_volume_label.get_rect(center=(self.setting_box.centerx - 120, self.volume_bar_rect.y - 20))
            volume_text = self.font_item.render(f"{int(GameSettings.AUDIO_VOLUME * 100)}%", True, (50, 50, 50))
            screen.blit(self.text_volume_label, text_rect)
            screen.blit(volume_text, (self.setting_box.centerx + 200, self.volume_bar_rect.y))

            ## 禁音
            if self.is_muted:
                self.mute_button_on.draw(screen)
            else:
                self.mute_button_off.draw(screen)
            status_text = f"Mute: {'ON' if self.is_muted else 'OFF'}"
            text_surface = self.font_item.render(status_text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(self.setting_box.centerx - 110, self.setting_box.centery-40))
            screen.blit(text_surface, text_rect)


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
        self.setting_button.draw(screen)
        self.bag_button.draw(screen)