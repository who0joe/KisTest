# -*- coding: utf-8 -*-

import KIS_Common as Common
import pprint
import json
import time
import line_alert #라인 메세지를 보내기 위함!

import pandas as pd
import random
import yfinance as yf

#pip3 install yfinance
# https://yamalab.tistory.com/181
 


USStockList = list()
#파일 경로입니다.
US_file_path = "/var/autobot/UsStockCodeList.json"

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(US_file_path, 'r') as json_file:
        USStockList = json.load(json_file)

except Exception as e:
    print("Exception by First")



line_alert.SendMessage("Make Stock Data US Start!!" + str(len(USStockList)))


UsStockDataList = list()


for stock_code in USStockList:

    try:


        print(stock_code, " ..Start.. ")
        ticker = yf.Ticker(stock_code)
        stock_info = ticker.info

        stockDataDict = dict()
        stockDataDict['StockCode'] = stock_code
        stockDataDict['StockName'] = stock_info['longName']
        stockDataDict['StockNowPrice'] = stock_info['currentPrice']
        stockDataDict['StockMarket'] = stock_info['quoteType'] #구분
        stockDataDict['StockDistName'] = stock_info['sector']  #섹터

        try:
            stockDataDict['StockMarketCap'] = float(stock_info['marketCap']) #시총
        except Exception as e:
            stockDataDict['StockMarketCap'] = 0

        try:
            stockDataDict['StockPER'] = float(stock_info['trailingPE']) #PER
        except Exception as e:
            stockDataDict['StockPER'] = 0

        try:
            stockDataDict['StockPBR'] = float(stock_info['priceToBook']) #PBR
        except Exception as e:
            stockDataDict['StockPBR'] = 0


        try:
            stockDataDict['StockEPS'] = float(stock_info['trailingEps']) #EPS
        except Exception as e:
            stockDataDict['StockEPS'] = 0


        try:
            stockDataDict['StockEV_EBITDA'] = float(stock_info['enterpriseToEbitda']) #EV/EVITDA
        except Exception as e:
            stockDataDict['StockEV_EBITDA'] = 0
            



        try:
            stockDataDict['StockROA'] = float(stock_info['returnOnAssets']) #ROA
        except Exception as e:
            stockDataDict['StockROA'] = 0
            
            
        try:
            stockDataDict['StockROE'] = float(stock_info['returnOnEquity']) #ROE
        except Exception as e:
            stockDataDict['StockROE'] = 0
            
            
        try:
            stockDataDict['StockOperatingMargin'] = float(stock_info['operatingMargins']) #영업이익률
        except Exception as e:
            stockDataDict['StockOperatingMargin'] = 0
            
        try:
            stockDataDict['StockProfitMargin'] = float(stock_info['profitMargins']) #순이익률
        except Exception as e:
            stockDataDict['StockProfitMargin'] = 0
            
                
        
        UsStockDataList.append(stockDataDict)
        
        #pprint.pprint(stockDataDict)
            

            
        time.sleep(random.random()*0.001)
        


        print(stock_code, " ..Done.. ")

    except Exception as e:
        print("Exception ", e)




print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
pprint.pprint(UsStockDataList)

print("--------------------------------------------------------")


#파일 경로입니다.
us_data_file_path = "/var/autobot/UsStockDataList.json"
#파일에 리스트를 저장합니다
with open(us_data_file_path, 'w') as outfile:
    json.dump(UsStockDataList, outfile)

line_alert.SendMessage("Make Stock Data US Done!!" + str(len(UsStockDataList)))

