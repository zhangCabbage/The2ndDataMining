# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def daysDistance(timeStamp):
    """
    当前日期距离7月1号，有多少天
    """
    days = [0, 31, 62, 92, 123, 153, 184]  #从7月开始
    return days[timeStamp/10000 - 7] + timeStamp / 100 % 100 - 1


def averageModel1():
    """
    通过9月、10.15-10.30 所有的数据，算出一周的平均
    然后把此一周数据重复4遍作为11月正月数据的预测值。
    """
    df = pd.read_csv("train.csv", header=None)
    df.columns = ["personId", "timeStamp", "locId"]
    df = pd.DataFrame({'count' : df.groupby( ["timeStamp", "locId"] ).size()}).reset_index()
    df = df[((df.timeStamp > 90000) & (df.timeStamp < 100000)) | ((df.timeStamp >= 101500) & (df.timeStamp < 103124))]

    def time2WeekDays(timeStamp):
        """
        timeStamp对应于一周的第几天，哪个时刻 --> dhh
        """
        return daysDistance(timeStamp) % 7 * 100 + timeStamp % 100

    df["weekDayStamp"] = map(time2WeekDays, df["timeStamp"])
    df = df.groupby(["weekDayStamp", "locId"])["count"].agg({"num":np.mean}).reset_index()
    df.sort_values(["locId", "weekDayStamp"], inplace = True)
    
    df.num = df.num.round().astype(int) #取整
    df.columns = ["timestamp", "loc_id", "numOfPeople"]
    df = df[["loc_id", "timestamp", "numOfPeople"]] #重排各列，df一周平均数据
    df.to_csv("result.csv", index=False)


def averageModel2():
    """
    按周对齐, 按月对齐
    """
    df = pd.read_csv("People.csv", header=None)

    def parseTime(timeStamp):
        days = daysDistance(timeStamp) - 1
        return days / 7 % 3 * 1000 + days % 7 * 100 + timeStamp % 100

    df["week-stamp"] = map(parseTime, df["time-stamp"])
    df.groupby(["week-stamp", "loc-id"])


def pictureOfLocIn4Week():
    """
    输出每个地点每月一周7天的人流量波动图
    """
    originalDf = pd.read_csv("train.csv", header=None)
    originalDf.columns = ["personId", "timeStamp", "locId"]

    locIds = xrange(1, 37)
    for locId in locIds:
        print "locId --> ", locId
        df = pd.DataFrame({'count' : originalDf[originalDf.locId == locId].groupby("timeStamp").size()}).reset_index().sort_values("timeStamp")
        df["weeks"] = map(lambda time: daysDistance(time) / 7, df["timeStamp"]) #第几周
        df["hours"] = map(lambda time: daysDistance(time) % 7 * 24 + time % 100, df["timeStamp"]) #第几小时

        fig, ax = plt.subplots()
        labels = []
        dateStr = ["7.1-7.7", "7.29-8.4", "8.26-9.1", "9.23-9.29"] #提取4个月4周
        week = [0, 4, 8, 12]

        for i in xrange(len(week)):
            print "week --> ", week[i]
            tmpDf = df[df.weeks == week[i]]
            if not tmpDf.empty:
                ax = tmpDf.plot(ax=ax, x="hours", y="count")
                labels.append(dateStr[i])

        print labels
        lines, _ = ax.get_legend_handles_labels()
        ax.set_xticks(range(0, 169, 24)) #输出刻度
        ax.legend(lines, labels, loc='best')
        plt.savefig("loc_{}.png".format(locId), dpi=1000) #保存图片


