# EDaM - Extracting Data Metadata

With EDaM, you can get detailed information about your data.

## Installation
Make sure you have a version of Python3 installed on your device (https://www.python.org/downloads/).
Go to the terminal and check your version with `python3 --version`. 

In the project root directory, run the following commands:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

after installing all requirements navigate to gui file and run.

```bash
streamlit run app.py
```
open this link http://localhost:8501/ in your browser. Then have fun 😊

### Statistical Metrics
the metrics implemented in EDaM are as follows:

#### Numeric Metrics
`min`: Minimum of a property \
`max`: Maximum of a property \
`mean`: Mean of a property \
`median`: 50th percentile of a property \
`std`: Standard deviation \
`mode`: Most common value \
`skewness`: Asymmetry of the distribution \
`kurtosis`: Peakedness or tail heaviness of the distribution \
`mad`: Mean absolute deviation from the median \
`histogram`: Histograms of distribution of values \
`histogram_plot`: Histograms of distribution of values and additionally a plot of the histogram saved as png \
`quartiles`: 25th, 50th and 75th quantile \
`iqr`: Difference between first and third quartile \
`range`: Range
 

#### Text Metrics
`min_length`: String with smallest number of characters \
`max_length`: String with largest number of characters \
`avg_length`: Average string length \
`num_unique_strings`: Number of unique strings


#### Boolean Metrics
`true_count`: Number of `True` values  
`false_count`: Number of `False` values  
`true_ratio`: Ratio of `True` values (True count divided by total number of elements)  
`false_ratio`: Ratio of `False` values (False count divided by total number of elements)  
`mode`: Most frequent Boolean value (`True` or `False`)


#### Categorical Metrics
`num_categories`: Number of unique categories \
`mode`: Most common category \
`frequency_dist`: Distribution of category frequency


#### Array Metrics
`avg_count`: Average number of elements in the array \
`min_count`: Smallest number of elements in the array \
`max_count`: Largest number of elements in the array \
`avg_length`: : Average length of strings per array (first calculate the average string length for each array, then take the mean across arrays) \
`min_length`: Smallest string of all elements in all arrays \
`max_length`: Longest string of all elements in all arrays \
`avg_value`: Average of numerical values per array (first calculate the mean of each array, then take the mean across arrays) \
`min_value`: Smallest value in any array \
`max_value`: Largest value in any array


