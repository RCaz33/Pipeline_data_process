
import os
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
    
    
def get_data(path):
    """Agregate data from a folder

    Args:
        path (string): source of data
        
    Returns:
        pd.DataFrame(): the agregated data
    """
    wl=list()

    for f in os.listdir(path):
        if f.lower().endswith(".csv"):
                    # print(f2)
                    path2 = os.path.join(path,f)
                    data = pd.read_csv(path2,delimiter=";",header=None)
                    data[0] = data[0].apply(lambda x : round(x))
                    data.drop_duplicates(subset=0, inplace=True)
                    data.columns = [0,f[:-4]]
                    wl.append(data)
                    
    u = pd.DataFrame(data=range(4000))
    for i in range(len(wl)):
        u = pd.merge(u,wl[i], left_on=0, right_on=0,how='inner').reset_index(drop=True)
        
    u.index = u[0]
    u.drop(columns=0, inplace=True)
    u.columns =[ x[:-4] for x in  u.columns]
    
    return u


def do_ML_magic(u, n_clust):    
    """Use data to create groups with KMeans

    Args:
        u (pd.DataFrame): the data to use
        n_clust (int): the number of groups
        
    Returns:
        pd.DataFrame: the data with groups
        np.array: the weight from the PCA transformation
    """

    pca = PCA(n_components=5)
    weights = pca.fit_transform(u.T)
    kmeans = KMeans(n_clusters=n_clust, random_state=0, n_init="auto").fit(u.T)
    groups = u.T
    groups['kmeans'] = kmeans.labels_

    return groups, weights, kmeans


def get_me_the_graph(groups,n_clust):
    cmap = plt.cm.coolwarm
    values = np.linspace(0, 1, n_clust)
    colors = cmap(values)
    mm_sc = MinMaxScaler()
    offset=0

    cmap = plt.cm.coolwarm
    num_points = 3
    colors = [cmap(i / (num_points - 1)) for i in range(num_points)]
    f,ax = plt.subplots(1,3,figsize=(12,4))
    for i, y in enumerate(mm_sc.fit_transform(groups.groupby('kmeans').mean().T).T):
        ax[1].plot(y+offset,c=colors[i])
        offset+=1
        
    for i, y in enumerate(mm_sc.fit_transform(groups.groupby('kmeans').mean().T.iloc[-500:,:]).T):
        ax[2].plot(y,c=colors[i])
        
    for i, y in enumerate(mm_sc.fit_transform(groups.groupby('kmeans').mean().T.iloc[180:600,:]).T):
        ax[0].plot(y,c=colors[i])
        
    ax[0].set_title("peak D/G/D'")
    ax[1].set_title("full spectra")
    ax[2].set_title("peak 2D")

    for i in range(3):
        ax[i].set_xlabel('indexes')
        
    ax[2].legend(["group "+str(k)+" : "+str(v)+" indiv" for k,v in groups['kmeans'].value_counts().sort_index().items()],title='groupes et individus')
    st.pyplot(f)
    
def get_me_the_other_graph(groups, kmeans, weights, n_clust):
    cmap = plt.cm.coolwarm
    values = np.linspace(0, 1, n_clust)
    colors = cmap(values)
    
    f, ax = plt.subplots(1,3,figsize=(18,5))

    # colors=['red','blue','green','orange']

    sc = StandardScaler()

    # cmap={1:'red',2:'blue',3:'green',4:'orange'}
    for i in range(n_clust):
        sc.fit(groups.groupby('kmeans').mean().iloc[[i],:].values.reshape(-1,1))
        ax[0].plot(groups.columns[:-1].astype(int),
                sc.transform(groups.groupby('kmeans').mean().iloc[[i],:].values.reshape(-1,1)),
                c=colors[i])
    ax[0].legend(range(n_clust),title='group')
    ax[0].set_title("Moyennes par groupes scaled")

    ax[1].scatter(weights[:,0],weights[:,1],c=[colors[label] for label in kmeans.labels_])
    ax[1].set_title("color by group number")
    # ax[2].scatter(weights[:,0],weights[:,1],c=label[:,0])
    ax[2].set_title("spectre / catégories")

    import seaborn as sns
    sns.heatmap(groups['kmeans'].reset_index().value_counts().sort_index().reset_index().pivot_table(values='count',index='index',columns='kmeans').fillna(0), annot=True, cmap='coolwarm')
    ax[2].set_ylabel("")
    
    st.pyplot(f)