import fitz  
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
from surya.ocr import run_ocr
from surya.model.detection import segformer
from surya.model.recognition.model import load_model
from surya.model.recognition.processor import load_processor
import torch

langs = ["uk"] 
det_processor, det_model = segformer.load_processor(), segformer.load_model()
rec_model, rec_processor = load_model(), load_processor()

Image.MAX_IMAGE_PIXELS = 48000000
print('Ready')




def process_page(page_num, pdf_path):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(page_num)
    pix = page.get_pixmap(dpi=500)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)




    predictions = run_ocr([img], [langs], det_model, det_processor, rec_model, rec_processor)
    page_text=''
    d=dict(predictions[0])['text_lines']
    for el in d:
        page_text+=str(dict(el)['text'])+'\n'


    supplier_info = None
    if page_num == 0:
        width, height = pix.width, pix.height
        left = width // 2
        upper = 0
        right = width
        lower = height // 2
        top_right_corner = img.crop((left, upper, right, lower))



        predictions_supp = run_ocr([top_right_corner], [langs], det_model, det_processor, rec_model, rec_processor)
        supplier_info=''
        d1=dict(predictions_supp[0])['text_lines']
        for el in d1:
            supplier_info+=str(dict(el)['text'])+'\n'



       

    return page_num, page_text, supplier_info

def extract_text(pdf_path):
    pdf_document = fitz.open(pdf_path)
    num_pages = len(pdf_document)
    extracted_text = ""
    supplier_info = None

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(process_page, page_num, pdf_path) for page_num in range(num_pages)]
        
        for future in as_completed(futures):
            page_num, page_text, page_supplier_info = future.result()
            extracted_text += page_text + "\n"
            if page_num == 0:
                supplier_info = page_supplier_info
    torch.cuda.synchronize()
    torch.cuda.empty_cache()
    return extracted_text, supplier_info

if __name__ == '__main__':
   print(extract_text('few-shots/1.pdf')[0])