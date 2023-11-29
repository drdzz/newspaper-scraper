import requests
from openai import OpenAI
import sys
from bs4 import BeautifulSoup
import json
import re

from selenium import webdriver 
import pandas as pd 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC

# TODO
# - Falta hacer que presente las noticias en algun tipo de Dashboard en Obsidian
# - Falta hacer un scraper aparte de youtube con API key de google, sacar el video de lavanguardia en html es rarisimo y a obisidan no le mola, 
#   pero youtube si y queda muy bonito embedded, hace falta buscar el titular en youtube y siempre es el primer resultado. El scrapeo se ha de hacer en json...etc
# - AI: Poner que analize todas los titulares y escoja
# - AI: Falta lo de procesar los textos por algun tipo de IA (creo que sera una mierda)


# Arguments 
url = "https://www.lavanguardia.com/internacional/20231128/9412163/dormimos-sillas.html"
#url = "https://www.lavanguardia.com/internacional/20231129/9413984/rio-mar.html"
#url2 = "https://www.lavanguardia.com/internacional/20231124/9402260/orban-hungria-ue-leyen-consulta-antieuropea-ultraconservador.html"
youtube_url = "https://www.youtube.com/results?search_query=+"
lavanguardia = "https://www.lavanguardia.com"
#client = OpenAI(api_key='sk-')

# GET Request
def httpGet(url):
    resp = requests.get(url)
    html = resp
    return html

# BeautifulSoup object 
def crearSopa(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def gpt(): # Para nada esto funciona solo estaba tanteando textos sueltos y experimentando con prompts
    response = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    response_format={ "type": "json_object" },
    messages=[
        {"role": "system", "content": "You are a helpful assistant designed to enumerate all factions/parties/entities from a text and decide if author of text shows any bias towards any of them, result shall be short."},
        {"role": "user", "content": "La alianza entre el Partido Popular Europeo el grupo liberal y la ultraderecha ha convertido esta tarde el -semivacío- hemiciclo del Parlamento Europeo en Estrasburgo en un auténtico ring de boxeo entre los defensores y los detractores de la ley de amnistía que actualmente se tramita en el Congreso, una iniciativa que de acuerdo con el Gobierno, los socialistas y la izquierda europea es un asunto constitucional interno pero que los primeros presentan como el principio del fin no de España sino de Europa. En el centro de todas las miradas la Comisión Europea que hoy se ha puesto de perfil y ha evitado avanzar cualquier conclusión sobre el contenido de la ley."}
    ] 
    )
    print(response.choices[0])

# buscaod Youtube Video 
def videoFinder(titular): # esta era la idea, estoy apunto de desecharla, aunque esta es la manera mas sencilla seguro
        search_url = f'{youtube_url}{titular}'
        search_url = search_url.replace(' ','+')
        driver = webdriver.Chrome() 
        driver.get(search_url)
        user_data = driver.find_elements('xpath', '//*[@id="video-title"]')
        links = []
        for i in user_data:
                    links.append(i.get_attribute('href'))
        link = links[0]
        return link            

# This suplanta crear Textos /imagenes /videos por separado, separa cabecera y noticia en si 
def articleModules(soup): 
    titulo = soup.find('h1')
    titulo1 = titulo.text
    titulo = "## " + titulo1
    subtitulos = soup.find_all('h2', class_='epigraph') 
    subs = [sub.text for sub in subtitulos]
    video_tags = soup.find('div', class_='multimedia-video') #, class_='jw-video jw-reset')

    article = soup.find('div', class_='article-modules')
    fotos = soup.find_all('img', {'data-full-src': lambda x: x and 'lavanguardia' in x})
    images_in_modules = set() if article is None else set(article.find_all('img', {'data-full-src': lambda x: x and 'lavanguardia' in x}))
    foto_portada = list(set(fotos).difference(images_in_modules))

    if video_tags:
        link = videoFinder(titulo1)
        link = f"![]({link})"
        return titulo, subs, link
    if foto_portada:
        foto_portada_src = foto_portada[0].get('data-full-src')
        foto_alt = foto_portada[0].get('alt')
        foto_portada_markdown = f"![Image]({foto_portada_src})\n"
        foto_pie = f"*{foto_alt}*\n"
        return titulo, subs, foto_portada_markdown, foto_pie, article # es posible que hayan mas condicione spara que devuelva distintas cosas
    else:
        return titulo, subs, article

