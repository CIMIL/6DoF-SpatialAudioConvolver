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

import sofar, os,sys,argparse, numpy as np


# take --in as input (string, path to sofa file) and --out as output (string, path to sofa file)

# argparse
parser = argparse.ArgumentParser(description='Modify number of channels and IR length in SOFA')
parser.add_argument('--input',              '-i', type=str, help='Path to input SOFA file', required=True)
parser.add_argument('--output',             '-o', type=str, help='Path to output SOFA file', required=True)
parser.add_argument('--new_num_channels',   '-ch', type=int, help='Number of channels for the output SOFA file')
parser.add_argument('--new_ir_length',      '-ir', type=int, help='IR length for the output SOFA file')
parser.add_argument('--verbose',            '-v', action='store_true', help='Print verbose information')
parser.add_argument('--force_overwrite',    '-f', action='store_true', help='Write over existing file')
args = parser.parse_args()

# Check if --sofa is provided
if args.input is None:
    print('Please provide a path to a SOFA file using --input')
    sys.exit()
if args.output is None:
    print('--out argument was not provided, so only input sofa information will be printed')
elif (os.path.exists(args.output) or os.path.exists(args.output+'.sofa')) and not args.force_overwrite:
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

sofafile = sofar.read_sofa(SOFA_PATH, verify=False, verbose=args.verbose)

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

if args.new_num_channels is None and args.new_ir_length is None:
    print('Please provide either --new_num_channels or --new_ir_length to modify the SOFA file')
    sys.exit()

# print(args.verbose)

printVerbose = lambda *cargs, **ckwargs: print(*cargs, **ckwargs) if args.verbose else None


if args.output is not None:

    # Create new sofa
    # new_sofa = sofar.Sofa(convention='SingleRoomSRIR') # _1.0?
    import copy
    new_sofa = copy.deepcopy(sofafile)

    old_irs = sofafile.Data_IR
    new_irs = old_irs
    new_receiver_positions = sofafile.ReceiverPosition
    new_delays = sofafile.Data_Delay


    # +-----------------------------+
    # | First modify Channel number |
    # +-----------------------------+

    print('sofafile.Data_IR shape (M,R,N):', old_irs.shape)
    assert old_irs.shape == (input_dimensions['M'], input_dimensions['R'], input_dimensions['N']), 'IR shape is not correct (is (%d, %d, %d) but should be (%d, %d, %d))'%(old_irs.shape[0], old_irs.shape[1], old_irs.shape[2], input_dimensions['M'], input_dimensions['R'], input_dimensions['N'])
    # Shape of IRs is (M, R, N)
    old_receiver_positions = sofafile.ReceiverPosition
    # Shape of RP is (M, 3, 1) so it should change as well
    old_delays = sofafile.Data_Delay
    # Shape of delays is (I,R) so it should change as well
    if args.new_num_channels is not None and args.new_num_channels != input_dimensions['R']:
        if args.new_num_channels < input_dimensions['R']:
            print('Reducing channels from %d to %d'%(input_dimensions['R'], args.new_num_channels))
            new_irs = old_irs[:,:args.new_num_channels,:]
            new_receiver_positions = old_receiver_positions[:args.new_num_channels,:,:]
            new_delays = old_delays[:,:args.new_num_channels]
        else:
            print('Inflating channel number from %d to %d'%(input_dimensions['R'], args.new_num_channels))
            # If new number of channels is greater than existing, replicate the last channel to avoid silent channels that may be optimized away when convolving
            for i in range(args.new_num_channels - input_dimensions['R']):
                new_irs = np.concatenate((new_irs, old_irs[:,-1:,:]), axis=1)
                new_receiver_positions = np.concatenate((new_receiver_positions, old_receiver_positions[-1:,:,:]), axis=0)
                new_delays = np.concatenate((new_delays, old_delays[:,-1:]), axis=1)

        
        printVerbose('New IR shape:', new_irs.shape)
        assert new_irs.shape == (input_dimensions['M'], args.new_num_channels, input_dimensions['N']), 'New IR shape is not correct (is (%d, %d, %d) but should be (%d, %d, %d))'%(new_irs.shape[0], new_irs.shape[1], new_irs.shape[2], input_dimensions['M'], args.new_num_channels, input_dimensions['N'])
        printVerbose('New receiver positions shape:', new_receiver_positions.shape)
        assert new_receiver_positions.shape == (args.new_num_channels, 3, 1), 'New receiver positions shape is not correct (is (%d, %d, %d) but should be (%d, %d, %d))'%(new_receiver_positions.shape[0], new_receiver_positions.shape[1], new_receiver_positions.shape[2], args.new_num_channels, 3, 1)
        printVerbose('New delays shape:', new_delays.shape)
        assert new_delays.shape == (input_dimensions['I'], args.new_num_channels), 'New delays shape is not correct (is (%d, %d) but should be (%d, %d))'%(new_delays.shape[0], new_delays.shape[1], input_dimensions['I'], args.new_num_channels)
    else:
        print('Number of channels will remain the same')

    # Copy all listener positions from the input sofa
    new_sofa.ListenerPosition = sofafile.ListenerPosition
    # Apply modified receiver positions
    new_sofa.ReceiverPosition = new_receiver_positions
    # Apply modified delays
    new_sofa.Data_Delay = new_delays

    # +------------------------+
    # | Then modify IR length  |
    # +------------------------+

    # In the case of shortening the IRs, we will just cut the IRs
    # In the case of lengthening the IRs, we will add noise to the middle of the IRs, in what is possibly the sustain part of the IR, keeping tails more realistic

    cur_num_channes = args.new_num_channels if args.new_num_channels is not None else input_dimensions['R']
    if args.new_ir_length is not None and args.new_ir_length != input_dimensions['N']:
        if args.new_ir_length < input_dimensions['N']:
            print('Reducing IR length from %d to %d cutting the middle'%(input_dimensions['N'], args.new_ir_length))
            # new_irs = new_irs[:,:,:args.new_ir_length] ## The old way was to cut from the end, but it messes with the tail
            # Cut the IRs in the middle
            halflen1 = int(args.new_ir_length/2)
            halflen2 = args.new_ir_length - halflen1
            new_irs = np.concatenate((new_irs[:,:,:halflen1],
                                      new_irs[:,:,input_dimensions['N']-halflen2:]), axis=2)
            assert new_irs.shape[2] == args.new_ir_length, 'New IR length is not correct (is %d but should be %d)'%(new_irs.shape[2], args.new_ir_length)
        else:
            print('Inflating IR length from %d to %d'%(input_dimensions['N'], args.new_ir_length))

            # Add noise of shape (M, R, newN-oldN) to IRs
            noise = np.random.rand(input_dimensions['M'], cur_num_channes, args.new_ir_length - input_dimensions['N']) * 2 - 1
            # Remove 30dB from the noise
            gain = 10**(-30/20)
            noise = noise * gain
            # print('Noise shape:', noise.shape)
            # new_irs = np.concatenate((new_irs, noise), axis=2)
            # Add noise to the middle of the IRs]
            new_irs = np.concatenate((new_irs[:,:,:int(args.new_ir_length/2)], noise, new_irs[:,:,int(args.new_ir_length/2):]), axis=2)

    else:
        print('IR length will remain the same')


    # Apply modified IRs    
    new_sofa.Data_IR = new_irs
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


