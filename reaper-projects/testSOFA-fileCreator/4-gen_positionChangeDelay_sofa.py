##
# Modify number of channels and IR length in SOFA to create test files for performance/load measures of convolution plugins.
#
# Usage:
# ? python modify_SOFA.py --input <path to input SOFA file> --output <path to output SOFA file> --new_num_channels <number of channels> --new_ir_length <IR length>
#
# Example:
# > python modify_SOFA.py --input "test.sofa" --output "test_modified.sofa" --new_num_channels 64
#
# This will create a new SOFA file with 64 channels and the same IR length as the input file.
# If the original file has more than 64 channels, the new will be just the first 64 channels.
# If the original file has less than 64 channels, the new will be just copies of previous IRs
#
##
print('This script is VERY specific and not intended for use with SOFAs other than tindari (http://www.angelofarina.it/Public/PHE-2020/6DOF/Tindari.sofa)')

listeners_to_keep = [167,168]
irs_to_zero = [167]
VERBOSE = True 

import sofar, os,sys,argparse, numpy as np
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# take --in as input (string, path to sofa file) and --out as output (string, path to sofa file)

# argparse
SOFA_PATH = './updated_tindari.sofa'
assert os.path.exists(SOFA_PATH), 'Input file \"%s\" does not exist, please call script 0 with tindari.sofa as input and \"%s\" as output'%(SOFA_PATH,SOFA_PATH)
OUTPUT = './position_change_delaytest.sofa'



sofafile = sofar.read_sofa(SOFA_PATH, verify=False, verbose=VERBOSE)
print('Read SOFA file:', SOFA_PATH)

print('Reading dimensions from input SOFA file...')
input_dimensions = {
        'R': int(sofafile.get_dimension('R')),
        'N': int(sofafile.get_dimension('N')),
        'E': int(sofafile.get_dimension('E')),
        'M': int(sofafile.get_dimension('M')),
        'I': int(sofafile.get_dimension('I'))
    }
print('Done, Dimensions:')


print("Ir Length (N)",input_dimensions['N'])
print("Num Channels (R)",input_dimensions['R'])
nch = int(input_dimensions['R'])
if np.sqrt(nch) == int(np.sqrt(nch)):
    print("\tPotential Ambisonics IRs of %d order"%(int(np.sqrt(nch))-1))
print("Num Sources (E)",input_dimensions['E'])
print("Num Listeners (M)",input_dimensions['M'])
# print("Whatisthis I",input_dimensions['I'])
print()

del SOFA_PATH # Prevent accidental usage of input path



printVerbose = lambda *cargs, **ckwargs: print(*cargs, **ckwargs) if VERBOSE else None


if True: #args.output is not None:
    # Create new sofa
    # new_sofa = sofar.Sofa(convention='SingleRoomSRIR') # _1.0?
    import copy
    new_sofa = copy.deepcopy(sofafile)

    new_receiver_positions = sofafile.ReceiverPosition
    new_delays = sofafile.Data_Delay

    
    new_sofa.ListenerPosition = new_sofa.ListenerPosition[listeners_to_keep]

    for n_listeners in range(input_dimensions['M']):
        if n_listeners in irs_to_zero:
            print("Zeroing IR for listener %d"%(n_listeners))
            print('input_dimensions[\'R\']',input_dimensions['R'] )
            print('type(input_dimensions[\'R\'])',type(input_dimensions['R']) )
            print('input_dimensions[\'N\']',input_dimensions['N'] )
            print('type(input_dimensions[\'N\'])',type(input_dimensions['N']) )
            r = input_dimensions['R']
            n = input_dimensions['N']
            toapply = np.zeros((r,n))
            print('toapply.shape',toapply.shape)

            new_sofa.Data_IR[n_listeners, : , :] = toapply
    new_sofa.Data_IR = new_sofa.Data_IR[listeners_to_keep]


    new_sofa.SourcePosition = new_sofa.SourcePosition[listeners_to_keep]


    new_sofa.verify()
    # Now print dimensions
    print('\n+------------------------+')
    print('New IR shape:', new_sofa.Data_IR.shape)
    print('New number of channels (R):', new_sofa.get_dimension('R'))
    print('New IR length (N):', new_sofa.get_dimension('N'))
    print('New number of sources (E):', new_sofa.get_dimension('E'))
    print('New number of listeners (M):', new_sofa.get_dimension('M'))
    print('+------------------------+')

    
    sofar.write_sofa(filename= OUTPUT, sofa= new_sofa, compression=0)


else:
    print('Output file was not provided, so sofa object will not be saved')


