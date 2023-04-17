# There Goes the Neighborhood: Localized Economic Effects of Marijuana Retail Sales in Colorado
You can see the research paper resulting from this work [here](https://docs.google.com/document/d/1b-B1AH5x936uNTl-BACd1XyukfQ1K_p6i-C_gLP3j04/edit?usp=sharing).

## Recreating the Results:

Here is how to generate the result files:

1. Download the zip file from current repository.
2. Open Average Growth Rate Comparison.ipynb, click ***Cell -> Run All*** on the menu bar. Then, a group of histograms showing the general trend of difference between control and treatment group will be generated.
3. Open Linear Regression .ipynb, click ***Cell -> Run All*** on the menu bar. Then, separate linear models for each outcome variable will be created and fitted. Their corresponding coefficients and p values will show up and be exported to Linear Regression Results.csv. In the same notebook, a group of scatter plots showing how outcome variable changes vs. different cumulative store months (outliers removed) can also be seen.

## Recreating the Data:

If you'd additionally like to recreate our data gathering processes, the original CO state license information can be found [here](https://drive.google.com/drive/folders/0B-ZjnNx-rL_mTHU4dHhiX1dEbU0?resourcekey=0-j0x5DFB5M-7nNRLa-8g2Zw). The **get_data.py** file includes basic instructions and all of our code used to manipulate these original manually-collected records, make API calls for Google Maps address matching and geocoding, and transform and save the resulting data. The **get_census_data.ipynb** notebook can be run in full to collect and save relevant tract-level Census variables. 

## A Guide to the Files:

**tract_similarity_match.ipynb**
  - Divide control and treatment groups, and apply propensity score matching.

**Data_Prep_DID.ipynb**
  - Prepare data needed for later Difference-in-Difference analysis.

**Average Growth Rate Comparison.ipynb**
  - Compare control and treatment groups.

**Growth Rate Comparison.png**
  - Histogram (result image) generated from 'Average Growth Rate Comparison'.

**Linear Regression.ipynb**
  - Linear regression model to explore the relationships and p-values, also check the validity of the results got from 'Average Growth Rate Comparison'.

**Scatter Plot.png**
  - Scatter plots of how outcome variable changes vs. different cumulative store months, outliers removed.

**Linear Regression Results.csv**
  - P values and coefficients from the linear regression model.
