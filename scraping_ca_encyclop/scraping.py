import os
import time
import glob
import pickle
import random
import requests
from bs4 import BeautifulSoup
import pandas as pd


from fake_useragent import UserAgent
ua = UserAgent()

import logging
logging.basicConfig(
    filename='encyclop_log.log',
     level=logging.INFO, 
     format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
     datefmt='%H:%M:%S'
 )


def get_art_metaData(art_url):
    # article_url = "https://www.thecanadianencyclopedia.ca/en/article/agricultural-stabilization-board"
    art_rep = requests.get(art_url,headers={'User-Agent': ua.random}).text
    art_soup = BeautifulSoup(art_rep,'html.parser')

    for _ in art_soup.find_all('div',id="article-content-def"):
        text = '\n'.join(p.text for p in _.find_all('p'))
    
    infos = art_soup.find('div',class_="article-informations")
    auth = ' | '.join(a.text for a in infos.find_all('a')) 
    temp = infos.find_all("td", class_="article-details-table")
    first_published = temp[0].text
    last_Update = temp[1].text
    
    return text, auth, first_published, last_Update


def get_page_data(soup):

    lks = soup.find_all("div", class_="search-single-info")
    df = {}
    df["title"] = list()
    df["link"] = list()
    df["desc"] = list()
    df["text"] = list()
    df["auth"] = list()
    df["first_published"] = list()
    df["last_Update"] = list()

    for lk in lks:
        link = lk.find("a").get('href')
        if 'article' in link:
            time.sleep(random.randint(3,6))
            df["title"].append(lk.find('h3').text)
            df["link"].append(link)
            df["desc"].append(lk.find('p').text)
            text, auth, first_published, last_Update = get_art_metaData(link)
            df['text'].append(text)
            df["auth"].append(auth)
            df["first_published"].append(first_published)
            df["last_Update"].append(last_Update)

            logging.info(f'{link.split("/")[-1]} saved')

    df = pd.DataFrame.from_dict(df)

    return df


def get_url_articles(url):
    df_total = pd.DataFrame()
    rep = requests.get(url,headers={'User-Agent': ua.random}).text
    # lecture du code html et la recherche des balises <em>
    soup = BeautifulSoup(rep,'html.parser')
    # récupérer le nombre de page
    temp = soup.find_all("a", class_="page-link")
    
    #retotuner df pour la premiere page
    df_total = df_total.append(get_page_data(soup))
    logging.info(f'{url} page 1 done')

    #append df pour les autres pages
    if len(temp)>0:
        number_pages = int(temp[-2].get('href').split('=')[-1])

        for i in range(2,number_pages+1):
            time.sleep(random.randint(2,5))

            other_link = url+"?page="+str(i)
            rep = requests.get(other_link,headers={'User-Agent': ua.random}).text
            soup = BeautifulSoup(rep,'html.parser')
            df_total = df_total.append(get_page_data(soup)) #get artilces from this theme at this page
            logging.info(f'{url} page {i} done on {number_pages} : {round((i*100)/number_pages,2)}%')
            
    df_total.reset_index(drop=True, inplace=True)
    df_total["cat1"] = url.split('/')[-3]
    df_total["cat2"] = url.split('/')[-2]
    df_total["cat3"] = url.split('/')[-1]
    
    if not os.path.exists("./articles"):
        os.mkdir('./articles')


    with open(f'articles/{url.split("/")[-3]}_{url.split("/")[-2]}_{url.split("/")[-1]}.pkl', 'wb') as pickFile:
        pickle.dump(df_total, pickFile)

    logging.info(f'Shape of this url DataFrame : {df_total.shape}')
    logging.info(f'theme {url.split("/")[-3:]} done')

    # return df_total

def getAllEncyclopLink(first_url):

    logging.info(f'getting all themes')

    # url = 'https://www.thecanadianencyclopedia.ca/en/browse/things'
    rep = requests.get(first_url,headers={'User-Agent': ua.random}).text
    soup = BeautifulSoup(rep,'html.parser')

    all_articles = []
    for _ in soup.find_all('div', class_="sb-tab sb-tab--separator"):
        link = (_.find('a').get('href'))
        if len(link.split('/')) == 8:
            all_articles.append(link)

    with open('articles/articles_theme_link.txt', 'w') as t:
        for _ in all_articles:
            t.write(f'{_}\n')

    logging.info(f'all themes in the kernel')

    return all_articles


def e_s(s,e):
    delta = round(e-s)
    if delta >= 60:
        return round(delta/60,2)
    else:
        return delta


if __name__ == '__main__':
    
    logging.info(f'we start')

    s= time.time()

    url = 'https://www.thecanadianencyclopedia.ca/en/browse/things'
    
    all_articles_links = getAllEncyclopLink(url)
    
    # all_encyclop = pd.DataFrame()
    
    for idx,url in enumerate(all_articles_links):
        time.sleep(2)
        get_url_articles(url) #tous les articles de cette thematique
        logging.info(f'Percentage on total links : {round((idx*100)/len(all_articles_links),2)}%')

    e = time.time()

    logging.info(f'all done in {e_s(s,e)} secs')

    logging.info(f'all saved at articles')


    total = pd.DataFrame()
    for f in glob.glob('articles/*.pkl'):
        df = pd.read_pickle(f)
        total = total.append(df)

    with open('articles/01_total_encyclopedia.pkl','wb') as pick:
        pickle.dump(total,pick)
