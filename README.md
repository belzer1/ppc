# purephotonicscontrol

A python package to easily communicate with [PurePhotonics](https://www.pure-photonics.com/) lasers through python. 
Most purephotonics features are implemented, so the user can create their own computer controlled laser sequence.
The package has been developed for the PPCL560 laser, but should generalise to other products.

The package assumes that the PPCL560 laser is interfaced with a Teensy 3.6 as outlined in (TO DO!). This interface is useful for creating triggerable signals from the laser. If the laser is connected directly to a PC (no Teensy), then set `com_type='direct'` when initialising laser communication.

## Installation

The easiest way to install the package is with pip:

```
pip install purephotonicscontrol
```

## Usage

Initalise communication with the laser
```
ITLA = purephotonicscontrol.lasercommands.laser("COM4")
```
Then give the laser whatever commands you like
```
ITLA.SetFrequency(191.50)
ITLA.SetPower(7.0)
ITLA.EnableLaser(True)
```

### Prerequisites

This package requires pyserial and numpy, but these should be automatically installed when you pip install

## Contributing

Contributions to the package are welcome. The recommended workflow to contribute is:
1. **Fork** the repo on GitHub
2. **Clone** the project to your own machine
3. **Commit** changes to your own branch
4. **Push** your work back up to your fork
5. Submit a **Pull request** so that we can review your changes

## Authors

* **Matthew Berrington** (*primary developer*) - [bitbucket profile](https://bitbucket.org/matthewberrington)
* **PurePhotonics** (*inital work*) [website](https://www.pure-photonics.com/)

## License

GNU General Public License v3

## Acknowledgments

* Many thanks go to PurePhotonics for making their python interface example publically available at [link](https://www.pure-photonics.com/s/ITLA_v3-CUSTOMER.PY). Their work forms the base of this python package