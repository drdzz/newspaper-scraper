import tomarkdown
import methods



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
                found_tags.append(tag)
    if not found_tags:
        print(link)
    tema = methods.extractTema(link)
    return header, found_tags, tema

def gafcodgadidigu(link):
    html = methods.httpGet(link)
    soup = methods.crearSopa(html)
    return


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
    links = methods.getLinks('https://www.theguardian.com/')
    news = getTags(links[0][:])  # remember getLins() returns headlines aswell (this was optional for future tagging)
    mds = loopThroughNews(news)
    toWrite(mds)
    return