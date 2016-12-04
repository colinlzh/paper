# -*- coding:utf-8 -*- ＃
import sys
import time
from operator import add
from pyspark import SparkContext
import networkx as nx
def timeconverter(s):
    t=s.split(",")
    c=time.localtime(float(t[0])/1000)
    return (t[3],time.strftime("%Y-%m-%d %H:%M:%S",c)+","+t[2])
def key(x):
    t=x.split(",")
    return (t[0]+","+t[1].split(" ")[0])
def slice(l):
    name=u"食堂"
    d={}
    final=[]
    for i in range(len(l)):
        lll=l[i]
        t=l[i].split(" ")
        tm=int(t[2][:2])
        station=t[0]
        if (name in station) and i+1<len(l):
            next=l[i+1]
            nt=next.split(" ")
            ntime=int(nt[2][:2])
            if (name in next) and t[1]==nt[1] and ntime-tm>=2:#need to add
                low=tm
                high=ntime
                for i in l:
                    if (name in i):
                        continue
                    mt=i.split(" ")
                    mtime=mt[2][:2]
                    if low<int(mtime) and int(mtime)<high:
                        mstation=mt[0]
                        if mstation in d.keys():
                            d[mstation]+=1
                        else:
                            d[mstation]=1
                    else:
                        continue
                s=sorted(d.items(),key=lambda x:x[1],reverse=True)
                d={}
                final.append(lll)
                low=time.mktime(time.strptime(t[1]+" "+t[2],"%Y-%m-%d %H:%M:%S"))
                high=time.mktime(time.strptime(nt[1]+" "+nt[2],"%Y-%m-%d %H:%M:%S"))
                ftime=time.localtime((high-low)/2+low)
                if(len(s)>0 ):
                    final.append(s[0][0]+" "+t[1]+" "+time.strftime("%Y-%m-%d %H:%M:%S",ftime).split(" ")[1])
            else:
                final.append(l[i])
        else:
            final.append(l[i])
    return final
def sliceplace(l):
    name="Cant"
    d={}
    final=[]
    for i in range(len(l)):
        lll=l[i]
        t=l[i].split(" ")
        tm=int(t[2][:2])
        station=t[0]
        if (name in station) and i+1<len(l):
            next=l[i+1]
            nt=next.split(" ")
            ntime=int(nt[2][:2])
            if (name in next) and t[1]==nt[1] and ntime-tm>=2:#need to add
                low=tm
                high=ntime
                for i in l:  #calc the timezone what this sutdent often do
                    if (name in i):
                        continue
                    mt=i.split(" ")
                    mtime=mt[2][:2]
                    if low<int(mtime) and int(mtime)<high:  #in the time zone
                        mstation=mt[0]
                        if mstation in d.keys():
                            d[mstation]+=1
                        else:
                            d[mstation]=1
                    else:
                        continue
                s=sorted(d.items(),key=lambda x:x[1],reverse=True)
                lack=0
                for j in s:
                    lack+=j[1]
                d={}
                final.append(lll)
                low=time.mktime(time.strptime(t[1]+" "+t[2],"%Y-%m-%d %H:%M:%S"))
                high=time.mktime(time.strptime(nt[1]+" "+nt[2],"%Y-%m-%d %H:%M:%S"))
                ftime=time.localtime((high-low)/2+low)
                if(len(s)>0 and s[0][1]/lack>=0.5):
                    final.append(s[0][0]+" "+t[1]+" "+time.strftime("%Y-%m-%d %H:%M:%S",ftime).split(" ")[1])
                else:
                    final.append("unknown"+" "+t[1]+" "+time.strftime("%Y-%m-%d %H:%M:%S",ftime).split(" ")[1])
            else:
                final.append(l[i])
        else:
            final.append(l[i])
    return final
def mi(l):
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.mktime(time.strptime(l[0][1]+" "+l[0][2],"%Y-%m-%d %H:%M:%S"))-1))
def ad(l):
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.mktime(time.strptime(l[-1][1]+" "+l[-1][2],"%Y-%m-%d %H:%M:%S"))+1))
def word2num(w):
    w=w.replace(u"男","1")
    w=w.replace(u"女","0")
    w=w.replace(u"本科","1")
    w=w.replace(u"硕士","2")
    w=w.replace(u"博士","3")
    t=w.split("|")
    return (t[1],t[2]+"|"+t[3]+"|"+t[4]+"|"+t[5]+"|"+t[6])
