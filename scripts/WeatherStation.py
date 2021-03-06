#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import os
# sys.path.append(r'../lib')

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath + "/lib")

import epd7in5
import epdconfig
import time
from PIL import Image,ImageDraw,ImageFont,ImageChops
import traceback
import datetime
import requests
import logging

fontTempSize = ImageFont.truetype(rootPath + '/lib/Font.ttc', 30)
fontWeekSize = ImageFont.truetype(rootPath + '/lib/Font.ttc', 60)
fontDateSize = ImageFont.truetype(rootPath + '/lib/Font.ttc', 40)
fontTimeSize = ImageFont.truetype(rootPath + '/lib/Font.ttc', 70)
oilStrTime = ""
weekStr = ""
oilStrWeek = ""
countUpdate_1 = False
countUpdate_2 = False
countUpdate_3 = False
countUpdate_4 = False
SwitchDay = True
weatherTextToday = [""]*2
weatherTextTomorrow = [""]*2
weatherIconToday = ""
weatherIconTomorrow = ""
tempArray = ["------"]*13

def getTime():
    return(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"   ")

#获取天气
def getTemp():                                                                     # 连接超时,6秒，下载文件超时,7秒
    r = requests.get('http://t.weather.sojson.com/api/weather/city/101280701',timeout=(6,7)) 
    r.encoding = 'utf-8'
    print(getTime()+'状态码: '+str(r.status_code), flush=True)
    if r.status_code == 200:
        print(getTime()+'服务器正常!', flush=True)
    elif r.status_code == 404:
        print(getTime()+'网页不存在!', flush=True)
        return
    elif r.status_code == 500:
        print(getTime()+'服务器错误!', flush=True)
        return
    try:
        tempList = [
        (r.json()['cityInfo']['city']),             #城市
        (r.json()['data']['forecast'][0]['low']),   #最低温度
        (r.json()['data']['forecast'][0]['high']),  #最高温度
        (r.json()['data']['shidu']),                #湿度
        str(r.json()['data']['pm25']),              #Pm2.5
        (r.json()['data']['forecast'][0]['fx']),    #风向
        (r.json()['data']['forecast'][0]['fl']),    #风力
        (r.json()['data']['quality']),              #空气质量
        (r.json()['cityInfo']['updateTime']),       #更新时间
        (r.json()['data']['forecast'][0]['type']),  #今日天气
        (r.json()['data']['forecast'][0]['notice']),#今日天气
        (r.json()['data']['forecast'][1]['type']),  #明日天气
        (r.json()['data']['forecast'][1]['notice']) #明日天气
        ]
    except:
        tempList = ["------"]*13
        print(getTime()+'获取天气数据失败...', flush=True)
        return tempList
    else:
        print(getTime()+'获取天气数据成功...', flush=True)
        return tempList

def UpdateWeatherText(tempArray,TodayTomorrow):
    TextTemp = tempArray[TodayTomorrow].split('，') #使用逗号分隔字符串，分两行显示
    if(len(TextTemp)<2):                            #如果是整句话没有逗号，正数第五个字强制分隔防止出屏幕
        strtemp = tempArray[TodayTomorrow]
        TextTemp = [""]*2
        TextTemp[0] = strtemp[0:5]
        TextTemp[1] = strtemp[5:]
    return TextTemp

def UpdateWeatherIcon(tempType):  #匹配天气类型图标
    if(tempType == "大雨"  or tempType == "中到大雨"):
        return "大雨.bmp"
    elif(tempType == "暴雨"  or tempType == "大暴雨" or 
        tempType == "特大暴雨" or tempType == "大到暴雨" or
        tempType == "暴雨到大暴雨" or tempType == "大暴雨到特大暴雨"):
        return "暴雨.bmp"
    elif(tempType == "沙尘暴" or tempType == "浮尘" or
        tempType == "扬沙" or tempType == "强沙尘暴" or
        tempType == "雾霾"):
        return "沙尘暴.bmp"
    return (tempType + ".bmp")
        
def todayWeek(nowWeek):
    if nowWeek == "0":
        return"星期天"
    elif nowWeek =="1":
        return"星期一"
    elif nowWeek =="2":
        return"星期二"
    elif nowWeek =="3":
        return"星期三"
    elif nowWeek =="4":
        return"星期四"
    elif nowWeek =="5":
        return"星期五"
    elif nowWeek =="6":
        return"星期六"

def UpdateData():
    tempArray = getTemp()
    global weatherTextToday
    global weatherTextTomorrow
    global weatherIconToday
    global weatherIconTomorrow
    weatherTextToday = UpdateWeatherText(tempArray,10)
    weatherTextTomorrow = UpdateWeatherText(tempArray,12)
    weatherIconToday = UpdateWeatherIcon(tempArray[9])
    weatherIconTomorrow = UpdateWeatherIcon(tempArray[11])
    return tempArray


#348 ~ 640 像素 居中显示
#居中显示的方法 一个字宽度30像素 例如重479像素开始 多加一个字 少空 15 个像素
def alignCenter(string,scale,startPixel):
    charsCount = 0
    for s in string:
        charsCount += 1
    charsCount *= scale/2
    charsCount = startPixel - charsCount
    return charsCount

