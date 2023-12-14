import requests
from bs4 import BeautifulSoup

# GET Request
def httpGet(url):
    resp = requests.get(url)
    html = resp
    return html

# BeautifulSoup object 
def crearSopa(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def newsPapers(diarios):
    soups = []
    for diario in diarios:
        html = httpGet(diario).text
        soup = crearSopa(html)
        soups.append(soup)
    return soups

def news(soups,diarios):
    links = []
    for soup in soups:
        tags = soup.find_all('a')
        for tag in tags:
            href = tag.get('href')
            if href and any(diario in href for diario in diarios): 
                links.append(href)

    sorted = set(links) # quita duplucados
    return  sorted# eventualmente lo unico que me interesarán seran los links


diarios = ["https://www.theguardian.com/europe", "https://www.nytimes.com/", "https://www.lavanguardia.com/", "https://www.elperiodico.com/es/"]
sopas = newsPapers(diarios)
links = news(sopas,diarios)
for link in links:
    print(link)

print(len(links))