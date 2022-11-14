# -*- coding: utf-8 -*-

import KIS_Common as Common
import pprint
import json
import time
import KIS_API_Helper_KR as KisKR

import pandas as pd
import line_alert

Common.SetChangeMode("REAL")


KoreaStockList = list()
#파일 경로입니다.
korea_file_path = "/var/autobot/KrStockCodeList.json"

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(korea_file_path, 'r') as json_file:
        KoreaStockList = json.load(json_file)

except Exception as e:
    print("Exception by First")


line_alert.SendMessage("Make Stock Data Korea Start!!")

KrStockDataList = list()


for stock_code in KoreaStockList:

    try:


        print(stock_code, " ..Start.. ")

        data = KisKR.GetCurrentStatus(stock_code)

        
        
        if data['StockNowStatus'] == '00' or data['StockNowStatus'] == '55' or data['StockNowStatus'] == '57' : 

            if data['StockMarket'] == "ETN" or data['StockMarket'] == "ETF" or (float(data['StockPER']) == 0 and float(data['StockPBR']) == 0 and float(data['StockEPS']) == 0  and float(data['StockBPS']) == 0) :
                print("Maybe...ETF..ETN.. ")
            else:

                try:
                    stockcode = data['StockCode']
                    print("---------------------------------------------------")
                    print(stockcode,"..크롤링..")

                    url = "https://finance.naver.com/item/main.naver?code=" + stockcode
                    dfs = pd.read_html(url,encoding='euc-kr')
                    #pprint.pprint(dfs)


                    data_dict = dfs[4]

                    data_keys = list(data_dict.keys())


                    for key in data_keys:
                        if stockcode in key:
                            print(key)
                            print("현재가: ",data_dict[key][0]) #현재가
                            print("매출액: ",data_dict[key][5]) #매출액
                            print("영업이익: ",data_dict[key][6]) #영업이익
                            print("영업이익증가율: ",data_dict[key][8]) #영업이익증가율
                            print("ROE: ",data_dict[key][11]) #ROE

                            #들여쓰기가 중요합니다.
                            #영상 설명에서는 저도 실수 했는데 이렇게 if문 안쪽에 아래 로직이 있어야 정상입니다!
                            
                            ##################################################
                            #영업이익을 이렇게 미리 데이터를 만들어 넣을 수도 있다.
                            try:

                                data['StockOperProfit'] = float(data_dict[key][6])
                                
                            except Exception as e:
                                data['StockOperProfit'] = -1 # 영상엔 없지만 문자열등 숫자가 아닌 값이 있다면 -1로 처리해주자

                            #ROE를 여기 데이터를 만들어 넣을 수도 있다
                            try:

                                data['StockROE'] = float(data_dict[key][11])

                            except Exception as e:
                                try:
                                    # 영상엔 없지만 문자열등 숫자가 아닌 값이 있다면 EPS와 BPS를 통해 구하고
                                    data['StockROE'] = float(data['StockEPS']) / float(data['StockBPS']) * 100.0
                                except Exception as e:
                                    data['StockROE'] = -1 #이것도 예외처리가 되었다면 -1로 해주자

                            #이렇게 정보를 가져올때 수치들이 숫자가 아니라 문자열 등이 들어갈 경우를 대비해 try~ except로 감싸주고 예외처리를 하면 안전합니다!!!!!!!
                            ##################################################
                            

                    time.sleep(0.5)
                        
                except Exception as e:
                    print("Except:", e)
                


                KrStockDataList.append(data)
                
                pprint.pprint(data)
            

            
        time.sleep(0.2)

        print(stock_code, " ..Done.. ")

    except Exception as e:
        print("Exception ", e)




print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
pprint.pprint(KrStockDataList)

print("--------------------------------------------------------")


#파일 경로입니다.
kr_data_file_path = "/var/autobot/KrStockDataList.json"
#파일에 리스트를 저장합니다
with open(kr_data_file_path, 'w') as outfile:
    json.dump(KrStockDataList, outfile)

line_alert.SendMessage("Make Stock Data Korea Done!!" + str(len(KrStockDataList)))


