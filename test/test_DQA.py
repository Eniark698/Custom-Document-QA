import os
pwd = os.getcwd()
os.environ['HF_HOME'] = os.path.join(pwd, 'cache')

from transformers import pipeline
from PIL import Image

pipe = pipeline("document-question-answering", model="naver-clova-ix/donut-base-finetuned-docvqa")

question = "What is the purchase amount?"
image = Image.open("test/1.png")

print(pipe(image=image, question=question))

## [{'answer': '20,000$'}]