#刷新循环
while (True):
    print(getTime()+'start...', flush=True)
    epd = epd7in5.EPD()
    epd.init()

    timeUpdate = datetime.datetime.now()
    strtime = timeUpdate.strftime('%Y-%m-%d') #年月日
    strtime2 = timeUpdate.strftime('%H:%M')   #时间
    strtime3 = timeUpdate.strftime('%M')      #分钟
    strtime4 = timeUpdate.strftime('%w')      #星期
    strtime5 = timeUpdate.strftime('%H')      #小时
    
    if(strtime4 != oilStrWeek):  #每天重置更新天气
        weekStr = todayWeek(strtime4)
        oilStrWeek = strtime4
        countUpdate_1 = True
        countUpdate_2 = True
        countUpdate_3 = True
        countUpdate_4 = True
        tempArray = UpdateData()
        epd.Clear()
        print(getTime()+'重置更新天气', flush=True)

    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    #显示星期
    draw.text((10, 0), weekStr, font = fontWeekSize, fill = 0)
    #显示时间   
    draw.text((430, 0), strtime2, font = fontTimeSize, fill = 0)
    #显示年月日
    draw.text((410, 330), strtime, font = fontDateSize, fill = 0)
    #显示图标
    bmp = Image.open(rootPath + '/pic/icon.png')
    Himage.paste(bmp,(15,80))

    # 天气API 只有这几个点会更新,减少无用请求
    intTime = int(strtime5)

    if(countUpdate_1 and  intTime == 7):
        tempArray = UpdateData()
        countUpdate_1 = False
        epd.Clear()
        print(getTime()+strtime2 + '更新天气', flush=True)
    elif(countUpdate_2 and intTime == 11):
        tempArray = UpdateData()
        countUpdate_2 = False
        epd.Clear()
        print(getTime()+strtime2 + '更新天气', flush=True)
    elif(countUpdate_3 and intTime == 16):
        tempArray = UpdateData()
        countUpdate_3 = False
        epd.Clear()
        print(getTime()+strtime2 + '更新天气', flush=True)
    elif(countUpdate_4 and intTime == 21 ):
        tempArray = UpdateData()
        countUpdate_4 = False
        epd.Clear()
        print(getTime()+strtime2 + '更新天气', flush=True)
        

    #显示城市/更新时间
    draw.text((15, 335), tempArray[0], font = fontTempSize, fill = 0)
    draw.text((110, 335), tempArray[8] + "更新", font = fontTempSize, fill = 0)

    #显示温度 (自带的字库不能显示℃ ,更换字体文件可解决)
    temp_L = tempArray[1].replace("低温","")
    temp_L = temp_L.replace("℃","")
    temp_L = temp_L.replace(" ","")
    temp_H = tempArray[2].replace("高温","")
    temp_H = temp_H.replace("℃","")
    temp_H = temp_H.replace(" ","")
    draw.text((70,90),"温度: "+ temp_L+"~"+temp_H, font = fontTempSize, fill = 0)  
    
    #显示湿度
    draw.text((70,133),"湿度: "+ tempArray[3], font = fontTempSize, fill = 0)
    #显示PM2.5
    draw.text((70,177),"PM 2.5: "+ tempArray[4], font = fontTempSize, fill = 0)
    #显示风向
    draw.text((70,225), tempArray[5] +" "+ tempArray[6], font = fontTempSize, fill = 0)
    #空气质量
    draw.text((70,266),"空气质量: "+ tempArray[7], font = fontTempSize, fill = 0)
    

    if(SwitchDay):#天气滚动
        draw.text((348,90),"今日：", font = fontTempSize, fill = 0) 
        #显示天气图标
        tempTypeIcon = Image.open(rootPath + "/pic/weatherType/" + weatherIconToday)
        Himage.paste(tempTypeIcon,(450,90))
        draw.text((alignCenter(tempArray[9],30,479),177),tempArray[9], font = fontTempSize, fill = 0)
        draw.text((alignCenter(weatherTextToday[0],30,479),225),weatherTextToday[0], font = fontTempSize, fill = 0)
        draw.text((alignCenter(weatherTextToday[1],30,479),266),weatherTextToday[1], font = fontTempSize, fill = 0)
        SwitchDay = False
    else:
        draw.text((348,90),"明日：", font = fontTempSize, fill = 0)
        tempTypeIcon = Image.open(rootPath + "/pic/weatherType/" + weatherIconTomorrow)
        Himage.paste(tempTypeIcon,(450,90))
        draw.text((alignCenter(tempArray[11],30,479),177),tempArray[11], font = fontTempSize, fill = 0)
        draw.text((alignCenter(weatherTextTomorrow[0],30,479),225),weatherTextTomorrow[0], font = fontTempSize, fill = 0)
        draw.text((alignCenter(weatherTextTomorrow[1],30,479),266),weatherTextTomorrow[1], font = fontTempSize, fill = 0)
        SwitchDay = True

    #画竖线(x开始值，y开始值，x结束值，y结束值)
    draw.rectangle((325, 90, 326, 290), fill = 0)
    #画横线
    draw.rectangle((0, 315, 680, 317), fill = 0)
    #刷新屏幕
    print(getTime()+strtime2 + '刷新屏幕...', flush=True)
    Himage = ImageChops.invert(Himage)
    epd.display(epd.getbuffer(Himage))
    #屏幕休眠
    epd.sleep()
    print(getTime()+strtime2 + '屏幕休眠...', flush=True)
    if(intTime >= 1 and intTime <= 6): #2点～6点 每小时刷新一次
        time.sleep(3600)
    else:
        time.sleep(600)