def pictureOfLocMonth(df, locId):
    """
    out
    """
    print "locId --> ", locId
    df = pd.DataFrame({'count' : df[df.locId == locId].groupby("timeStamp").size()}).reset_index().sort_values("timeStamp")
    df["month"] = map(lambda time: time / 10000, df["timeStamp"]) #第几月

    months = [7, 8, 9, 10]
    xticks = [[0, 7, 14, 21, 28],[0, 4, 11, 18, 25],[0, 1, 8, 15, 22],[0, 6, 13, 20, 27]]
    for i in range(len(months)):
        print "local --> ", locId, ", months --> ", months[i]
        tmpDf = df[df.month == months[i]]
        tmpDf["days"] = map(lambda time: time / 100 % 100 - 1, tmpDf["timeStamp"]) #第几天
        ax = tmpDf.plot(x="days", y="count")

        ax.set_xticks(xticks[i])
        plt.savefig("loc_{}_month_{}.png".format(locId, months[i]), dpi=1200)


def picture(df):
    """
    4周时间，每周36个地点的人流量
    """
    dateStr = ["7.1-7.7", "7.29-8.4", "8.26-9.1", "9.23-9.29"]
    week = [0, 4, 8, 12]

    df = pd.DataFrame({'count' : df.groupby( ["timeStamp", "locId"] ).size()}).reset_index().sort_values("timeStamp")
    df["weeks"] = map(lambda time: daysDistance(time) / 7, df["timeStamp"]) #第几周
    df["hours"] = map(lambda time: daysDistance(time) % 7 * 24 + time % 100, df["timeStamp"]) #第几小时

    df = df[df.weeks == 0]

    fig, ax = plt.subplots()
    locIds = xrange(1, 37)
    labels = map(lambda loc: "locId {}".format(loc), locIds)

    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    markers = ['', '.', '^', 'v', 'o', '*', 'p']
    for i in locIds:
        print "locId --> ", i
        ax = df[(df.locId == i)].plot(ax=ax, x="hours", y="count", color=colors[(i - 1) % len(colors)], marker=markers[(i - 1) / len(colors)])

    lines, _ = ax.get_legend_handles_labels()
    ax.legend(lines, labels, loc='upper right', ncol=6)
    plt.savefig("week_7.1-7.7.png", dpi=3000)


def outputForecastData(df):
    """
    输出结果
    """
    df.columns = ["loc_id", "timestamp", "numOfPeople"]
    # 设置输出时间 - timestamp
    timestamp = []
    month = 11 #预测月
    monthDays = [0, 0, 0, 0, 0, 0, 0, 31, 31, 30, 31, 30, 31]
    for day in range(1, monthDays[month] + 1):
        for hour in range(0, 24):
            timestamp.append(month * 10000 + day * 100 + hour)

    timestamp *= 36
    df.timestamp = timestamp

    df.to_csv("result.csv", header=False, index=False)



class PreprocessData(object):
    """
    数据预处理类
    """
    def flowMatrix(self):
        """
        把数据处理成[pos * time]的矩阵，矩阵中值为对应pos和time的人流量nums
        """
        df = pd.read_csv("train.csv", header=None)
        df.columns = ["personId", "timeStamp", "locId"]
        df = pd.DataFrame({'nums' : df.groupby(["locId", "timeStamp"]).size()}).reset_index()

        dates = []
        months = [7, 8, 9, 10]
        monthDays = [31, 31, 30, 31]
        for i in xrange(4):
            for day in xrange(1, monthDays[i] + 1):
                for hour in xrange(24):
                    dates.append(months[i] * 10000 + day * 100 + hour)

        outDf = pd.DataFrame(0, index=range(1, 37), columns=dates) #index为行，columns为列

        for _, row in df.iterrows():
            pos = row.locId
            time = row.timeStamp
            count = row.nums
            outDf[time][pos] = count

        outDf.to_csv("flowMatrix.csv")

    def flowDiffMatrix(self):
        """
        流量差异矩阵
        """
        pass



if __name__ == '__main__':
    # averageModel1()
    # pictureOfLocIn4Week()



    # df = pd.read_csv("train.csv", header=None)
    # df.columns = ["personId", "timeStamp", "locId"]

    # picture(df)
    # pictureOfLocAll(df, 1)


    # PreprocessData().flowMatrix()

    










