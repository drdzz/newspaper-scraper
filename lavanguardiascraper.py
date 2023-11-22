import requests
import openai
import sys
from bs4 import BeautifulSoup
import json

# TODO
# Poner mas tipos de noticias solo soporta una, no hay videos ni noticias en directo. LEE LINEA 95
# Poner que scarpee todas las noticias y escoja las que mas me gusten
#     una vez eso funcione poner que salgan todas a la vez en la seccion de noticias de obsidiam, mouseover...etc
#     que salgan en distintas columans etc.
# Falta lo de procesar los textos por algun tipo de IA


# Arguments
url = "https://www.lavanguardia.com/internacional/20231120/9390826/milei-argentina-elecciones.html"

# GET Request
def httpGet(url):
    resp = requests.get(url)
    html = resp.text
    return html

# BeautifulSoup object 
def crearSopa(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup

# This suplanta crear Textos /imagenes /videos por separado
def articleModules(soup): 
    titulo = soup.find('h1')
    titulo = "## " + titulo.text
    subtitulos = soup.find_all('h2', class_='epigraph') 
    subs = [sub.text for sub in subtitulos]
    
    article = soup.find('div', class_='article-modules')
    fotos = soup.find_all('img', {'data-full-src': lambda x: x and 'lavanguardia' in x})
    images_in_modules = set() if article is None else set(article.find_all('img', {'data-full-src': lambda x: x and 'lavanguardia' in x}))
    
    foto_portada = list(set(fotos).difference(images_in_modules))

    if foto_portada:
        foto_portada_src = foto_portada[0].get('data-full-src')
        foto_alt = foto_portada[0].get('alt')
        foto_portada_markdown = f"![Image]({foto_portada_src})\n"
        foto_pie = f"*{foto_alt}*\n"
        return titulo, subs, foto_portada_markdown, foto_pie, article
    return titulo, subs, article

# 
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
    with open ('/Users/marc.ponce/Documents/Obsidian Vault/noticia.md','w',encoding='utf-8') as file:      #  For MacOS
        for linea in noticia:
            file.write(linea)
    return

"""# Lista de Noticia
def crearNoticia(titulo,subtitulos,foto_portada,foto_pie,extracted_elements):
    noticia = []
    noticia.append(titulo)
    noticia.append("\n---------------\n")
    if subtitulos:
        for subtitulo in subtitulos:
            noticia.append(f"- **{subtitulo}**\n")
            noticia.append("---------------\n")    
    noticia.append(foto_portada)
    noticia.append(foto_pie+"\n\n\n")
    for data in extracted_elements:
        noticia.append(data)
    return noticia"""

# Noticia Normal
def noticiaNormal(modules):
    noticia = []
    article = extractArticle(modules[4]) # Aqui espera algo mas largo de lo que le paso, depende de la noticia! (lee linea 42)
    noticia.append(modules[0])
    noticia.append("\n---------------\n")
    if modules[1]:
        for subtitulo in modules[1]:
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
    article = extractArticle(modules[2]) # Aqui espera algo mas largo de lo que le paso, depende de la noticia! (lee linea 42)
    noticia.append(modules[0])
    noticia.append("\n--------------\n")
    if modules[1]:
        for subtitulo in modules[1]:
            noticia.append(f"- **{subtitulo}**\n")
            noticia.append("------------\n")
    for data in article:
        noticia.append(noticia)
    escribirNoticia(noticia)
    return noticia

# Noticia Video
def noticiaVideo(url):
    return 

# Noticia 
def noticia(url):
    html = httpGet(url)
    soup = crearSopa(html)
    modules = articleModules(soup)
    if len(modules) == 5:
        noticia = noticiaNormal(modules)
    elif len(modules) == 3:
        noticia = noticiaOpinion(modules)

    return noticia

noticia(url)