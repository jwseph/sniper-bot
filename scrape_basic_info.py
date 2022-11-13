import asyncio
from getpass import getpass

from schoology import Student, SchoologySession


PEOPLE_URL = 'https://mukilteo.schoology.com/search/user?page={page}&s=+++'
s = SchoologySession(f'{input("Student ID: ")}@mukilteo.wednet.edu', getpass())


async def main():
    people_soup = s.get_soup(PEOPLE_URL.format(page=0))
    n = int(people_soup.select_one('#main-inner > div.results-counter').text.removesuffix('results').strip().split(' ')[-1])
    
    loop = asyncio.get_event_loop()
    futures = [loop.run_in_executor(None, s.get_soup, PEOPLE_URL.format(page=p_i)) for p_i in range(-(-n//10))]

    students = Student.import_students('data.json')

    for future in futures:
        soup = await future
        
        for student in soup.select('#main-inner > div.item-list > ul > li.search-summary > div'):
            sid = student.select_one('div.item-title > a')['href'][::-1].split('/', 1)[0][::-1]
            if sid in students:
                students[sid].update(soup=student)
            else:
                students[sid] = Student(soup=student)
  
    Student.export_students(students, 'data2.json')


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())