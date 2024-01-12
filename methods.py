from bs4 import BeautifulSoup
import requests
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options

# GET Request
def httpGet(url):
    resp = requests.get(url)
    html = resp
    return html

# BeautifulSoup object 
def crearSopa(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup

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

# Escribe noticia
def escribirNoticia(noticia,titulo):
    #with open('C:\\Users\\marc.ponce\\Documents\\Obsidian Vault\\noticia.md','w',encoding='utf-8') as file:     # For Windows
    with open (f'/Users/marc.ponce/Documents/Obsidian Vault/noticias/{titulo}.md','w',encoding='utf-8') as file:      #  For MacOS
        for i in range(len(noticia)):
            if i>0:
                file.write(noticia[i])
    return

def extractTema(url):
    tema = url.split('/')[3] if len(url.split('/')) > 3 else None
    return tema