# MANBAMM-control

Python software library for controlling lab equipment used in the MANBAMM project.

Intended for use internally in our lab, so use at your own risk. No guarantees. No documentation, but the code is quite straight-forward. Don't hesitate to contact us should you have questions.


## Installation hints

We work with Miniconda Python distribution, strictly connected to the [`conda-forge`](https://conda-forge.org/) channel, and specific required components ('packages') installed. See "Recommended Python configuration" at the end of this document.

At present, we do not provide a ready-to-install package of this `MANBAMM-control` library. Instead, we prefer to copy the scripts directly into the data directory for the experiment that we are running. This is a way of ensuring that we know which code was precisely used to run the experiment.

For GUI development, we use [`Remi`](https://github.com/rawpython/remi). This is a very lightweight, platform-independent library that uses a web-browser for the graphical interface (via HTML5/CSS/JavaScript) with the actual application running as a web-server in Python. Very clever! No large framework to be installed. We make small extensions to this library (modified widgets, etc.), collected in `remi_extras.py`


## Currently supported equipment list

The communication between the Python control scripts and the supported devices uses the [`manbamm.devcomms`](https://github.com/mhvwerts/MANBAMM-control/tree/main/python-src/devcomms) module

### Aladdin syringe pump

The well-known red "Aladdin" syringe pump by World Precision Instruments (https://www.wpi-europe.com/), equipped with RS232 serial communications, and TTL control.

Development has started on a small GUI application for Aladdin pump configuration & control. This app is functional, but not yet polished.


### MOLTECH-FSS flow sensor system

The flow sensor hardware modules developed at MOLTECH-Anjou are described [here](https://github.com/mhvwerts/MANBAMM-control/tree/main/MOLTECH-flow-sensor-system).


### MOLTECH-FLSH flash box

[Experimental orange box](https://github.com/mhvwerts/MANBAMM-control/tree/main/MOLTECH-flashbox) under continuous development for generating TTL pulse sequences.


### VICI EUHA chromatography valve (RS232)

VICI (Valco Instruments Co. Inc.) micro-controlled EUHA valve, with RS232 serial communications. It also found its place in the GUI control, so that it may be controlled simultaneously with an attached Aladdin pump.


### VICI EUHA chromatography valve (TTL interface via Arduino, under development)

VICI (Valco Instruments Co. Inc.) EUHA valve actuator controlled directly using the "standard interface" on the back of the actuator enclosure via an Arduino Uno board with tailored switching electronics.


## Recommended Python configuration

These are the instructions to obtain our recommended, standardized Miniconda Python 3.12 environment with the required components ('packages') installed. The instructions are intended for use with Windows 10 / Windows 11, but could easily be adapted for other operating systems.

1. Prior to installing Miniforge, carefully remove all previously installed Python distributions.

2. Go to https://conda-forge.org/download/

3. Run the installer. **USE THE RECOMMENDED (DEFAULT) OPTIONS** (in particular, install "Just for me" (not for other users)).

4. After installation, open  "Miniforge Prompt" from the Start Menu to have access to the command line interface to enter the configuration commands to be executed.

5. Create a separate Conda environment, with all required packages installed. This is done by entering.
```
conda create --name std312 python=3.12 numpy scipy matplotlib xarray tqdm numba remi marimo pillow h5py spyder jupyterlab ipywidgets openpyxl tifffile lmfit pyserial pyqtgraph 
```
Alternatively, the following should also work (if you have a copy of the file `requirements.txt` from this GitHub repository available in your working directory).
```
conda install --name std312 --file requirements.txt                        
```

6. Activate the environment using the following command. This will give access to the installed packages.
```
conda activate std312
```

7. Run Spyder from the command line (with the `std312` environment activated)
```
spyder
```

8. After a short wait, the Spyder IDE will be up and running, and a handy shortcut will have been created in the start menu (with automatic activation of the `std312`) environment.
 
9. You can use Spyder to interact with the Python. Alternatively, you can open the  ""Miniforge Prompt" from the Start Menu. **Important!** Each time you open the Miniforge prompt command line terminal, first use the `conda activate std312` command before anything else. This is required to switch to the `std312` environment where all the required packages and Python modules are installed.

