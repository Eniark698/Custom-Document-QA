import os
pwd = os.getcwd()
os.environ['HF_HOME'] = os.path.join(pwd, 'cache')
import transformers
import torch
from dotenv import load_dotenv
from os import environ
load_dotenv()
from convert_pdf_to_image import extract_text_from_all_pdfs

# Define your input and output folders
input_folder = 'input'
output_folder = 'output'
temp = 'temp'

# Process all PDFs and get the concatenated text
all_texts = extract_text_from_all_pdfs(input_folder)

# Model setup
model_id = "unsloth/llama-3-8b-Instruct-bnb-4bit"
#model_id = "unsloth/llama-3-70b-Instruct-bnb-4bit"

# Initialize the pipeline for text generation
pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    torch_dtype=torch.float32,  # Force CPU usage
    device=0  # Ensure the model uses the CPU
)

# Function to extract the final sum from the text using the model
def extract_final_sum(text):
   prompt = f"Extract the final sum and month date of reporting period from the following text:\n{text}\nJson:"
   output = pipeline(prompt, max_new_tokens=50)
   
   # Extract the sum from the generated text
   generated_text = output[0]["generated_text"]
   sum_value = generated_text
   return sum_value

# Process each document and find the final sum
for pdf_name, text in all_texts.items():
   summary = extract_final_sum(text)
   print(f"Extracted summary from {pdf_name}: {summary}")