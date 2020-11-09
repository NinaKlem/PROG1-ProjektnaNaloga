# -*- coding: utf-8 -*-

import os
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd


arso_naprave_dir = os.path.abspath('')
rawdata_excel = os.path.join(arso_naprave_dir, 'rawdata_excel')
rawdata_csv = os.path.join(arso_naprave_dir, 'rawdata_csv')

arso_naprave_url = 'http://okolje.arso.gov.si/onesnazevanje_zraka/devices'

arso_naprave_vzorec = re.compile(r'http://okolje.arso.gov.si/onesnazevanje_zraka/.{*}')
arso_naprave_prikazano_besedilo = re.compile(r'Emisije.{*} snovi v zrak iz industrijskih obratov za leto \d{r}', flags=re.DOTALL)

def loadPage(url):
    """
    url: naslov, niz
    response: objekt
    """
    response = requests.get(url)
    response.raise_for_status()
    if response.encoding == None:
        response.encoding = 'utf-8'
    return response

def saveFILE(infile, encoding):
    """
    infile: response.encoding oz. requests.get(url).text oz. loadPage(url).text
    encoding: response.encoding oz. requests.get(url).encoding oz. loadPage(url).encoding
    outfile: html-datoteka
    """
    with open('outfile.html', 'w', encoding = encoding) as outfile:
        outfile.write(infile)
    return outfile


def getLinks(html):
    """
    html: html-datoteka
    links: seznam povezav
    """
    links = []
    for link in html.findAll('a', attrs={'href': re.compile(r'http://okolje.arso.gov.si/onesnazevanje_zraka/')}, string = re.compile('Emisije')):
        links.append(link.get('href'))
    return links


def main():  
    page = loadPage(arso_naprave_url)  
    saveFILE(page.text, page.encoding)
    
    with open(os.path.join(arso_naprave_dir, 'outfile.html'), 'r') as infile:
        outfile_html = BeautifulSoup(infile)
    
# V datoteki outfile.html najde povezave na *.xls(x) datoteke s podatki o emisijah, jih shrani v seznam in uredi: 
    links = getLinks(outfile_html)
    links.insert(2, 'http://okolje.arso.gov.si/onesnazevanje_zraka/uploads/datoteke/EmisijeZrak2016%20DRUGA%20OBJAVA.xlsx')
    
# Preimenuje in shrani *.xls(x) datoteke (rawdata_excel) in *.csv (rawdata_csv)
    for i in range(len(links)): 
        response = loadPage(links[i])
        ext = os.path.splitext(links[i])[1]
        if re.search('[.]xls', ext):
            filename_excel = 'EmisijeZrak' + str(2018-i) + ext
        else:
            filename_excel = 'EmisijeZrak' + str(2018-i) + '.xls'
        with open(os.path.join(arso_naprave_dir, rawdata_excel, filename_excel), 'wb') as infile:
            infile.write(response.content)
            infile.close()
               
    for file in os.listdir(os.chdir(rawdata_excel)):
        filename_csv = os.path.splitext(file)[0] + '.csv'
        infile = pd.read_excel(file)
        outfile = infile.to_csv(os.path.join(rawdata_csv, filename_csv))
        
