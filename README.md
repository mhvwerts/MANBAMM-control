# MANBAMM-control

Python software library for controlling lab equipment used in the MANBAMM project.

Intended for internal use, so use at your own risk. No guarantees. No documentation, but the code is quite straight-forward. Don't hesitate to contact us should you have questions.

## Installation hints

We work with Miniconda Python distribution, strictly connected to the [`conda-forge`](https://conda-forge.org/) channel.

At present, we do not provide a ready-to-install package of this `MANBAMM-control` library. Instead, we prefer to copy the scripts directly into the data directory for the experiment that we are running. This is a way of ensuring that we know which code was precisely used to run the experiment.

The library depends on non-standard packages which are listed in `requirements.txt`. They can be installed using:

```
conda install --file requirements.txt                        
```

For GUI development, we use [`Remi`](https://github.com/rawpython/remi). This is a very lightweight, platform-independent library that uses a web-browser for the graphical interface (via HTML5/CSS/JavaScript) with the application that running as a web-server in Python. Very clever! No large framework to be installed. We make small extensions to this library (modified widgets, etc.), collected in `remi_extras.py`


## Equipment list

### Aladdin syringe pump

The well-known red "Aladdin" syringe pump by World Precision Instruments (https://www.wpi-europe.com/), equipped with RS232 serial communications, and TTL control.

Development has started on a small GUI application for Aladdin pump configuration & control. This app is functional, but not yet polished.


### VICI EUHA chromatography valve

VICI (Valco Instruments Co. Inc.) micro-controlled EUHA valve, with RS232 serial communications. It also found its place in the GUI control, so that it may be controlled simultaneously with an attached Aladdin pump.

