import requests
import traceback
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

# - AI: Poner que analize todas los titulares y escoja
# - AI: Falta lo de procesar los textos por algun tipo de IA (creo que sera una mierda)


# Arguments 
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
        search_url = search_url.replace('%','')
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
    video_tags = soup.find('div', class_='main-video') #, class_='jw-video jw-reset')

    article = soup.find('div', class_='article-modules')
    fotos = soup.find_all('img', {'data-full-src': lambda x: x and 'lavanguardia' in x})
    images_in_modules = set() if article is None else set(article.find_all('img', {'data-full-src': lambda x: x and 'lavanguardia' in x}))
    foto_portada = list(set(fotos).difference(images_in_modules))
    if video_tags:
        link = videoFinder(titulo1)
        link = f"![|100%]({link})"
        return titulo, subs, link, article
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
def escribirNoticia(noticia,titulo):
    #with open('C:\\Users\\marc.ponce\\Documents\\Obsidian Vault\\noticia.md','w',encoding='utf-8') as file:     # For Windows
    with open (f'/Users/marc.ponce/Documents/Obsidian Vault/News/{titulo}.md','w',encoding='utf-8') as file:      #  For MacOS
        for i in range(len(noticia)):
            if i>0:
                file.write(noticia[i])
    return

# Noticia Normal
def noticiaNormal(modules,titulo):
    noticia = []
    article = extractArticle(modules[4]) 
    noticia.append(modules[0])
    noticia.append("\n---------------\n")
    if modules[1]:
        for subtitulo in modules[1]:
            #print(subtitulo)
            noticia.append(f"- **{subtitulo}**\n")
            noticia.append("---------------\n")    
    noticia.append(modules[2])
    noticia.append(modules[3]+"\n\n\n")
    for data in article:
        noticia.append(data)
    escribirNoticia(noticia,titulo)
    return noticia 

# Noticia Opinion
def noticiaOpinion(modules,titulo):
    noticia = []
    #(modules)
    article = extractArticle(modules[2])
    noticia.append(modules[0])
    noticia.append("\n--------------\n")
    if modules[1]:
        for subtitulo in modules[1]:
            noticia.append(f"- **{subtitulo}**\n")
            noticia.append("------------\n")
    for data in article:
        noticia.append(data)
    escribirNoticia(noticia, titulo)
    return noticia

# Noticia Video
def noticiaVideo(modules,titulo):
    noticia = []
    article = extractArticle(modules[3]) 
    noticia.append(modules[0])
    noticia.append("\n---------------\n")
    if modules[1]:
        for subtitulo in modules[1]:
            noticia.append(f"- **{subtitulo}**\n")
            noticia.append("---------------\n")    
    noticia.append(modules[2])
    noticia.append("\n\n\n")
    for data in article:
        noticia.append(data)
    escribirNoticia(noticia,titulo)
    
    return noticia 

# Noticia 
def noticia(url,titulo):
    html = httpGet(url)
    html = html.text
    soup = crearSopa(html)
    modules = articleModules(soup)
    if len(modules) == 5:
        noticia = noticiaNormal(modules,titulo)
    elif len(modules) == 3:
        noticia = noticiaOpinion(modules,titulo)
    elif len(modules) == 4:
        noticia = noticiaVideo(modules,titulo)
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
        if (noticia.text != 'Últimas noticias') or ('/vida/' in link):
            link = f"{lavanguardia}{noticia.get('href')}"    
            noticia = noticia.text
            links.append(link)
            titulares.append(noticia)
    return titulares, links # eventualmente lo unico que me interesarán seran los links


noticias = noticiasLinks(lavanguardia)[0]
links = noticiasLinks(lavanguardia)[1]
noticiaserror = []
linkserror = []

for i in range(len(noticias)):
    if "emagister" in links[i] or "https://www.lavanguardia.comhttps://www.lavanguardia.com" in links[i]:
        continue  # Skip this link
    try:
        noticia(links[i], noticias[i])
    except Exception as exc: 
        #print(exc)
        noticiaserror.append(noticias[i])
        linkserror.append(links[i])
        print("algo ocurrio para:")
        print(noticias[i])
        #traceback.print_exc()

print("Ahora Errores:")

for i in range(len(noticiaserror)):
    try:
        noticia(linkserror[i], noticiaserror[i])
    except Exception as exc: 
        print(exc)
        print("Otra vez para para:")
        print(linkserror[i])
