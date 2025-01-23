import math 

def printPartitionsMcfx(ir_length, min_size, max_size = 8192, printtype = 'none', VERBOSE=False):
    printVerbose = print if VERBOSE else lambda *a, **k: None
    orig_ir_len = ir_length
    orig_min_size = min_size
    log2minsize = math.log(min_size)/math.log(2) 
    assert log2minsize == float(int(log2minsize)), "min_size is not a power of 2"
    log2maxsize = math.log(max_size)/math.log(2) 
    assert log2maxsize == float(int(log2maxsize)), "max_size is not a power of 2"

    fourNcounter = 0
    part_counter = 0
    while ir_length > 0:
        ir_length -= min_size
        if printtype == 'verbose':
            printVerbose('Partition %d has length %d \t\t\t%d remaining'%(part_counter,min_size,ir_length))
        if printtype == 'graphic':
             charc = '-'
             index = int(math.log2(int(min_size//orig_min_size)))
            #  print('\n',index)
             charc = 'abcdefghilmnopqrstuvz'[index]
             printVerbose('|'+charc*(index+1)+'|', end='')
        assert ir_length > -1* max_size # Ensure that nothing went as wrong as to subtract a full max size from zero
        part_counter = (part_counter+1)
        fourNcounter = part_counter%4
        if fourNcounter == 0 and  min_size < 8192:
                min_size = 2**(math.log(min_size)/math.log(2) +1)
    
    if printtype != 'none':
        printVerbose('')
        printVerbose('\n\n')   
    printVerbose('-'*80)
    printVerbose('For an IR length of %d samples, MCFX with a first\npartition size of %d samples and a maximum of %d\nwill create %d partitions'%(orig_ir_len, orig_min_size, max_size, part_counter))
    printVerbose('-'*80)
    return orig_min_size, max_size, part_counter


def printUniformPartitions(ir_length, part_size, VERBOSE=False):
    printVerbose = print if VERBOSE else lambda *a, **k: None
    printVerbose('-'*80)
    printVerbose('For an IR length of %d samples, any uniform partition convolver with buffer size %d\nwill create %d partitions'%(ir_length, part_size, int(round(ir_length/part_size,0))))
    printVerbose('-'*80)
    return int(round(ir_length/part_size,0))


for buffersize in [256]: #[64,128,256,512,1024]:
    for irlen in [0.1,0.2,0.5,1,2,5,10]:
        irlen_smp = 48000*irlen
        print("IRLEN=%.1f, BUFFERSIZE=%d"%(irlen,buffersize))
        unif_part = printUniformPartitions(irlen_smp, buffersize)
        nonunif_min, nonunif_max, nonunif_part = printPartitionsMcfx(irlen_smp, buffersize)

        print('Uniform partitions: %d, Non-uniform partitions: %d'%(unif_part, nonunif_part))
        print('\n')