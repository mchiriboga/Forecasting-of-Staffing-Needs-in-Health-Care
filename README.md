# DSCI_591_capstone-Providence

Forecasting of Staffing Needs

### Contributors:

- [Luo (Iris) Yang](https://github.com/lyiris22)
- [Marcelle Chiriboga](https://github.com/mchiriboga)
- [Patrick Tung](https://github.com/tungpatrick)
- [Weifeng (Davy) Guo](https://github.com/DavyGuo)

### Milestones:
 |Deliverable|Link|
 |---|---|
 |Proposal Presentation|[RISE presentation](https://github.com/UBC-MDS/DSCI_591_capstone-Providence/blob/master/doc/Proposal_Presentation.ipynb)|
 ||[.pdf slides](https://github.com/UBC-MDS/DSCI_591_capstone-Providence/blob/master/doc/Proposal_Presentation.pdf)|
 | Proposal Report |[Proposal link](https://github.com/UBC-MDS/DSCI_591_capstone-Providence/blob/master/doc/proposal.pdf)|
 |Final Presentation|[RISE presentation](https://github.com/UBC-MDS/DSCI_591_capstone-Providence/blob/master/doc/Final_Presentation_slides.ipynb)|
 ||[.pdf slides](https://github.com/UBC-MDS/DSCI_591_capstone-Providence/blob/master/doc/Final_Presentation.pdf)|

## Setup
To install all the necessary packages, please navigate to the root directory and install the necessary packages through the following codes:

If you are using Mac, please open `Terminal` and enter the following:
```
chmod +x setup.sh
./setup.sh
```

If you are using Windows, please open any command prompt window and enter the following:
```
sh setup.sh
```

## How to use:

### Exception Count Prediction Tool:
This tool allows you to train your data and predict the number of exceptions for a given timeframe. The predicted data will be outputted into a directory under `/data/predictions/`. The predicted file would be called `predictions.csv`. To use this tool, please enter the following into terminal or command prompt:

```
cd src
python exception_prediction_gui.py
```
You can then select the file you want to train with (i.e. `exception_hours.csv`), and input the start and end date of the prediction timeframe.

### Urgent Exception Prediction Tool:

### Exception Classification Tool:
