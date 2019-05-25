import scipy.cluster.hierarchy as sch
import scipy
import numpy as np
import glob
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import NMF
import matplotlib
import matplotlib.pyplot as plt
#from Clustering.clustering_functions import KMeans
from sklearn.decomposition import PCA

class Model1:

    def __init__(self,path):
        self.path = path
        self.all_files = glob.glob(path)
        self.df, self.df2 = self.read_to_df(self.all_files)
        self.k_clusters = 6
        self.categories = np.arange(23)
        self.users = ""
        self.labels = ""
        self.centroids = ""
        self.dimension_reduce = ""
        self.userSkupina = ""

    def read_to_df(self,all_files):
        df = pd.concat((pd.read_csv(f, header=0, sep='\t', usecols=[3, 10, 13], dtype={"Clicks": np.float},  names=["UserID", "AdIndustry", "Clicks"]) for f in all_files), ignore_index=True)
        df = df.loc[(df["AdIndustry"] != 0)] #& (df["AdIndustry"] != "0")]
        df = df.groupby(["UserID", "AdIndustry"]).sum()
        df = df.loc[df["Clicks"] > 0]
        pomozni = df.copy().reset_index()
        #df2 = df.copy().reset_index() # real clicks
        #del df2["AdIndustry"]
        #df2 = df2.groupby("UserID").sum().reset_index()
        df = df.groupby(level=0).apply(lambda x: 100 * x/x.sum()).reset_index()
        df.rename(columns={df.columns[2]: "Size"}, inplace=True)
        #self.df = df
        #self.df2 = df2
        return df,pomozni


    def build_matrix_1(self,df):
        from collections import defaultdict
        self.users = self.df["UserID"].unique() # vsi unikatni userji (no duplicates)

        vektoruser = defaultdict(dict) # slovar slovarjev

        # index je row index(tega nerabmo)
        # user = UserID in SiteCategory in Size
        for index, user in self.df.iterrows():
            vektoruser[user["UserID"]][user["AdIndustry"]] = user["Size"] # prvi slovar so userji, kljuci so slovarji kategorij vrednosr je size(procenti)

        # predpripavimo matriko, tako da vse vrednosti nastavimo na 0
        matrika=[]
        for _ in range(0,len(self.users)):
            row=[]
            for _ in range(0,len(self.categories)):
                row.append(0)
            matrika.append(row)

        # skozi vse userje (i = vrstica) in skozi vse kategorije (j = stolpec)
        for i,user in enumerate(self.users):
            for j,category in enumerate(self.categories):
                if user in vektoruser and category in vektoruser[user]:
                    matrika[i][j] = vektoruser[user][category]
        return np.array(matrika)

    def kmeans(self, k):
        self.k_clusters = k
        matrika = self.build_matrix_1(self.df)
        embedding = PCA(n_components=2)
        self.dimension_reduce =  embedding.fit_transform(matrika)
        kmeans = KMeans(n_clusters=self.k_clusters, max_iter=150).fit(self.dimension_reduce)
        self.labels = kmeans.labels_
        self.centroids = kmeans.cluster_centers_

    '''
    kmeans = KMeans(K=6, X=dimension_reduce, M=dimension_reduce, resolve_empty='singleton')
    kmeans.initialise()
    kmeans.cluster()
    clustering_results = kmeans.clustering_results
    labels = np.where(clustering_results == 1)[1]
    '''
    def plot(self):
        color = {0:"red", 1:"blue", 2:"yellow", 3:'green', 4:'violet', 5:'pink', 6: 'black'}
        for c, x in zip(self.labels, self.dimension_reduce):
            plt.plot(x[0], x[1], ".", color=color[c], markersize=10.0, alpha=0.2)

        for x,y in self.centroids:
            plt.plot(x,y,"x", color="black", markersize=20.0, alpha=0.4)
        plt.show()

    def results(self):
        matrika = []
        for _ in range(self.k_clusters):
            row = []
            for _ in self.categories:
                row.append(0)
            matrika.append(row)

        self.userSkupina = { i: set() for i in range(self.k_clusters)}

        for i,x in enumerate(self.users):
            poizvedba = self.df2.loc[self.df2["UserID"] == x]
            kliki = poizvedba["Clicks"].sum()
            self.userSkupina[self.labels[i]].add((x,kliki))

        # TODO: Izboljšaj to gradnjo matrike, ker je počasnejša od tvoje mame.
        for k,v in self.userSkupina.items(): # k = gruca a.k.a vrstice
            vsi = sum(n for _,n in v)    # vsi kliki v gruci
            for i in self.categories:    # za vsako kategorijo
                sestevek = 0
                for user,_ in v:         # za vsakega userja v gruci gledam koliko klikov na kategorijo ma
                    sql = self.df2.loc[(self.df2["UserID"] == user) & (self.df2["AdIndustry"] == i)]
                    if not sql.empty:
                        sestevek += sql.values[0][2]
                matrika[k][i] = sestevek/vsi
        return np.array(matrika)


modelMario = Model1(r"C:\dataMining\0\export_2019-02-23.csv")
modelMario.kmeans(6)
print(modelMario.results())