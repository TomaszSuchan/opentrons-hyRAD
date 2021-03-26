# Hybridization and wash protocol for hyRAD

This protocol requires magnetic and PCR module. Maximum 8 samples can be
processed at once, and this is advisable number as an 8-channel pipette is used
for speed. You can change the number of samples in the script (line 15), but
this affects only the number of wells to which all the buffers will be pipetted.
You should therefore make sure to put the tips in the corresponding positions
in the tipracks in slots 1 and 5. For example, when processing 4 samples, the
tips should be in 4 upper rows of those tipracks.

The protocol stops several times and requires your attention then:

- first, load the libraries with blocking mix in column 2 on the PCR and press resume,
- the robot then proceeds to denaturation of the samples with the blocking mix for 5 min,
- after 5 min, the PCR machine opens and you should put the the hybridization mix in column 1 on the PCR and press resume,
- the robot proceeds to incubate both samples at the hybridization temperature for 5 min, then mix the hybridization mix with the blocking mix and library,
- then the main hybridization starts, you should stop it manually after the required amount of time,
- make sure you place the required reagents on the racks before stopping the hybridization!
- then the robot proceeds with the washes and does not require any input until the end of the protocol,
- at the end of the protocol, the washed and enriched libraries are in the 1st column on the magnet; the bead solution should be used in a subsequent PCR or, alternatively, the DNA can be eluted off the probes by incubating at 95 °C
