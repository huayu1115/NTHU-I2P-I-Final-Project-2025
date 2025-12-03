import pygame as pg
from src.interface.windows.window import Window
from src.interface.components import Button
from src.core import GameManager
from src.utils import GameSettings, Logger

class ShopWindow(Window):
    def __init__(self, game_manager: GameManager, font_title: pg.font.Font, font_item: pg.font.Font):
        super().__init__(game_manager, 600, 500) 
        self.font_title = font_title
        self.font_item = font_item
        
        self.current_goods = []
        self.buy_buttons = []

    def setup_shop(self, goods: list[dict]):
        '''每次與商人對話時呼叫此函式來更新商品列表'''
        self.current_goods = goods
        self.buy_buttons.clear()
        
        # 動態生成購買按鈕
        start_y = self.rect.y + 90
        for i, item in enumerate(goods):
            btn = Button(
                "UI/button_shop.png",
                "UI/button_shop_hover.png",
                self.rect.right - 100, start_y + (i * 45),
                30, 30,
                on_click=lambda target=item: self.buy_item(target)
            )
            self.buy_buttons.append(btn)

        if not self.is_open:
            self.toggle()

    def buy_item(self, item_data: dict):
        price = item_data.get("price", 0)
        name = item_data.get("name", "Unknown")
        
        # 檢查金錢是否足夠
        bag_items = self.game_manager.bag._items_data
        coins_item = next((i for i in bag_items if i["name"] == "Coins"), None)
        
        current_money = coins_item["count"] if coins_item else 0
        
        if current_money >= price:
            # 扣錢
            if coins_item:
                coins_item["count"] -= price
            
            # 加物品到背包 (檢查是否已擁有)
            existing_item = next((i for i in bag_items if i["name"] == name), None)
            if existing_item:
                existing_item["count"] = existing_item.get("count", 1) + 1
            else:
                new_item = item_data.copy()
                new_item["count"] = 1
                if "price" in new_item: del new_item["price"]
                bag_items.append(new_item)
                
            Logger.info(f"Bought {name} for {price} coins.")
        else:
            Logger.info("Not enough money!")

    def update(self, dt: float):
        if not self.is_open: return
        super().update(dt)
        for btn in self.buy_buttons:
            btn.update(dt)

    def draw(self, screen: pg.Surface):
        if not self.is_open: return
        self.draw_background(screen)

        # 標題
        title = self.font_title.render("Shop", True, (255, 255, 255))
        screen.blit(title, (self.rect.centerx - title.get_width()//2, self.rect.y + 20))

        # 繪製商品列表
        start_y = self.rect.y + 90
        for i, item in enumerate(self.current_goods):
            name = item.get("name", "Unknown")
            price = item.get("price", 0)
            desc = item.get("description", "")

            text = f"{name} - ${price}"
            surf = self.font_item.render(text, True, (255, 255, 255))
            screen.blit(surf, (self.rect.x + 40, start_y + (i * 45) + 5))

        for btn in self.buy_buttons:
            btn.draw(screen)