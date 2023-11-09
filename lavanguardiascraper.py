import requests
import openai
import sys
from bs4 import BeautifulSoup
import json

# TODO
# subtituloslista
# Poner que pille <h2 y h3> de enmedio de la noticia (quotes etc...) (parece que ya esta si hay mas tipos de textos entonces no)
# Poner mas tipos de noticias solo soporta una, no hay videos ni noticias en directo.
# Poner que scarpee todas las noticias y escoja las que mas me gusten
#     una vez eso funcione poner que salgan todas a la vez en la seccion de noticias de obsidiam, mouseover...etc
#     que salgan en distintas columans etc.
# Falta lo de procesar los textos por algun tipo de IA

# Arguments
url = "https://www.lavanguardia.com/politica/20231108/9363668/psoe-junts-sacuden-presion-calendario-encauzar-acuerdo.html"

# GET Request
def httpGet(url):
    resp = requests.get(url)
    html = resp.text
    return html

# BeautifulSoup object 
def crearSopa(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup


###################################### NEW WAY (more general) ################################
# This suplanta crear Textos /imagenes /videos por separado
def articleModules(soup):
    article = soup.find('div', class_='article-modules')
    return article

def extractArticle(article):
    extracted_elements = []
    for element in article.find_all():
    if element.name in ['p', 'img', 'h3']:
        selected_tags.append(element)

# Print the selected tags in the order they appear
for tag in selected_tags:
    print(tag)
    """tag_attr_pairs = [('p', {'class': 'paragraph'}), ('img', None), ('h2', {'class': 'epigraph'})]
    for tag, attrs in tag_attr_pairs:
        # Find the elements based on the tag and attributes
        if attrs:
            elements = article.find_all(tag, attrs=attrs)
        else:
            elements = article.find_all(tag)

        # Add the found elements to the extracted list
        extracted_elements.extend(elements)
    for i in range(len(extracted_elements)):
        if extracted_elements[i].name == 'img':
            img_link = extracted_elements[i].get('data-full-src')
            extracted_elements[i] = f"![Image|100]({img_link})"
    for element in extracted_elements:
        print(element)"""

##############################################################################################

# Titulos de noticia
def crearTextos(soup):
    titulo = soup.find('h1')
    titulo = "## " + titulo.text
    subtitulo = soup.find('h2', class_='epigraph')  # subtituloslista : mira aqui por si hay mas de un subtit debajo el titulo
    subtitulo = "- " + f"**{subtitulo.text}**" + "\n"

    texts = soup.findAll('p', class_='paragraph')
    subtitles = soup.find_all('h3', class_='subtitle')
    count = 0
    for subtitle in subtitles:
        subtitle = f"##### {subtitle.text}"
        texts.insert(0, "---------\n")
        texts.insert(1, subtitle + "\n")
        count = count + 1 
    texts.insert(count * 2,"-------\n")
    #texts = [str(text) for text in texts]
    for i in range(len(texts)):
        if isinstance(texts[i],str):
            continue
        else:
            texts[i] = texts[i].text + "\n\n"
    return titulo, subtitulo, texts

# Imagenes de noticia
def crearImagenes(soup):
    #Exctract and add image links
    image_links = []
    for img in soup.find_all('img'):
        src = img.get('src')
        if src and "www.lavanguardia.com" in src:
            image_links.append(f"![Image|700]({src})")
            subpicture = soup.find('p', class_='caption-title') #text under photo
    if subpicture:
        image_links[-1] += f"\n*{subpicture.text[:-1]}*\n\n"
    return image_links

# Lista de Noticia
def crearNoticia(titulo,subtitulo,texts,image_links):
    noticia = []
    noticia.append(titulo)
    noticia.append("\n---------------\n")
    noticia.append(subtitulo)
    noticia.append("---------------\n")
    noticia.extend(image_links)
    for data in texts:
        noticia.append(data)
    return noticia

# Escribe noticia
def escribirNoticia(noticia):
    with open('C:\\Users\\drdzz\\Desktop\\Obsidian Vault\\noticia.md','w',encoding='utf-8') as file:
        for linea in noticia:
            #print("??",linea) #optional
            file.write(linea)
    return

# Noticia Normal
def noticiaNormal(url):
    html = httpGet(url)
    soup = crearSopa(html)
    contents = list(crearTextos(soup))
    contents.insert(2, crearImagenes(soup))
    noticia = crearNoticia(contents[0],contents[1],contents[3],contents[2])
    escribirNoticia(noticia)
    return noticia

# Noticia Video
def noticiaVideo(url):
    return 

# Noticia Opinion
def noticiaOpinion(url):
    return 



html = httpGet(url)
soup = crearSopa(html)
article = articleModules(soup)
extracted = extractArticle(article)

