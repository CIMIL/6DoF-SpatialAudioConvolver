from PIL import Image
import os
from glob import glob

os.chdir(os.path.abspath(os.path.dirname(__file__)))

SAVEAS = 'jpg'
CROPPED_FOLDER = "cropped"
os.makedirs(CROPPED_FOLDER,exist_ok=True)

if len(sorted(glob('./Screenshot*.png'))) > 0:
    screenshots = sorted(glob('./Screenshot*.png'))
else:
    screenshots = sorted(glob('./Screenshot*.jpg'))
# print(screenshots)
for s in screenshots:
    fname = os.path.splitext(os.path.join(CROPPED_FOLDER, "crop_"+os.path.basename(s)))[0]
    if SAVEAS == 'jpg' and os.path.exists(fname+'.jpg'):
        continue
    if SAVEAS == 'png' and os.path.exists(fname+'.png'):
        continue

    im = Image.open(s)
    im2 = im.crop((2120,300,1920*1.7,800))
    
    if SAVEAS == 'jpg':
        rgb_im = im2.convert('RGB')
        fname += '.jpg'
        rgb_im.save(fname, format='JPEG', subsampling=2, quality=50)	#
    else:
        fname += '.png'
        im2.save(fname)	# save as jpg
    print(fname, end='\r')