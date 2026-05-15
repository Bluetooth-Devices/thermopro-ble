# Thermopro BLE

<p align="center">
  <a href="https://github.com/bluetooth-devices/thermopro-ble/actions?query=workflow%3ACI">
    <img src="https://img.shields.io/github/workflow/status/bluetooth-devices/thermopro-ble/CI/main?label=CI&logo=github&style=flat-square" alt="CI Status" >
  </a>
  <a href="https://thermopro-ble.readthedocs.io">
    <img src="https://img.shields.io/readthedocs/thermopro-ble.svg?logo=read-the-docs&logoColor=fff&style=flat-square" alt="Documentation Status">
  </a>
  <a href="https://codecov.io/gh/bluetooth-devices/thermopro-ble">
    <img src="https://img.shields.io/codecov/c/github/bluetooth-devices/thermopro-ble.svg?logo=codecov&logoColor=fff&style=flat-square" alt="Test coverage percentage">
  </a>
</p>
<p align="center">
  <a href="https://python-poetry.org/">
    <img src="https://img.shields.io/badge/packaging-poetry-299bd7?style=flat-square&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAASCAYAAABrXO8xAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAJJSURBVHgBfZLPa1NBEMe/s7tNXoxW1KJQKaUHkXhQvHgW6UHQQ09CBS/6V3hKc/AP8CqCrUcpmop3Cx48eDB4yEECjVQrlZb80CRN8t6OM/teagVxYZi38+Yz853dJbzoMV3MM8cJUcLMSUKIE8AzQ2PieZzFxEJOHMOgMQQ+dUgSAckNXhapU/NMhDSWLs1B24A8sO1xrN4NECkcAC9ASkiIJc6k5TRiUDPhnyMMdhKc+Zx19l6SgyeW76BEONY9exVQMzKExGKwwPsCzza7KGSSWRWEQhyEaDXp6ZHEr416ygbiKYOd7TEWvvcQIeusHYMJGhTwF9y7sGnSwaWyFAiyoxzqW0PM/RjghPxF2pWReAowTEXnDh0xgcLs8l2YQmOrj3N7ByiqEoH0cARs4u78WgAVkoEDIDoOi3AkcLOHU60RIg5wC4ZuTC7FaHKQm8Hq1fQuSOBvX/sodmNJSB5geaF5CPIkUeecdMxieoRO5jz9bheL6/tXjrwCyX/UYBUcjCaWHljx1xiX6z9xEjkYAzbGVnB8pvLmyXm9ep+W8CmsSHQQY77Zx1zboxAV0w7ybMhQmfqdmmw3nEp1I0Z+FGO6M8LZdoyZnuzzBdjISicKRnpxzI9fPb+0oYXsNdyi+d3h9bm9MWYHFtPeIZfLwzmFDKy1ai3p+PDls1Llz4yyFpferxjnyjJDSEy9CaCx5m2cJPerq6Xm34eTrZt3PqxYO1XOwDYZrFlH1fWnpU38Y9HRze3lj0vOujZcXKuuXm3jP+s3KbZVra7y2EAAAAAASUVORK5CYII=" alt="Poetry">
  </a>
  <a href="https://github.com/ambv/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" alt="black">
  </a>
  <a href="https://github.com/pre-commit/pre-commit">
    <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=flat-square" alt="pre-commit">
  </a>
</p>
<p align="center">
  <a href="https://pypi.org/project/thermopro-ble/">
    <img src="https://img.shields.io/pypi/v/thermopro-ble.svg?logo=python&logoColor=fff&style=flat-square" alt="PyPI Version">
  </a>
  <img src="https://img.shields.io/pypi/pyversions/thermopro-ble.svg?style=flat-square&logo=python&amp;logoColor=fff" alt="Supported Python versions">
  <img src="https://img.shields.io/pypi/l/thermopro-ble.svg?style=flat-square" alt="License">
</p>

Thermopro BLE Sensors

## Installation

Install this via pip (or your favourite package manager):

`pip install thermopro-ble`

## Supported devices

This library decodes ThermoPro Bluetooth Low Energy advertisements. It
does not pair with or connect to devices for sensor data — readings are
parsed passively from the broadcasts each thermometer emits.

Devices are matched by the advertised name prefix. The following families
have decoders with test coverage:

| Family  | Verified models                | Sensors                                             |
| ------- | ------------------------------ | --------------------------------------------------- |
| `TP35x` | TP357, TP357S, TP358, TP358S   | Temperature, humidity, battery                      |
| `TP39x` | TP393                          | Temperature, humidity, battery                      |
| `TP96x` | TP960R, TP962R (TempSpike)     | Internal/ambient probe temperature, battery         |
| `TP97x` | TP970R, TP972S (TempSpike Pro) | Tip/center/end probe temperatures, ambient, battery |

A device whose advertised name starts with one of the family prefixes
above will be decoded by the matching path. Other ThermoPro products
(including models that communicate exclusively over GATT rather than
broadcasting their readings, such as the TP902/TP920) are not supported
by the advertisement parser.

### GATT services

In addition to the passive parser, `ThermoProDevice` exposes a
`set_datetime()` GATT write for clock synchronization. It is known to
work on the TP358 and TP358S; other models may accept the same write but
have not been verified — use `ThermoProDevice.supports_set_datetime()`
to gate calls from downstream integrations.

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- prettier-ignore-start -->
<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- markdownlint-disable -->
<!-- markdownlint-enable -->
<!-- ALL-CONTRIBUTORS-LIST:END -->
<!-- prettier-ignore-end -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

## Credits

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[browniebroke/cookiecutter-pypackage](https://github.com/browniebroke/cookiecutter-pypackage)
project template.
