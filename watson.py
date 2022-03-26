import requests

url = 'https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/5fc7d4c8-423d-46a0-a292-7972a7876104'
apikey = '9eyPYz8ZBEuJUSaNXiFMKQgMLBcDbSKFszpJYWlL3Ipj'

def analyze(text):
  return requests.post(
    f'{url}/v1/analyze?version=2021-08-01',
    auth=('apikey', apikey),
    json={
      'language': 'en',
      'text': text,
      "features": {
        "classifications": {
          "model": "tone-classifications-en-v1"
        }
      }
    }
  ).json()

if __name__ == '__main__':
  import json
  while True:
    print(json.dumps(analyze(input('> ')), indent=2))