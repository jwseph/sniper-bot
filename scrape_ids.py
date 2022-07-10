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

s = requests.session()

schoology_resp = requests.get('https://mukilteo.schoology.com')
schoology_soup = BeautifulSoup(schoology_resp.content, features='lxml')
students = []
#json.dump(students, open('data.json', 'w'), indent=2, default=to_dict)

login_resp = requests.post('https://sts.mukilteo.wednet.edu'+schoology_soup.find('form', {'id': 'loginForm'})['action'], {'UserName': input('gimme ur username')+'@mukilteo.wednet.edu', 'Password': input('password pls very legiet')})
login_soup = BeautifulSoup(login_resp.content, features='lxml')
login_soup_SAMLResponse = login_soup.find('form').find('input', {'name': 'SAMLResponse'})['value']
receive_resp = s.post('https://mukilteo.schoology.com/login/saml/receive', {'SAMLResponse': login_soup_SAMLResponse})
receive_soup = BeautifulSoup(receive_resp.content, features='lxml')



data = [Student(student) for student in json.load(open('data.json', 'r'))] # Schoology data


x = [(student, i) for i, student in enumerate(data) if student.school == 'Olympic View']
print(len(x))


loop = asyncio.get_event_loop()
futures = [(loop.run_in_executor(None, get_soup, student.url), i) for student, i in x]
for future, i in futures:
  soup = await future
  if soup is None:
    print('NONENONE')
    continue
  email_box = soup.select_one('.admin-val.email a')
  if email_box is None: continue
  email = email_box['href']
  if not email.endswith('@mukilteo.wednet.edu'): continue
  print(email[7:-20])
  data[i].id = email[7:-20]

