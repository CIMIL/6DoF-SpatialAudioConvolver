##
# Drop listener positions and relative IRs, keeping only provided list of IDa

import sofar, os,sys,argparse, numpy as np


# take --in as input (string, path to sofa file) and --out as output (string, path to sofa file)

# argparse
parser = argparse.ArgumentParser(description='Modify number of channels and IR length in SOFA')
parser.add_argument('--input',              '-i', type=str, help='Path to input SOFA file')
parser.add_argument('--output',             '-o', type=str, help='Path to output SOFA file')
# parser.add_argument('--listeners_to_keep',   '-keep', type=int, help='Number of channels for the output SOFA file')
parser.add_argument('--listeners_to_keep',   '-keep', nargs='+', help='<Required> Set flag', required=True)

parser.add_argument('--verbose',            '-v', action='store_true', help='Print verbose information')
args = parser.parse_args()



listeners_to_keep = (','.join(args.listeners_to_keep)).split(',')
try:
    listeners_to_keep = [int(i) for i in listeners_to_keep]
except ValueError:
    print('Please provide a list of integers')
    sys.exit()

print('Listeners to keep:', listeners_to_keep)

# Check if --sofa is provided
if args.input is None:
    print('Please provide a path to a SOFA file using --input')
    sys.exit()
if args.output is None:
    print('--out argument was not provided, so only input sofa information will be printed')
elif os.path.exists(args.output) or os.path.exists(args.output+'.sofa'):
    print('Output file already exists. Please provide a different name')
    sys.exit()
elif not os.path.exists(os.path.dirname(os.path.abspath(args.output))):
    print('Output directory does not exist')
    sys.exit()

# Check if file exists
if not os.path.exists(args.input):
    print('File not found')
    sys.exit()

SOFA_PATH = args.input

sofafile = sofar.read_sofa(SOFA_PATH, verify=False, verbose=True)

# sofafile.add_missing()
# sofafile.add_attribute('ListenerView_Units', 'metre') #, dtype='string', dimensions=None)
# sofafile.add_attribute('SourceView_Units', 'metre')

# sofafile.verify()

# Print length of IRs (Dimension N)
print('File: "%s"'%(os.path.basename(SOFA_PATH)))

print('Reading dimensions from input SOFA file...')
input_dimensions = {
        'R': sofafile.get_dimension('R'),
        'N': sofafile.get_dimension('N'),
        'E': sofafile.get_dimension('E'),
        'M': sofafile.get_dimension('M'),
        'I': sofafile.get_dimension('I')
    }
print('Done, Dimensions:')


print("Ir Length",input_dimensions['N'])
print("Num Channels",input_dimensions['R'])
nch = int(input_dimensions['R'])
if np.sqrt(nch) == int(np.sqrt(nch)):
    print("\tPotential Ambisonics IRs of %d order"%(int(np.sqrt(nch))-1))
print("Num Sources",input_dimensions['E'])
print("Num Listeners",input_dimensions['M'])
# print("Whatisthis I",input_dimensions['I'])
print()

for tokeep in listeners_to_keep:
    if tokeep >= input_dimensions['M']:
        print('Listener ID %d is out of range'%(tokeep))
        sys.exit()
print ('All listener IDs to keep are within range')

del SOFA_PATH # Prevent accidental usage of input path


printVerbose = lambda *cargs, **ckwargs: print(*cargs, **ckwargs) if args.verbose else None


if args.output is not None:

    # Create new sofa
    new_sofa = sofar.Sofa(convention='SingleRoomSRIR') # _1.0?
    import copy
    new_sofa = copy.deepcopy(sofafile)

    old_irs = sofafile.Data_IR
    new_irs = old_irs
    new_receiver_positions = sofafile.ReceiverPosition
    new_delays = sofafile.Data_Delay

    # Drop listener positions and relative IRs, keeping only provided list of IDs
    new_sofa.ListenerPosition = new_sofa.ListenerPosition[listeners_to_keep]
    new_sofa.Data_IR = new_sofa.Data_IR[listeners_to_keep]
    new_sofa.SourcePosition = new_sofa.SourcePosition[listeners_to_keep]


