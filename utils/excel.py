import openpyxl
import logging

def save_to_excel(articles, filepath):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "News - NYTimes"

    headers = [
        "Título", "Data", "Descrição",
        "Nome da Imagem", "Quantidade de Frases", "Contém Valor Monetário"
    ]
    ws.append(headers)

    for a in articles:
        ws.append([
            a["title"],
            a["date"],
            a["description"],
            a["img_filename"],
            a["search_phrase_count"],
            a["contains_money"],
        ])

    wb.save(filepath)
    logging.info(f"Excel salvo em: {filepath}")