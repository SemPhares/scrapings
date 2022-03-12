import re
import time
import json
import numpy as np
from random import randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

 
# service = Service('chromedriver')
# service.start()
# options = Options() #webdriver.chromeOptions()

# create webdriver object
# driver = webdriver.Chrome(executable_path="../chromedriver.exe")
# driver = webdriver.Firefox(executable_path='geckodriver.exe')

class inpi_data:
    
    def __init__(self,nom,prenom):
        self.nom = nom
        self.prenom = prenom
        self.driver = webdriver.Chrome(executable_path="../chromedriver.exe") #webdriver.Remote()
        
        
    def getNbPages(self):
        all_pages = self.driver.find_elements(By.XPATH,"//a[@role='button'][contains(@class,'mr-3 pointer page-number ')]")
        return len(all_pages)

    def getLinksFromPage(self):
        elems = self.driver.find_elements(By.XPATH, "//a[contains(@class,'not-link')]")
        links = list(set([elem.get_attribute('href') for elem in elems]))
        return links

    def getPagesLinks(self,nb_pages=3,all_pages=False):

        all_links = []
        l1 = 'https://data.inpi.fr/search?advancedSearch=%257B%257D&filter=%257B%257D&nbResultsPerPage=50&order=asc'
        l2 = "&page=1&q="+self.prenom+'%20'+self.nom+'&sort=relevance&type=companies'
        link = l1+l2
        self.driver.get(link)
        time.sleep(3)
        nb_ = self.getNbPages()

        all_links.append(self.getLinksFromPage())
        
        if all_pages:
            for i in range(2,nb_+1):
                self.driver.get(link.replace('page=1',f'page={i}'))
                all_links.append(self.getLinksFromPage())
        else:
            for i in range(2,nb_pages+1):
                self.driver.get(link.replace('page=1',f'page={i}'))
                all_links.append(self.getLinksFromPage())
        
        all_links = [lk for page_likns in all_links for lk in page_likns]

        return all_links


    def get_attr(slef,web_elements):
        # return [_.get_attribute("innerHTML") for _ in web_elements ]
        return [el.text for el in web_elements] 

    def list_dict_from_page(self):
        all_values = self.driver.find_elements(By.XPATH,"//p[contains(@class, 'font-size-0-9-rem')]")
        values = self.get_attr(all_values)
        
        identity=[]
        representants =[]
        etablissements=[]
        for i in range(len(values)):
            if 'Pour plus d\'informations sur les représentants' in values[i]:
                identity = values[0:i]

            if "Type d'établissement" in values[i]:
                representants = values[len(identity)+1:i]   
                etablissements=values[i:]
                break

        return identity,representants,etablissements

    def get_dict_identity(self,identity):
        header = {}
        for i in range(0,len(identity),2):
            header.update({identity[i]:identity[i+1]})
            
        return header

    def getIndicesToDelete(self,keys):
        return [i for i, j in enumerate(keys) if j == "Nom d'usage"]

    def dropNomDusage(self, ls, indices_to_delete):
        clean_list = np.delete(ls, indices_to_delete).tolist()
        return clean_list

    def getTheDict(self,keys,n_):
        TheDict = {}

        for j in range(0,len(keys),n_):
            try:
                i=next(ls)
                rep[i] = {k:v for (k,v) in zip(keys[j:j+n_],values[j:j+n_])}
            except:
                break
            
        return TheDict


    def get_dict_representative(self,representatives):

        rep = {}
        representatives = [re.sub('<\w*>|\n|</em>|<em class="highlight-elasticsearch">', '',_).strip() for _ in representatives] 
        nb_rep_ = representatives.count('Nom, Prénom(s)')
        
        if nb_rep_==0:
            return {"Zero Message":'Jiraya founds no representatives'}

        else:
            
            ls = (k for k in range(1,nb_rep_+1))

            keys = [representatives[i] for i in range(0,len(representatives),2)]
            indices_to_delete = self.getIndicesToDelete(keys)
            keys = self.dropNomDusage(keys,indices_to_delete)
            values = self.dropNomDusage([representatives[i] for i in range(1,len(representatives),2)],indices_to_delete)

            nb_rep_attr_ = int(len(keys)/nb_rep_)
            
            for j in range(0,len(keys),nb_rep_attr_):
                try:
                    i=next(ls)
                    rep[i] = {k:v for (k,v) in zip(keys[j:j+nb_rep_attr_],values[j:j+nb_rep_attr_])}
                except:
                    break

            # rep = getTheDict(keys,nb_rep_attr_)
            return  rep

    def get_dict_benef(self):
        all_keys = self.driver.find_elements(By.XPATH,"//p[contains(@class, 'mb-0 font-size-13 inpi-light')]")
        all_values = self.driver.find_elements(By.XPATH,"//p[contains(@class, 'font-size-15')]")

        keys = self.get_attr(all_keys)
        values = self.get_attr(all_values)

        nb_benef_ = keys.count('Nom prénom')
        if nb_benef_==0:
            return {'Zero Message':'Jiraya founds no beneficiaries'}
        else : 
            nb_benf_attr_ = int(len(keys)/nb_benef_)

            beneficiaires = {}
            ls = (k for k in range(1,nb_benef_+1))
        
            for j in range(0,len(keys),nb_benf_attr_):
                try:
                    i=next(ls)
                    beneficiaires[i] = {k:v for (k,v) in zip(keys[j:j+nb_benf_attr_],values[j:j+nb_benf_attr_])}
                except:
                    break

            return beneficiaires

    def get_dict_ets(self,etablissements):

        keys = [etablissements[i] for i in range(0,len(etablissements),2)]
        values = [etablissements[i] for i in range(1,len(etablissements),2)]

        nb_ets_ = keys.count("Type d'établissement")
        if nb_ets_ ==0:
            return {'Zero message': 'Jiraya founds no etablissement'}
        else:
                
            nb_ets_attr_ = int(len(keys)/nb_ets_)

            etablissements = {}
            ls = (k for k in range(1,nb_ets_+1))
        
            for j in range(0,len(keys),nb_ets_attr_):
                try:
                    i=next(ls)
                    etablissements[i] = {k:v for (k,v) in zip(keys[j:j+nb_ets_attr_],values[j:j+nb_ets_attr_])}
                except:
                    break

            return etablissements

    def dict_from_page(self,identity,representatives,etablissements):
        TheDict = { "identity": self.get_dict_identity(identity),
                    "representatives" : self.get_dict_representative(representatives),
                    "beneficiaires": self.get_dict_benef(),
                    "etablissements": self.get_dict_ets(etablissements)
                            }
        return TheDict


    def run(self,all_pages=False):
        links = self.getPagesLinks(nb_pages=1, all_pages=all_pages)
        all_enterprise = dict()
        for i in range(len(links)):
            self.driver.get(links[i])
            identity,representatives,etablissements = self.list_dict_from_page()
            all_enterprise[i] = self.dict_from_page(identity,representatives,etablissements)

        return all_enterprise



