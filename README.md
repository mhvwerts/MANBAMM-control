# MANBAMM-control

Python software library for controlling lab equipment used in the MANBAMM project.

Intended for internal use, so use at your own risk. No guarantees. No documentation, but the code is quite straight-forward. Don't hesitate to contact us should you have questions.


## Installation hints

We work with Miniconda Python distribution, strictly connected to the [`conda-forge`](https://conda-forge.org/) channel, and specific required components ('packages') installed. See "Recommended Python configuration" at the end of this document.

At present, we do not provide a ready-to-install package of this `MANBAMM-control` library. Instead, we prefer to copy the scripts directly into the data directory for the experiment that we are running. This is a way of ensuring that we know which code was precisely used to run the experiment.

For GUI development, we use [`Remi`](https://github.com/rawpython/remi). This is a very lightweight, platform-independent library that uses a web-browser for the graphical interface (via HTML5/CSS/JavaScript) with the actual application running as a web-server in Python. Very clever! No large framework to be installed. We make small extensions to this library (modified widgets, etc.), collected in `remi_extras.py`


## Currently supported equipment list

### Aladdin syringe pump

The well-known red "Aladdin" syringe pump by World Precision Instruments (https://www.wpi-europe.com/), equipped with RS232 serial communications, and TTL control.

Development has started on a small GUI application for Aladdin pump configuration & control. This app is functional, but not yet polished.


### VICI EUHA chromatography valve

VICI (Valco Instruments Co. Inc.) micro-controlled EUHA valve, with RS232 serial communications. It also found its place in the GUI control, so that it may be controlled simultaneously with an attached Aladdin pump.



## (Recommended) Python configuration

*Last tested on 2025-01-15, Windows 11 64-bit; Miniconda3 Python 3.12*

*Next time, consider the new https://conda-forge.org/download/*

These are the instructions to obtain our recommended, standardized Miniconda Python 3.12 environment with the required components ('packages') installed. The instructions are intended for use with Windows 10 / Windows 11, but could easily be adapted for other operating systems.

0. Prior to installing Miniconda3, carefully remove all previously installed Python distributions.

1. Go to https://www.anaconda.com/download/success , then locate the Miniconda installer.

2. Download [Miniconda3 Windows 64-bit installer](https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe).

3. Run the installer. **USE THE RECOMMENDED (DEFAULT) OPTIONS** (in particular, install "Just for me" (not for other users)).

4. After installation, open  "Anaconda Powershell Prompt" from the Start Menu to have access to the command line interface to enter the configuration commands to be executed

5. Execute *precisely* the following commands to configure Miniconda to work with the Conda-forge repository.
```
conda config --remove channels https://repo.anaconda.com/pkgs
conda config --remove channels https://repo.anaconda.com/pkgs/main
conda config --remove channels https://repo.anaconda.com/pkgs/r
conda config --add channels conda-forge
conda config --set channel_priority strict
conda update conda
conda update --all
```

6. Create a separate Conda environment, with all required packages installed. This is done by entering.
```
conda create --name std312 python=3.12 numpy scipy matplotlib xarray tqdm numba pillow h5py spyder jupyterlab ipywidgets openpyxl tifffile lmfit pyserial remi 
```
Alternatively, the following should also work (if you have the file `requirements.txt` from this GitHub repository available).
```
conda install --name std312 --file requirements.txt                        
```

7. Activate the environment using the command. This will give access to the installed packages.
```
conda activate std312
```

8. Run Spyder from the command line (with the `std312` environment activated)
```
spyder
```

9. After a short wait, the Spyder IDE will be up and running, and a handy shortcut will have been created in the start menu (with automatic activation of the `std312`) environment.
 
11. You can use Spyder to interact with the Python. Alternatively, you can open the  "Anaconda Powershell Prompt (miniconda3)" from the Start Menu. **Important!** Each time you open the Powershell, first use the `conda activate std312` command before anything else. This is required to switch to the `std312` environment where all the required packages and Python modules are installed.

