# pimidipy Scripts

## Overview

This repository hosts user and sample Python scripts that utilize the Blokas [pimidipy](https://github.com/BlokasLabs/pimidipy) library.

If you're looking to expand your Raspberry Pi's MIDI capabilities, check out [**Pimidi**](https://blokas.io/pimidi/) by Blokas. Pimidi is a hardware add-on that adds 2 MIDI inputs and 2 MIDI outputs to your Raspberry Pi, and it can be stacked up to 4 units high for even more I/O.

Each `.py` file in the root of the repo or `samples` subfolder is a standalone runnable Python program.

## Setup and Running

The script repository is automatically set up by installing the pimidipy [Patchbox OS module](https://blokas.io/patchbox-os/docs/modules/). Once installed, the default location for the scripts is `/var/pimidipy-scripts`.

Run `patchbox` to active the `pimidipy` module and select which of the .py scripts within `/var/pimidipy-scripts` or `/var/pimidipy-scripts/samples` to run.

When using the Patchbox OS module, any modifications to the scripts in this repository will automatically restart the currently active script, ensuring that changes take effect immediately.

Alternatively, if not using Patchbox OS, clone this repository, and run the .py files directly on your own.

## Contributing

We welcome contributions from the community! You can share your work by submitting a pull request to this repository. Additionally, you can post your scripts online at [Patchstorage.com](https://patchstorage.com/platform/pimidipy/).
