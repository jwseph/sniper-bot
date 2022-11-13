import asyncio
from getpass import getpass

from schoology import Student, SchoologySession

s = SchoologySession(input('gimme ur username')+'@mukilteo.wednet.edu', getpass('gimme ur password'))

data = Student.import_students('data.json')

x = [(sid, student) for sid, student in data.items() if student.school[-1] in s.schools and student.id == None]
print(len(x))

loop = asyncio.get_event_loop()
futures = [(sid, loop.run_in_executor(None, s.get_soup, student.url)) for sid, student in x]
for sid, future in futures:
  soup = await future
  if soup is None:
    print('No soup for', data[sid].name)
    continue
  email_box = soup.select_one('.admin-val.email a')
  if email_box is None: continue
  email = email_box['href']
  if not email.endswith('@mukilteo.wednet.edu'): continue
  print(f'[{email[7:-20]}] {data[sid].name}')
  data[sid].id = email[7:-20]


Student.export_students(data, 'data3.json')