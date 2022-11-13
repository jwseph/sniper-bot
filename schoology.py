import requests
from bs4 import BeautifulSoup
import json
import asyncio
from getpass import getpass



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


SCHOOL_URLS = {
    'Mukilteo School District': 'https://www.mukilteoschools.org/',
    'ACES': 'https://www.mukilteoschools.org/ac',
    'Challenger': 'https://www.mukilteoschools.org/ch',
    'Columbia': 'https://www.mukilteoschools.org/co',
    'CBTC': 'https://www.mukilteoschools.org/Page/336',
    'Discovery': 'https://www.mukilteoschools.org/di',
    'ECEAP': 'https://www.mukilteoschools.org/page/12058',
    'Endeavour': 'https://www.mukilteoschools.org/en',
    'Explorer': 'https://www.mukilteoschools.org/ex',
    'Fairmount': 'https://www.mukilteoschools.org/fa',
    'Harbour Pointe': 'https://www.mukilteoschools.org/hp',
    'Horizon': 'https://www.mukilteoschools.org/hz',
    'Kamiak': 'https://www.mukilteoschools.org/ka',
    'Lake Stickney': 'https://www.mukilteoschools.org/ls',
    'Mariner': 'https://www.mukilteoschools.org/ma',
    'Mukilteo Elementary': 'https://www.mukilteoschools.org/me',
    'Special Education': 'https://www.mukilteoschools.org/page/1194',
    'Virtual Academy': 'https://www.mukilteoschools.org/mva',
    'Odyssey': 'https://www.mukilteoschools.org/oe',
    'Olivia Park': 'https://www.mukilteoschools.org/op',
    'Olympic View': 'https://www.mukilteoschools.org/ov',
    'Pathfinder': 'https://www.mukilteoschools.org/pkc',
    'Picnic Point': 'https://www.mukilteoschools.org/pi',
    'Serene Lake': 'https://www.mukilteoschools.org/sl',
    'Sno-Isle Skills Center': 'https://snoisletech.com/',
    'Summer School - Elementary': 'https://www.mukilteoschools.org/Page/12059',
    'Summer School - Middle/High': 'https://www.mukilteoschools.org/Page/12059',
    'Summer School - Skills Center': 'https://www.mukilteoschools.org/Page/12059',
    'Voyager': 'https://www.mukilteoschools.org/vo',
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
    
    def __ior__(self, other):
        if other.name is not None: self.name = other.name
        if other.id is not None: self.id = other.id
        if other.url is not None: self.url = other.url
        self.image = list(dict.fromkeys(self.image) | dict.fromkeys(other.image))
        self.school = list(dict.fromkeys(self.school) | dict.fromkeys(other.school))
        return self
      
    def to_dict(self):
        return {
            'name': self.name,
            'image': self.image,
            'school': self.school,
            'url': self.url,
            'id': self.id
        }
  
    @staticmethod
    def import_students(filename: str) -> dict[str, 'Student']:
        with open(filename, 'r') as f:
            return {sid: Student(student) for sid, student in json.load(f).items()}
    
    @staticmethod
    def export_students(students: dict[str, 'Student'], filename: str):
        with open(filename, 'w') as f:
            json.dump(students, f, indent=4, default=Student.to_dict)



class SchoologySession(requests.Session):

    def __init__(self, email: str, password: str):
        super().__init__()
        schoology_resp = requests.get('https://mukilteo.schoology.com/')
        schoology_soup = BeautifulSoup(schoology_resp.content, features='lxml')
        login_resp = requests.post('https://sts.mukilteo.wednet.edu'+schoology_soup.find('form', {'id': 'loginForm'})['action'], {'UserName': email, 'Password': password})
        login_soup = BeautifulSoup(login_resp.content, features='lxml')
        try:
            login_soup_SAMLResponse = login_soup.find('form').find('input', {'name': 'SAMLResponse'})['value']
        except TypeError:
            raise ValueError(
                'Incorrect user ID or password\n'
                'Maybe you forgot the @mukilteo.wednet.edu?'
            )
        receive_resp = self.post('https://mukilteo.schoology.com/login/saml/receive', {'SAMLResponse': login_soup_SAMLResponse})
        receive_soup = BeautifulSoup(receive_resp.content, features='lxml')
        user_data = json.loads(receive_soup.select_one('#body > script').text.removeprefix('window.siteNavigationUiProps='))['props']['user']
        self.uid = str(user_data['uid'])
        self.schools = {SCHOOL_MAP.get(building['name'], building['name']) for building in user_data['buildings']}


    def get_soup(self, url: str):
        r = self.get(url)
        while not r.ok: #  r.status_code == 429:
            r = self.get(url)
            if not r.ok and r.status_code != 429: print(r.status_code)
            # print(429)
        # print(r.status_code)
        return BeautifulSoup(r.content, features='lxml') if r.ok else None


    async def scrape_basic_info(self, input_file: str='data.json', output_file: str='data2.json'):
        people_url = 'https://mukilteo.schoology.com/search/user?page={page}&s=+++'
        people_soup = self.get_soup(people_url.format(page=0))
        n = int(people_soup.select_one('#main-inner > div.results-counter').text.removesuffix('results').strip().split(' ')[-1])
        print(f"Scraping {n} students' basic info")

        loop = asyncio.get_event_loop()
        futures = [loop.run_in_executor(None, self.get_soup, people_url.format(page=p_i)) for p_i in range(-(-n//10))]
        
        students = Student.import_students(input_file)

        for future in futures:
            soup = await future
            
            for student_soup in soup.select('#main-inner > div.item-list > ul > li.search-summary > div'):
                uid = student_soup.select_one('div.item-title > a')['href'][::-1].split('/', 1)[0][::-1]

                new_student = Student(soup=student_soup)
                print(f'{("["+new_student.school[-1]+"]").rjust(36)} {new_student.name}')

                if uid in students:
                    students[uid] |= new_student
                    continue

                students[uid] = new_student
        
        Student.export_students(students, output_file)
    

    async def scrape_ids(self, input_file: str='data.json', output_file: str='data2.json'):
        students = Student.import_students(input_file)

        x = [(uid, student) for uid, student in students.items() if student.school[-1] in self.schools and student.id == None]
        print(f"Scraping {len(x)} students' ids from {', '.join(s.schools[-1])}")

        loop = asyncio.get_event_loop()
        futures = [(uid, loop.run_in_executor(None, self.get_soup, student.url)) for uid, student in x]

        for uid, future in futures:
            soup = await future
            
            if soup is None:
                print('No soup for', students[uid].name)
                continue
        
            email_box = soup.select_one('.admin-val.email a')
            if email_box is None: continue

            email = email_box['href']
            if not email.endswith('@mukilteo.wednet.edu'): continue
            
            students[uid].id = email[7:-20]
            print(f'{("["+students[uid].id+"]").rjust(36)} {students[uid].name}')

        Student.export_students(students, output_file)



if __name__ == '__main__':
    import time
    import nest_asyncio
    nest_asyncio.apply()
    
    email = input('Student ID: ')+'@mukilteo.wednet.edu'
    password = getpass('Password: ')
    s = SchoologySession(email, password)

    f = s.scrape_basic_info if input('(1) Scrape basic info or (2) Scrape ids: ').strip() == '1' else s.scrape_ids

    input_file, output_file = input('Input file name: '), input('Output file name: ')

    start_time = time.time()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(f(input_file, output_file))

    print(f'Finished in {time.time()-start_time}s')