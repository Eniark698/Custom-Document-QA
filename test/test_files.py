import requests
import pickle
import json
import os
import time
from dotenv import load_dotenv
load_dotenv()



url = f"http://localhost:{os.environ['PORT']}/upload"
d=[]
pwd=os.getcwd()
for j in range(2):
    for i, el in enumerate(os.listdir(os.path.join(pwd,'few-shots'))):
        payload = {}
        files=[
        ('file',(el,open(os.path.join(pwd,'few-shots', el),'rb'),'application/pdf'))
        ]
        headers = {}

        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        d.append(json.loads(response.text))
        time.sleep(2)
        print(i+1)

with open('list.pkl', 'wb') as f:
    pickle.dump(d, f)

