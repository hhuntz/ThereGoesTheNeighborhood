# ThereGoesTheNeighborhood

## Files

tract_similarity_match.ipynb
  - Divide control and treatment groups, and apply propensity score matching.

Data_Prep_DID.ipynb
  - Prepare data needed for later Difference-in-Difference analysis.

Average Growth Rate Comparison.ipynb
  - Compare control and treatment groups.

Growth Rate Comparison.png
  - Histogram (result image) generated from 'Average Growth Rate Comparison'.

Linear Regression .ipynb
  - Linear regression model to explore the relationships and p-values, also check the validity of the results got from 'Average Growth Rate Comparison'.

Scatter Plot.png
  - Scatter plots of how outcome variable changes vs. different cumulative store months, outliers removed.

Linear Regression Results.csv
  - P values and coefficients got from the linear regression model.


## Run Code

1. Open Average Growth Rate Comparison.ipynb, click Cell -> Run All on the menu bar. Then, a group of histograms showing the general trend of difference between control and treatment group will be generated.
2. Open Linear Regression .ipynb, click Cell -> Run All on the menu bar. Then, separate linear models for each outcome variable will be created and fitted. Their corresponding coefficients and p values will show and be exported to Linear Regression Results.csv. In the same notebook, a group of scatter plots showing how outcome variable changes vs. different cumulative store months (outliers removed) can also be seen.


