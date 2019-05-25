import numpy as np
import glob
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from random import randint
from collections import defaultdict
PATH = r"C:\Users\Domen Brunček\Desktop\FRI\4 semester\Data Mining\Project\podatki\filtered_data\0\export_2019-02-23.csv"


class ModelUsersWithNoClicks:
    def __init__(self, path):
        self.all_files = glob.glob(path)
        self.df = self.process_data()
        self.matrix = self.make_matrix()

    def process_data(self):
        original_df = pd.concat((pd.read_csv(f, header=0, sep='\t', usecols=[3, 9], names=["UserID", "SiteCategory"], dtype={"UserID": np.int64, "siteCategory": np.float}) for f in self.all_files), ignore_index=True)
        df = original_df.loc[(original_df["SiteCategory"] != 0)]
        df = df.groupby(["UserID", "SiteCategory"]).size()
        df = df.groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).reset_index()
        df.rename(columns={df.columns[2]: "Size"}, inplace=True)
        return df

    def make_matrix(self):
        users = self.df["UserID"].unique()[:-1]  # vsi unikatni userji (no duplicates)
        categories = self.df["SiteCategory"].unique()[:-1]  # vse unikatne kategorija

        vector_users = defaultdict(dict)  # slovar slovarjev
        # user = UserID in SiteCategory in Size
        for index, user in self.df.iterrows():
            vector_users[user["UserID"]][user["SiteCategory"]] = user["Size"]  # prvi slovar so userji, kljuci so slovarji kategorij vrednosr je size(procenti)

        # fill matrix rows with 0
        matrika = []
        for _ in range(0, len(users)):
            row = []
            for _ in range(0, len(categories)):
                row.append(0)
            matrika.append(row)

        # skozi vse userje (i = vrstica) in skozi vse kategorije (j = stolpec)
        for i, user in enumerate(users):
            for j, category in enumerate(categories):
                if user in vector_users and category in vector_users[user]:
                    matrika[i][j] = vector_users[user][category]
        return np.array(matrika)

    def kMeans(self, k, plot=False):
        embedding = PCA(n_components=2)
        dimension_reduce = embedding.fit_transform(self.matrix[:100])
        print(dimension_reduce)

        colors = ["#%06X" % randint(0, 0xFFFFFF) for i in range(k)]
        kmeans = KMeans(n_clusters=k, max_iter=1000).fit(dimension_reduce)
        labels = kmeans.labels_
        centroids = kmeans.cluster_centers_
        if plot: self.plot(dimension_reduce, colors, labels, centroids)

    def plot(self, dimensions, colors, labels, centroids):
        print("plot")
        for c, x in zip(labels, dimensions):
            plt.plot(x[0], x[1], ".", color=colors[c], markersize=10.0)
        for x, y in centroids:
            plt.plot(x, y, "x", markersize=5, color="black")
        plt.show()
        print("plotted")

    def show_df(self):
        print(self.matrix)


a = ModelUsersWithNoClicks(PATH)
a.kMeans(5, True)
