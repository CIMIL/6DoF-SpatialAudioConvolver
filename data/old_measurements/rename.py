from glob import glob
import os

os.chdir(os.path.dirname(__file__))

splFolders = glob('./*spl/')

renamed = 0
for folder in splFolders:
    files = glob(os.path.join(folder,'*.txt'))
    for file in files:
        if '36ch36' in file:
            os.rename(file,file.replace('36ch36','IR_1x36ch_4095samples_'))
            renamed += 1

if renamed == 0:
    print('Warning: No files renamed')
else:
    print('Renamed '+str(renamed)+' files')