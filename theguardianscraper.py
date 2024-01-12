import tomarkdown
import methods


def newsPapers(diario):
    soups = []
    html = methods.httpGet(diario).text
    soup = methods.crearSopa(html)
    soups.append(soup)
    
    return soups

def html_to_markdown(html_code): ## Kinda works pero no es el comportamiento que espero
    markdown_text = tomarkdown.rewriteToMd(html_code)
    
    return markdown_text

# To extract the tags from the Article html
def getTags(links):
    tags = []
    temas = []
    for link in links:
        new = []
        a = articleExtractor(link)
        header = a[0]
        article = a[1]
        tema = a[2]
        temas.append(tema)
        new.append(header)
        new.append(article)
        tags.append(new)
    return tags, temas

# To markdown
def tag2md(tags):
    md = tomarkdown.tag2md(tags)
    
    return md

def headers(new):
    md_headers = tomarkdown.rewriteToMd(new)

    return md_headers

def linksGuardian(soup):
    links = []
    headlines = []
    tags = soup.find_all('div', class_="dcr-omk9hw")
    for tag in tags:
        tag = tag.find('a')
        headline = tag.get('aria-label')
        href = tag.get('href')
        link = 'https://theguardian.com' + href
        links.append(link)
        headlines.append(headline)
    return  links, headlines # eventualmente lo unico que me interesarán seran los links

def linksPeriodico(soup):
    links = []
    headlines = []
    tags = soup.find_all('h2', class_="title")
    for tag in tags:
        tag = tag.find('a')
        if tag:
            href = tag.get('href')
            headline = tag.get('title')
            links.append(href)
            headlines.append(headline)

    return  links, headlines

def linksVanguardia(soup):
    headlines = []
    links = []
    vang = "https://www.lavanguardia.com"
    noticias = soup.find_all('a', itemprop='headline')
    for noticia in noticias:
        link = f"{vang}{noticia.get('href')}"    
        headline = noticia.text
        links.append(link)
        headlines.append(headline)
    return links, headlines

def articleExtractor(link):
    tags_to_find = ['h2', 'h3', 'img', 'video', 'p']
    found_tags = []
    html = methods.httpGet(link)
    soup = methods.crearSopa(html.text)
    article = (soup.find('article', class_='article-default') or soup.find('div', id='maincontent'))
    header = headers(soup)
    # en esta linia que escribo es donde podrias aun usar el metodo tomarkdown para extraer en md del tiron, (solo lo tienes hecho para guardian)
    if article:
        # Find tags sequentially in the order they appear in the content
        for tag in article.find_all(tags_to_find):
            if tag.name in tags_to_find:  # Check if the found tag matches the desired tags
                #print(tag)
                found_tags.append(tag)
    if not found_tags:
        print(link)
    tema = methods.extractTema(link)
    return header, found_tags, tema

def gafcodgadidigu(link):
    html = methods.httpGet(link)
    soup = methods.crearSopa(html)
    return

# To find all news from a list of newspapers
def getLinks(diario):
    sopas = newsPapers(diario)
    linkAndHeadlines = linksGuardian(sopas[0])
    links = linkAndHeadlines[0]
    headlines = linkAndHeadlines[0] # Reserve this for easier categorization, probably not needed since headline inside news anyway
    return links, headlines

def createNewMd(headers, body, tema):
    new = []
    for header in headers:
        new.append(header)
    for paragraph in body:
        new.append(paragraph)
    if tema =='world' or ' global-development':
        tema = 'internacional'
    elif tema == 'technology':
        tema = 'tecnologia'
    
    new.append(f"\n#news #{tema}")
    return new

def loopThroughNews(news):
    new = []
    i = 0
    for a in news[0]:
        try:
            md_article = tag2md(a[1])
            b = createNewMd(a[0],md_article, news[1][i])
            new.append(b)
        except Exception as exc:
            print(exc)
        i = i+1 
    return new

def toWrite(md_list):
    for md in md_list:
        titulo = md[0]
        body = md[1:]
        methods.escribirNoticia(body, titulo[2:])
    
    return

def run():
    links = getLinks('https://www.theguardian.com/')
    news = getTags(links[0][:])  # remember getLins() returns headlines aswell (this was optional for future tagging)
    mds = loopThroughNews(news)
    toWrite(mds)
    return