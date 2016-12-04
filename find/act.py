# -*- coding:utf-8 -*- ＃
import sys
import time
from operator import add
from pyspark import SparkContext
from numpy import *
import networkx as nx
import operator
import os
import scipy as sp
import numpy as np
import scipy.stats as ss
CONSTANT=300


def location_to_motif(locations):
    dateFlag = ''
    motifList = []
    for i in range(0,len(locations)):
        t=locations[i].split(" ")
        _date = t[1]
        _time = t[2]
        station = t[0]
        if dateFlag=='' or \
        time.mktime(time.strptime(_date+" "+_time,"%Y-%m-%d %H:%M:%S"))-time.mktime(time.strptime(dateFlag,"%Y-%m-%d"))>=97200 or\
                (_time>"03 " and timeFlag<"03"):#if another day, initialize
            dateFlag = _date
            timeFlag = _time
            motifList.append({})
            nodeDict = {}
        if station not in nodeDict.keys():#map station name to node num
            nodeDict[station] = len(nodeDict)
        if nodeDict[station] not in motifList[-1].keys():#add the appeared node to today's motif graph
            motifList[-1][nodeDict[station]] = []
        if (i+1)<len(locations):
            ndate=locations[i+1].split(' ')[1]
            ntime=locations[i+1].split(' ')[2]
            t=time.mktime(time.strptime(_date,"%Y-%m-%d"))
            tt=time.mktime(time.strptime(ndate+" "+ntime,"%Y-%m-%d %H:%M:%S"))
            if tt-t<97200 and _time>"03":#yet is today's
                n_station = locations[i+1].split(' ')[0]
                if not n_station==station:
                    if n_station not in nodeDict.keys():
                        nodeDict[n_station] = len(nodeDict)
                    if not motifList[-1][nodeDict[station]].count(nodeDict[n_station])>0:
                        motifList[-1][nodeDict[station]].append(nodeDict[n_station])

    return motifList

def location_to_motif_anddate(locations):
    dateFlag = ''
    motifList = []
    for i in range(0,len(locations)):
        t=locations[i].split(" ")
        _date = t[1]
        _time = t[2]
        station = t[0]
        if dateFlag=='' or \
         time.mktime(time.strptime(_date+" "+_time,"%Y-%m-%d %H:%M:%S"))-time.mktime(time.strptime(dateFlag,"%Y-%m-%d"))>=97200 or\
                (_time>"03 " and timeFlag<"03"):
            dateFlag = _date #如果不进行这一步的话，说明理论上还要划归到昨天，因此后续轨迹全要划到昨天MOTIF
            shit={}
            timeFlag = _time
            shit[_date]={}
            motifList.append(shit)
            nodeDict = {}
        if station not in nodeDict.keys():#map station name to node num
            nodeDict[station] = len(nodeDict)
        if nodeDict[station] not in shit[dateFlag].keys():#add the appeared node to today's motif graph
            shit[dateFlag][nodeDict[station]] = []
        if (i+1)<len(locations):
            ndate=locations[i+1].split(' ')[1]
            ntime=locations[i+1].split(' ')[2]
            t=time.mktime(time.strptime(_date,"%Y-%m-%d"))
            tt=time.mktime(time.strptime(ndate+" "+ntime,"%Y-%m-%d %H:%M:%S"))
            if (tt-t<97200) and _time>"03":#yet is today's
                n_station = locations[i+1].split(' ')[0]
                if not n_station==station:
                    if n_station not in nodeDict.keys():
                        nodeDict[n_station] = len(nodeDict)
                    if not shit[dateFlag][nodeDict[station]].count(nodeDict[n_station])>0:
                        shit[dateFlag][nodeDict[station]].append(nodeDict[n_station])
    return motifList
def style_conv(list_dict):
    dicts = str(list_dict).strip('[]')
    dicts = dicts.split(', {')
    rsl = []
    for i in range(0, len(dicts)):
        if i ==0:
            rsl.append(dicts[i])
        else:
            rsl.append('{' + dicts[i])
    return rsl
def list2dict(l):
    d={}
    for i in l:
        d[int(i.split("|")[1])]=i.split("|")[0]
    return d
def sor(l):
    return sorted(l,key=lambda x:x.split(" ")[1]+x.split(" ")[2]+x.split(" ")[0])
def frequence(l):
    ll=location_to_motif(l)
    dic={}
    for i in ll:
        i=str(i)
        for name in mlist:
            if len(i)!=len(name):
                continue
            if i==name:
                break
            if nx.is_isomorphic(nx.DiGraph(eval(i)),nx.DiGraph(eval(name))):
                i=name
        if i in dic.keys():
            dic[i]+=1
        else:
            dic[i]=1

    d=sorted(dic.items(),key=lambda x:x[1],reverse=True)
    long=d[0][0]
    if len(d)>=2:
        if d[1][1]>=30 and len(d[1][0])>len(d[0][0]):
            long=d[1][0]
    return (dic,long)
