import requests
from bs4 import BeautifulSoup
import asyncio


def get_soup(url):
    r = s.get(url)
    while r.status_code == 429:
        #print('oof')
        r = s.get(url)
    print(r.status_code)
    return BeautifulSoup(r.content, features='lxml') if r.ok else None

username, password = '1602362@mukilteo.wednet.edu', 'JoajCas123'
s = requests.session()
    

async def main():

    schoology_resp = requests.get('https://mukilteo.schoology.com')
    schoology_soup = BeautifulSoup(schoology_resp.content, features='lxml')
    login_resp = requests.post('https://sts.mukilteo.wednet.edu'+schoology_soup.find('form', {'id': 'loginForm'})['action'], {'UserName': username, 'Password': password})
    login_soup = BeautifulSoup(login_resp.content, features='lxml')
    login_soup_SAMLResponse = login_soup.find('form').find('input', {'name': 'SAMLResponse'})['value']

    receive_resp = s.post('https://mukilteo.schoology.com/login/saml/receive', {'SAMLResponse': login_soup_SAMLResponse})
    receive_soup = BeautifulSoup(receive_resp.content, features='lxml')
    #user_data = json.loads(receive_soup.select_one('#body > script').text.replace('window.siteNavigationUiProps=', ''))['props']['user']


    n = 500
    #n = 19755
    loop = asyncio.get_event_loop()
    futures = [loop.run_in_executor(None, get_soup, f'https://mukilteo.schoology.com/search/user?page={p}&s=%20%20%20') for p in range(-(-n//10))]

    students = []

    for p, future in enumerate(futures):
        soup = await future
        students += [
            [
                student.select_one('div.item-title > a').text,
                #student.select_one('a > div > div > img')['src'].replace('imagecache/profile_sm', 'imagecache/profile_reg'),
                student.select_one('div.item-info > span.item-school').text
            ]
            for student in soup.select('#main-inner > div.item-list > ul > li.search-summary > div')
        ]

    print(students)
        

asyncio.run(main())
