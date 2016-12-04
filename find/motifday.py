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
def word2num(w):
    w=w.replace(u"男","1")
    w=w.replace(u"女","0")
    w=w.replace(u"硕士","2")
    w=w.replace(u"本科","1")
    w=w.replace(u"博士","3")
    t=w.split("|")
    return (t[1],t[2]+"|"+t[3]+"|"+t[4]+"|"+t[5]+"|"+t[6])

def iso(m,l):
    b=nx.DiGraph(eval(m))
    for a in l:
        if len(a)!=len(m):
            continue
        if nx.is_isomorphic(nx.DiGraph(eval(a)),b):
            return a
    return m
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
def datemot(l):
    lll=location_to_motif_anddate(l).iterms()
    days=[]
    for i in lll:
        if dic[str(i[list(i.keys())[0]])] <4:
            days.append(list(i.keys())[0])
    print(days)
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
def buildingfunc(s):
    if s.find(u"陈瑞球")!=-1:
        return u"陈瑞球"
    elif s.find(u"图书馆")!=-1 and s.find(u"包玉刚")==-1:
        return u"图书馆"
    elif s.find(u"媒体与设计实验室")!=-1:
        return u"媒体与设计实验室"
    elif s.find(u"机械与动力工程学院")!=-1:
        return u"机械与动力工程学院"
    elif s.find(u"东中院")!=-1:
        return u"东中院"
    elif s.find(u"校医院")!=-1:
        return u"校医院"
    elif s.find(u"药学楼")!=-1:
        return u"药学楼"
方面






















































































































































































































3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333LLLLLLLLLLLLK
';K;return u"材料楼"
    elif s.find(u"东中院")!=-1:
        return u"东中院"
    elif s.find(u"电信群楼")!=-1:
        return u"电信群楼"
    elif s.find(u"木兰学院")!=-1:
        return u"木兰学院"
    elif s.find(u"分析测试中心")!=-1:
        return u"分析测试中心"
    elif s.find(u"农学生物学院")!=-1:
        return u"农学生物学院"
    elif s.find(u"上交通中心")!=-1:
        return u"闵行候车室"
    elif s.find(u"航空航天学院")!=-1:
        return u"航空航天学院"
    elif s.find(u"系统生物研究院")!=-1:
        return u"系统生物研究院"
    else:
        return s
def lis2str(l):
    n=10
    s=""
    t=sorted(l,key=lambda x:x[1],reverse=True)
    if len(t)<n:
        for i in range(len(t)):
            s+=t[i][0]+":"+str(t[i][1])+"|"
        return s
    for i in range(n):
        s+=t[i][0]+":"+str(t[i][1])+"|"
    return s
