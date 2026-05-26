import datetime
import logging
import traceback

from utils import *
    
def process(config):
    extractor = Extractor(config)
    
    try:
        extractor.accept_cookies()
        extractor.search()
        extractor.solve_captcha()
        extractor.apply_filters()
        
        date_limit = get_date_limit(config["months"])
        logging.info(f"Data limite para artigos: {date_limit.strftime('%d/%m/%Y')}")
        
        while True:
            last_article = extractor.find_last_element("[data-testid='search-bodega-result']")
            last_article_date = last_article.locator("[data-testid='todays-date']").inner_text()
            last_article_date_parsed = parse_date(last_article_date)
            logging.info(f"Data do último artigo encontrado: {last_article_date_parsed.strftime('%d/%m/%Y')}")

            if last_article_date_parsed < date_limit:
                break
            
            extractor.scroll(4, 6) 
            extractor.sleep(1, 2)
            extractor.load_more()
                
        articles = extractor.scrape_articles(date_limit)
        
        for article in articles:
            if article["img_filename"]:
                download_image(article["img_url"], "output/images", article["img_filename"])
        
        excel_path = f"output/NYTimes_News_{datetime.now().strftime('%d%m%Y_%H%M%S')}.xlsx"
        save_to_excel(articles, excel_path)
        
    except Exception as e:
        logging.error(f"Erro no extractor: {e}")
        take_screenshot(extractor.page, "error")
        logging.error(traceback.format_exc())
        raise
    finally:
        extractor.close()
