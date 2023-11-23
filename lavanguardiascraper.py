import requests
from openai import OpenAI
import sys
from bs4 import BeautifulSoup
import json

# TODO
# - AI: Poner que scarpee todas las noticias y escoja las que mas me gusten
# - AI: Falta lo de procesar los textos por algun tipo de IA (creo que sera una mierda)
# - Falta hacer que presente las noticias en algun tipo de Dashboard en Obsidian
# - Falta hacer un scraper aparte de youtube con API key de google, sacar el video de lavanguardia en html es rarisimo y a obisidan no le mola, 
#   pero youtube si y queda muy bonito embedded, hace falta buscar el titular en youtube y siempre es el primer resultado. El scrapeo se ha de hacer en json...etc


# Arguments
url = "https://www.lavanguardia.com/internacional/20231123/9399334/empieza-alto-fuego-gaza.html"
youtube_url = "https://www.youtube.com/results?search_query=+"

#client = OpenAI(api_key='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')

# GET Request
def httpGet(url):
    resp = requests.get(url)
    html = resp.text
    return html

# BeautifulSoup object 
def crearSopa(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def gpt():
    response = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    response_format={ "type": "json_object" },
    messages=[
        {"role": "system", "content": "You are a helpful assistant designed to enumerate all factions/parties/entities from a text and decide if author of text shows any bias towards any of them, result shall be short."},
        {"role": "user", "content": "La alianza entre el Partido Popular Europeo el grupo liberal y la ultraderecha ha convertido esta tarde el -semivacío- hemiciclo del Parlamento Europeo en Estrasburgo en un auténtico ring de boxeo entre los defensores y los detractores de la ley de amnistía que actualmente se tramita en el Congreso, una iniciativa que de acuerdo con el Gobierno, los socialistas y la izquierda europea es un asunto constitucional interno pero que los primeros presentan como el principio del fin no de España sino de Europa. En el centro de todas las miradas la Comisión Europea que hoy se ha puesto de perfil y ha evitado avanzar cualquier conclusión sobre el contenido de la ley."}
    ]
    )
    print(response.choices[0])

# Youtube Video Finder
def videoFinder(youtube_url,titular):
        url = youtube_url+titular
        html = httpGet(url)
        soup = crearSopa(html)
        link = soup.find('a')
        if link: 
            print(link)
        else:
            print("no") # esto es para debug, aqui esta el punto de trabajo ahora mismo. Scrapear el link de la primera noticia resultante de la busqueda de YT


# This suplanta crear Textos /imagenes /videos por separado
def articleModules(soup): 
    titulo = soup.find('h1')
    titulo = "## " + titulo.text
    subtitulos = soup.find_all('h2', class_='epigraph') 
    subs = [sub.text for sub in subtitulos]
    video = soup.find('video')
    print(video)
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

# This extracts the contents inside the paragraphs
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
        noticia.append(data)
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

#noticia(url)) #funciona 

videoFinder(youtube_url,'No tengo dinero') # estoy probando este metodo, falta scrapear