def shower(ll):
    l=[]
    tdate=""
    shower=[]
    for line in ll:
        s=line.split(" ")
        day = s[1]
        _time = s[2]
        if tdate=="":#第一条数据强制转换为凌晨3点的宿舍
            l.append(u"宿舍"+" "+day+" "+"03:00:01")
            l.append(line)
            tdate=day
        elif tdate!=day and _time>"03":#天数转换的时候，检查是否有上一天没写入的shower数据
            if len(shower)>=1:
                l.append(u"宿舍"+" "+mi(shower))
                l.append(shower[0][0])
                l.append(u"宿舍"+" "+ad(shower))
                shower=[]
            l.append(u"宿舍"+" "+\
                     time.strftime("%Y-%m-%d",time.localtime((time.mktime(time.strptime(tdate,"%Y-%m-%d"))+86400)))\
                     +" "+"02:59:59")
            l.append(u"宿舍"+" "+day+" "+"03:00:01")
            l.append(line)
            tdate=day
        else :#天数没有转换的时候，水控转换为数据，浴室行为储存，直到遇到当天下一条非浴室行为数据
            if u"浴室" in line:
                shower.append((line,day,_time))
            #     为避免多个浴室洗澡行为，需要将洗澡储存起来
            elif u"水控" in line:
                l.append(u"宿舍"+" "+day+" "+_time)
            elif len(shower)>1:
                l.append(u"宿舍"+" "+mi(shower))
                l.append(shower[0][0])
                l.append(u"宿舍"+" "+ad(shower))
                shower=[]
            else:
                l.append(line)
    return l
def sor(l):
    return sorted(l,key=lambda x:x.split(" ")[1]+x.split(" ")[2]+x.split(" ")[0])
def merge(l):
    re=[]
    if len(l)==1:
        return l
    l=sorted(l,key=lambda x:x.split(",")[0]+x.split(",")[1]+x.split(",")[2])
    t=l[0].split(",")
    start=t[0]
    end=t[1]
    place=t[2]
    i=1
    while( i <len(l)):
        t=l[i].split(",")
        if i==len(l)-1:
            if place==t[2]:
                re.append(start+","+t[1]+","+place+","+t[3])
            else:
                re.append(l[i])
        else:
            if place==t[2]:
                end=t[1]
            else:
                re.append(start+","+end+","+place+","+t[3])
                start=t[0]
                end=t[1]
                place=t[2]
        i+=1
    return re
def motifiso(l):

    existed={}
    flag=False
    for i in l:
        name=i[0]
        number=i[1]
        lmotif=nx.DiGraph(eval(name))
        for oldname in existed.keys():
            if len(oldname)!=len(name):
                continue
            oldmotif=nx.DiGraph(eval(oldname))
            if nx.is_isomorphic(oldmotif,lmotif):
                flag=True
                existed[oldname]+=number
                break
        if not flag:
            existed[name]=number
        flag=False
    ditem=sorted(existed.items(),key= lambda x:x[1],reverse=True)
    # dnum=sorted(d.values(),reverse=True)
    s=ditem
    t=[]
    for i in range(len(ditem)):
        t.append(ditem[i][0]+"|"+str(i))
    return (s,t)
def entrolist(l,sc,index):
    l=l.reduceByKey(add).collect()
    # motif,number
    # index=sorted(index,key=lambda x: int(x=x.split("|")[1]))
    d={}
    for i in l:
        name=i[0]
        number=i[1]
        motif=nx.DiGraph(eval(name))
        for i in range(len(index)):
            indexname=index[i].split("|")[0]
            if len(indexname)!=len(name):
                continue
            if indexname==name:
                if indexname in d.keys():
                    d[indexname]+=number
                else:
                    d[indexname]=number
                break
            if nx.is_isomorphic(nx.DiGraph(eval(indexname)),motif):
                if indexname in d.keys():
                    d[indexname]+=number
                else:
                    d[indexname]=number
                break
    # index means the sorted all sutdents' motif list, use it to get a normalized result
    # d=sorted(d.items(),key= lambda x:x[1],reverse=True)
    index=sorted(index,key=lambda x: int(x=x.split("|")[1]))
    s=[]
    for count in range(50):
        indexname=index[count].split("|")[0]
        s.append(indexname+":"+str(d[indexname]))
    s=sc.parallelize(s).coalesce(1)
    return s
