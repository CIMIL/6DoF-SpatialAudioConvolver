import soundfile as sf
import numpy as np

SAMPLE_RATE = 48000
DURATION_SECONDS = 10
IMPULSE_FREQUENCY_HZ = 10

impulse = np.zeros(int(DURATION_SECONDS * SAMPLE_RATE))

for i in range(0, len(impulse), int(SAMPLE_RATE / IMPULSE_FREQUENCY_HZ)):
    impulse[i] = 1

# Write 24-bit wav file
sf.write("impulse.wav", impulse, SAMPLE_RATE, subtype='PCM_24')