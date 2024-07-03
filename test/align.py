# import PIL.Image
# import fast_deskew
# import cv2
# import PIL
# import numpy as np
# INPUT_IMAGE_PATH = "test/photo.jpg"
# result_image, _ = fast_deskew.deskew_image(INPUT_IMAGE_PATH, False) 
# result_image=PIL.Image.fromarray(result_image.astype(np.uint8))

# result_image.save("test/photo1.jpg")

from PIL import Image
from skimage import io
from skimage.transform import rotate
from skimage.color import rgb2gray
from deskew import determine_skew
import numpy as np

Image.MAX_IMAGE_PIXELS = 966178500

def deskew(_img):
    # image = io.imread(_img)
    image = np.array(_img)
    grayscale = rgb2gray(image)
    angle = determine_skew(grayscale)
    rotated = rotate(image, angle, resize=True) * 255
    return rotated.astype(np.uint8)


image=Image.fromarray(deskew(Image.open('test/photo.jpg')))
image.save('test/photo1.jpg')