def location_to_motif(locations):
    dateFlag = ''
    motifList = []
    for i in range(0,len(locations)):
        t=locations[i].split(" ")
        _date = t[1]
        tm = t[2]
        station = t[0]
        if dateFlag=='' or \
        time.mktime(time.strptime(_date+" "+tm,"%Y-%m-%d %H:%M:%S"))-time.mktime(time.strptime(dateFlag,"%Y-%m-%d"))>=97200 or\
                (tm>"03 " and timeFlag<"03"):#if another day, initialize
            dateFlag = _date
            timeFlag = tm
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
            if tt-t<97200 and tm>"03":#yet is today's
                n_station = locations[i+1].split(' ')[0]
                if not n_station==station:
                    if n_station not in nodeDict.keys():
                        nodeDict[n_station] = len(nodeDict)
                    if not motifList[-1][nodeDict[station]].count(nodeDict[n_station])>0:
                        motifList[-1][nodeDict[station]].append(nodeDict[n_station])

    return motifList
def style_conv(list_dict):
    dicts = str(list_dict).strip('[]')
    dicts = dicts.split(', {')
    rsl = []
    for i in xrange(0, len(dicts)):
        if i ==0:
            rsl.append(dicts[i])
        else:
            rsl.append('{' + dicts[i])
    return rsl
