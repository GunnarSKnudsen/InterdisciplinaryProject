import numpy as np
from scipy import stats

# get normally distributed data
data = np.random.normal(size=100) + 0.01


# do 1 sample ttest
ttest = stats.ttest_1samp(data, 0.0)
ttest.pvalue