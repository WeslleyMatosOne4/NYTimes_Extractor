import logging
import yaml
import re
import os
import requests
from datetime import datetime, timedelta

def init_logging():
    logging.basicConfig(filename=f'logs/{datetime.now().strftime("%d%m%Y_%H%M%S")}.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
        
def load_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)
    
def get_date_limit(months):
    today = datetime.today()
    if months <= 1:
        return today.replace(day=1)
    return (today - timedelta(days=30 * (months - 1))).replace(day=1)
    
def parse_date(date_str):
    if re.search(r'(\d+)([mh])', date_str):
        return datetime.now()
    else:   
        for date_format in ["%B %d", "%b %d", "%B. %d", "%b. %d", "%B. %d, %Y", "%b. %d, %Y"]:
            try:
                date = datetime.strptime(date_str.title(), date_format)
                if date.year == 1900:
                    date = date.replace(year=datetime.now().year)
                return date
            except:
                continue
        return datetime.now()
    
def count_search_prhases(text, phrases):
    text_lower = text.lower()
    return sum(1 for phrase in phrases if phrase.lower() in text_lower)

def contains_money(description):
    match = re.search(r'\$\s?([\d,.]+)', description)
    if match:
        return True
    return False

def download_image(url, folder, filename):
    """Baixa e salva a imagem"""
    if not url:
        return ""
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    try:
        response = requests.get(url, timeout=10)
        with open(filepath, "wb") as f:
            f.write(response.content)
        logging.info(f"Imagem salva em: {filepath}")
        return filename
    except Exception as e:
        print(f"Erro ao baixar imagem: {e}")
        return ""
    
def take_screenshot(page, name):
    screenshot_path = f"logs/screenshots/{name}_{datetime.now().strftime('%d%m%Y_%H%M%S')}.png"
    page.screenshot(path=screenshot_path)
    logging.info(f"Screenshot salva em: {screenshot_path}")
    

