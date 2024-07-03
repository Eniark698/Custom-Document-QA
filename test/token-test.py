import os
pwd = os.getcwd()
os.environ['HF_HOME'] = os.path.join(pwd, 'cache')
from transformers import AutoTokenizer
from convert_pdf_to_image import extract_text_with_high_quality


# Your input string
input_string = extract_text_with_high_quality('./few-shots/1.pdf')



# Load the tokenizer
tokenizer = AutoTokenizer.from_pretrained("unsloth/llama-3-8b-Instruct-bnb-4bit")


# Tokenize the input string
tokens = tokenizer.encode(input_string)

# Get the number of tokens
num_tokens = len(tokens)

# Print the number of tokens
print(f"Number of tokens: {num_tokens}")

# Define the model's maximum token window (assuming it's 2048 for Llama-3, adjust if different)
max_token_window = 4096

# Check if the number of tokens exceeds the max token window
if num_tokens > max_token_window:
    print(f"Number of tokens exceeds the maximum token window of {max_token_window}.")
else:
   print(f"Number of tokens is within the maximum token window of {max_token_window}.")
