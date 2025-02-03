bool MtxConvMaster::Configure(int numins, int numouts, int blocksize, int maxsize, int minpart, int maxpart, bool safemode)
{
    if (!numins || !numouts || !blocksize || configuration_)
        return false;

	if (minpart < blocksize)
		minpart = blocksize;

    if (maxpart < blocksize)
        maxpart = blocksize;

	minpart_ = nextPowerOfTwo(minpart);
	maxpart_ = nextPowerOfTwo(maxpart);


    numins_ = numins;
    numouts_ = numouts;


    blocksize_ = nextPowerOfTwo(blocksize);

    maxsize_ = 0;

#if 0
    // for now use uniform partitioning and no multithreading
    partitions_.add(new MtxConvSlave());

    int numpartitions = ceil((float)maxsize/blocksize_);

    partitions_.getLast()->Configure(blocksize_, numpartitions, 0, 0, &inbuf_, &outbuf_); // for now no offset and zero priority

    numpartitions_ = 1;

    maxsize_ = maxsize;

#else


    // gardener scheme -> n, n, 2n 2n, 4n 4n, 8n 8n, ....

    // try bit different...

    int partsize = minpart_;
    numpartitions_=0;
    int priority = 0;
    int offset = 0;


    while (maxsize > 0) {

        int numpartitions = 4;

        numpartitions_++;
        partitions_.add(new MtxConvSlave());


        if (partsize >= maxpart_)
        {
            // max partition size reached -> put rest into this partition...
            numpartitions = (int)ceilf((float)maxsize/(float)partsize);

        } else {

            numpartitions = jmin(numpartitions, (int)ceilf((float)maxsize/(float)partsize));

        }

        partitions_.getLast()->Configure(partsize, numpartitions, offset, priority, &inbuf_, &outbuf_);

        maxsize_ += numpartitions*partsize;

        offset += numpartitions*partsize;
        maxsize -= numpartitions*partsize;

        priority--;

        partsize *= 2;

    }
#endif

    // resize the in/out buffers
	inbufsize_ = 4 * maxpart_;

    outbufsize_ = jmax(2*maxsize_, blocksize_);

    inbuf_.setSize(numins_, inbufsize_);
    outbuf_.setSize(numouts_, outbufsize_);

    inbuf_.clear();
    outbuf_.clear();

    // set the outoffset which will be != 0 if minpart_ > blocksize is used
    if (safemode)
        outoffset_ = -minpart_; // safe mode, has higher latency
    else
        outoffset_ = blocksize_ - minpart_;    // minimum latency mode -> might cause problems with some hosts that send varying (incomplete) blocks (eg. adobe premiere, nuendo)

    if (outoffset_ < 0)
        outoffset_ += outbufsize_;

    // set the actual buffersize and compute correct offsets!
    for (int i=0; i < numpartitions_; i++) {
        MtxConvSlave *partition = partitions_.getUnchecked(i);
        partition->SetBufsize(inbufsize_, outbufsize_, blocksize_);
    }


    // print debug info
    DebugInfo();

    configuration_ = true;

    skip_count_ = 0;

    return true;
}