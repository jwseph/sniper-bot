import requests
from bs4 import BeautifulSoup
import asyncio
import json


def get_soup(url):
    r = s.get(url)
    while r.status_code == 429:
        #print('oof')
        r = s.get(url)
    print(r.status_code)
    return BeautifulSoup(r.content, features='lxml') if r.ok else None
json.dumps(sorted(sorted(students, key=(lambda student: student.name[::-1].split(' ', 1)[1][::-1])), key=(lambda student: student.name[::-1].split(' ', 1)[0][::-1])), indent=2, default=to_dict)
class Student:
  __slots__ = 'name', 'image', 'school', 'url', 'id'
  def __init__(self, obj=None, **kwargs):
    if 'soup' in kwargs:
      soup = kwargs['soup']
      self.name = soup.select_one('div.item-title > a').text
      self.image = soup.select_one('a > div > div > img')['src'].replace('imagecache/profile_sm', 'imagecache/profile_reg')
      self.school = soup.select_one('div.item-info > span.item-school').text
      self.url = 'https://mukilteo.schoology.com'+soup.select_one('div.item-title > a')['href']+'/info'
      self.id = None
    elif obj is not None:
      self.name = obj['name']
      self.image = obj['image']
      self.school = obj['school']
      self.url = obj['url']
      self.id = obj['id']
    else:
      raise ValueError('Neither soup or obj was passed in Student constructor.')
  def to_dict(self):
    return {
      'name': self.name,
      'image': self.image,
      'school': self.school,
      'url': self.url,
      'id': self.id
    }
def to_dict(student: Student):
  return student.to_dict()


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


    n = 19755
    #n = 19755
    loop = asyncio.get_event_loop()
    futures = [loop.run_in_executor(None, get_soup, f'https://mukilteo.schoology.com/search/user?page={p}&s=%20%20%20') for p in range(-(-n//10))]

    students = []

    for future in futures:
        soup = await future
        students += [
            Student(soup=student)
            for student in soup.select('#main-inner > div.item-list > ul > li.search-summary > div')
        ]

    json.dump(students, open('data.json', 'w'), indent=2, default=to_dict)
    # globals()['x'] = json.dumps(students, default=to_json)
    # print(x)

await main()
# asyncio.run(main())