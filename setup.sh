#!/bin/sh
conda install -y pip
pip install wheel
conda install -y pandas
conda install -y numpy
conda install -y pystan
conda install -c conda-forge -y fbprophet
pip install PySimpleGUI
pip install stldecompose
conda install -y scipy
