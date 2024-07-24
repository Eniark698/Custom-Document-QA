import os
pwd = os.getcwd()
os.environ['HF_HOME'] = os.path.join(pwd, 'cache')
import transformers

import fitz  
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
from surya.ocr import run_ocr
from surya.model.detection import model
from surya.model.recognition.model import load_model
from surya.model.recognition.processor import load_processor
import torch
import gc
import numpy as np
from traceback import format_exc


langs = ["uk"] 
Image.MAX_IMAGE_PIXELS = 48000000
# os.environ['RECOGNITION_BATCH_SIZE']='128'
# os.environ['DETECTOR_BATCH_SIZE']='18'
# os.environ['ORDER_BATCH_SIZE']='18'


def process_page(page_num, pdf_path):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(page_num)
    pix = page.get_pixmap(dpi=int(os.environ['DPI']))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)



    predictions = run_ocr([img], [langs], det_model, det_processor, rec_model, rec_processor)
    page_text=''
    d=dict(predictions[0])['text_lines']
    for el in d:
        page_text+=str(dict(el)['text'])+'\n'


    supplier_info = None
    if page_num == 0:
        
        supplier_info=''
        for el in d:
            el=dict(el)

            a = np.array(el['polygon'])
            mean=a.mean(axis=0)
            if (mean[1]<1500) and ((mean[0]>2000) or (a[1][0]>2400) and (a[2][0]>2400)):
                supplier_info+=str(el['text'])+' \n'



    return page_num, page_text, supplier_info

def extract_text(pdf_path):
    pdf_document = fitz.open(pdf_path)
    num_pages = len(pdf_document)
    extracted_text = ""
    supplier_info = None

    try:
        global det_model, det_processor, rec_model, rec_processor
        det_processor, det_model = model.load_processor(), model.load_model(device='cuda', dtype=torch.float16)
        rec_model, rec_processor = load_model(device='cuda', dtype=torch.bfloat16), load_processor()
    except:
        print(format_exc())
        try:
            del det_model, det_processor, rec_model, rec_processor
        except:
            pass
        torch.cuda.synchronize()
        with torch.no_grad():
            torch.cuda.empty_cache()
        gc.collect()
        return None




    with ThreadPoolExecutor(max_workers=int(os.environ['PARALLEL_OCR'])) as executor:
        futures = [executor.submit(process_page, page_num, pdf_path) for page_num in range(num_pages)]
        
        for future in as_completed(futures):
            page_num, page_text, page_supplier_info = future.result()
            extracted_text += page_text + " \n"
            if page_num == 0:
                supplier_info = page_supplier_info

    del det_model, det_processor, rec_model, rec_processor
    torch.cuda.synchronize()
    with torch.no_grad():
        torch.cuda.empty_cache()
    gc.collect()
    return extracted_text, supplier_info

if __name__ == '__main__':
    print(extract_text('1.pdf')[1])