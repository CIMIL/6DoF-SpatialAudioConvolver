#include <cmath>
#include <iostream>
using namespace std;
# define private public

/** Returns the smallest power-of-two which is equal to or greater than the given integer. */
inline int nextPowerOfTwo (int n) noexcept
{
    --n;
    n |= (n >> 1);
    n |= (n >> 2);
    n |= (n >> 4);
    n |= (n >> 8);
    n |= (n >> 16);
    return n + 1;
}


/** Returns the smaller of two values. */
template <typename Type>
constexpr Type jmin (Type a, Type b)                                   { return b < a ? b : a; }

// float ceilf(float _X)
// {
//     return (float)ceil(_X);
// }


template <typename Type>
constexpr Type jmax (Type a, Type b)                                   { return a < b ? b : a; }


class DummyMCFX
{
public:

    bool configure(int numins, int numouts, int blocksize, int maxsize, int minpart, int maxpart, bool safemode)
    {
        if (!numins || !numouts || !blocksize || configuration_)
            return false;
        cout << "Called \"configure\" with parameters" << endl;
        cout << "numins:\t" << to_string(numins) << endl;
        cout << "numouts:\t" << to_string(numouts) << endl;
        cout << "blocksize:\t" << to_string(blocksize) << endl;
        cout << "maxsize:\t" << to_string(maxsize) << endl;
        cout << "minpart:\t" << to_string(minpart) << endl;
        cout << "maxpart:\t" << to_string(maxpart) << endl;
        cout << "safemode:\t" << to_string(safemode) << endl << endl;

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

        
    // #if 0
        
    //     // for now use uniform partitioning and no multithreading
    //     partitions_.add(new MtxConvSlave());

    //     int numpartitions = ceil((float)maxsize/blocksize_);

    //     partitions_.getLast()->Configure(blocksize_, numpartitions, 0, 0, &inbuf_, &outbuf_); // for now no offset and zero priority

    //     numpartitions_ = 1;

    //     maxsize_ = maxsize;

    // #else


        // gardener scheme -> n, n, 2n 2n, 4n 4n, 8n 8n, ....

        // try bit different...

        int partsize = minpart_;
        numpartitions_=0;
        int priority = 0;
        int offset = 0;


        while (maxsize > 0) {

            int numpartitions = 4;

            numpartitions_++;
            // partitions_.add(new MtxConvSlave());

            cout<< "partsize:" << partsize << endl;

            if (partsize >= maxpart_)
            {
                // max partition size reached -> put rest into this partition...
                numpartitions = (int)ceilf((float)maxsize/(float)partsize);

            } else {

                numpartitions = jmin(numpartitions, (int)ceilf((float)maxsize/(float)partsize));

            }

            // partitions_.getLast()->Configure(partsize, numpartitions, offset, priority, &inbuf_, &outbuf_);

            maxsize_ += numpartitions*partsize;

            offset += numpartitions*partsize;
            maxsize -= numpartitions*partsize;

            priority--;

            partsize *= 2;

        }
    // #endif

        // resize the in/out buffers
        inbufsize_ = 4 * maxpart_;

        outbufsize_ = jmax(2*maxsize_, blocksize_);

        // inbuf_.setSize(numins_, inbufsize_);
        // outbuf_.setSize(numouts_, outbufsize_);

        // inbuf_.clear();
        // outbuf_.clear();

        // set the outoffset which will be != 0 if minpart_ > blocksize is used
        if (safemode)
            outoffset_ = -minpart_; // safe mode, has higher latency
        else
            outoffset_ = blocksize_ - minpart_;    // minimum latency mode -> might cause problems with some hosts that send varying (incomplete) blocks (eg. adobe premiere, nuendo)

        if (outoffset_ < 0)
            outoffset_ += outbufsize_;

        // set the actual buffersize and compute correct offsets!
        for (int i=0; i < numpartitions_; i++) {
            cout << "Here I would be setting the buffersizes of paritition " << to_string(i) << " to "  << to_string(inbufsize_) << ' ' << to_string(outbufsize_) << ' ' << to_string(blocksize_) << endl;
            // MtxConvSlave *partition = partitions_.getUnchecked(i);
            // partition->SetBufsize(inbufsize_, outbufsize_, blocksize_);

        }


        // print debug info
        // DebugInfo();

        configuration_ = true;

        // skip_count_ = 0;

        return true;
    }

    DummyMCFX()
    {
        configuration_ = false;
    }

private:
    int                 inbufsize_;         // size of time domain input buffer (2*maxpart_)
    int                 outbufsize_;        // size of time domain output buffer (2*maxsize_)

    int                 inoffset_;          // current ring buffer write offset
    int                 outoffset_;         // current ring buffer read offset

    int                 blocksize_;         // Blocksize of host process (how many samples are processed in each callback)

    int                 minpart_;           // Size of first partition
    int                 maxpart_;           // Maximum partition size

    int                 numins_;            // Number of Input Channels
    int                 numouts_;           // Number of Output Channels

    int                 numpartitions_;     // Number of Partition Levels (different blocklengths)

    int                 maxsize_;           // maximum filter length

    bool                configuration_;     // isconfigured
};


int main(void) {
    cout << "Test Partitions..." << endl;
    DummyMCFX dummyObj;
    
    //  configure(int numins, int numouts, int blocksize, int maxsize, int minpart, int maxpart, bool safemode)
    int numins = 1;
    int numouts = 16;
    int blocksize = 64;
    int IRLEN = 64*12;
    int minpart = 64;
    int maxpart = 8096;
    bool safemode = false;
    
    dummyObj.configure(numins,
                        numouts,
                        blocksize,
                        IRLEN,
                        minpart,
                        maxpart,
                        safemode);
    cout << "Done." << endl;
    
    cout << "Now maxsize_ is " << to_string(dummyObj.maxsize_) << endl;
    cout << "So biggest partition is " << to_string(dummyObj.maxsize_/4) << endl;
    cout << "Now numpartitions_ is " << to_string(dummyObj.numpartitions_) << "// Number of Partition Levels (different blocklengths)" << endl;
    int                 numpartitions_;     // Number of Partition Levels (different blocklengths)
}