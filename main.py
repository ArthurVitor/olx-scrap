import cloudscraper
from bs4 import BeautifulSoup
import json

# Cria o scraper usando o Cloudscraper
scraper = cloudscraper.create_scraper()

# Função para gravar os dados no arquivo JSON a cada imóvel
def escrever_no_json(imovel, arquivo='imoveis.json'):
    try:
        # Tenta abrir o arquivo e adicionar o novo imóvel
        with open(arquivo, 'r+', encoding='utf-8') as json_file:
            dados = json.load(json_file)
            dados.append(imovel)  # Adiciona o novo imóvel à lista existente
            json_file.seek(0)
            json.dump(dados, json_file, ensure_ascii=False, indent=4)
    except FileNotFoundError:
        # Se o arquivo não existir, cria o arquivo com a lista contendo o primeiro imóvel
        with open(arquivo, 'w', encoding='utf-8') as json_file:
            json.dump([imovel], json_file, ensure_ascii=False, indent=4)

# Itera pelas páginas
for page in range(1, 101):
    print(f"################## Page: {page}")
    url = f"https://www.olx.com.br/imoveis/venda/estado-pb?o={page}"

    # Faz a requisição para a página principal
    response = scraper.get(url)

    if response.status_code == 200:
        html_content = response.text  # Obtém o conteúdo HTML da página principal
        allImoveis = BeautifulSoup(html_content, 'html.parser')  # Faz o parse do HTML

        # Encontra todas as tags <a> desejadas
        a_tags = allImoveis.find_all(
            'a',
            attrs={
                'data-ds-component': 'DS-NewAdCard-Link',
                'class': 'olx-ad-card__link-wrapper'
            }
        )

        # Itera sobre as tags <a>
        for index, a_tag in enumerate(a_tags, start=1):
            href = a_tag.get('href')  # Obtém o link da tag <a>
            if href:
                print(f"Anúncio {index}: {href}")
                # Faz a requisição para o link do anúncio
                ad_response = scraper.get(href)

                if ad_response.status_code == 200:
                    ad_html_content = ad_response.text  # Obtém o conteúdo HTML do anúncio
                    ad_soup = BeautifulSoup(ad_html_content, 'html.parser')  # Faz o parse do HTML

                    # Busca o elemento <span> desejado para o nome do imóvel
                    nome = ad_soup.find(
                        'span',
                        attrs={
                            'data-ds-component': 'DS-Text',
                            'class': 'olx-text olx-text--title-medium olx-text--block ad__sc-1l883pa-2 bdcWAn'
                        }
                    )

                    preco = ad_soup.find(
                        'span',
                        attrs={
                            'data-ds-component': 'DS-Text',
                            'class': 'olx-text olx-text--title-large olx-text--block'
                        }
                    )

                    area_util = ad_soup.find(
                        'span',
                        attrs={
                            'class': 'ad__sc-hj0yqs-0 ekhFnR'
                        }
                    )

                    quartos = ad_soup.find(
                        'a',
                        attrs={
                            'class': 'olx-link olx-link--small olx-link--grey ad__sc-2h9gkk-3 lkkHCr',
                            'data-ds-component': 'DS-Link'
                        }
                    )

                    banheiros_garagem = ad_soup.findAll(
                        'span',
                        attrs={
                            'class': 'ad__sc-hj0yqs-0 ekhFnR'
                        }
                    )

                    detalhes = ad_soup.find_all(
                        'span',
                        attrs={
                            'data-ds-component': 'DS-Text',
                            'class': 'olx-text olx-text--body-small olx-text--block olx-text--semibold'
                        }
                    )

                    detalhes_lista = []  # Lista para armazenar os detalhes do imóvel

                    for detalhe in detalhes:
                        if detalhe.text.strip() == 'Exibir mais dicas':
                            break
                        detalhes_lista.append(detalhe.text.strip())  # Adiciona o detalhe à lista

                    try:
                        # Cria o dicionário do imóvel
                        imovel = {
                            "nome": nome.text.strip() if nome else None,
                            "preco": preco.text.strip() if preco else None,
                            "area_util": area_util.text.strip() if area_util else None,
                            "quartos": quartos.text.strip() if quartos else None,
                            "banheiros": banheiros_garagem[1].text.strip() if len(banheiros_garagem) > 1 else None,
                            "garagem": banheiros_garagem[2].text.strip() if len(banheiros_garagem) > 2 else None,
                            "detalhes": detalhes_lista
                        }

                        # Escreve o imóvel no arquivo JSON
                        escrever_no_json(imovel)

                        print(f"Nome: {imovel['nome']}")
                        print(f"Preço: {imovel['preco']}")
                        print(f"Área útil: {imovel['area_util']}")
                        print(f"Quartos: {imovel['quartos']}")
                        if imovel["banheiros"]:
                            print(f"Banheiros: {imovel['banheiros']}")
                        if imovel["garagem"]:
                            print(f"Garagem: {imovel['garagem']}")
                        print(f"Detalhes: {imovel['detalhes']}")
                        print(' ')

                    except IndexError:
                        continue
                else:
                    print(f"Falha ao acessar o link do anúncio. Código de status: {ad_response.status_code}")
    else:
        print(f"Falha ao buscar a página principal. Código de status: {response.status_code}")
