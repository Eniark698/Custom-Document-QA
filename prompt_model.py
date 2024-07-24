import os
pwd = os.getcwd()
os.environ['HF_HOME'] = os.path.join(pwd, 'cache')
from read_file import extract_text


from llama_cpp import Llama
from pprint import pprint
import time
import torch
from json import JSONDecoder
import gc
from datetime import datetime
import locale
locale.setlocale(locale.LC_TIME, 'uk_UA.UTF-8')
from traceback import format_exc
import re

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
            result, _ = decoder.raw_decode(text[match:])
            return result
        except ValueError:
            pos = match + 1



def convert_date(date_str):
    try:
        datetime.strptime(date_str, '%d.%m.%Y')
        return date_str
    except ValueError:
        pass

    date_str = date_str.replace(' року', '')

    # Parse the date string to a datetime object
    date_obj = datetime.strptime(date_str, '%d %B %Y')

    # Format the datetime object to the desired format
    formatted_date = date_obj.strftime('%d.%m.%Y')

    return formatted_date




def extract_final_sum_and_period(text):
    prompt = f"""
    ###Instruction
    Extract the final(total) cost of services to be paid by the customer in favor of the executed, to the nearest hundredth (cents of UAH, on ukrainian its 'копійка' or 'коп.', try not to skip any digit of given number), 
    begining and end date of reporting period(each period field has to be in format dd.MM.yyyy) to json from the following text:

    
    ###Example
    Json:
    {{
        "reporting_period_start":"01.01.2024',
        "reporting_period_end":"30.02.2024",
        "final_sum":"10102,51"
    }}

    ###Data
    \n{text}\n

    



    ###Answer
    Json:"""
    output = llm(
        prompt,
        max_tokens=100) 

    return extract_json_from_string(output['choices'][0]['text'])










def extract_code_and_name(text):
    
    prompt = f"""
    ###Instruction
    There will be two ways of what you should do, based on input data (on ukrainian): 
    supplier from this text can be 'Фізична особа-підприємець' or in short 'ФОП' чи 'Товариство з обмеженою відповідальністю'(in some cases 'Приватне підприємство'), or in short 'ТзОВ'. 
    In both cases you need to extract the suppier full name with general name, Unified State Register of Enterprises and Organisations of Ukraine of the VAT payer, in short USRoEaOoU(on ukrainian called 'EDRPOU'), code 
    and individual tax number, in short 'ITN', of the VAT payer(sometimes can be called 'ІПН', or 'Індивідуальний податковий код' on ukrainian). In fist case ('Фізична особа-підприємець'), 'EDRPOU'(if exists) will be equal to 'ІПН', and length of 'ІПН' will be 10
    , in second case ('Товариство з обмеженою відповідальністю'), length of 'ІПН' will be 12, and length of 'EDRPOU' will be 7 or 8 or 12(if 7 then add one zero to the begining, if 12 then must be equal to 'ІПН').
    If you can not find 'ITN' code, try to find nearest 10 or 12 digit number. If you can not find 'USRoEaOoU' code, try to find nearest 7,8 or 10 digit number. For full name filed extract whole name with general name
    Extract this info from the following text:

    


    ###Example
    Json:
    {{
        "full_name":"Товариство з обмеженою відповідальністю 'Берта Груп'",
        "USRoEaOoU":"12345678",
        "ITN":"123456789010"
    }}

    ###Example
    Json:
    {{  
        "full_name":"ФІЗИЧНА ОСОБА-ПІДПРИЄМЕЦЬ МОЗОЛЬ НАЗАРІЙ ЮРІЙОВИЧ",
        "USRoEaOoU":"1234567890",
        "ITN":"1234567890"
    }}



    
    ###Data
    \n{text}\n



    ###Answer
    Json:"""
    output = llm(
     
        prompt,
        max_tokens=200) 
    
    return extract_json_from_string(output['choices'][0]['text'])


def get_info(text1, text2):
    global llm
    llm = Llama(
        # model_path="./cache/gemma-2-9b-it-Q8_0.gguf",
        model_path="./cache/gemma-2-9b-it-Q6_K_L.gguf",
        # n_gpu_layers=-1, 
        n_ctx=8192, 
        verbose=False,
        temperature=0.01,
        use_mlock=True,
    )   




    try:
        d = dict(extract_final_sum_and_period(text1))
        b=extract_code_and_name(text2)
        if b==None:
            raise Exception
        d.update(b)
    except:
        print(format_exc())
        del llm
        torch.cuda.synchronize()
        with torch.no_grad():
            torch.cuda.empty_cache()
        gc.collect()
        return {}



    d = {key: str(val) for key, val in d.items()} 


    if d['USRoEaOoU'] in ['12345678','1234567890', ''] or len(d['USRoEaOoU']) not in [7,8,9,10,12] :
        d['USRoEaOoU']=None

    if d['USRoEaOoU']!=None and len(d['ITN']) not in [10,12] and len(d['USRoEaOoU'])==8:
        d['ITN']=d['USRoEaOoU'][:-1]+d['ITN'][6:]

    if d['USRoEaOoU']!=None and len(d['USRoEaOoU'])==12 and d['ITN'] in d['USRoEaOoU'] : 
        d['ITN']=d['USRoEaOoU']

    if d['ITN'] in ['1234567890','123456789010', ''] or len(d['ITN']) not in [10,12] :
        d['ITN']=None
        
    d['reporting_period_end']=convert_date(d['reporting_period_end'])
    d['reporting_period_start']=convert_date(d['reporting_period_start'])



    d['full_name']=d['full_name'].replace('\n',' ').strip()


    if type(d['final_sum'])=='str' or type(d['final_sum'])==str:
        d['final_sum']=d['final_sum'].replace('.',',')


    if d['final_sum']!= None:
        pattern = r'^\d+,\d{2}$'
        if re.match(pattern, d['final_sum'].strip()):
            pass
        else:
            return d['final_sum']==None


    del llm
    torch.cuda.synchronize()
    with torch.no_grad():
        torch.cuda.empty_cache()
    gc.collect()
    return d









if __name__=='__main__':
    from read_file import extract_text
    # pprint(get_info(*extract_text('64e5af73-5205-408f-bee8-209f2dd0a13a.pdf')))
    pprint(get_info(*extract_text('7224ba5b-4ac8-4543-ad8e-47cdb950607a.pdf')))

    