# -*- coding: utf-8 -*-
# python version : 3.6

import urllib.request
import pandas as pd
import os
import json
import datetime
import random
from lxml import etree

Proxies_POOLs =[]

def init_proxiesPOOLs():  #初始化IP代理池
    global Proxies_POOLs
    with open('./prxies_pools.csv','r') as f:
        contents = f.readlines()
        f.close()
    num = len(contents)
    for i in range(num):
        details = contents[i].split(',')
        proxy= {details[2].strip('\n') :"%s:%s"%(details[0],details[1])}
        Proxies_POOLs.append(proxy) 

def get_OneProxy(): # 随机化 返回一个代理IP
    global Proxies_POOLs
    proxyNums = len(Proxies_POOLs)
    proxy = Proxies_POOLs[random.randint(0,proxyNums-1)]
    #print(proxy)
    return proxy

def use_proxy(url):
    req=urllib.request.Request(url)
    proxy_addr = None # get_OneProxy()
    req.add_header("User-Agent","Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0")
    proxy=urllib.request.ProxyHandler(proxy_addr)
    opener=urllib.request.build_opener(proxy,urllib.request.HTTPHandler)
    urllib.request.install_opener(opener)
    data=urllib.request.urlopen(req).read().decode('utf-8','ignore')
    return data
  
def get_OneDayInformation(url,peroid): 
    content=use_proxy(url)
    #print (content)
    day_news = []
    
    try:        
        html =  etree.HTML(content) 
        titles = html.xpath('//div[@class="bg_htit"]/h2/a/text()')               
        talk_times = html.xpath('//div[@id="center"]/div[@class="block_m"]/div[@class="talk_time"]/text()')
        div_mainnews = html.xpath('//div[@id="center"]/div[@class="block_m"]/div[@class="p_content"]/div[@class="p_mainnew"]')
        news = [[] for i in range(4)]
        for title in titles:
            news[0].append(title)            
        for talk_time in talk_times:
            tt = talk_time.strip()
            if tt !='\r\n' and tt !='':
                news[1].append(tt)                
        for mainnew in div_mainnews:
            mn = mainnew.xpath('string(.)')       
            news[2].append(mn)
            #extract keywords and links
            keywords = mainnew.xpath('.//a/text()')
            keywords_link = mainnew.xpath('.//a/@href')
            link_nums = len(keywords)
            key_links = []
            for k in range(link_nums):
                key_links.append( {'keyword':keywords[k],'link':keywords_link[k]})
            if len(key_links)>0:
                news[3].append(key_links)
            else:
                news[3].append([])
        #print('Length : news[0] = %s    news[1] = %s news[2] = %s  news[3]=%s'%(len(news[0]),len(news[1]),len(news[2]),len(news[3]) ))
        nums = len(news[0])
        if (nums>0):
            print("Found %5d news"%nums)
        else:
            print("Not Found")
            return 0
        for i in range(nums):
            day_news.append({'title':news[0][i],'talk_time':news[1][i],'mainnews':news[2][i],'keywords_links':news[3][i]})
            #print("title:%s\ntalk_time: %s\nmainnewes: %s\n"%(news[0][i],news[1][i],news[2][i]))
            print("%s\n%s\n%s"%(news[0][i],news[1][i],news[2][i]))
##            print("详情请访问:")
##            tar = news[3][i]
##            for x in range(len(tar)):
##                print("\t%s"%(tar[x]["link"]))
        print("\n")
        fname = './SolidotNews_%s.json'% peroid
        with open(fname,'w',encoding='utf-8') as f:
            f.write(str(day_news))
            f.close()
        
    except etree.ParserError as e: 
            print("At url=%s  \nError type = %s"%(url,e  ))        
 
def get_NewsFromDateRange():
    peroid_range = pd.period_range('11/01/2018','12/01/2018',freq='D')
    for day in peroid_range:
        url = "https://www.solidot.org/?issue=%s"%(str(day).replace('-',''))
        print(url)        
        get_OneDayInformation(url)

        
def main(): 
    init_proxiesPOOLs()
    ResentDaysNews = 3  # '最近三天Solidot网站新闻  1 表示今天
    ResentDaysNews_list = []
    for i in range(ResentDaysNews):
        ResentDaysNews_list.append( (datetime.datetime.now()+datetime.timedelta(days= -(i) )).strftime("%Y%m%d"))
    print(ResentDaysNews_list)
    for day in ResentDaysNews_list:
        url = "https://www.solidot.org/?issue=%s"%(day)
        get_OneDayInformation(url,day) 
    return 
    #get_NewsFromDateRange()

 
if __name__ == '__main__':    
    main()
