import re
import numpy as np
import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt

class Correlation:
    def __init__(self, data_dir):
        from os import listdir
        from os.path import isfile, join

        self.data_dir = data_dir
        self.cc_names = [re.sub('.csv', '', f) for f in listdir(data_dir) if isfile(join(data_dir, f))]
        self.cc_names.sort()

    def gen_time_series_df(self):
        """
        Generates a pandas dataframe from coins on data_dir with cols:
        Data  Currency1 Currency2 Currency3 ...
        """
        cc_df = pd.DataFrame()

        for currency in self.cc_names:
            df = self.__read_currency_csv(currency)
            df = self.__set_date_as_index(df)
            df = df.rename(columns={'Open': currency})

            cc_df = pd.concat([cc_df, df], axis=1)

        cc_df.sort_index(inplace=True)

        return cc_df

    def calc_corr(self):
        """
        Calculates correlation from gen_time_series_df() method
        """
        return self.gen_time_series_df().corr(method='pearson')

    def plot_corr_heatmap(self):
        """
        It uses seaborn to plot a heatmap from calc_corr() method
        """
        sn.heatmap(self.calc_corr(), cmap='RdYlGn_r', vmax=1.0, vmin=-1.0, linewidths=0.5)

        plt.yticks(np.arange(len(self.cc_names)), self.cc_names, rotation=0)
        plt.xticks(np.arange(len(self.cc_names)), self.cc_names, rotation=90)

        plt.show()

    def plot_clustermap(self):
        """
        It uses seaborn to plot a clusterized heatmap with dendrograms on
        the axes
        """

        cm = sn.clustermap(self.calc_corr(), cmap='RdYlGn_r', vmax=1.0, vmin=-1.0, linewidths=0.5)

        plt.setp(cm.ax_heatmap.yaxis.get_majorticklabels(), rotation=0)
        plt.setp(cm.ax_heatmap.xaxis.get_majorticklabels(), rotation=90)

        plt.show()

    def plot_dendrogram(self, method='average'):
        from scipy.cluster.hierarchy import dendrogram, linkage

        dendrogram(linkage(self.calc_corr(), method))

        plt.xticks(size=12)
        plt.show()

    def top_linear_correlated(self, i=5):
        corr = self.calc_corr()
        top_dict = {currency: len(corr[currency][corr[currency] > 0.9]) for currency in corr}
        top_currencies = zip(top_dict.values(), top_dict.keys())
        top_currencies.sort(reverse=True)
        return top_currencies[:5]

    def top_inverse_correlated(self, i=5):
        corr = self.calc_corr()
        top_dict = {currency: len(corr[currency][corr[currency] < -0.6]) for currency in corr}
        top_currencies = zip(top_dict.values(), top_dict.keys())
        top_currencies.sort(reverse=True)
        return top_currencies[:5]

    def __read_currency_csv(self, currency):
        return pd.read_csv(self.data_dir + currency + '.csv', usecols=['Date', 'Open'])

    def __set_date_as_index(self, df):
        df.Date = pd.to_datetime(df.Date)
        df.set_index('Date', inplace=True)
        return df
