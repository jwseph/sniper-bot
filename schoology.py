import requests
from bs4 import BeautifulSoup
import json


SCHOOL_MAP = {
  'Mukilteo School District': 'Mukilteo School District',
  'ACES High School': 'ACES',
  'Challenger Elementary School': 'Challenger',
  'Columbia Elementary School': 'Columbia',
  'Community Based Transition Center': 'CBTC',
  'Discovery Elementary School': 'Discovery',
  'Early Childhood Ed. & Assistance': 'ECEAP',
  'Endeavour Elementary School': 'Endeavour',
  'Explorer Middle School': 'Explorer',
  'Fairmount Elementary School': 'Fairmount',
  'Harbour Pointe Middle School': 'Harbour Pointe',
  'Horizon Elementary School': 'Horizon',
  'Kamiak High School': 'Kamiak',
  'Lake Stickney Elementary School': 'Lake Stickney',
  'Mariner High School': 'Mariner',
  'Mukilteo Elementary School': 'Mukilteo Elementary',
  'Mukilteo Special Education': 'Special Education',
  'Mukilteo Virtual Academy': 'Virtual Academy',
  'Odyssey Elementary School': 'Odyssey',
  'Olivia Park Elementary School': 'Olivia Park',
  'Olympic View Middle School': 'Olympic View',
  'Pathfinder Kindergarten Center': 'Pathfinder',
  'Picnic Point Elementary School': 'Picnic Point',
  'Serene Lake Elementary School': 'Serene Lake',
  'Sno-Isle TECH Skills Center': 'Sno-Isle Skills Center',
  'Summer School - Elementary': 'Summer School - Elementary',
  'Summer School - Middle/High': 'Summer School - Middle/High',
  'Summer School - Skills Center': 'Summer School - Skills Center',
  'Voyager Middle School': 'Voyager',
}


class Student:
  __slots__ = 'name', 'image', 'school', 'url', 'id'

  def __init__(self, obj=None, **kwargs):
    if 'soup' in kwargs:
      soup = kwargs['soup']
      self.name = soup.select_one('div.item-title > a').text
      self.image = [soup.select_one('a > div > div > img')['src'].replace('imagecache/profile_sm', 'imagecache/profile_reg')]
      school = soup.select_one('div.item-info > span.item-school').text
      self.school = [SCHOOL_MAP.get(school, school)]
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

  def update(self, **kwargs):
    assert 'soup' in kwargs
    soup = kwargs['soup']
    image = soup.select_one('a > div > div > img')['src'].replace('imagecache/profile_sm', 'imagecache/profile_reg')
    school = soup.select_one('div.item-info > span.item-school').text
    school = SCHOOL_MAP.get(school, school)
    if image in self.image: self.image.remove(image)
    if school in self.school: self.school.remove(school)
    if len(self.image) > 0: print(image+" "+self.image[0])
    self.image.append(image)
    self.school.append(school)
      
  def to_dict(self):
    return {
      'name': self.name,
      'image': self.image,
      'school': self.school,
      'url': self.url,
      'id': self.id
    }


class SchoologySession(requests.Session):

  def __init__(self, username: str, password: str):
    super().__init__()
    schoology_resp = requests.get('https://mukilteo.schoology.com/')
    schoology_soup = BeautifulSoup(schoology_resp.content, features='lxml')
    login_resp = requests.post('https://sts.mukilteo.wednet.edu'+schoology_soup.find('form', {'id': 'loginForm'})['action'], {'UserName': username, 'Password': password})
    login_soup = BeautifulSoup(login_resp.content, features='lxml')
    login_soup_SAMLResponse = login_soup.find('form').find('input', {'name': 'SAMLResponse'})['value']
    receive_resp = self.post('https://mukilteo.schoology.com/login/saml/receive', {'SAMLResponse': login_soup_SAMLResponse})
    
    receive_soup = BeautifulSoup(receive_resp.content, features='lxml')
    user_data = json.loads(receive_soup.select_one('#body > script').text.removeprefix('window.siteNavigationUiProps='))['props']['user']
    self.uid = str(user_data['uid'])
    self.schools = [SCHOOL_MAP.get(building['name'], building['name']) for building in user_data['buildings']]

  def get_soup(self, url: str):
    r = self.get(url)
    while not r.ok:  # r.status_code == 429
      r = self.get(url)
    print(r.status_code)
    return BeautifulSoup(r.content, features='lxml') if r.ok else None

