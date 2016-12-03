# -*- coding:utf-8 -*- ＃
import sys
import time
from operator import add
from pyspark import SparkContext
from numpy import *
import operator
import os
if __name__ == "__main__":
    sc = SparkContext(appName="PythonWordCount")
    lines = sc.textFile("./tc/user.csv", 1)
    item=sc.textFile("./tc/item.csv",1).map(lambda x:(x.split(",")[0],1)).distinct()
    lines=lines.map(lambda x:(x.split(",")[1],x)).join(item).map(lambda x:x[1][0])
    buyer=lines.filter(lambda x:x.split(",")[5]<"2014-12-18" and x.split(",")[2]=="4")\
                .map(lambda x:(x.split(",")[0],1)).reduceByKey(add)\
                .filter(lambda x:x[1]>2).distinct()
    ab=lines.map(lambda x:(x.split(",")[0],x)).join(buyer).map(lambda x:x[1][0])
    see=ab.filter(lambda x: x.split(",")[2]=='1' and ("2014-12-17" in x or "2014-12-16" in x))\
                .map(lambda x:(x.split(",")[0]+","+x.split(",")[1]),1).reduceByKey(add).filter(lambda x:x[1]<=2)
    fold=ab.filter(lambda x: x.split(",")[2]=='2' and "2014-12-17 23" in x)\
                .map(lambda x:x.split(",")[0]+","+x.split(",")[1]).distinct().map(lambda x:(x,1))
    car=ab.filter(lambda x: x.split(",")[2]=='3' and ("2014-12-17" in x or "2014-12-16" in x))\
                .map(lambda x:x.split(",")[0]+","+x.split(",")[1]).distinct().map(lambda x:(x,1))
    b=lines.filter(lambda x: x.split(",")[2]=='4' and "2014-12-18" in x)\
                .map(lambda x:x.split(",")[0]+","+x.split(",")[1]).distinct().map(lambda x:(x,1))
    c=ab.filter(lambda x:x.split(",")[2]=='4' and ("2014-12-17" in x or "2014-12-16" in x))\
                .map(lambda x:x.split(",")[0]+","+x.split(",")[1]).distinct().map(lambda x:(x,1))
    # a=see.leftOuterJoin(c).filter(lambda x:x[1][1]==None)
    # see.saveAsTextFile(sys.argv[1])
    a=car.leftOuterJoin(c).filter(lambda x:x[1][1]==None).distinct()
    # a=a.union(car).distinct()
    c=a.join(b).distinct().count()
    # lines.saveAsTextFile(sys.argv[1])
    # # b=lines.filter(lambda x:x[-1]=='|').distinct().sortBy(lambda x:x.split("|")[2]+x.split(" ")[0])
    print("******************OK***********************"+str(a.count())+","+str(b.count())+","+str(c))
    sc.stop()