import methods
import traceback

# Arguments  
lavanguardia = "https://www.lavanguardia.com"

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
        link = methods.videoFinder(titulo1)
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
    
# Noticia Normal
def noticiaNormal(modules,titulo,tema):
    noticia = []
    article = extractArticle(modules[4])
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
    noticia.append(f"#news #{tema}\n")
    methods.escribirNoticia(noticia,titulo)
    return noticia 

# Noticia Opinion
def noticiaOpinion(modules,titulo,tema):
    noticia = []
    article = extractArticle(modules[2])
    noticia.append(modules[0])
    noticia.append("\n--------------\n")
    if modules[1]:
        for subtitulo in modules[1]:
            noticia.append(f"- **{subtitulo}**\n")
            noticia.append("------------\n")
    for data in article:
        noticia.append(data)
    noticia.append(f"#news #{tema}\n")
    methods.escribirNoticia(noticia, titulo)
    return noticia

# Noticia Video
def noticiaVideo(modules,titulo,tema):
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
    noticia.append(f"#news #{tema}\n")
    print("titulooo",titulo)
    methods.escribirNoticia(noticia,titulo)
    
    return noticia 


# Noticia 
def noticia(url,titulo):
    html = methods.httpGet(url)
    html = html.text
    tema = methods.extractTema(url)
    if tema is None:
        print(url)
    soup = methods.crearSopa(html)
    modules = articleModules(soup)
    if len(modules) == 5:
        noticia = noticiaNormal(modules,titulo,tema)
    elif len(modules) == 3:
        noticia = noticiaOpinion(modules,titulo,tema)
    elif len(modules) == 4:
        noticia = noticiaVideo(modules,titulo,tema)
    return noticia

def noticiasLinks(lavanguardia):

    noticias = []
    titulares = []
    links = []
    html = methods.httpGet(lavanguardia)
    html = html.text
    soup = methods.crearSopa(html)
    noticias = soup.find_all('a', itemprop='headline')
    for noticia in noticias:
        link = f"{lavanguardia}{noticia.get('href')}"    
        noticia = noticia.text
        links.append(link)
        titulares.append(noticia)
    return titulares, links # eventualmente lo unico que me interesarán seran los links

def run():
    
    #noticias, links = noticiasLinks(lavanguardia)
    links, noticias = methods.getLinks(lavanguardia)
    noticiaserror = []
    linkserror = []

    for i in range(len(noticias)):
        if "emagister" in links[i] or "https://www.lavanguardia.comhttps://www.lavanguardia.com" in links[i] or "Últimas noticias" in noticias[i] or not links[i] or "participacion" in links[i] or "motor" in links[i] or "television" in links[i] or "comprar" in links[i] or "comer" in links[i] or "gente" in links[i] or "magazine" in links[i] or "/vida/" in links[i]:
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
            #print(exc)
            print("Otra vez para para:")
            print(linkserror[i])
    return

