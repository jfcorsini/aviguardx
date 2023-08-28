## What is this?

This repository contains the work for identifying and detecting flying objects using two antennas. This was done for a [Product Development Project course](http://pdp.fi/) at Aalto University.

The code responsible for building the website where the final images were displayed can be found [here](https://github.com/jfcorsini/aviguardx-app).

The structure of this project is split into multiple submodules:

- **gnuradio**: Contains the GNURadio file that was used to process data from a KerberosSDR device, which uses 2 RTL-SDR dongles. This repository also contains a logic to run the data acquisition for a few seconds to capture some data into a specific folder.

- **processing**: This logic was implemented by forking [Max Manning - Passive Radar](https://github.com/Max-Manning/passiveRadar) and doing some simplifications for the needs of this solution. This will read the data obtained from **gnuradio** acquired data and process it, generating an image that should show if there are something moving. Check out [this page](https://dopplerfish.com/passive-radar/) for more information about how passive radar works.

- **FRCNN_predict**: This contains all of the neural network logic that was trained to identify flying objects using the images from **processing** submodule. These images contains bistatic range in Y-axis and bistatic doppler shift in X-axis. The return will be all of the objects found and their position.

Note that since the Neural Network files are way too big, we are not pushing to github any model. Therefore, some files should be created in the `/FRCNN_predict/model_data` in order to have the Neural Network working properly. More details might be added.

- **visualization**: This submodule will be responsible for drawing on a map the possible positions of flying objects given the response of the neural network.

## Usage

First clone the repository and make a conda environment with the required packages (or install them manually).

```
git clone https://github.com/jfcorsini/aviguardx
cd aviguardx
conda env create -f environment.yaml
conda activate radar-env
```

The run the whole data processing pipeline, i.e. read binary files then run tracking logic, you can run

```
python main.py
```

In case it is necessary to run a specific section of this software, some extra commands are provided such as

```
python main.py <command> <result_directory>
```

where `<command>` can be either **ML**, for neural network processing, **gnuradio** to read data from antenna, **process** to process some already acquired data, and **ui** to generate UI outputs. The `<result_directory> is the directory that will be used either as input or output, depending on the command used.

Binary data will be stored in `/data` and outputted images in `/results`

### Running Example

If one cannot read data from the antennas, this repository contain two files in `/data/circulating` which can be unzipped and used.

## Reading data from KerberosSDR

First of all, ensure the computer has GNU Radio properly installed. A guide to install it on a Jetson NX Xavier can be found [here](https://www.notion.so/Setting-up-Jetson-NX-Xavier-96d1ed3423614d159a5ccc1a463881c2).
