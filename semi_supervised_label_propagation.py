#-*- coding: utf-8 -*-
#%matplotlib inline
from matplotlib.font_manager import FontProperties  
import matplotlib.pyplot as plt  
import numpy as np
import pandas as pd
import os
plt.rcParams['font.sans-serif'] = ['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
s=pd.read_csv('/Users/ppj/actday.csv',header=None)
s.columns=['day','s','fre','jj','pp']
s.fre=1/s.fre
cluster_s=s.loc[:,['day','fre','s']]   ##'s'为总天数
index_label1=cluster_s[cluster_s.day>100][cluster_s.fre>3.5].index    ###10.06%  占比   标为较活跃人群
index_label2=cluster_s[cluster_s.day<20][cluster_s.fre<2].index    #10.2%       标为不太活跃人群
cluster_s['label']=-1                            ##未标定的label定为-1
cluster_s.label[index_label1]=1
cluster_s.label[index_label2]=0
###用于训练时，需要将数据缩小化，以便效果明显
cluster_s.day=cluster_s.day/10
cluster_s.s=cluster_s.s/10
### X为训练数据   y为label
X=np.array(cluster_s.loc[:,["day",'fre','s']])
y=np.array(cluster_s.label)

#label propagation
print(__doc__)

# Authors: Clay Woolam <clay@woolam.org>
# License: BSD

import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn import svm
from sklearn.semi_supervised import label_propagation

##  训练数据
ls100 = (label_propagation.LabelSpreading().fit(X, y), y)
#rbf_svc = (svm.SVC(kernel='rbf').fit(X, y), y)

clf=ls100[0]
df1=pd.DataFrame(X,columns=['day','fre','s'])
df1['label']=clf.predict(X)
df1['label0']=cluster_s.label
location=np.array(df1.loc[:,['day','fre']])
labels=np.array(df1.loc[:,'label'])

####plot label propgation
plt.figure(1)
plt.subplot(1, 1, 1)
import numpy as np
from itertools import cycle
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn.datasets.samples_generator import make_blobs
#################################################################################
colors = cycle('bg')
for k, col in zip(range(2), colors):
    my_members = labels == k                       #就是把同种标签的坐标都取出来，并将同种标签的都打上同种颜色
    #cluster_center = cluster_centers[k]
    plt.plot(location[my_members, 0], location[my_members, 1], col + '.')
    #plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
             #markeredgecolor='k', markersize=7)
#plt.title('Estimated number of clusters: %d,the bandwidth: %.4f' % (n_clusters_,bandwidth))
plt.savefig('semi_supervised_label_propogation.png')

###修改未标定的label0 -1 改为2 以便画图
def change_label0(label0):
    if label0==-1:
        return 2
    else:
        return label0

####plot  原始未标定和部分标定图
df1.label0=df1.label0.map(change_label0)

location0=np.array(df1.loc[:,['day','fre']])
labels0=np.array(df1.loc[:,'label0'])
plt.figure(1)
plt.subplot(1, 1, 1)
import numpy as np
from itertools import cycle
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn.datasets.samples_generator import make_blobs
#################################################################################
colors = cycle('bgy')
for k, col in zip(range(3), colors):
    my_members = labels0 == k                       #就是把同种标签的坐标都取出来，并将同种标签的都打上同种颜色
    #cluster_center = cluster_centers[k]
    plt.plot(location0[my_members, 0], location[my_members, 1], col + '.')
    #plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
             #markeredgecolor='k', markersize=7)
#plt.title('Estimated number of clusters: %d,the bandwidth: %.4f' % (n_clusters_,bandwidth))
plt.savefig(u'标定与未标定的.png')


