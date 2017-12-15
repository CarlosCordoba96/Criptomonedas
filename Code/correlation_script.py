import re
import pandas as pd

from os import listdir
from os.path import isfile, join


cc_names = [re.sub('.csv', '', f) for f in listdir('Top100/') if isfile(join('Top100/', f))]

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

cc_df.corr().to_csv("crypcorrelation.csv")
