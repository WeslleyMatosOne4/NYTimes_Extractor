
# Desafio Técnico

## Objetivo
Automatizar o processo de extração de dados do site de notícias NY Times.


## Estrutura e organização do projeto

```Bash
NYTimes_Extractor/
├── config.yaml
├── docker-compose.yaml
├── Dockerfile
├── entrypoint.sh
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
├── automation/
│   ├── __init__.py
│   └── process.py
├── utils/
│   ├── __init__.py
│   ├── excel.py
│   ├── extractor.py
│   └── utils.py
├── logs
└── output
```


## Instalação

Necessário python 3.12 para executar o processo.
Instale as dependencias usando:

```ssh
pip install -r requirements
```

Em seguida execute o processo com:
```ssh
python main.py
```
## Config

É possivel alterar os parametros da pesquisa no arquivo 'config.yaml':

- `search_phrase`: frase que será utilizada na pesquisa;
- `categories`: categorias relacionadas a pesquisa;
- `months`: periodo de busca das nóticias.


## Deployment

Este bot pode ser instalado em um container Docker utilizando o docker-compose.yml, utilizando o commando:

```bash
  docker-compose up --build
```


## Autor

- [@WeslleyPinheiro](https://github.com/WeslleyMatosOne4)

