# QuantUS-UTC

[QuantUS](https://github.com/TUL-Dev/QuantUS) is an open-source quantitative analysis tool designed for ultrasonic tissue characterization (UTC) and contrast enhanced ultrasound (CEUS) imaging analysis. This repository contains all code behind the UTC features of the software.

## Overview

In general, QuantUS provides an ultrasound system-independent platform for standardized, interactive, and scalable quantitative ultrasound research. QuantUS follows a two-tier architecture that separates core functionality in the [backend](https://github.com/TUL-Dev/PyQuantUS) from user interaction support in the frontend. The software is compatible on Mac OS X, Windows, and Linux.

This repository supports UTC analysis on 2D RF and IQ data by computing spectral parameters (i.e. midband fit, spectral slope, spectral intercept) using the sliding window method within a region of interest (ROI), generating parametric maps. Additionally, it also includes implementations for calculating the attenuation coefficient, Nakagami parameters, backscatter coefficient, effective scatterer diameter, and effective scatterer concentration. However, validation studies are required to confirm the accuracy of these additional parameters.

The UTC feature of QuantUS also supports a CLI for scalable batch processing. More information and an example can be found in [scCanonUtc.ipynb](CLI-Demos/scCanonUtc.ipynb) and [terasonUtc.ipynb](CLI-Demos/terasonUtc.ipynb). The CLI is accessible through QuantUS's pip-accessible [backend](https://github.com/TUL-Dev/PyQuantUS).

For more information, see our [documentation](https://tul-dev.github.io/PyQuantUS/).

![MBF Parametric Map Example](Images/mbfSc.png)

## Requirements

* [Python](https://www.python.org/downloads/)

## Environment

First, download [Python3.11.8](https://www.python.org/downloads/release/python-3118/) (non-Conda version) from the Python website. Once installed, note its path. We will refer to this path as `$PYTHON` below.

Next, complete the following steps. Note lines commented with `# Unix` should only be run on MacOS or Linux while lines commented with `# Windows` should only be run on Windows.

```shell
git clone https://github.com/TUL-Dev/QuantUS.git
cd QuantUS
$PYTHON -m pip install virtualenv
$PYTHON -m virtualenv .venv
source .venv/bin/activate # Unix
.venv\Scripts\activate # Windows cmd
sudo apt-get update & sudo apt-get install python3-dev # Linux
pip install -r requirements.txt
```

Following this example, this environment can be accessed via the `source .venv/bin/activate`
command from the repository directory on Unix systems, and by `.venv\Scripts\activate` on Windows.

## Building

After configuring a Python virtual environment, finish preparing QuantUS to be run using the following commands:

```shell
# Using Python virtual env (Mac/Linux)
chmod +x saveQt.sh
./saveQt.sh

# Using Python virtual env (Windows)
ren saveQt.sh saveQt.bat
.\saveQt.bat
```

## Running

### Mac/Linux

```shell
source .venv/bin/activate
python main.py
```

### Windows

```shell
call .venv\scripts\activate.bat
python main.py
```

## Sample Data

[This folder](https://drive.google.com/drive/folders/1B153p1JFc8OxHzYYpb_ijH-9Yr_wfe30?usp=sharing)
contains minimal sample data required to get started with UTC.
Note that since phantom data must be collected using
identical transducer settings as the images they're compared to, we
do not recommend using phantoms from this folder for analysis on custom
data.

## Reference Phantom Dataset

(in progress)
