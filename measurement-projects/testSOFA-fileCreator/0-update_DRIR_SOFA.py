import sofar, os,sys,argparse


# take --in as input (string, path to sofa file) and --out as output (string, path to sofa file)

# argparse
parser = argparse.ArgumentParser(description='update convention of SOFA files')
parser.add_argument('--input', type=str, help='Path to input SOFA file')
parser.add_argument('--output', type=str, help='Path to output SOFA file')
args = parser.parse_args()

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

SOFA_PATH = args.input## "D:/develop-farina-proj/MATRICES(hrtf-and-SOFA)/SOFA/ambix_o7_test.sofa"

sofafile = sofar.read_sofa(SOFA_PATH, verify=False, verbose=True)

# sofafile.add_missing()
sofafile.add_attribute('ListenerView_Units', 'metre') #, dtype='string', dimensions=None)
sofafile.add_attribute('SourceView_Units', 'metre')

# sofafile.verify()

# Print length of IRs (Dimension N)
print('File: "%s"'%(os.path.basename(SOFA_PATH)))
print("Ir Length",sofafile.get_dimension('N'))
print("Num Channels",sofafile.get_dimension('R'))
print("Num Sources",sofafile.get_dimension('E'))
print("Num Listeners",sofafile.get_dimension('M'))


if args.output is not None:
    oldconvention = sofafile._convention['GLOBAL_SOFAConventions']['default']
    if 'SingleRoomDRIR' in oldconvention:
        newconvention = 'SingleRoomSRIR_1.0'
    elif 'SingleRoomSRIR' in oldconvention:
        print('SOFA file already in SingleRoomSRIR_1.0 convention')
        sys.exit()
    else:
        raise ValueError('SOFA Convention %s not supported'%(oldconvention))

    print('Copying sofa object...')
    sofafile2 = sofafile.copy()
    print('Done.\n')



    VERBOSE = False
    if VERBOSE:
        print("Conventions", sofar.list_conventions())

    print('Upgrading to SingleRoomSRIR...')
    sofafile2.upgrade_convention('SingleRoomSRIR_1.0')
    print('Done.\n')

    print('Verifying...')
    sofafile2.verify()
    print('Done.\n')

    print('Saving to %s'%args.output)
    sofar.write_sofa(filename=args.output, sofa=sofafile2, compression=0)
    print('Done.\n')
else:
    print('Output file was not provided, so sofa object will not be saved')