#     # +-----------------------------+
#     # | First modify Channel number |
#     # +-----------------------------+

#     print('sofafile.Data_IR shape:', old_irs.shape)
#     # Shape of IRs is (M, R, N)
#     old_receiver_positions = sofafile.ReceiverPosition
#     # Shape of RP is (M, 3, 1) so it should change as well
#     old_delays = sofafile.Data_Delay
#     # Shape of delays is (I,R) so it should change as well
#     if args.new_num_channels is not None and args.new_num_channels != input_dimensions['R']:
#         if args.new_num_channels < input_dimensions['R']:
#             print('Reducing channels from %d to %d'%(input_dimensions['R'], args.new_num_channels))
#             new_irs = old_irs[:,:args.new_num_channels,:]
#             new_receiver_positions = old_receiver_positions[:args.new_num_channels,:,:]
#             new_delays = old_delays[:,:args.new_num_channels]
#         else:
#             print('Inflating channel number from %d to %d'%(input_dimensions['R'], args.new_num_channels))
#             # If new number of channels is greater than existing, replicate the last channel to avoid silent channels that may be optimized away when convolving
#             for i in range(args.new_num_channels - input_dimensions['R']):
#                 new_irs = np.concatenate((new_irs, old_irs[:,-1:,:]), axis=1)
#                 new_receiver_positions = np.concatenate((new_receiver_positions, old_receiver_positions[-1:,:,:]), axis=0)
#                 new_delays = np.concatenate((new_delays, old_delays[:,-1:]), axis=1)

        
#         printVerbose('New IR shape:', new_irs.shape)
#         assert new_irs.shape == (input_dimensions['M'], args.new_num_channels, input_dimensions['N']), 'New IR shape is not correct (is (%d, %d, %d) but should be (%d, %d, %d))'%(new_irs.shape[0], new_irs.shape[1], new_irs.shape[2], input_dimensions['M'], args.new_num_channels, input_dimensions['N'])
#         printVerbose('New receiver positions shape:', new_receiver_positions.shape)
#         assert new_receiver_positions.shape == (args.new_num_channels, 3, 1), 'New receiver positions shape is not correct (is (%d, %d, %d) but should be (%d, %d, %d))'%(new_receiver_positions.shape[0], new_receiver_positions.shape[1], new_receiver_positions.shape[2], args.new_num_channels, 3, 1)
#         printVerbose('New delays shape:', new_delays.shape)
#         assert new_delays.shape == (input_dimensions['I'], args.new_num_channels), 'New delays shape is not correct (is (%d, %d) but should be (%d, %d))'%(new_delays.shape[0], new_delays.shape[1], input_dimensions['I'], args.new_num_channels)
#     else:
#         print('Number of channels will remain the same')

#     # Copy all listener positions from the input sofa
#     new_sofa.ListenerPosition = sofafile.ListenerPosition
#     # Apply modified receiver positions
#     new_sofa.ReceiverPosition = new_receiver_positions
#     # Apply modified delays
#     new_sofa.Data_Delay = new_delays

#     # +------------------------+
#     # | Then modify IR length  |
#     # +------------------------+

#     if args.new_ir_length is not None and args.new_ir_length != input_dimensions['N']:
#         raise NotImplementedError('IR length modification not implemented yet')
#     else:
#         print('IR length will remain the same')

    new_sofa.verify()
    # Now print dimensions
    print('\n+------------------------+')
    print('New IR shape:', new_sofa.Data_IR.shape)
    print('New number of channels (R):', new_sofa.get_dimension('R'))
    print('New IR length (N):', new_sofa.get_dimension('N'))
    print('New number of sources (E):', new_sofa.get_dimension('E'))
    print('New number of listeners (M):', new_sofa.get_dimension('M'))
    print('+------------------------+')

    
    sofar.write_sofa(filename= args.output, sofa= new_sofa, compression=0)


else:
    print('Output file was not provided, so sofa object will not be saved')


