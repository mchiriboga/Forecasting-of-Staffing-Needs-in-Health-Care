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
 |Proposal Presentation|[RISE presentation](https://github.com/UBC-MDS/DSCI_591_capstone-Providence/blob/master/doc/1.Proposal_Presentation.ipynb)|
 ||[.pdf slides](https://github.com/UBC-MDS/DSCI_591_capstone-Providence/blob/master/doc/2.Proposal_Presentation.pdf)|
 | Proposal Report |[.md](https://github.com/UBC-MDS/DSCI_591_capstone-Providence/blob/master/doc/3.Proposal_Report.md))|
 ||[rendered .pdf](https://github.com/UBC-MDS/DSCI_591_capstone-Providence/blob/master/doc/4.Proposal_Report.pdf)|
 |Final Presentation|[RISE presentation](https://github.com/UBC-MDS/DSCI_591_capstone-Providence/blob/master/doc/5.Final_Presentation_slides.ipynb)|
 ||[.pdf slides](https://github.com/UBC-MDS/DSCI_591_capstone-Providence/blob/master/doc/6.Final_Presentation.pdf)|
 |Final Report|[.Rmd](https://github.com/UBC-MDS/DSCI_591_capstone-Providence/blob/master/doc/7.Final_Report.Rmd)|
 ||[rendered .pdf](https://github.com/UBC-MDS/DSCI_591_capstone-Providence/blob/master/doc/8.Final_Report.pdf)|

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
This tool allows you to train your data an predict the number of urgent exceptions, given the productive hours of the period you want to predict. The predicted data will be saved in `/data/predictions`. The predicted file would be called `urgent_predictions.csv`. To use this tool, please enter the following into terminal or command prompt:

```
cd src
python urgent_prediction_gui.py
```

You will need a file of exception hours and a file of productive hours for past years as training data. Also you will need a file of productive hours for the period you want to predict, which can be an estimation.

### Exception Classification Tool:

The exception classification tool allows users to wrangle both `training data` and `exception data`, then use them to predict possible `EARNING_CATEGORY` for each exception. The predicted file would be called `classification_result.csv`. To use this tool, please enter the following into terminal or command prompt:

```
python src/Exception_Classification.py --raw_data_path="data/user_specified_training_data.csv" --exception_data_path="data/user_specified_exception_data.csv" --output_data_path="data"
```

You will need to specify the file containing historical data of exceptions for training data, and also the file of exceptions waiting to be fulfilled.

### Dashboard

The dashboard can be found [here](https://github.com/UBC-MDS/DSCI_591_capstone-Providence/blob/master/src/phc_dashboard.twb).

Tableau doesn’t support relative paths, meaning every data source connection in a .twb file points to an absolute path. So after cloning or forking the repo, the users will need to update the data source connections in their local machine when they first open the dashboard, ensuring the data source paths point to the correct files on their computer. For that, follow the instructions described [here](https://onlinehelp.tableau.com/current/pro/desktop/en-us/connect_basic_replace.htm).
