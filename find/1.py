#coding:utf-8  
import sys
from numpy import *
import time
import datetime
import networkx as nx
import pylab as plt
def mi(l):
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.mktime(time.strptime(l[0][1]+" "+l[0][2],"%Y-%m-%d %H:%M:%S"))-1))
def ad(l):
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.mktime(time.strptime(l[-1][1]+" "+l[-1][2],"%Y-%m-%d %H:%M:%S"))+1))

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
def slice(l):
    d={}
    final=[]
    for i in range(len(l)):
        lll=l[i]
        t=l[i].split(" ")
        ti=int(t[2][:2])
        station=t[0]
        if (u"食堂" in station or u"华联" in station) and i+1<len(l):
            next=l[i+1]
            nt=next.split(" ")
            ntime=int(nt[2][:2])
            nstation=nt[0]
            if (u"食堂" in next or u"华联" in next) and t[1]==nt[1] and ntime-ti>=2:#need to add
                low=ti
                high=ntime
                for i in l:
                    if (u"食堂" in i or u"华联" in i):
                        continue
                    mt=i.split(" ")
                    mtime=mt[2][:2]
                    mstation=mt[0]
                    if low<int(mtime) and int(mtime)<high:
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
                # print("********************"+s[0][0]+" "+t[1]+" "+time.strftime("%Y-%m-%d %H:%M:%S",ftime).split(" ")[1])
                if(len(s)>0):
                    final.append("********************"+s[0][0]+" "+t[1]+" "+time.strftime("%Y-%m-%d %H:%M:%S",ftime).split(" ")[1])
            else:
                final.append(l[i])
        else:
            final.append(l[i])
    return final
def place(s):
    if s.find(u"陈瑞球")!=-1:
        return u"陈瑞球"
    elif s.find(u"光彪楼")!=-1 or s.find(u"光标")!=-1:
        return u"光彪楼"
    elif s.find(u"光")!=-1 and s.find(u"体")!=-1:
        return u"光明体育场"
    elif (s.find(u"图书馆")!=-1 and s.find(u"包玉刚")) or s.find(u"新图")!=-1:
        return u"图书馆"
    elif s.find(u"媒")!=-1 and s.find(u"多")==-1:
        return u"媒体与设计实验室"
    elif s.find(u"校医院")!=-1:
        return u"校医院"
    elif s.find(u"药学楼")!=-1:
        return u"药学楼"
    elif s.find(u"材料")!=-1:
        return u"材料楼"
    elif s.find(u"木兰")!=-1 or s.find(u"船 ")!=-1:
        return u"木兰学院"
    elif s.find(u"分析测试中心")!=-1:
        return u"分析测试中心"
    elif s.find(u"农学生物学院")!=-1:
        return u"农学生物学院"
    # elif s.find(u"上交通中心")!=-1:
    #     return u"闵行候车室"
    elif s.find(u"航空航天学院")!=-1:
        return u"航空航天学院"
    elif s.find(u"外语楼")!=-1:
        return u"外语楼"
    elif s.find(u"网络中心")!=-1 or s.find(u"网络信息")!=-1 or s.find(u"图书信息")!=-1 or s.find(u"图信")!=-1 or s.find(u"图文信息中心")!=-1:
        return u"网络信息中心"
    elif s.find(u"铁生")!=-1:
        return u"铁生馆"
    elif s.find(u"铁生")!=-1:
        return u"铁生馆"
    elif s.find(u"逸夫")!=-1:
        return u"逸夫科技楼"
    # elif s.find(u"东中")!=-1:
    #     return u"东中院"
    # elif s.find(u"东上")!=-1:
    #     return u"东中院"
    # elif s.find(u"东下")!=-1:
    #     return u"东下院"
    elif s.find(u"菁菁堂")!=-1:
        return u"菁菁堂"
    elif s.find(u"人文")!=-1:
        return u"人文楼"
    elif s.find(u"生命")!=-1 or (s.find(u"生")!=-1 and s.find(u"农")!=-1):
        return u"农学生物学院"
    elif (s.find(u"外")!=-1 and s.find(u"语")!=-1) or s.find(u"外院")!=-1:
        return u"外语楼"
    elif s.find(u"致远游泳")!=-1:
        return u"游泳馆"
    elif (s.find(u"新体")!=-1 or s.find(u"综合体")!=-1):
        return u"新体育馆-近沧源路"
    elif (s.find(u"南")!=-1 and s.find(u"体育馆")!=-1) or(s.find(u"南体")!=-1 and s.find(u"篮球")!=-1) or(s.find(u"南体")!=-1 and s.find(u"排球")!=-1):
        return u"西南体育馆-南体"
    elif (s.find(u"学术")!=-1 and s.find(u"中心")!=-1) or s.find(u"學術活動")!=-1:
        return u"学术活动中心"
    elif (s.find(u"学生服务")!=-1) or (s.find(u"学服")!=-1):
        return u"学生服务中心"
    elif s.find(u"系统")!=-1:
        return u"系统生物研究院"
    elif s.find(u"文选")!=-1:
        return u"文选医学楼"
    elif (s.find(u"电")!=-1 and (s.find(u"院")!=-1 or s.find(u"群")!=-1) or s.find(u"电信楼")!=-1):
        return u"电信群楼"
    elif (s.find(u"机")!=-1 and (s.find(u"院")!=-1 or s.find(u"群")!=-1) or s.find(u"机械楼")!=-1):
        return u"机械与动力工程学院"
    else:
        return ""
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
                    # final.append("unknown"+" "+t[1]+" "+time.strftime("%Y-%m-%d %H:%M:%S",ftime).split(" ")[1])
                    continue
            else:
                final.append(l[i])
        else:
            final.append(l[i])
    return final
