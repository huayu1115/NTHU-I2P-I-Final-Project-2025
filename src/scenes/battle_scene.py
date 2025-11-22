'''check point 2 - 5: Enemy Interaction'''
import pygame as pg
import random
from src.scenes.scene import Scene
from src.core import GameManager
from src.utils import GameSettings, Logger, Position
from src.interface.components import Button
from src.core.services import scene_manager
from src.sprites import BackgroundSprite, Sprite
from src.entities.monster import Monster

class BattleScene(Scene):
    background: BackgroundSprite

    ## 儀表板
    dashboard_rect: pg.Rect
    btn_fight: Button
    btn_run: Button

    ## 怪獸
    player: Monster | None = None
    enemy: Monster | None = None 

    def __init__(self):
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background1.png")
        self.font = pg.font.Font("./assets/fonts/Minecraft.ttf", 24)
        self.game_manager = None 

        self.turn_timer = 0.0
        self.state = "PLAYER"

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

        # 切換按鈕
        self.btn_switch = Button(
            "UI/raw/UI_Flat_Button02a_3.png", "UI/raw/UI_Flat_Button02a_1.png", 
            300, btn_y, 
            btn_width, btn_height,
            on_click=self.switch_monster
        )

        # 逃跑按鈕
        self.btn_run = Button(
            "UI/raw/UI_Flat_Button02a_3.png", "UI/raw/UI_Flat_Button02a_1.png", 
            500, btn_y, 
            btn_width, btn_height,
            on_click=self.run_away
        )


    ## 攻擊邏輯 ##    
    def player_attack(self):
        if self.state != "PLAYER" or not self.enemy: 
            return
        
        Logger.info("Player chose to Fight!")
        damage = random.randint(15, 25)
        self.enemy.take_damage(damage)
        self.log_text = f"You dealt {damage} damage!"

        if self.enemy.hp <= 0:
            self.enemy.hp = 0
            self.state = "WON"
            self.log_text = f"You defeated {self.enemy.name}!"
            self.turn_timer = 0
        else:
            self.state = "ENEMY"
            self.turn_timer = 0

    ## 逃跑邏輯 (資料回寫)##
    def run_away(self):
        Logger.info("Player chose to Run!")
        if self.player and self.player.data:
            self.player.data["hp"] = self.player.hp
            Logger.info(f"Battle ended. HP saved: {self.player.hp}")
        scene_manager.change_scene("game")

    ## 戰鬥結束處理 (資料回寫) ##
    def _end_battle(self):
        if self.player and self.player.data:
            self.player.data["hp"] = self.player.hp
            Logger.info(f"Battle ended. HP saved: {self.player.hp}")
        scene_manager.change_scene("game")

    ## 切換怪獸邏輯 ##
    def switch_monster(self):
        if self.state != "PLAYER": 
            return
        if not self.all_monsters: 
            return

        found_index = -1
        total_monsters = len(self.all_monsters)

        for i in range(1, total_monsters):
            check_index = (self.current_monster_index + i) % total_monsters
            if self.all_monsters[check_index].get("hp", 0) > 0:
                found_index = check_index
                break

        if found_index == -1:
            self.log_text = "No other Pokemon available!"
            return

        if self.player:
            self.player.data["hp"] = self.player.hp

        self.current_monster_index = found_index
        new_data = self.all_monsters[found_index]
        self.player = Monster(new_data, is_player=True)

        self.log_text = f"Go! {self.player.name}!"
        self.state = "ENEMY"
        self.turn_timer = 0

   ## 自動切換邏輯: 當前怪獸死掉時觸發 ##
    def _auto_switch(self) -> bool:
        if self.player:
            self.player.data["hp"] = 0

        found_index = -1
        for i, m_data in enumerate(self.all_monsters):
            if m_data.get("hp", 0) > 0:
                found_index = i
                break
        
        if found_index == -1:
            return False 

        self.current_monster_index = found_index
        new_data = self.all_monsters[found_index]
        self.player = Monster(new_data, is_player=True)
        
        self.log_text = f"Go {self.player.name}!"
        return True

    def enter(self):
        # 檢查是否成功接收到 game_manager
        if self.game_manager is None:
            Logger.error("GameManager not set in BattleScene!")
            return
        
        if self.game_manager and self.game_manager.bag:
            monsters = getattr(self.game_manager.bag, "_monsters_data", [])
            
            self.all_monsters = monsters 
            self.current_monster_index = -1
            
            if monsters:
                found_alive = False
                for i, m_data in enumerate(monsters):
                    if m_data.get("hp", 0) > 0:
                        self.player = Monster(m_data, is_player=True)
                        self.current_monster_index = i
                        found_alive = True
                        break
                if not found_alive:
                    Logger.warning("All monsters are dead!")
                    self.log_text = "You have no energy to fight..."
                    self.player = None
                    self.enemy = None
                    self.state = "LOST"
                    self.turn_timer = 0 
                    return
                
                # 從背包隨機選一隻當作敵人
                enemy_data = random.choice(monsters)
                self.enemy = Monster(enemy_data, is_player=False)
                self.enemy.hp = self.enemy.max_hp
                self.log_text = f"A wild {self.enemy.name} appeared!"
                self.state = "PLAYER"

            else:
                self.player = None
                self.enemy = None
                self.state = "LOST"
        
        

    ## update 支援四種狀態 ##
    def update(self, dt: float):
        if self.state == "PLAYER":
            self.btn_fight.update(dt)
            self.btn_run.update(dt)
            self.btn_switch.update(dt)
        elif self.state == "ENEMY":
            self.turn_timer += dt
            if self.turn_timer > 1.0:
                if self.player:
                    dmg = random.randint(10, 20)
                    self.player.take_damage(dmg)
                    self.log_text = f"{self.enemy.name} attacked! ({dmg} dmg)"
                    
                    if self.player.hp <= 0:
                        self.player.hp = 0
                        if self._auto_switch():
                            self.state = "PLAYER"
                        else:
                            self.state = "LOST"
                            self.log_text = "You fainted..."
                    else:
                        self.state = "PLAYER"
                self.turn_timer = 0
        elif self.state in ["WON", "LOST"]:
            self.turn_timer += dt
            if self.turn_timer > 2.0:
                self._end_battle()
       
    def draw(self, screen: pg.Surface):
        self.background.draw(screen)
        
        ## 繪製儀錶板 ##
        pg.draw.rect(screen, (40, 40, 40), self.dashboard_rect)
        pg.draw.rect(screen, (255, 255, 255), self.dashboard_rect, 3)

        if self.state == "PLAYER":
            self.btn_fight.draw(screen)
            self.btn_run.draw(screen)
            self.btn_switch.draw(screen)

            # 繪製按鈕文字 (使用兼容寫法)
            for btn, text in [(self.btn_fight, "Fight"), (self.btn_switch, "Switch"), (self.btn_run, "Run")]:
                txt_surf = self.font.render(text, True, (0, 0, 0))
                rect = getattr(btn, 'hitbox', btn.hitbox)
                screen.blit(txt_surf, txt_surf.get_rect(center=rect.center))
         
        ## 繪製對手 ##
        if self.enemy:
            self.enemy.draw(screen)
            rect = self.enemy.sprite.rect if self.enemy.sprite else pg.Rect(0,0,0,0)
            self.draw_hp_bar(screen, rect.x + 10, 70, self.enemy.hp, self.enemy.max_hp, self.enemy.name)
            
        ## 繪製玩家 ##
        if self.player:
            self.player.draw(screen)
            rect = self.player.sprite.rect if self.player.sprite else pg.Rect(0,0,0,0)
            self.draw_hp_bar(screen, rect.x + 50, rect.top + 80, self.player.hp, self.player.max_hp, self.player.name)

        ## 戰鬥訊息 ##
        log_txt = self.font.render(self.log_text, True, (255, 255, 255))
        log_rect = log_txt.get_rect(center=(GameSettings.SCREEN_WIDTH // 2, self.dashboard_rect.top - 30))
        bg_rect = log_rect.inflate(20, 10)
        s = pg.Surface((bg_rect.width, bg_rect.height))
        s.set_alpha(150)
        s.fill((0,0,0))
        screen.blit(s, bg_rect.topleft)
        screen.blit(log_txt, log_rect)



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