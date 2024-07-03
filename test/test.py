from transformers import BigBirdTokenizer, BigBirdForQuestionAnswering
import torch
from convert_pdf_to_image import extract_text_from_all_pdfs

# Process all PDFs and get the concatenated text
all_texts = extract_text_from_all_pdfs('input')['1.pdf']

# Load the tokenizer and model
tokenizer = BigBirdTokenizer.from_pretrained('google/bigbird-roberta-base')
model = BigBirdForQuestionAnswering.from_pretrained('google/bigbird-roberta-base')

# Define a function to extract key information from a document
def extract_info(document, question, max_length=4096):
    # Tokenize the document and the question
   inputs = tokenizer(question, document, return_tensors='pt', max_length=max_length, truncation=True)
   
   # Ensure inputs fit within the model's context window
   input_ids = inputs['input_ids']
   attention_mask = inputs['attention_mask']
   
   # Perform inference
   outputs = model(input_ids, attention_mask=attention_mask)
   start_scores = outputs.start_logits
   end_scores = outputs.end_logits
   
   # Extract the answer
   start_index = torch.argmax(start_scores)
   end_index = torch.argmax(end_scores) + 1
   answer_tokens = tokenizer.convert_ids_to_tokens(input_ids[0][start_index:end_index].tolist())
   answer = tokenizer.convert_tokens_to_string(answer_tokens)
   
   return answer

# Define your documents and the questions
documents = [
   all_texts,
 
   # Add more documents as needed
]
questions = [
   "What is the final price?",
   "What is the reporting date?",
   # Add more questions as needed
]

# Process each document and extract the required information
for doc in documents:
   print(f"Processing document: {doc[:100]}...") # Print the first 100 characters for context
   for question in questions:
       try:
           answer = extract_info(doc, question)
           print(f"Question: {question}\nAnswer: {answer}\n")
       except ValueError as e:
           print(e)
           break