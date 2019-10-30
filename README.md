# InSituToolkit
An installer for in situ transcriptomics image processing tools. This toolkits builds on top of many open source tools such as:
- starfish
- napari
- imagingDB

## Installation
We recommend that you use a virtual environment such as virtualenv. If you do not have virtual environment installed, first install it:

Next, clone the master branch of this repository.
```sh
$ git clone https://github.com/czbiohub/InSituToolkit.git
```
Navigate into the InSituToolkit directory and create the virtual environment
```sh
$ python -m venv .venv
```

Finally, install the InSituToolkit
```sh
$ pip install -e .
```
Currently, we need to use a custom version of `slicedimage`. Install it using the following:
```sh
$ pip install git+https://github.com/kevinyamauchi/slicedimage.git@add_png#egg=slicedimage --force-reinstall
```

## Usage
We have examples of how to use the toolkit in the examples directory.
