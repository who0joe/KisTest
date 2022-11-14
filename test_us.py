# -*- coding: utf-8 -*-


import KIS_Common as Common
import json
import pandas as pd
import pprint


Common.SetChangeMode("VIRTUAL")

UsTradingDataList = list()
#파일 경로입니다.
US_file_path = "/Users/TY/Documents/class101/UsTradingDataList.json"

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(US_file_path, 'r') as json_file:
        UsTradingDataList = json.load(json_file)

except Exception as e:
    print("Exception by First")
    
    

df = pd.DataFrame(UsTradingDataList)

#아래 예들은 단순 예시들로 다양한 조건을 만들수 있습니다 

# 정배열...
df = df[df.StockPrice_0 > df.StockMA5_0].copy()
df = df[df.StockMA5_0 > df.StockMA20_0].copy()
df = df[df.StockMA20_0 > df.StockMA60_0].copy()
df = df[df.StockMA60_0 > df.StockMA120_0].copy()


'''
#역배열
df = df[df.StockPrice_0 < df.StockMA5_0].copy()
df = df[df.StockMA5_0 < df.StockMA20_0].copy()
df = df[df.StockMA20_0 < df.StockMA60_0].copy()
df = df[df.StockMA60_0 < df.StockMA120_0].copy()
'''

'''
#RSI지표가 30에서 빠져나왔을 때
df = df[df.StocUsSI_1 < 30.0].copy()
df = df[df.StocUsSI_0 > 30.0].copy()
'''

'''
#볼밴 하단밖에서 안으로 들어 왔을 때 
df = df[df.StockBB_Lower_1 > df.StockPrice_1].copy()
df = df[df.StockBB_Lower_0 < df.StockPrice_0].copy()
'''



df = df.sort_values(by="StockMoney_0", ascending=False)
pprint.pprint(df)




#미국 시총이나 재무지표가 들어 있는 파일
UsStockDataList = list()
#파일 경로입니다.
StockData_file_path = "/Users/TY/Documents/class101/UsStockDataList.json"

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(StockData_file_path, 'r') as json_file:
        UsStockDataList = json.load(json_file)

except Exception as e:
    print("Exception by First")



df_sd = pd.DataFrame(UsStockDataList)


TopCnt = 20
NowCnt = 0

for idx, row in df.iterrows():
    
    if NowCnt < TopCnt:

        print("-----------------------------------")
        print(row['StockCode'])
        print("거래대금: ", row['StockMoney_0'])
        print("전날대비 거래대금: ", row['StockMoneyRate'])
        print("등락률 : ", round(row['StocUsate'],2))
        
        for idx2, row2 in df_sd.iterrows():
            
            if row['StockCode'] == row2['StockCode']:

                print("시총: ", row2['StockMarketCap'])
                print("현재가 : ", row2['StockNowPrice'])
                print("영업이익률 : ", row2['StockOperatingMargin'])
                print("EPS(주당 순이익) : ", row2['StockEPS'])
                print("PER(현재가 / 주당 순자산) : ", row2['StockPER'])
                print("PBR(현재가 / 주당 순자산) : ", row2['StockPBR'])
                print("ROE : ", row2['StockROE'])
                print("ROA : ", row2['StockROA'])
                print("EV/EBITDA : ", row2['StockEV_EBITDA'])
                
                break
        print("-----------------------------------")


        NowCnt += 1