if __name__ == "__main__":
    # This program is going to get people who has attended the activity,get their all motif
    # and motif frequence, also have to get date,motif tuple to see if their motifs ok
    name="l206004"
    sc = SparkContext(appName="PythonWordCount")


    ##    ALL
    info=sc.textFile("./NEWNET/nuser", 1)\
        .map(word2num)
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
    chang=place.map(lambda x:(x.split(",")[0],x.split(",")[2])).mapValues(buildingfunc)\
        .map(lambda x:((x[0],x[1]),1))\
        .reduceByKey(add)

    low=chang.filter(lambda x:x[1]<=10).map(lambda x:(x[0][1],1)).reduceByKey(add)
    high=chang.filter(lambda x:x[1]>10).map(lambda x:(x[0][1],1)).reduceByKey(add)
    low=low.join(high).filter(lambda x:x[1][0]>x[1][1]).map(lambda x:x[0])
    low.saveAsTextFile(sys.argv[1])
    # place=place.map(lambda x:((x.split(",")[0],x.split(",")[1].split(" ")[0]),x.split(",")[2]))\
    #         .mapValues(buildingfunc)\
    #         .groupByKey().mapValues(list).mapValues(lambda x:list(set(x))).flatMapValues(lambda x:x)
    # # day=lines.mapValues(location_to_motif_anddate).mapValues(lambda x:dic2str(x))\
    # #     .join(freq)\
    # #     .mapValues(lambda x:motfreq(x[0],x[1]))\
    # #     .flatMapValues(lambda x:x)\
    # #     .map(lambda x:((x[0],x[1].split("|")[0]),x[1]))\
    # #     .join(place).map(lambda x:x[0][0]+"||"+x[1][0]+"||"+x[1][1])
    # day=lines.mapValues(location_to_motif_anddate).mapValues(lambda x:dic2str(x))\
    #     .join(freq)\
    #     .mapValues(lambda x:motfreq(x[0],x[1]))\
    #     .flatMapValues(lambda x:x)\
    #     .map(lambda x:((x[0],x[1].split("|")[0]),x[1]))\
    #     .join(place)\
    #     .map(lambda x:((x[0][0],x[1][1]),x[0][0]+"||"+x[1][0]+"||"+x[1][1]))\
    #     .join(chang)\
    #     .map(lambda x:x[1])
    # day.saveAsTextFile(sys.argv[1])
    # # # 94059437||2014-11-04|{0: [1], 1: [2], 2: [0]}|{0: [1], 1: [0]}|10||东上院
    #
    # #######   DAYANDPLACE
    # # easy=day.map(lambda x:((x.split("||")[1].split("|")[0],x.split("||")[2]),1))\
    # #     .reduceByKey(add)
    # # when=day.map(lambda x:((x.split("||")[1].split("|")[0],x.split("||")[2]),x.split("||")[1]))\
    # #              .filter(lambda x: int(x[1].split("|")[-1])<3)\
    # #              .mapValues(abplace).filter(lambda x:x[1]<3 and x[1]>0)\
    # #             .map(lambda x:((x[0],x[1]),1))\
    # #             .reduceByKey(add)\
    # #             .map(lambda x:(x[0][0],(x[0][1],x[1])))\
    # #             .groupByKey().mapValues(list).mapValues(onetwo)
    # # mday=day.map(lambda x:((x.split("||")[1].split("|")[0],x.split("||")[2]),\
    # #                       int(x.split("||")[1].split("|")[-1]))).filter(lambda x:x[1]<3)\
    # #                         .mapValues(lambda x:1).reduceByKey(add)
    # # mday=easy.join(mday).mapValues(lambda x:str(x[0])+"|"+str(x[1]))\
    # #     .join(when).map(lambda x:x[0][0]+"|"+x[0][1]+"|"+str(x[1][0])+"|"+x[1][1])
    # # mday.saveAsTextFile(sys.argv[1]+"dayandplace")
    #
    # ######    ABNORMAL DISCOVER
    # # 94059437||2014-11-04|{0: [1], 1: [2], 2: [0]}|{0: [1], 1: [0]}|10||东上院
    # # day=sc.textFile("./paper/1560all",1).map(lambda x:(x.split("||")[1].split("|")[0],x)).cache()
    # # day=day.map(lambda x:(x.split("||")[1].split("|")[0],x)).cache()
    # # ab=day.filter(lambda x:int(x[1].split("||")[1].split("|")[3])<3)\
    # #     .map(lambda x:((x[0],x[1].split("||")[2]),1)).reduceByKey(add)\
    # #     .map(lambda x:(x[0][0],(x[0][1],x[1]))).groupByKey()\
    # #     .mapValues(list).mapValues(lis2str).map(lambda x:x[0]+"|"+x[1])
    # ac=day.map(lambda x:((x[0],x[1].split("||")[2]),1)).reduceByKey(add)\
    #     .map(lambda x:(x[0][0],(x[0][1],x[1]))).groupByKey()\
    #     .mapValues(list).mapValues(lis2str).map(lambda x:x[0]+"|"+x[1])
    # # for i in ab:
    # #     print(i)
    # ab.saveAsTextFile(sys.argv[1])
    # ac.saveAsTextFile(sys.argv[1]+"al")
    # when=day.map(lambda x:((x.split("||")[1].split("|")[0],x.split("||")[2]),x.split("||")[1]))\
    #              .filter(lambda x: int(x[1].split("|")[-1])<4)\
    #              .mapValues(abplace).filter(lambda x:x[1]<3  and x[1]>0)\
    #             .map(lambda x:((x[0],x[1]),1))\
    #             .reduceByKey(add)\
    #             .map(lambda x:(x[0][0],(x[0][1],x[1])))\
    #             .groupByKey().mapValues(list).mapValues(onetwo)
    # mday=day.map(lambda x:((x.split("||")[1].split("|")[0],x.split("||")[2]),\
    #                       int(x.split("||")[1].split("|")[-1]))).filter(lambda x:x[1]<4)\
    #                         .mapValues(lambda x:1).reduceByKey(add)
    # mday=easy.join(mday).mapValues(lambda x:str(x[0])+"|"+str(x[1]))\
    #     .join(when).map(lambda x:x[0][0]+"|"+x[0][1]+"|"+str(x[1][0])+"|"+x[1][1])
    # mday.saveAsTextFile(sys.argv[1])
    print("******************OK***********************")
    sc.stop()