import os
pwd = os.getcwd()
os.environ['HF_HOME'] = os.path.join(pwd, 'cache')
from dotenv import load_dotenv
from os import environ
load_dotenv()
import torch
from transformers import AutoModel, AutoTokenizer, pipeline
from huggingface_hub import login

# Login with your token
login(token=os.environ['HF_TOKEN'])


from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

quantization_config = BitsAndBytesConfig(load_in_4bit=True)

tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-9b-it")
model = AutoModelForCausalLM.from_pretrained(
    "google/gemma-2-9b-it",
    quantization_config=quantization_config,
    device_map="cuda",
    torch_dtype=torch.float16,

    attn_implementation="flash_attention_2"
)

# input_text = "Write me a poem about Machine Learning."
# input_ids = tokenizer(input_text, return_tensors="pt").to("cuda")

# outputs = model.generate(**input_ids)
# print(tokenizer.decode(outputs[0]))

chat = [
    { "role": "user", "content": "Write a json" },
]
prompt = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
inputs = tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt")
outputs = model.generate(input_ids=inputs.to(model.device), max_new_tokens=150)
print(tokenizer.decode(outputs[0]))
