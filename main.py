from automation import *
import logging

if __name__ == "__main__":
    init_logging()
    config = load_config()

    try:
        logging.info("Início da automação.")
        process(config)
    except Exception as e:
        logging.error(f"Erro durante execução: {type(e)} - {e}")
        print(f"Erro durante execução: {type(e)} - {e}", flush=True)
        
    logging.info("Fim da automação.")
