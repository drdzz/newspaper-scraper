from bs4 import BeautifulSoup
import requests
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
import os

# GET Request
def httpGet(url):
    resp = requests.get(url)
    html = resp
    return html

# BeautifulSoup object 
def crearSopa(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def newsPapers(diario):
    soups = []
    html = httpGet(diario).text
    soup = crearSopa(html)
    soups.append(soup)
    
    return soups

# To find all news from a list of newspapers
def getLinks(diario):
    sopas = newsPapers(diario)
    if "theguardian" in diario:
        linkAndHeadlines = linksGuardian(sopas[0])
    elif "lavanguardia" in diario:
        linkAndHeadlines = linksVanguardia(sopas[0])
    elif "elperiodico" in diario:
        print("")
    links = linkAndHeadlines[0]
    headlines = linkAndHeadlines[1] # Reserve this for easier categorization, probably not needed since headline inside news anyway
    return links, headlines

# buscaod Youtube Video 
def videoFinder(titular): # esta era la idea, estoy apunto de desecharla, aunque esta es la manera mas sencilla seguro
        youtube_url = "https://www.youtube.com/results?search_query=+"

        search_url = f'{youtube_url}{titular}lavanguardia'
        search_url = search_url.replace(' ','+')
        search_url = search_url.replace('%','')
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(search_url)
        user_data = driver.find_elements('xpath', '//*[@id="video-title"]')
        links = []
        for i in user_data:
                    links.append(i.get_attribute('href'))
        link = links[0]
        return link            



def escribirNoticia(noticia, titulo):
    directory = "/Users/marc.ponce/Documents/Obsidian Vault/noticias/"
    os.makedirs(directory, exist_ok=True)

    # Sanitize the title by replacing "/" with another character (e.g., "_")
    sanitized_titulo = titulo.replace("/", "_")

    file_path = os.path.join(directory, f"{sanitized_titulo}.md")

    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            for line in noticia:
                file.write(line)
    except FileNotFoundError:
        print(f"Error: The directory '{directory}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")


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

def extractTema(url):
    tema = url.split('/')[3] if len(url.split('/')) > 3 else None
    return tema