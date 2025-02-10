##
# This script generates different variants of the Tindari SOFA for testing purposes
#
# It calls the script 2-modify_SOFA.py repeatedly to generate different SOFA files
##

import os

channel_numbers = [16,36,64]
ir_lengths_seconds = [0.1,0.2,0.5,1,2,5,10]
SAMPLE_RATE = 48000
SOFAFILE = './tindari_drop.sofa'

os.chdir(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.abspath("2-modify_SOFA.py")
OUTFOLDER = "out_tindari_variants"
os.makedirs(OUTFOLDER,exist_ok=True)

command = lambda id,ch, length_samp, lengthstring: f"python {SCRIPT_PATH} -i {SOFAFILE} -o ./{OUTFOLDER}/{id}_{ch}ch_{lengthstring}_tindari_drop.sofa -ch {ch} -ir {length_samp}"

id = 1
test_x = []
test_y = []
test_label = []
for idch,ch in enumerate(channel_numbers):
    for length in ir_lengths_seconds:
        length_samp = int(length*SAMPLE_RATE)

        if length<1:
            lengthstring = f"{int(length*1000)}ms"
        else:
            lengthstring = f"{length}s"

        strid = str(id).zfill(2)
        print(command(strid,ch,length_samp,lengthstring))
        os.system(command(strid,ch,length_samp,lengthstring))

        id+=1


