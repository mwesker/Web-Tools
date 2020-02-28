#! python3

from time import sleep
import requests
from bs4 import BeautifulSoup
import xmltodict
import re
import json
import sys
import UCCS_Scraper
from urllib.parse import urlparse


STAGING = "cms.staging"
PROD = "www"
ACQUIA = ""

def getSiteMap(site, board, k, t , server=PROD):
    # 'https://www.uccs.edu/<sitename>/sitemap.xml'
    list_id = getList(board, k, t)
    cards, card_ids = getExsitingCards(board, list_id, k, t)

    baseURL = f'https://{server}.uccs.edu/{site}/sitemap.xml'

    userAgent = "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11"
    headers = {'User-Agent': userAgent}

    # get the web page
    res = requests.get(baseURL, headers=headers)

    # get the response in HTML
    page = res.text

    # parse the HTML
    soup = BeautifulSoup(page, 'html.parser')

    docx = soup.prettify()
    doc = xmltodict.parse(docx)

    # Good to here

    stuff = ''
    tracker = {}
    counter = 0
    for i in doc['urlset']['url']:
        res = requests.get(i['loc'], headers=headers)
        page = res.text
        soup = BeautifulSoup(page, 'html.parser')
        a = soup.select('title')
        if i['loc'] not in tracker:
            tracker[str(i['loc'])] = 'Collected'
            # stuff += (re.sub(r'\s\|.*$', '', a[0].text) + '\n\n')
            # stuff += (i['loc'] + '\n\n')
            # stuff += ('\n' + '-' * 20 + '\n\n\n')
            title = (re.sub(r'\s\|.*$', '', a[0].text) + '\n\n')
            description = i['loc']
            counter = createCards(list_id, cards, title, description, k, t, counter)

    return str(counter) + ' cards were created on the ' + str(site) + ' board.'


def getList(boardId, k, t):

    BOARD_URL = "https://api.trello.com/1/boards/{}/lists".format(boardId)

    querystring = {"cards": "none", "card_fields": "all", "filter": "open", "fields": "all", "key": k, "token": t}

    response = requests.request("GET", BOARD_URL, params=querystring)

    responseAsJson = json.loads(response.text)

    listId = [i['id'] for i in responseAsJson]

    return listId[0]


def createCards(listId, listCards, title, description, k, t, counter=0):
    CARD_URL = "https://api.trello.com/1/cards"


    querystring = {"name": title, "desc": description, "pos": "bottom", "idList": listId, "keepFromSource": "all",
                   "key": k, "token": t}


    if description not in listCards and (description + '/') not in listCards:
        requests.request("POST", CARD_URL, params=querystring)
    sleep(.1)
    counter = counter + 1
    return counter


def getExsitingCards(boardID, listId, k, t):
    print(boardID)
    #querystring = {"fields": 'name', "key": k, "token": t}

    #response = requests.request("GET", "https://api.trello.com/1/lists/{}/cards".format(listId), params=querystring)

    # responseAsJson = json.loads(response.text)

    # cards = [i['name'].replace('\\\n', '') for i in responseAsJson]

    querystring = {"key": k, "token": t}

    response = requests.request("GET", "https://api.trello.com/1/boards/{}/cards/visible".format(boardID), params=querystring)

    responseAsJson = json.loads(response.text)
    #print(responseAsJson)
    card_id = [i['id'] for i in responseAsJson]
    cards_desc = [i['desc'] for i in responseAsJson]



    return cards_desc, card_id


def initializeChecking(site, board, k, t):

    return getSiteMap(site, board, k, t)


# ignore this is an experiment
def desc(boardID, k, t):
    cards, cards_id = getExsitingCards(boardID, '', k, t)


    for c in cards_id:
        sleep(.25)
        url = f"https://api.trello.com/1/cards/{c}"
        querystring = {"fields": "desc", "attachments": "false", "attachment_fields": "all", "members": "false",
                       "membersVoted": "false", "checkItemStates": "false", "checklists": "none",
                       "checklist_fields": "all",
                       "board": "false", "list": "false", "pluginData": "false", "stickers": "false",
                       "sticker_fields": "all", "customFieldItems": "false", "key": k, "token": t}

        response = requests.request("GET", url, params=querystring)
        responseAsJson = json.loads(response.text)

        description = responseAsJson['desc'].replace("/index.php", '')
        #description = responseAsJson['desc']

        querystring = {"key": k, "token": t, "desc": description}

        print(description)
        response = requests.request("PUT", "https://api.trello.com/1/cards/{}".format(c),
                                    params=querystring)

# ignore this is an experiment
def exists(boardID, k, t):
    cards, cards_id = getExsitingCards(boardID, '', k, t)


    for c in cards_id:


        url = f"https://api.trello.com/1/cards/{c}"
        querystring = {"fields": "desc", "attachments": "false", "attachment_fields": "all", "members": "false",
                       "membersVoted": "false", "checkItemStates": "false", "checklists": "none",
                       "checklist_fields": "all",
                       "board": "false", "list": "false", "pluginData": "false", "stickers": "false",
                       "sticker_fields": "all", "customFieldItems": "false", "key": k, "token": t}

        response = requests.request("GET", url, params=querystring)
        responseAsJson = json.loads(response.text)
        print(responseAsJson)
        description = responseAsJson['desc']

        r = requests.request("GET", 'https://oit.uccs.edu' + urlparse(description).path.replace('oit/', ''))
        if (r.status_code != 404):
            url = f"https://api.trello.com/1/cards/{c}/Labels"
            querystring = {"color": "orange", 'name': 'Exists', "key": k, "token": t}
            response = requests.request("POST", url, params=querystring)


        sleep(.1)


def checklinks(site, boardID, k, t):
    l = UCCS_Scraper.crawl(site)
    cards, ids = getExsitingCards(boardID, '', k, t)
    card = {cards[i]: ids[i] for i in range(len(ids))}

    for c in card.keys():
        a = re.sub('^http:', 'https:', c)
        print(c, card[c], a in l)
        if c in l:
            url = f"https://api.trello.com/1/cards/{card[c]}/Labels"
            querystring = {"color": "sky", 'name': 'Linked', "key": k, "token": t}
            response = requests.request("POST", url, params=querystring)









#desc('JergcfMf', KEY, Token)

#exists('JergcfMf', KEY, Token)

siteName = "" # https://www.uccs.edu/sitename -> siteName = "sitename"
boardID = "" # https://trello.com/b/JergcfMf/test -> boardID = "JergcfMf"
KEY = "89ef7014af1d0b50519e67cbb1dbb832" #
Token = "45c874ca75300b2bb4330be5a330dfa336675c68b73089d486a0297f9c756313" #

initializeChecking(siteName, boardID, KEY, Token)


# checklinks() does not handle Acquia
#checklinks(siteName, boardID, KEY, Token) # make sure UCCS_Scraper.py is in the same directory