def motfreq(l,dic):
    re=[]
    for i in l:
        j=i.split("|")[1]
        if j in dic[0].keys():
            re.append(i+"|"+dic[1]+"|"+str(dic[0][j]))
    return re
def dic2str(dl):
    r=[]
    for d in dl:
        for k in d.keys():
            dname=str(d[k])
            for name in mlist:
                if len(dname)!=len(name):
                    continue
                if dname==name:
                    r.append(k+"|"+name)
                    break
                if nx.is_isomorphic(nx.DiGraph(d[k]),nx.DiGraph(eval(name))):
                    r.append(k+"|"+name)
                    break
    return r
def abplace(l):
    mot=l.split("|")[1]
    basic=l.split("|")[2]
    G=nx.DiGraph(eval(mot))
    H=nx.DiGraph(eval(basic))
    return G.number_of_nodes()-H.number_of_nodes()
def onetwo(l):
    if len(l)<2:
        if l[0][0]==1:
            return str(l[0][1])+"|0"
        else :
            return "0|"+str(l[0][1])
    else :
        if l[0][0]==1:
            return str(l[0][1])+"|"+str(l[1][1])
        else :
            return str(l[1][1])+"|"+str(l[0][1])
if __name__ == "__main__":
    # This program is going to get people who has attended the activity,get their all motif
    # and motif frequence, also have to get date,motif tuple to see if their motifs ok
    name="l206004"
    sc = SparkContext(appName="PythonWordCount")


    ###    ALL
    # info=sc.textFile("./NEWNET/nuser", 1)\
    #     .map(word2num)
    mlong=sc.textFile("./paper/"+name+"0iso",1).collect()
    mlong=sorted(mlong,key=lambda x:int(x.split("|")[1]))
    mlist=[]
    for i in mlong:
        mlist.append(str(i.split("|")[0]))
    # lines=sc.textFile("./paper/all",1).map(lambda x:(x.split("||")[0],x.split("||")[1])).cache()
    lines=sc.textFile("./paper/"+name,1)
    lines = lines.map(lambda x:(x.split(" ")[0],x.split(" ")[1]+" "+x.split(" ")[2]+" "+x.split(" ")[3]))\
                .groupByKey()\
                .mapValues(list)\
                .mapValues(sor)
    freq=lines.mapValues(frequence)
    # 我们不用去的总次数来定义一个人常去的点，而是用最常见motif的模式下最多去的点来定义一个人的常去点
    place=sc.textFile("./paper/"+name+"zplace",1)\
        # to this step, we got 11001313,2014-09-15 12:09:08,第三食堂
    user=place.filter(lambda x: u"菁菁堂" in x and "2014-10-23" in x).map(lambda x:(x.split(",")[0],1))
    day=lines.mapValues(location_to_motif_anddate).mapValues(lambda x:dic2str(x))\
        .join(freq)\
        .mapValues(lambda x:motfreq(x[0],x[1]))\
        .flatMapValues(lambda x:x)
    # 94059437|2014-11-04|{0: [1], 1: [2], 2: [0]}|{0: [1], 1: [0]}
    act=day.join(user).map(lambda x:((x[1][0].split("|")[0],x[1][0].split("|")[3]),1))\
        .reduceByKey(add).filter(lambda x:int(x[0][1])<2).map(lambda x:(x[0][0],x[1]))\
        .reduceByKey(add)\
        .map(lambda x:x[0]+"|"+str(x[1]))
    all=day.map(lambda x:((x[1].split("|")[0],x[1].split("|")[3]),1))\
        .reduceByKey(add).filter(lambda x:int(x[0][1])<2).map(lambda x:(x[0][0],x[1]))\
        .reduceByKey(add)\
        .map(lambda x:x[0]+"|"+str(x[1]))

    act.saveAsTextFile(sys.argv[1])
    all.saveAsTextFile(sys.argv[1]+"al")
    # all=day.map(lambda x:((x[1].split("|")[0],x[1].split("|")[3]),1))\
    #     .reduceByKey(add).filter(lambda x:int(x[0][1])<3).map(lambda x:(x[0][0],x[1]))\
    #     .reduceByKey(add)\
    #     .map(lambda x:x[0]+"|"+str(x[1]))
    # all.saveAsTextFile(sys.argv[2])
    # 94059437,2014-11-04|{0: [1], 1: [2], 2: [0]}|{0: [1], 1: [0]}|10
    print("******************OK***********************")
    sc.stop()