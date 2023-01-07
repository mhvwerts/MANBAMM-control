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

## Equipment list

### Aladdin syringe pump

The well-known red "Aladdin" syringe pump by World Precision Instruments (https://www.wpi-europe.com/), equipped with RS232 serial communications, and TTL control.





