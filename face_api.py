# TODO: Use multiple FaceSets for >5 results and >10k face_tokens - combine using confidence

import aiohttp
import asyncio
import os
import json

from dotenv import load_dotenv
load_dotenv()


class FaceAPI:
    def __init__(
        self,
        api_key=os.getenv('FACEPP_API_KEY'),
        api_secret=os.getenv('FACEPP_API_SECRET'),
        api_endpoint='https://api-us.faceplusplus.com/facepp/v3/'
    ):
        self.auth_params = {'api_key': api_key, 'api_secret': api_secret}
        self.base_endpoint = api_endpoint
        self.session = aiohttp.ClientSession()
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_value, tb):
        await self.session.close()
    def post(self, endpoint: str, params: dict = {}):
        return self.session.post(
            self.base_endpoint+endpoint,
            params=self.auth_params|params,
        )
    
    async def upload_images(self, schools={'Kamiak', 'Mariner'}):
        '''Uploads the images in the /images folder into a new FaceSet'''

        student_ids = {}  # Key is face_token
        q = []

        for student_id, student in json.load(open('data.json')).items():
            if len(set(student['school'])&schools) == 0: continue
            for image_url in student['image']:
                if not image_url[:-11].endswith('.jpg'): continue
                q.append((student_id, self.upload_image(image_url)))
        
        # Create faceset
        resp = await self.post('faceset/create')
        faceset_token = (await resp.json())['faceset_token']

        while q:
            face_tokens = []
            while q and len(face_tokens) < 5:
                student_id, promise = q.pop(0)
                face_token = await promise
                if not face_token: continue
                student_ids[face_token] = student_id
                face_tokens.append(face_token)
            await self.add_face(faceset_token, face_tokens)
        
        json.dump(student_ids, open('student_ids.json', 'w'))
        return faceset_token

    async def upload_image(self, image_url: str) -> str|None:
        resp = await self.post('detect', {'image_url': image_url})
        while resp.status == 403:
            resp = await self.post('detect', {'image_url': image_url})
        print(resp.status)
        if not resp.ok: return
        data = await resp.json()
        if len(data['faces']) != 1: return
        return data['faces'][0]['face_token']
    
    async def add_face(self, faceset_token: str, face_tokens: list[str]):
        assert len(face_tokens) <= 5
        resp = await self.post('faceset/addface', {
            'faceset_token': faceset_token,
            'face_tokens': ','.join(face_tokens),
        })
    
    async def search_face(self, image_url: str, faceset_token: str, *, k: int = 5) -> dict[str, float]:
        '''Searches for a face in a FaceSet'''
        resp = await self.post('search', {
            'image_url': image_url,
            'faceset_token': faceset_token,
            'return_result_count': k,
        })
        print(resp.status)
        assert resp.ok
        data = await resp.json()

        student_ids = json.load(open('student_ids.json'))
        results = {}
        for result in data['results']:
            student_id = student_ids[result['face_token']]
            if student_id in results: continue
            results[student_id] = result['confidence']            
        return results


async def main():
    async with FaceAPI() as fa:
        # faceset_token = await fa.upload_images()
        faceset_token = '6b4ad750d4143ce758a395336a553085'
        print('FaceSet token:', faceset_token)
        results = await fa.search_face('https://cdn.discordapp.com/attachments/931711737353371699/1074076770879414342/IMG_1228.jpg', faceset_token)
        students = json.load(open('data.json'))
        for student_id, confidence in results:
            name = students[student_id]['name']
            print(f'{confidence}% | {name}')

if __name__ == '__main__':
    asyncio.run(main())