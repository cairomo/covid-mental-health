# Covid-19 effects on mental health dataset and Dash app

COVID-19 data was downloaded from [CDC](https://data.cdc.gov/), YouGov data was downloaded from [YouGov Covid-19 tracker](https://github.com/YouGov-Data/covid-19-tracker)

## Getting Started

### Running the app locally

First create a virtual environment with conda or venv inside a temp folder, then activate it.

```
virtualenv venv

# or using conda
conda create --name ds4a py36 python=3.6
conda activate ds4a

# Windows
venv\Scripts\activate
# Or Linux
source venv/bin/activate

```

Clone the git repo, then install the requirements with pip

```

git clone https://github.com/cairomo/covid-mental-health
cd covid-mental-health
pip install -r requirements.txt

```

Run the app

```

python app.py

```

App based on [this dash smaple app](https://github.com/plotly/dash-sample-apps/tree/master/apps/dash-opioid-epidemic)
