from bs4 import BeautifulSoup as bs

def rewriteToMd(soup):
    noticia = []
    titulo = f"{soup.find('h1').text}\n"
    noticia.append(titulo)
    subti = soup.find('div', class_='dcr-1oosqmb') or soup.find('div', class_='dcr-95in8m') or soup.find('div', class_='dcr-xq41iu')
    forpic = (soup.find('div', class_='dcr-1y30hqo') or soup.find('div', class_="dcr-1s2dckq"))
    pic = None
    if forpic:
        pic = forpic.find('picture')
    if subti:
        subs1 = subti.find_all('p')
        subs = []
        noticia.append("-----------\n")
        for sub in subs1:
            subs.append(f"- **{sub.text}**")
        noticia.append("-----------\n")
        for sub in subs:
            noticia.append(sub)
        noticia.append("\n-----------\n")
    if pic:
        for tag in pic:
            link = tag.get('src')
            subpic = tag.get('alt')
            if link:
                noticia.append(f"![]({link})\n")
                noticia.append(f"*{subpic}*\n\n")

    return noticia

def tag2md(tags):
    stuff = []

    for tag in tags:
        if type(tag) is not str:
    
            if tag.name == 'h2':
                stuff.append(f"##### {tag.text}")
            elif tag.name == 'h3':
                stuff.append(f"###### {tag.text}")
            elif tag.name == 'img': # falta cambiar esto al otor metodo, ya que tag2md solo va los paragraphs y algun h2 supongo 
                stuff.append(f"![|100%]({tag.get('src')})"+"{width=100%}\n")
                stuff.append(f"*{tag.get('alt')}*\n\n")
            elif tag.name == 'video':
                stuff.append(f"Aqui habia un video")
            elif tag.name == 'p':
                stuff.append(f"{tag.text}\n\n")
            else:
                pass

    return stuff

