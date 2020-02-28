from time import sleep
import requests
from bs4 import BeautifulSoup
import xmltodict
import re
import json
import urllib.parse
from copy import deepcopy

BASE_URL = "https://www.uccs.edu"

USER_AGENT = "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11"



def add_to_queue(queue, additions, visited):

    for add in additions:
        add = re.sub('^http:', 'https:', add)
        if add not in queue and (add not in visited and urllib.parse.urljoin(BASE_URL, add) not in visited):
            queue.append(add)

    return queue


def request(agent, path):


    headers = {'User-Agent': agent}

    response = requests.get(path, headers=headers)
    #print(response.headers)

    page = response.text

    parsed_page = BeautifulSoup(page, 'html.parser')

    return parsed_page



def extract_element(page, selector):
    elements = page.find_all('a')
    return elements

def extract_attributes(elements, attribute):

    attribute_list = []

    for e in elements:

        try:
            attribute_list.append(e.attrs[attribute])
        except Exception as es:
            pass
    return attribute_list

def filter_attributes(attributes, filter='', regex='', partial=''):

    filtered_list = []

    if partial:
        for query in attributes:
            print(query)
            if partial in query and not re.search('\..+?$', query[-6:]):

                filtered_list.append(query)

    return filtered_list




def crawl(site):

    queue = []
    visited = []
    a = request(USER_AGENT, urllib.parse.urljoin(BASE_URL, site))
    b = extract_element(a, 'a')
    c = extract_attributes(b, 'href')
    d = filter_attributes(c, partial='/'+site)
    queue = add_to_queue([], d, visited)

    while queue:
        page = queue.pop()
        sleep(1)
        page = urllib.parse.urljoin(BASE_URL, page)
        page = re.sub('^http:', 'https:', page)
        if page not in visited:
            visited.append(page)
        try:
            a = request(USER_AGENT, page)
            b = extract_element(a, 'a')
            c = extract_attributes(b, 'href')
            d = filter_attributes(c, partial='/'+site)
            queue = add_to_queue(deepcopy(queue), d, visited)
            a = b = c = d = []
            print(page)
        except Exception as e:
            print(page)

    return visited