if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    stay=900000
    holiday=['2014-10-01', '2014-10-02', '2014-10-03', '2015-01-01', '2015-01-19', '2015-01-20', '2015-01-21', '2015-01-22', '2015-01-23', '2015-01-24', '2015-01-25', '2015-01-26', '2015-01-27', '2015-01-28', '2015-01-29', '2015-01-30', '2015-01-31']
    sc = SparkContext(appName="PythonWordCount")
    wifiacc = sc.textFile("./NEWNET/nuser", 1).map(lambda x:(x.split("|")[0],x.split("|")[1])).distinct()
    wifiinfo = sc.textFile("/user/omnilab/warehouse/WifiSyslogSession/wifilog2014-09-*",1)
    wifiinfo2=sc.textFile("/user/omnilab/warehouse/WifiSyslogSession/wifilog2014-1*",1)
    wifiinfo=wifiinfo.union(wifiinfo2)
    wifiinfo2 = sc.textFile("/user/omnilab/warehouse/WifiSyslogSession/wifilog2015-01-*",1)
    wifiinfo=wifiinfo.union(wifiinfo2).filter(lambda x: x.split(",")[-1]!="")\
                    .map(lambda x:(x.split(",")[-1],x.split(",")[1]+","+x.split(",")[2]+","+x.split(",")[4]+","+x.split(",")[-1]))\
                    .groupByKey().mapValues(list).mapValues(merge)\
                    .flatMapValues(lambda x:x)\
                    .map(lambda x:x[1])\
                    .filter(lambda x:float(x.split(",")[1])-float(x.split(",")[0])>stay)\
                    .map(lambda x:timeconverter(x))
    # to this step, we get one term's information which has stay time more than 10min
    # now the format is (jaccount,format time,place)
    al=wifiinfo.filter(lambda x:x[1].split(",")[0].split(" ")[0]>"2014-09-13" and x[1].split(",")[0].split(" ")[0] not in holiday and u"徐汇" not in x[1].split(",")[1] and u"法华" not in x[1].split(",")[1])\
            .join(wifiacc)\
            .map(lambda x: x[1][1]+","+x[1][0])
    # we do this to take the right time zone and space zone,and replace mac adress with student number
    # now the format is (student number|time|duration|place)
    # 因为新体实行订票机制，因此非健身刷卡不为驻留行为。
    trade = sc.textFile("./EMC/trade.txt", 1)\
                .filter(lambda x:"1000190" not in x or "200" in x)\
                .filter(lambda x:x.split("\t")[3][:10]>"2014-09-13" and x.split("\t")[3][:10] not in holiday)\
    			.map(lambda x:(x.split("\t")[0],x))
    account=sc.textFile("./NEWNET/euser",1)\
    			.map(lambda x:(x.split("\t")[0],x.split("\t")[1]))
    trade=trade.join(account).map(lambda x:(x[1][0].split("\t")[1],x[1][1]+","+x[1][0].split("\t")[3]))
    place=sc.textFile("./NEWNET/merchant",1).map(lambda x:(x.split("|")[1],x.split("|")[0]))
    trade=trade.join(place).map(lambda x: x[1][0]+","+x[1][1]).distinct()
    # we do this to get the ecard information
    # now the trade format is (student number,time,place)
    al=al.filter(lambda x: x.split(",")[-1]!="")\
            .map(lambda x:x.replace("|",","))\
            .union(trade)
    # al=al  .map(func)
    al=al.filter(lambda x:time.localtime(time.mktime(time.strptime(x.split(",")[1],"%Y-%m-%d %H:%M:%S"))-10800).tm_wday<5)
    #after union we get the session now,and now we throw weekend
    d=al.map(lambda x:x.split(",")[1].split(" ")[0]).distinct().count()
    # all days number
    source=al.map(lambda x:(x.split(",")[0],x))
    user=al.map(lambda x:key(x))\
            .distinct()\
            .map(lambda x: (x.split(",")[0],1))\
            .reduceByKey(add)\
            .filter(lambda x: x[1]>=80)\
            .map(lambda x: (x[0].split(",")[0],x[1]))
    #number of days stay in school
    action=al.map(lambda x:(x.split(",")[0],1)).reduceByKey(add)
    average=user.join(action).filter(lambda x:x[1][1]/x[1][0]>=4)  #average wifi and card use per day
    al=source.join(average)\
            .map(lambda x: (x[0],x[1][0].split(",")[2]+" "+x[1][0].split(",")[1]))\
            .groupByKey()\
            .mapValues(list)\
            .mapValues(sor)\
            .mapValues(shower)\
            .mapValues(sliceplace)\
            .flatMapValues(lambda x:x)\
            .map(lambda x:x[0]+","+x[1].split(" ")[1]+" "+x[1].split(" ")[2]+","+x[1].split(" ")[0])
    # to this step, we got 11001313,2014-09-15 12:09:08,第三食堂
    label=sc.textFile("./NEWNET/label",1).map(lambda x:(x.split("|")[0],x.split("|")[1]))
    al.sortBy(lambda x:x)\
        .saveAsTextFile(sys.argv[1]+"zplace")
    al=al.map(lambda x:(x.split(",")[-1],x))\
        .join(label)\
        .map(lambda x:(x[1][0].split(",")[0],x[1][1]+" "+x[1][0].split(",")[1]))\
        .groupByKey()\
        .mapValues(list)\
        .mapValues(sor)\
        .mapValues(slice)\
        .flatMapValues(lambda x:x)
    al.map(lambda x:x[0]+" "+x[1])\
        .sortBy(lambda x:x.split(" ")[0]+x.split(" ")[2]+x.split(" ")[3]+x.split(" ")[1])\
        .saveAsTextFile(sys.argv[1])
    al=al.filter(lambda x:x[1].find("null")==-1 and\
            time.localtime(time.mktime(time.strptime(x[1].split(" ")[1]+" "+x[1].split(" ")[2],"%Y-%m-%d %H:%M:%S"))-10800).tm_wday<5)
    boyf = al.groupByKey()\
                .mapValues(list)\
                .mapValues(sor)\
                .map(lambda x:(x[0],style_conv(location_to_motif(x[1]))))\
                .flatMapValues(lambda x:x)
    # bc=boyf.count()
    # # # to this step, we got a tuple:(student number,motif detail)
    # #
    info=sc.textFile("./NEWNET/nuser", 1).map(word2num)
    b=info.filter(lambda x:x[1].split("|")[0]=="1").join(boyf).map(lambda x:(x[1][1],1))
    g=info.filter(lambda x:x[1].split("|")[0]=="0").join(boyf).map(lambda x:(x[1][1],1))
    ben=info.filter(lambda x:x[1].split("|")[3]=="1").join(boyf).map(lambda x:(x[1][1],1))
    shuo=info.filter(lambda x:x[1].split("|")[3]=="2").join(boyf).map(lambda x:(x[1][1],1))
    bo=info.filter(lambda x:x[1].split("|")[3]=="3").join(boyf).map(lambda x:(x[1][1],1))
    # # # # get all the kinds
    boyf=boyf   .map(lambda x:(x[1],1))\
                .reduceByKey(add)
    # # #             # .sortBy(lambda x:x[1],ascending=False)
    # # # # # # get days number to get ready for sorting
    s,t=motifiso(boyf.collect())
    # # # # s is the number of most usual moti
    # # # # fs top 20, t is the sorted list of top 1000 motifs with index
    sc.parallelize(s).map(lambda x:str(x[0])+"|"+str(x[1])).saveAsTextFile(sys.argv[1]+"0number")
    # boyf.coalesce(1).saveAsTextFile(sys.argv[1]+"00000")
    sc.parallelize(t).saveAsTextFile(sys.argv[1]+"0iso")
    entrolist(b,sc,t).saveAsTextFile(sys.argv[1]+"1boy")
    entrolist(g,sc,t).saveAsTextFile(sys.argv[1]+"2girl")
    entrolist(ben,sc,t).saveAsTextFile(sys.argv[1]+"3ben")
    entrolist(shuo,sc,t).saveAsTextFile(sys.argv[1]+"4shu")
    entrolist(bo,sc,t).saveAsTextFile(sys.argv[1]+"5bo")
    b=al.map(lambda x:x[0]).distinct().count()
    print("******************OK***********************"+str(d)+","+str(b)+","+str(al.count()))
    sc.stop()