import logging
import re
import time
import random
from datetime import datetime

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from utils import take_screenshot
class Extractor:
    BASE_URL = "https://www.nytimes.com/"
    
    def __init__(self, config):
        self.search_phrase = config["search_phrase"]
        self.categories = config["categories"]
        self.months = config["months"]
        self.environment = config["environment"] == "PRD"
        self.page = self._init_page()
    
    def _init_page(self):
        self.p = sync_playwright().start()

        self.browser = self.p.chromium.launch(
            headless= self.environment,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-setuid-sandbox",
                "--display=:99"
            ]
        )

        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/New_York",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
            }
        )

        self.page = self.context.new_page()
        self.page.goto(self.BASE_URL)
        return self.page
        
    def sleep(self, min_sec=2, max_sec=4):
        time.sleep(random.uniform(min_sec, max_sec))

    def type(self, locator, text):
        locator.click()
        for char in text:
            self.page.keyboard.type(char, delay=random.randint(80, 250))

    def scroll(self, min_scroll=3, max_scroll=6):
        for _ in range(random.randint(min_scroll, max_scroll)):
            self.page.mouse.wheel(0, random.randint(300, 600))
            self.sleep(0.3, 0.8)

    def search(self):
        self.sleep()

        # Clica na lupa
        self.page.locator("[data-testid='search-button']").click()
        self.sleep(1, 2)

        # Digita com sendkeys mais lento
        logging.info(f"Realizando busca por: {self.search_phrase}")
        search_input = self.page.locator("[data-testid='search-input']")
        self.type(search_input, self.search_phrase)
        self.sleep(1, 2)
        self.page.keyboard.press("Enter")

        self.page.wait_for_load_state("domcontentloaded")
        logging.info("Busca realizada")
        self.sleep()

    def accept_cookies(self): 
        try:
            self.page.evaluate("window.Fides.showModal();")
            self.page.wait_for_selector("#fides-accept-all-button", timeout=10000)
            logging.info("Aceitando cookies...")
            self.page.click("#fides-accept-all-button")
            self.sleep()
        except Exception as e:
            raise Exception(f"Cookie banner não encontrado: {e}")
        
    def solve_captcha(self):
        try:
            iframe = self.page.locator("iframe[title*='DataDome']")

            if iframe:
                logging.info("Captcha não detectado, continuando...")
                return
            
            logging.warning("Captcha detectado! Tentando resolver...")
            
            iframe.wait_for(state="visible", timeout=10000)

            # botão captcha
            start_x = 844   
            start_y = 264   

            # destino do drag
            end_x = 1092     
            end_y = 264

            logging.info(f"Drag: ({start_x}, {start_y}) -> ({end_x}, {end_y})")

            self.page.mouse.move(start_x, start_y)
            self.page.mouse.down()
            self.sleep(0.3, 0.6)

            # arrasta o botão simulando um usuário real
            steps = 30
            for i in range(1, steps + 1):
                t = i / steps
                ease = t * t * (3 - 2 * t)
                x = start_x + (end_x - start_x) * ease
                y = start_y + random.uniform(-1, 1)
                self.page.mouse.move(x, y)
                self.sleep(0.01, 0.03)

            self.sleep(0.2, 0.4)
            self.page.mouse.up()
            self.sleep(2, 3)

        except Exception as e:
            logging.error(f"Erro ao resolver captcha: {e}")
            raise
        
    def apply_filters(self):
        # Ordenar por mais recentes
        try:
            self.page.locator("[id='search-sort']").click()
            self.sleep(0.5, 1)
            logging.info("Aplicando filtro de ordenação: Mais Recentes")
            self.page.locator("li", has_text="Sort by Newest").click()
            self.sleep(1, 2)
        except PlaywrightTimeout:
            pass

        # Filtro de categorias
        if self.categories:
            self.page.locator("[id='search-sections']").click()
            for category in self.categories:
                try:
                    logging.info(f"Aplicando filtro de categoria: {category}")
                    self.page.locator(f"li", has_text=category).first.click(timeout=5000)
                    self.sleep(1, 2)
                except PlaywrightTimeout:
                    logging.warning(f"Categoria {category} nao encontrada")
            self.page.locator("[id='search-sections']").click()
            

    def scrape_articles(self, date_limit):
        articles = []
        logging.info("Iniciando extração de artigos...")
        cards = self.page.locator("[data-testid='search-bodega-result']").all()
        
        for card in cards:
            article = self.parse_card(card)
            logging.info(f"Artigo encontrado: {article}")
            if datetime.strptime(article["date"], '%d/%m/%Y') >= date_limit:
                articles.append(article)

        return articles

    def parse_card(self, card):
        from utils import count_search_prhases, contains_money, parse_date
        
        title = card.locator("[data-tpl='h']").inner_text()
        if card.locator("[data-tpl='bo']").count() > 0:
            description = card.locator("[data-tpl='bo']").inner_text()
        else:
            description = ""
        date = card.locator("[data-testid='todays-date']").inner_text()
        if card.locator("img").count() > 0:
            img_url = card.locator("img").first.get_attribute("src")
        else:
            img_url = ""
                    
        img_filename = re.search(r'\/([^\/]+\.jpg)', img_url)
        img_filename = img_filename.group(1) if img_filename is not None else ""

        return {
            "title": title,
            "description": description,
            "date": parse_date(date).strftime('%d/%m/%Y'),
            "img_url": img_url,
            "img_filename": img_filename,
            "search_phrase_count": count_search_prhases(title + " " + description, [self.search_phrase]),
            "contains_money": contains_money(description)
        }

    def load_more(self):
        try:
            btn = self.page.locator("[data-testid='search-show-more-button']")
            logging.info("Carregando mais artigos...")
            if btn.is_visible(timeout=3000):
                btn.click()
                self.sleep(1, 3)
                return True
        except:
            pass
        return False
    
    def find_last_element(self, selector):
        element = self.page.locator(selector).last
        return element
            
    def close(self):
        try:
            self.page.close()
            self.context.close()
            self.browser.close()
        except Exception as e:
            logging.warning(f"Erro ao fechar browser: {e}")
        finally:
            self.p.stop()

    
        
