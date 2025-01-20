import os
import pandas as pd
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import tempfile



DATA_FNAME = ['measures_64spl_raw.csv']
INPUT_LENGTH_TIMES = [0.5*60, # 30 seconds
                      1*60,   # 1 minute
                      5*60]   # 5 minutes

def get_input_length(data, input_length_times, verbose=False,TOLERANCE_DIFF = 16):
    printVerbose = print if verbose else lambda *args, **kwargs: None
    res = []
    
    for idx in data.index:
        time = data.at[idx, 'time']
        x = data.at[idx, 'X'].astype(float)
        expected_time = time * x

        closest_input_time = None
        closest_input_time_diff = None
        printVerbose('\nTrying to find input time match for %.1f  (%s)' % (expected_time,data.at[idx, 'screenshot']))
        for input_time in INPUT_LENGTH_TIMES:
            diff = abs(input_time - expected_time)
            printVerbose("diff = ", diff, end=' ')
            if closest_input_time is None or diff < closest_input_time_diff:
                printVerbose('<-- This is the closest', end=' ')
                closest_input_time = input_time
                closest_input_time_diff = diff
            printVerbose()
        del diff 
        if closest_input_time_diff > TOLERANCE_DIFF:
            raise ValueError('Expected time (%.1f) is too far from any input time (%.1f)' % (expected_time,closest_input_time_diff))

        printVerbose(f'time = {time}, x = {x}, expected_time = {expected_time:.1f} (%d:%d)'%(expected_time//60,expected_time%60))
        res.append(closest_input_time)
    return res


for data_fname in DATA_FNAME:
    DATA_PATH = os.path.abspath(os.path.join('..', 'data',data_fname))
    assert os.path.exists(DATA_PATH), 'Data file not found'
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
        elapsed = data.at[idx, 'elapsed']
        remaining = data.at[idx, 'remaining']
        time = data.at[idx, 'time']
        
        if not pd.isna(elapsed) and elapsed != "":
            elapsed = elapsed.split(':')
            elapsed = float(elapsed[0])*60 + float(elapsed[1])
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
        elapsed = data.at[idx, 'elapsed']
        remaining = data.at[idx, 'remaining']
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
    data = data.drop(columns=['elapsed', 'remaining'])

    # print(data.head())

    input_length_s = get_input_length(data, INPUT_LENGTH_TIMES, verbose=False)

    # For short render times, the render time itself is less precise than Real-time ratio (X), so we recompute time based on that
    # (for < RECOMPUTE_S_THRESH seconds)
    # Also, we do not correct for super low real-time ratios (X) (<0.6)

    RECOMPUTE_S_THRESH = 130
    RECOMPUTE_TOLERANCE = 2
    for idx in data.index:
        time_logged = data.at[idx, 'time']
        data.at[idx, 'input_length'] = input_length_s[idx]

        if time_logged <= RECOMPUTE_S_THRESH and data.at[idx, 'X'] >= 0.6:
            # print(data.at[idx, 'screenshot'])
            # print('time_logged: %d (%d:%d)'%(time_logged,time_logged//60,time_logged%60))
            recomputed_time = input_length_s[idx]/data.at[idx, 'X']
            # print('time_re_calculated: %f (%d:%f)'%(recompute_time,recompute_time//60,recompute_time%60))

            if (abs(time_logged-recomputed_time) <= RECOMPUTE_TOLERANCE):
                # print('OK')
                data.at[idx, 'time'] = round(recomputed_time,2)
            else:
                raise ValueError('Time logged (%d) is different from recomputed time (%d)'%(time_logged,recomputed_time))
            # print()
        else:
            pass


    for idx in data.index:
        time = data.at[idx, 'time']
        ratio = data.at[idx, 'X']
        input_length = data.at[idx, 'input_length']

        print('time = %.3f (%d:%d), input_length = %d, ratio = %.2f, expected_ratio = %.2f' % (time,time//60,time%60,input_length,ratio,input_length/time))
        ratioerror = abs(ratio - input_length/time)
        assert ratioerror < 0.1, 'Ratio error is too high: %.2f' % ratioerror


    for idx in data.index:
        ratio = data.at[idx, 'X']
        data.at[idx, 'inverse_ratio'] = 1/ratio
        
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
        assert data.at[idx, ('X_std')] <= 0.91, 'Standard deviation of X is too high: %.2f (for id:%d)'  % (data.at[idx, ('X_std')], data.at[idx, ('id')])

    DATA_FNAME_AVERAGED = DATA_FNAME_CLEAN.replace('clean','averaged')
    data.to_csv(DATA_FNAME_AVERAGED, index=False)
    print('Data averaged and saved to', DATA_FNAME_AVERAGED)