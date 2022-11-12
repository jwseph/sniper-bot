import asyncio
import json
import os

from schoology import Student, SchoologySession


s = SchoologySession(os.environ['MSDUSERNAME'], os.environ['MSDPASSWORD'])

async def main():
  n = 20310
  #n = 19755
  loop = asyncio.get_event_loop()
  futures = [loop.run_in_executor(None, s.get_soup, f'https://mukilteo.schoology.com/search/user?page={p}&s=+++') for p in range(-(-n//10))]

  with open('data.json', 'r') as f:
    students = {sid: Student(student) for sid, student in json.load(f).items()}

  for future in futures:
    soup = await future
    
    for student in soup.select('#main-inner > div.item-list > ul > li.search-summary > div'):
      sid = student.select_one('div.item-title > a')['href'][::-1].split('/', 1)[0][::-1]
      if sid in students:
        students[sid].update(soup=student)
      else:
        students[sid] = Student(soup=student)
  
  json.dump(students, open('data2.json', 'w'), indent=2, default=Student.to_dict)
  # print(json.dumps(students, indent=2, default=to_dict))

# await main()
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())