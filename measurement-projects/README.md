Reaper Test Projects
---

The 42 Reaper projects in this directory are configured to test the computational load of the SPARTA-6DoFConv and MCFX-6DoFConv plugins under different configurations.
There are 21 projects for each plugin, each corresponding to one out of 7 lengths of the impulse responses (IRs) and one out of 3 Ambisonics orders (3rd, 5th and 7th, corresponding to 16, 36 and 64 channels respectively).
To reproduce the results of our paper on your machine, you need to open each project individually, load the SOFA file corresponding to the project ID (1 to 21) and render the master track as a multichannel file (Dry run is enough, saving the file is not necessary).

The SOFA files can either be found at this [link](https://drive.google.com/file/d/1tlfNX5tP-sHe_IDPvQb8vgGF79uvl_Rh/view?usp=sharing) or generated using the scripts in the `testSOFA-fileCreator` directory.
More instructions on how to generate the SOFA files can be found in the `README.md` file in the `testSOFA-fileCreator` directory.