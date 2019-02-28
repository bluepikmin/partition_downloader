import requests
import urllib.request
from bs4 import BeautifulSoup
import img2pdf

import os
import shutil


site_url = u'http://www.everyonepiano.com'

def search_song(search_string):
    # http://www.everyonepiano.com/Piano-search/?word=totoro&come=web
    soup = BeautifulSoup(requests.get(f'{site_url}/Piano-search/?word={search_string}&come=web').content, 'html.parser')
    results = soup.find('span', class_='EOPRed')
    print('nb de resultats : ' + results.string)
    nb_results = int(results.string)
    if nb_results == 0:
        print(u"Aucun résulat, pas de chance :'(")
        return 0
    # il y a 24 resultas par page, du coup on boucle si besoin
    page = 1
    while nb_results > 0:
        if page > 1:
            soup = BeautifulSoup(requests.get(f'{site_url}/Piano-search/?word={search_string}&come=web&p={page}').content, 'html.parser')
        lines = soup.find('div', class_="Body").find_all('li')
        for line in lines:
            title = line.find('div', class_='EOPIndexNewMusicTitle').string
            # on recupere juste l'id d'une url du type : '/Piano-5916.html'
            id = line.find('div', class_='EOPIndexNewMusicTitle').a.get('href').split('-')[-1][:-5]
            # on traitera la date pour l'afficher à la française
            date = line.find('div', class_='EOPIndexNewMusicUpdate').string.split('-')
            print(f'{id} - {title} ({date[2]}-{date[1]}-{date[0]})')
        nb_results -= 24
        page += 1
    return 1



def dld_partition(user_in):
    id_sheet = int(user_in)
    soup = BeautifulSoup(requests.get(f'{site_url}/Piano-{id_sheet}.html').content, 'html.parser')

    #on vérifie qu'il y a bien qqch à l'id indiqué
    if soup.find('div', class_="NoPianoId"):
        print(u"Hum, c'est confus, j'ai l'impression qu'il n'y a rien ici...   :-S")
        return -1

    song_name = soup.title.string.replace(u'- Free Piano Sheet Music & Piano Chords', '')
    ifr = soup.find(id="s_Frame")
    ifr_url = ifr['datasrc']
    soup = BeautifulSoup(requests.get(f'{site_url}/{ifr_url}').content, 'html.parser')
    imgs = soup.find_all('img', class_='img-responsive')
    if os.path.exists(str(id_sheet)):
        shutil.rmtree(str(id_sheet))
    os.mkdir(str(id_sheet))

    for img in imgs:
        img_url = site_url + img['src']
        img_name = img['src'].split('/')[-1]
        urllib.request.urlretrieve(img_url, str(id_sheet) + os.sep + img_name)
    # on fait un pdf
    files = [str(id_sheet) + os.sep + i for i in os.listdir(str(id_sheet)) if i.endswith(".png")]
    if not os.path.exists('PDF'):
        os.mkdir('PDF')
    with open('PDF' + os.sep + song_name + ".pdf", "wb") as f:
        f.write(img2pdf.convert(files))
    print(f'Partition téléchargée : {song_name}.pdf')
    # menage
    shutil.rmtree(str(id_sheet))
    return 1


while True:
    print('Entrez une recherche un identifiant si vous le connaissez (q pour quitter)')
    user_in = input(": ")
    if user_in == 'q':
        break
    if not user_in.isdigit():
        #ca doit etre une recherche...
        search_song(user_in)
        continue
    else:
        # ca doit etre un id, on dlde
        dld_partition(user_in)


