import asyncio
import json

from schoology import Student, SchoologySession

s = SchoologySession(input('gimme ur username'), input('gimme ur password'))

data = [Student(student) for student in json.load(open('data.json', 'r'))] # Schoology data


x = [(student, i) for i, student in enumerate(data) if student.school in s.schools]
print(len(x))


loop = asyncio.get_event_loop()
futures = [(loop.run_in_executor(None, s.get_soup, student.url), i) for student, i in x]
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

