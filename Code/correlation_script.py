import re
import numpy as np
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt

from matplotlib import cm as cm
from os import listdir
from os.path import isfile, join


cc_names = [re.sub('.csv', '', f) for f in listdir('Top100/') if isfile(join('Top100/', f))]
cc_names.sort()

cc_df = pd.DataFrame()

fields = ['Date', 'Open']


for currency in cc_names:
    # Load CSV
    df = pd.read_csv('Top100/' + currency + '.csv', usecols=fields)

    # Set Date as index and correct date type
    df.Date = pd.to_datetime(df.Date)
    df.set_index('Date', inplace=True)

    # Rename open column to crypto name
    df.rename(columns={'Open': currency}, inplace=True)

    # Add to principal crypto df
    cc_df = pd.concat([cc_df, df], axis=1, join_axes=[df.index])

cc_df.sort_index(inplace=True)

# cc_df = cc_df['2017-06-07':'2017-09-22']
correlations = cc_df.corr(method='pearson')
# correlations.to_csv("crypcorrelation.csv")

# Create a mask to display only lower triangle
mask = np.zeros_like(correlations)
mask[np.triu_indices_from(mask)] = True

# Create a heatmap with the mask
sb.heatmap(correlations, cmap='RdYlGn_r', vmax=1.0, vmin=-1.0 , mask = mask, linewidths=2.5)

# Show the plot
plt.yticks(rotation=0, size=6)
plt.xticks(rotation=90, size=6)
plt.show()
