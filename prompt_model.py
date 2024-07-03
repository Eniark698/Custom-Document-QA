import os
pwd = os.getcwd()
os.environ['HF_HOME'] = os.path.join(pwd, 'cache')


import time
import gc
import transformers
transformers.logging.set_verbosity_error()
import torch
import json
from json import JSONDecoder

from convert_pdf_to_image import extract_text







def extract_json_from_string(text, decoder=JSONDecoder()):
    """Find JSON objects in text, and yield the decoded JSON data

    Does not attempt to look for JSON arrays, text, or other JSON types outside
    of a parent JSON object.

    """
    pos = 0
    while True:
        match = text.find('{', pos)
        if match == -1:
            break
        try:
            result, index = decoder.raw_decode(text[match:])
            return result
            pos = match + index
        except ValueError:
            pos = match + 1




def reinit():
    
    try:
        del pipeline
    except:
       pass


    gc.collect()
    torch.cuda.synchronize()
    torch.cuda.empty_cache()
    pipeline = transformers.pipeline(
        "text-generation",
    model=model_id,
    model_kwargs={
        "torch_dtype": torch.float16 if torch.cuda.is_available() else torch.float32,
        #  "quantization_config": {"load_in_4bit": True},
        "low_cpu_mem_usage": True,
        "attn_implementation":"flash_attention_2"
    },
    device_map="cuda"
    )
    return pipeline


model_id = "unsloth/llama-3-8b-Instruct-bnb-4bit"







def extract_final_sum_and_period(text,pipeline):
 prompt = f"""
 ###Instruction
 Extract the final(total) sum, begining and end date of reporting period to json from the following text:

 
 ###Data
 \n{text}\n

 ###Example
 Json:
 {{
    "reporting_period_start":"01.01.2024',
    "reporting_period_end":"30.02.2024",
    "final_sum":"10102,51"
 }}



 ###Answer
 Json:"""
 output = pipeline(prompt, max_new_tokens=75)
 
 # Extract the sum from the generated text
 generated_text = output[0]["generated_text"]
 sum_value = generated_text
 return sum_value.replace(prompt,'')








def extract_code_and_name(text,pipeline):

 prompt = f"""
 ###Instruction
 Extract the suppier full name (with general name) and individual tax number of the VAT payer(always has 12 digits, sometimes can be called 'ІПН' on ukrainian) to json from the following text:

 
 ###Data
 \n{text}\n

 ###Example
 Json:
 {{
    "tax_number":"123456789101",
    "full_name":"Товариство з обмеженою відповідальністю 'Берта Груп'"
 }}

 ###Example
 Json:
 {{
    "tax_number":"123456789101",
    "full_name":"Фізична особа підприємець Мозоль Назарій Юрійович"
 }}




 ###Answer
 Json:"""
 output = pipeline(prompt, max_new_tokens=50)
 
 # Extract the sum from the generated text
 generated_text = output[0]["generated_text"]
 sum_value = generated_text
 return sum_value.replace(prompt,'')




















def get_info(text1,text2):
    pipeline=reinit()
    a=extract_final_sum_and_period(text1,pipeline)
    b=extract_code_and_name(text2,pipeline)
    # print(a)
    # print(b)
    sum_and_period_json=extract_json_from_string(a)
    code_and_name_json=extract_json_from_string(b)
    
    d = dict(sum_and_period_json)
    d.update(code_and_name_json)
    if len(d['tax_number'])!=12:
        d['tax_number']=None
    if type(d['final_sum'])=='str' or type(d['final_sum'])==str:
        d['final_sum']=d['final_sum'].replace('.',',')


    try:
        del pipeline
    except:
       pass


    gc.collect()
    torch.cuda.synchronize()
    torch.cuda.empty_cache()


    return d




if __name__=='__main__':
   from convert_pdf_to_image import extract_text
   print(get_info(*extract_text('few-shots/1.pdf')))