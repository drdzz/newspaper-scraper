import requests
import openai
import sys
from bs4 import BeautifulSoup
import json

# TODO
# subtituloslista
# Poner mas tipos de noticias solo soporta una, no hay videos ni noticias en directo.
# Poner que scarpee todas las noticias y escoja las que mas me gusten
#     una vez eso funcione poner que salgan todas a la vez en la seccion de noticias de obsidiam, mouseover...etc
#     que salgan en distintas columans etc.
# Falta lo de procesar los textos por algun tipo de IA


# Arguments
url = "https://www.lavanguardia.com/politica/20231111/9369432/sanchez-alcanza-mayoria-absoluta-transversal-avalar-reeleccion.html"

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
    subtitulo = soup.find('h2', class_='epigraph')  # subtituloslista : mira aqui por si hay mas de un subtit debajo el titulo
    subtitulo = f"- **{subtitulo.text}**\n" 
    article = soup.find('div', class_='article-modules')
    foto = soup.find('img', {'data-full-src': lambda x: x and 'lavanguardia' in x})
    foto_portada = f"![Image]({foto.get('data-full-src')})\n"
    foto_pie =  f"*{foto.get('alt')}*\n"
    return titulo, subtitulo, foto_portada, foto_pie, article

#
def extractArticle(article):
    extracted_elements = []
    for element in article.find_all():
        if element.name in ['p', 'img', 'h3']:
            extracted_elements.append(element)
    for i in range(len(extracted_elements)):
        if extracted_elements[i].name == 'img' and extracted_elements[i].has_attr('alt') and ("Horizontal" in extracted_elements[i]['alt']):  # solo las que tienen class = "nolazy"
            img_link = extracted_elements[i].get('data-full-src')
            extracted_elements[i] = f"![Image|100]({img_link})\n"
        elif extracted_elements[i].name == 'p':
            extracted_elements[i] = f"{extracted_elements[i].text}\n\n"
        elif extracted_elements[i].name == 'h3':
            extracted_elements[i] = f"-----------\n ###### **{extracted_elements[i].text}"+"**\n-----------------\n\n" #esto no chuta
   
    elements = []
    for i in range(len(extracted_elements)):
        if isinstance(extracted_elements[i],str):
            elements.append(extracted_elements[i])        

    return elements
    
# Lista de Noticia
def crearNoticia(titulo,subtitulo,foto_portada,foto_pie,extracted_elements):
    noticia = []
    noticia.append(titulo)
    noticia.append("\n---------------\n")
    noticia.append(subtitulo)
    noticia.append("---------------\n")
    noticia.append(foto_portada)
    noticia.append(foto_pie+"\n\n\n")
    for data in extracted_elements:
        noticia.append(data)
    return noticia

# Escribe noticia
def escribirNoticia(noticia):
    #with open('C:\\Users\\marc.ponce\\Documents\\Obsidian Vault\\noticia.md','w',encoding='utf-8') as file:     # For Windows
    with open ('/Users/marc.ponce/Documents/Obsidian Vault/noticia.md','w',encoding='utf-8') as file:      #  For MacOS
        for linea in noticia:
            file.write(linea)
    return

# Noticia Normal
def noticiaNormal(url):
    html = httpGet(url)
    soup = crearSopa(html)
    modules = articleModules(soup)
    article = extractArticle(modules[4])
    noticia = crearNoticia(modules[0],modules[1],modules[2],modules[3],article)
    escribirNoticia(noticia)
    return noticia

# Noticia Video
def noticiaVideo(url):
    return 

# Noticia Opinion
def noticiaOpinion(url):
    return 




