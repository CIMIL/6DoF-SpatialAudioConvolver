import os
import pandas as pd
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import tempfile



DATA_FNAME = ['measures_64spl_raw.csv',
              'measures_256spl_raw.csv',
              'measures_1024spl_raw.csv',
            #   'early_measurements_raw.csv',
              'measures_MOD_old_Plugin_raw_64.csv',
              'measures_MOD_old_Plugin_raw_256.csv']
# DATA_FNAME = ['measures_MOD_old_Plugin_raw_64.csv','measures_MOD_old_Plugin_raw_256.csv']
RELDIFF = 0.14
# RELDIFF = 0.29
INPUT_LENGTH_TIMES = [0.5*60, # 30 seconds
                      1*60,   # 1  minute
                      5*60,   # 5  minutes
                      10*60]  # 10 minutes

def get_input_length(data, input_length_times, verbose=False,rel_diff = RELDIFF, sourcecolumn='screenshot'):
    printVerbose = print if verbose else lambda *args, **kwargs: None
    res = []
    
    for idx in data.index:
        time = data.at[idx, 'time']
        x = data.at[idx, 'X'].astype(float)
        expected_time = time * x

        closest_input_time = None
        closest_input_time_diff = None
        printVerbose('\nTrying to find input time match for %.1f  (%s)' % (expected_time,data.at[idx, sourcecolumn]))
        for input_time in INPUT_LENGTH_TIMES:
            diff = abs(input_time - expected_time)
            printVerbose("diff = ", diff, end=' ')
            if closest_input_time is None or diff < closest_input_time_diff:
                printVerbose('<-- This is the closest', end=' ')
                closest_input_time = input_time
                closest_input_time_diff = diff
            printVerbose()
        del diff 
        cur_rel_diff = rel_diff if data.at[idx,'X'] > 0.2 else 0.49
        cur_rel_diff = cur_rel_diff if data.at[idx,'time'] > 10 else 0.16
        if closest_input_time_diff > cur_rel_diff*expected_time:
            print('time',time)
            print('x',x)
            print('cur_rel_diff',cur_rel_diff)
            print('expected_time',expected_time)
            print('closest_input_time_diff',closest_input_time_diff)
            print('cur_rel_diff*expected_time',cur_rel_diff*expected_time)
            raise ValueError('Expected time (%.1f) is too far from any input time (%.1f) for measure \'%s\'' % (expected_time,closest_input_time_diff,data.at[idx,sourcecolumn]))

        printVerbose(f'time = {time}, x = {x}, expected_time = {expected_time:.1f} (%d:%d)'%(expected_time//60,expected_time%60))
        res.append(closest_input_time)
    return res


for data_fname in DATA_FNAME:
    DATA_PATH = os.path.abspath(os.path.join('..', 'data',data_fname))
    assert os.path.exists(DATA_PATH), 'Data file \"%s\" not found'%(DATA_PATH)
    print('Cleaning data file:', DATA_PATH)

    with open (DATA_PATH, 'r') as f:
        datalines = f.readlines()
        for i in range(len(datalines)):
            datalines[i] = datalines[i].replace(' elapsed:','')
            datalines[i] = datalines[i].replace(' remaining:','')
            datalines[i] = datalines[i].replace(' time:','')
            datalines[i] = datalines[i].replace('elapsed:','')
            datalines[i] = datalines[i].replace('remaining:','')
            datalines[i] = datalines[i].replace('time:','')

            
            datalines[i] = datalines[i].replace(', ',',')
            datalines[i] = datalines[i].replace(' , ',',')
            datalines[i] = datalines[i].replace(' ,',',')

    tempfilen = tempfile.NamedTemporaryFile(delete=False)
    with open(tempfilen.name, 'w') as f:
        f.writelines(datalines)
    print (tempfilen.name)

    # load data with pandas
    data = pd.read_csv(tempfilen.name, engine='python')

    # Take column "irlen" and convert [\d]+ms to float/1000, and [\d]+s to float
    for idx in data.index:
        irlen = data.at[idx, 'irlen']
        if 'ms' in irlen:
            data.at[idx, 'irlen'] = float(irlen.replace('ms',''))/1000
        elif 's' in irlen:
            data.at[idx, 'irlen'] = float(irlen.replace('s',''))
        else:
            raise ValueError('irlen is not in ms or s format')
    # rename column irlen to irlen_s
    data = data.rename(columns={'irlen':'irlen_s'})


    # DF columns elapsed, remaining, and time are in the format mm:ss and as strings, conver to seconds
    # and store as floats
    for idx in data.index:
        elapsed = data.at[idx, 'elapsed'] if "elapsed" in data.columns else None
        remaining = data.at[idx, 'remaining'] if 'remaining' in data.columns else None
        time = data.at[idx, 'time']
        
        if not pd.isna(elapsed) and elapsed != "":
            elapsed = elapsed.split(':')
            try:
                elapsed = float(elapsed[0])*60 + float(elapsed[1])
            
            except IndexError:
                print('Index',idx, 'elapsedstr', elapsed)
            data.at[idx, 'elapsed'] = elapsed
        if not pd.isna(remaining) and remaining != "":
            remaining = remaining.split(':')
            remaining = float(remaining[0])*60 + float(remaining[1])
            data.at[idx, 'remaining'] = remaining
        if not pd.isna(time) and time != "":
            time = time.split(':')
            time = float(time[0])*60 + float(time[1])
            data.at[idx, 'time'] = time

    # for all lines that have 'elapsed' != "" ensure that also remainig is not ""
    # for all lines that have 'remaining' != "" ensure that also elapsed is not ""
    # in both cases, ensure that 'time' is ""
    
    for idx in data.index:
        elapsed = data.at[idx, 'elapsed'] if "elapsed" in data.columns else None
        remaining = data.at[idx, 'remaining'] if 'remaining' in data.columns else None
        time = data.at[idx, 'time']
        
        # # Check conditions
        if not pd.isna(elapsed) and elapsed != "":
            assert not pd.isna(remaining), 'Remaining is empty, but %s' % str(remaining)
            assert pd.isna(time), 'Time is not empty, but %s' % str(time)
        if not pd.isna(remaining) and remaining != "":
            assert not pd.isna(elapsed), 'Elapsed is empty, but %s' % str(elapsed)
            assert pd.isna(time), 'Time is not empty, but %s' % str(time)

        # Sum of elapsed and remaining should be placed in time
        if not pd.isna(elapsed) and not pd.isna(remaining):
            data.at[idx, 'time'] = elapsed + remaining
    
    # drop columns elapsed and remaining
    if 'elapsed' in data.columns:
        data = data.drop(columns=['elapsed'])
    if 'remaining' in data.columns:
        data = data.drop(columns=['remaining'])

    # print(data.head())
    if 'screenshot' in data.columns:
        sourcecolumn = 'screenshot'
    elif 'file' in data.columns:
        sourcecolumn = 'file'
    
    if 'input_length' not in data.columns:

        assert data['spl'].nunique() == 1
        print("data.at[0,'spl'] = ",data.at[0,'spl'])
        if data.at[0,'spl'] == "1024":
            print(data[(data['plugin']=='new') &\
                        (data['channels']==36) &\
                        (data['irlen_s']==10) &\
                        (data['spl']==1024)])
            exit()

        input_length_s = get_input_length(data, INPUT_LENGTH_TIMES, verbose=False,sourcecolumn=sourcecolumn)


        # For short render times, the render time itself is less precise than Real-time ratio (X), so we recompute time based on that
        # (for < RECOMPUTE_S_THRESH seconds)
        # Also, we do not correct for super low real-time ratios (X) (<0.6)

        RECOMPUTE_S_THRESH = 130
        RECOMPUTE_TOLERANCE_REL = 0.109
        for idx in data.index:
            time_logged = data.at[idx, 'time']
            data.at[idx, 'input_length'] = input_length_s[idx]

            if time_logged <= RECOMPUTE_S_THRESH and data.at[idx, 'X'] >= 0.6:
                # print(data.at[idx, 'screenshot'])
                # print('time_logged: %d (%d:%d)'%(time_logged,time_logged//60,time_logged%60))
                recomputed_time = input_length_s[idx]/data.at[idx, 'X']
                # print('time_re_calculated: %f (%d:%f)'%(recompute_time,recompute_time//60,recompute_time%60))

                RECOMPUTE_TOLERANCE = RECOMPUTE_TOLERANCE_REL*time_logged
                if (abs(time_logged-recomputed_time) <= RECOMPUTE_TOLERANCE) or (data.at[idx, 'X'] < 1.0) or (data.at[idx, 'time'] < 10):
                    # print('OK')
                    data.at[idx, 'time'] = round(recomputed_time,2)
                else:
                    print("Tolerance was %.1f%% (%.3f)"%(RECOMPUTE_TOLERANCE_REL*100,RECOMPUTE_TOLERANCE))
                    raise ValueError('Time logged for exp \'%s\' (%d) is different from recomputed time (%d)'%(data.at[idx,sourcecolumn],time_logged,recomputed_time))
                # print()
            else:
                pass


        for idx in data.index:
            time = data.at[idx, 'time']
            ratio = data.at[idx, 'X']
            input_length = data.at[idx, 'input_length']

            # print('time = %.3f (%d:%d), input_length = %d, ratio = %.2f, expected_ratio = %.2f' % (time,time//60,time%60,input_length,ratio,input_length/time))
            ratioerror = abs(ratio - input_length/time)
            assert ratioerror < 0.1, 'Ratio error is too high: %.2f' % ratioerror


    # We sent the inverse ratio (WHICH IS THE actual REAL-TIME FACTOR) to time/input_length
    # As 1/X is not as precise for offline renderings due to its precision fixed to 1 decimal place by Reaper
    for idx in data.index:
        # ratio = data.at[idx, 'X']
        # data.at[idx, 'inverse_ratio'] = 1/ratio
        data.at[idx, 'inverse_ratio'] = data.at[idx, 'time']/data.at[idx, 'input_length']
        assert data.at[idx, 'inverse_ratio'] > 0, 'Inverse ratio is negative'
        REL_TOLERANCE = 0.315
        # ensure that the inverse ratio is within 10% of 1/X
        # print(f"data.at[idx, 'inverse_ratio'] = {data.at[idx, 'inverse_ratio']:.2f}, 1/data.at[idx, 'X'] = {1/data.at[idx, 'X']:.2f}")
        # print(f"relative distance = {abs(data.at[idx, 'inverse_ratio'] - 1/data.at[idx, 'X'])/(1/data.at[idx, 'X']):.2f}")
        assert abs(data.at[idx, 'inverse_ratio'] - 1/data.at[idx, 'X']) < REL_TOLERANCE*1/data.at[idx, 'X'], 'Inverse ratio is too far from 1/X'


        
    DATA_FNAME_CLEAN = os.path.basename(DATA_PATH.replace('raw','clean'))
    
    data.to_csv(DATA_FNAME_CLEAN, index=False)
    # print('Overwriting',tempfilen.name)
    # print (data.head())
    print('Data cleaned and saved to', DATA_FNAME_CLEAN)



    # Now delete time and input_length, and average ratio (X) and inverse_ratio over the same id and plugin fields, and keep standard deviation column for each
    data = data.drop(columns=['time', 'input_length'])
    data = data.groupby(['id','plugin']).agg({'channels':'first','irlen_s':'first','spl':'first', 'X':['mean','std'],'inverse_ratio':['mean','std']})
    data.columns = ['_'.join(col).strip() for col in data.columns.values]
    data.columns = [col.replace('_first','') for col in data.columns.values]
    data = data.reset_index()
    # print(data.head())

    for idx in data.index:
        relative_tolerance = 0.1185
        tolerance = relative_tolerance * data.at[idx, ('X_mean')]
        # Print row idx
        # print(print(data.iloc[[idx]]))
        assert data.at[idx, ('X_std')] <= tolerance, 'Standard deviation of X is too high (>%.1f%% (>%.1f)): %.2f (for mean:%.1f, id:%d, plugin:%s) file %s'  % (relative_tolerance*100.0,tolerance,data.at[idx, ('X_std')], data.at[idx, ('X_mean')], data.at[idx, ('id')], data.at[idx, ('plugin')],DATA_FNAME_CLEAN)

    DATA_FNAME_AVERAGED = DATA_FNAME_CLEAN.replace('clean','averaged')
    data.to_csv(DATA_FNAME_AVERAGED, index=False)
    print('Data averaged and saved to', DATA_FNAME_AVERAGED)