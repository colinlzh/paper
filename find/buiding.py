# -*- coding:utf-8 -*- ＃
import time
from operator import add
from pyspark import SparkContext
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

def timeconverter(s):
    t=s.split(",")
    c=time.localtime(float(t[1])/1000)
    return time.strftime("%Y-%m-%d %H:%M:%S",c)+"|"+str(float(t[2])-float(t[1]))+"|"+t[3]
if __name__ == "__main__":
    holiday=['2014-10-01', '2014-10-02', '2014-10-03', '2015-01-01', '2015-04-05', '2015-05-01', '2015-01-19', '2015-01-20', '2015-01-21', '2015-01-22', '2015-01-23', '2015-01-24', '2015-01-25', '2015-01-26', '2015-01-27', '2015-01-28', '2015-01-29', '2015-01-30', '2015-01-31', '2015-02-01', '2015-02-02', '2015-02-03', '2015-02-04', '2015-02-05', '2015-02-06', '2015-02-07', '2015-02-08', '2015-02-09', '2015-02-10', '2015-02-11', '2015-02-12', '2015-02-13', '2015-02-14', '2015-02-15', '2015-02-16', '2015-02-17', '2015-02-18', '2015-02-19', '2015-02-20', '2015-02-21', '2015-02-22', '2015-02-23', '2015-02-24', '2015-02-25', '2015-02-26', '2015-02-27', '2015-02-28']
    sc = SparkContext(appName="PythonWordCount")
    a = sc.textFile("./paper/l208003zplace",1)\
        .map(lambda x:(x.split(",")[2],1)).reduceByKey(add).map(lambda x:x[0]+"|"+str(x[1]))
    # a=a.map(lambda x:(x.split(",")[0],x.split(",")[-1])).distinct().groupByKey().mapValues(list)
    a.saveAsTextFile(sys.argv[1])
    # print(a)
    # print("******************OK***********************"+str(e.count())+","+str(ee.count())+\
    #       str(n.count())+","+str(nn.count()))
    sc.stop()