Test SingleRoomSRIR SOFA creator
---

The scripts in this directory use the `sofar` Python library to take a SOFA file for 6DoF Ambisonics rendering (Single source, Single Room SIMO SRIR) and allows to modify the number of channels and length of the impulse responses.  
The output files are used for __computational load measurement__ of 6DoF plugins (in particular SPARTA 6DoFConv and the MCFX-6DoFconv plugin).

These scripts work with both the older SingleRoomDRIR and the newer SingleRoomSRIR conventions.

__WARNING:__ The output sofas are not usable for anything else than computational load measurement, as they just cut channels and IRs, or inflate them with copies of other IRs and white noise at -30 dB.

Files:
- `0-update_DRIR_SOFA.py:` This converts old [SingleRoomDRIR](https://www.sofaconventions.org/mediawiki/index.php/SingleRoomDRIR) into SOFAs compatible with the newer [SingleRoomSRIR](https://www.sofaconventions.org/mediawiki/index.php/SingleRoomSRIR) convention. This is useful with our old SOFA that you can find [here (www.angelofarina.it/Public/PHE-2020/6DOF/Tindari.sofa)](http://www.angelofarina.it/Public/PHE-2020/6DOF/Tindari.sofa).
- `1-drop_listenerPositions.py:` This script drops listener positions from SOFA files to speed up loading during testing. Listener positions only affect ram usage but three are enough to stress the CPU with position change.
Two indexes at the beginning of the script allow to select which positions to keep.
- `2-modify_SOFA.py`: This is the most important script. It takes a SOFA file and creates a new one with the desired number of channels and length of the impulse responses. Reducing either results in cutting, while increasing channels results in just copying some of the existing IRs, and increasing IR length results in adding white noise at -30 dB to the middle of the IR (in an attempt not to mess with tails see below ***). Similarly, reducing IR length results in cutting the middle portion of the IR.
- `3-create_test_sofas.py`: This script calls `2-modify_SOFA.py` multiple times to create a set of SOFA files for the measurements for our paper.


***
Some of the plugins tested do save computations when IR partitions are below reasonable dB levels, which could happen for tails.
Using a real SOFA ensures realistic tails and plugin behavious (load-wise) that follows, so we try to keep the realistic behaviour and not mess with tails.


_Domenico Stefani, Jan 2025_