vars
BPM = 80
SEQUENCE = ['random','ascending','descending']
LOOPS = [3]
SAMPLES_PER_LOOP = [3]
SAMPLES_AT_A_TIME = 2

within LOOPS play SAMPLES_PER_LOOP in SEQUENCE at the specified BPM.  The code should only allow SAMPLES_AT_A_TIME to be overlapping (stop samples that exceed SAMPLES_AT_A_TIME starting with the first played one)

if you run out of samples to use then pick another SAMPLES_PER_LOOP samples (selecting a new sequence from the array)