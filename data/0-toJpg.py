from PIL import Image
import os
from glob import glob

os.chdir(os.path.abspath(os.path.dirname(__file__)))

screenshots = sorted(glob('./Screenshot*.png'))
# print(screenshots)
for s in screenshots:
    im = Image.open(s)
    rgb_im = im.convert('RGB')
    rgb_im.save(os.path.splitext(os.path.basename(s))[0]+'.jpg', format='JPEG', subsampling=2, quality=50)	# save as jpg
    # Print rolling counter 
    print(os.path.splitext(os.path.basename(s))[0]+'.jpg', end='\r')