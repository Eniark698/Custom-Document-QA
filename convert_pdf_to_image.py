import fitz  
from PIL import Image
import pytesseract
import numpy as np
import fast_deskew
import cv2
from concurrent.futures import ThreadPoolExecutor, as_completed

Image.MAX_IMAGE_PIXELS = 48000000

def process_page(page_num, pdf_path):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(page_num)
    pix = page.get_pixmap(dpi=600)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
    img = np.ascontiguousarray(img[..., [2, 1, 0]], dtype=np.uint8)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Deskew image
    img, _ = fast_deskew.deskew_image(img, True)
    img = Image.fromarray(img.astype(np.uint8))

    page_text = pytesseract.image_to_string(img, lang='ukr', config='--psm 4 --oem 1')
    
    supplier_info = None
    if page_num == 0:
        width, height = pix.width, pix.height
        left = 5 * width // 10
        upper = 0
        right = width
        lower = height // 2
        top_right_corner = img.crop((left, upper, right, lower))
        supplier_info = pytesseract.image_to_string(top_right_corner, lang='ukr+eng', config='--psm 4 --oem 1')

    return page_num, page_text, supplier_info

def extract_text(pdf_path):
    pdf_document = fitz.open(pdf_path)
    num_pages = len(pdf_document)
    extracted_text = ""
    supplier_info = None

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_page, page_num, pdf_path) for page_num in range(num_pages)]
        
        for future in as_completed(futures):
            page_num, page_text, page_supplier_info = future.result()
            extracted_text += page_text + "\n"
            if page_num == 0:
                supplier_info = page_supplier_info

    return extracted_text, supplier_info

if __name__ == '__main__':
   print(extract_text('few-shots/1.pdf')[0])