# Extrae los distintos contenidos dentro de los parrafos, una cosa es la cabecera la otra la noticia
def extractArticle(article):
    extracted_elements = []
    for element in article.find_all():
        if element.name in ['p', 'img', 'h3', 'h2']:
            extracted_elements.append(element)
    for i in range(len(extracted_elements)):
        if not extracted_elements[i].find_parent('span', class_='module-details'):
            if extracted_elements[i].name == 'img' and extracted_elements[i].has_attr('alt') and ("Horizontal" in extracted_elements[i]['alt']):  # solo las que tienen class = "nolazy"
                img_link = extracted_elements[i].get('data-full-src')
                extracted_elements[i] = f"![Image|100%]({img_link})\n" # No pie de foto, pero da igual
            elif extracted_elements[i].name == 'p':
                extracted_elements[i] = f"{extracted_elements[i].text}\n\n"
            elif extracted_elements[i].name == ('h3' or 'h2') and ('subtitle' in extracted_elements[i]['class']):
                extracted_elements[i] = f"-----------\n**{extracted_elements[i].text}**\n\n-----------------\n"
        else: continue
    elements = []
    for i in range(len(extracted_elements)):
        if isinstance(extracted_elements[i],str):
            elements.append(extracted_elements[i])
    return elements
    
# Escribe noticia
def escribirNoticia(noticia):
    #with open('C:\\Users\\marc.ponce\\Documents\\Obsidian Vault\\noticia.md','w',encoding='utf-8') as file:     # For Windows
    with open ('/Users/marc.ponce/Documents/Obsidian Vault/test.md','w',encoding='utf-8') as file:      #  For MacOS
        for linea in noticia:
            file.write(linea)
    return

# Noticia Normal
def noticiaNormal(modules):
    noticia = []
    article = extractArticle(modules[4]) 
    noticia.append(modules[0])
    noticia.append("\n---------------\n")
    if modules[1]:
        for subtitulo in modules[1]:
            print(subtitulo)
            noticia.append(f"- **{subtitulo}**\n")
            noticia.append("---------------\n")    
    noticia.append(modules[2])
    noticia.append(modules[3]+"\n\n\n")
    for data in article:
        noticia.append(data)
    escribirNoticia(noticia)
    return noticia 

# Noticia Opinion
def noticiaOpinion(modules):
    noticia = []
    print(modules)
    article = extractArticle(modules[2])
    noticia.append(modules[0])
    noticia.append("\n--------------\n")
    if modules[1]:
        for subtitulo in modules[1]:
            noticia.append(f"- **{subtitulo}**\n")
            noticia.append("------------\n")
    for data in article:
        noticia.append(data)
    escribirNoticia(noticia)
    return noticia

# Noticia Video
def noticiaVideo(url):
    return 

# Noticia 
def noticia(url):
    html = httpGet(url)
    html = html.text
    soup = crearSopa(html)
    modules = articleModules(soup)
    if len(modules) == 5:
        noticia = noticiaNormal(modules)
    elif len(modules) == 3:
        # Noticia video tambien tiene 3 modulos solo!
        noticia = noticiaOpinion(modules)
    return noticia

def noticiasLinks(lavanguardia):
    noticias = []
    titulares = []
    links = []
    html = httpGet(lavanguardia)
    html = html.text
    soup = crearSopa(html)
    noticias = soup.find_all('a', itemprop='headline')
    for noticia in noticias:
        link = f"{lavanguardia}{noticia.get('href')}"
        noticia = noticia.text
        links.append(link)
        titulares.append(noticia)
    return titulares, links # eventualmente lo unico que me interesarán seran los links


noticia(url) #funciona 
#videoFinder('No tengo dinero') # estoy probando este metodo, falta scrapear ES UNA PUTA MOVIDA youtube rancios


#noticias = noticiasLinks(lavanguardia)[0]
#links = noticiasLinks(lavanguardia)[1]

"""for i in range(len(noticias)):
    if "Ofertas" in noticias[i]:
       print("YESSSSSSSSSSSS")
"""
