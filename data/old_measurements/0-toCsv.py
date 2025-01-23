from glob import glob
import pandas as pd
import numpy as np
import os
import re

os.chdir(os.path.dirname(__file__))

out_df = pd.DataFrame()

print('Converting all results to csv...')
outfolders = glob('./*spl/')
for outfolder in outfolders:
    name = os.path.dirname(outfolder)
    name = os.path.basename(name).rstrip('spl')
    assert name in ['64','128','256','512','1024'], 'Unexpected folder name \'%s\''%name

    files = {
        'old': sorted(glob(os.path.join(outfolder,'OLDsparta*.txt'))),
        'new': sorted(glob(os.path.join(outfolder,'spartaMcfx*.txt')))
    }
    # assert len(filesOLD) == len(filesNEW), 'Different number of files in %s (%d != %d)'%(outfolder,len(filesOLD),len(filesNEW))
    assert len(files['old']) > 0, 'No files found in %s for OLD plugin'%outfolder
    assert len(files['new']) > 0, 'No files found in %s for NEW plugin'%outfolder

    corename_counters = {}
    for plugin,files in files.items():
        for file in files:
            corename = '_'.join(file.split('_')[:3])
            if corename not in corename_counters:
                corename_counters[corename] = 0
            corename_counters[corename] += 1
            groupname = '_'.join(corename.split('_')[1:])
            
            print('Reading %s'%file)
            with open(file,'r') as f:
                lines = f.readlines()
            assert len(lines) == 1, 'Unexpected number of lines in %s'%file
            # lines[0] should match \d.\d\d
            timestr = lines[0].strip()
            assert re.match(r'\d\.((\d)||(\d\d))',timestr), 'Unexpected first line in file %s: %s'%(file,timestr)

            # Find channels
            channels = file.split('_')[1]
            assert re.match(r'1x\d\dch',channels), 'Unexpected channel format in file %s: %s'%(file,channels)
            regex_extract = r'''1x(?P<channels>\d\d)ch'''
            match = re.match(regex_extract,channels)
            channels = int(match.group('channels'))
            assert channels in [25,16,64,36]

            # irlen_s
            irlen_samples = file.split('_')[2]
            assert 'samples' in irlen_samples
            irlen_samples = int(irlen_samples.rstrip('samples'))
            irlen_s = irlen_samples/48000.0
            # print(file)
            assert round(irlen_s,6) in [0.085312,0.3,0.5,2.0], 'Unexpected irlen_s: %f'%irlen_s
            irlen_s = int(irlen_s) if irlen_s.is_integer() else irlen_s
            irlen_s = str(irlen_s)+'s' if (irlen_s >= 1.0) else str(int(irlen_s*1000))+'ms'
            # print(irlen_s)

            INPUT_TIME_S = 1000.0

            def timestr2seconds(timestr:str):
                # time string is in the format m.ss
                # convert to seconds
                m,s = timestr.split('.')
                m = float(m)
                s = float(s)
                return m*60 + s
            def format_timestr(timestr:str):
                return ':'.join(timestr.split('.'))
            
            timeseconds = timestr2seconds(timestr)
            timestr = format_timestr(timestr)

            # out_df
            # add entry to out_df
            new_row = pd.DataFrame({'plugin': [plugin], 
                                    'channels': [channels], 
                                    'irlen':[irlen_s],
                                    'spl': [name], 
                                    'measure': [corename_counters[corename]],
                                    'file': [file],
                                    'time': [timestr], 
                                    'input_length': [INPUT_TIME_S], 
                                    'X':[INPUT_TIME_S/timeseconds],
                                    'inverse_ratio':[timeseconds/INPUT_TIME_S]
                                    })
            out_df = pd.concat([out_df, new_row], ignore_index=True)

# Sort
out_df = out_df.sort_values(by=['spl','channels','irlen','plugin','measure'])
out_df = out_df.reset_index(drop=True)

corename_ids = {}
lastid=0
for idx in range(len(out_df)):
    corename = '_'.join(out_df.at[idx,'file'].split('_')[1:3])+'_'+out_df.at[idx,'spl']+"spl"
    if corename not in corename_ids:
        lastid += 1
        corename_ids[corename] = lastid
    out_df.at[idx,'id'] = str(corename_ids[corename])
    print('id is %d for %s'%(corename_ids[corename],corename))

# Sort columns so to have id as the first
cols = out_df.columns.tolist()
cols = cols[-1:] + cols[:-1]
out_df = out_df[cols]
    


# print(out_df)
savepath = '../early_measurements_raw.csv'
out_df.to_csv(savepath, index=False)