if __name__ == "__main__":
    l=[]
    d={}
    s={}
    k=5
    ratio=0
    da=0
    dd=0
    # with open("12602l",'rb') as ifile:
    #     for line in ifile:
    #         line=line.decode('utf-8')
    #         t=line.split("|")
    #         dd+=1
    #         for i in range(1,k+1):
    #             name=t[i].split(":")[0]
    #             num=int(t[i].split(":")[1])
    #             da+=num
    #             d[name]=(num,1) if name not in d.keys() else (d[name][0]+num,d[name][1]+1)
    #         l.append(line)
    #         print(line)
    # for i in d.keys():
    #     s[i]=d[i][0]/d[i][1]
    # re=[]
    # avd=da/dd/(1.6*k)
    # print(da/dd)
    # for line in l:
    #     t=line.split("|")
    #     for i in range(1,k+1):
    #         name=t[i].split(":")[0]
    #         num=int(t[i].split(":")[1])
    #         if num>=s[name]/1.7 and num>=avd:
    #             re.append(t[0]+"|"+name)
    #         # re.append(t[0]+"|"+name)
    # ratio=0
    # re=[]
    # with open("1",'rb') as ifile:
    #     for line in ifile:
    #         line=line.decode('utf-8')
    #         re.append(line[:-1])
    # print(len(re))


    # al=[]
    # with open("0al",'rb') as ifile:
    #     for line in ifile:
    #         line=line.decode('utf-8')
    #         t=line.split("|")
    #         for i in range(1,10):
    #             name=t[i].split(":")[0]
    #             num=int(t[i].split(":")[1])
    #             al.append((t[0],name,num))
    # ss=sorted(al,key=lambda x:x[2],reverse=True)
    # re=[]
    # ratio=0
    # for i in range(300):
    #     # print(ss[i][1])
    #     re.append(ss[i][0]+"|"+ss[i][1])
    #
    #
    # with open("xin",'rb') as ifile:
    #     for line in ifile:
    #         line=line.decode('utf-8')
    #         t=line.split("|")
    #         check=t[0].split(" ")[0]+"|"+t[1]
    #         if check in re:
    #             ratio+=1
    #         else:
    #             print(check)
    # print(len(re))
    # print(ratio)
    # x=[]
    # y=[]
    # d={}
    # for i in re:
    #     i=i.split("|")[1]
    #     d[i]=1 if i not in d.keys() else d[i]+1
    # t=sorted(d.items(),key=lambda x:x[1],reverse=True)
    # for i in t:
    #     x.append(i[0])
    #     y.append(i[1])
    #     print(i[1])
    # plt.xlabel("motif index")
    # plt.ylabel("accumulation number")
    # plt.xticks(range(len(x)),x)
    # plt.bar(range(len(x)),y,'r')
    # plt.show()
    with open("heat",'rb') as ifile:
        for line in ifile:
            line=line.decode('utf-8')
            t=line.split("|")
            for i in range(1,k):
                if(len(t)<=k):
                    break
                else:
                    name=t[i].split(":")[0]
                    num=int(t[i].split(":")[1])
                    da+=num
                    d[name]=(1) if name not in d.keys() else (d[name]+1)
    for i in d.keys():
        print(i+","+str(d[i]))