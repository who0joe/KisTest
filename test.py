import KIS_Common as Common
import KIS_API_Helper_US as KisUS
import KIS_API_Helper_KR as KisKR

import pprint
import time


import json
import pandas as pd

from pykrx import stock

#통합증거금을 사용하시는 분은 강의 영상을 잘 봐주세요!!

#REAL 실계좌 VIRTUAL 모의 계좌
Common.SetChangeMode("VIRTUAL") 

'''
#현재 장이 열렸는지 여부
if KisKR.IsMarketOpen() == True:
    print("Maket is Open!!")
else:
    print("Maket is Closed!!")



print("                                     ")
print("------------------------------------")
print("                                     ")


#내 잔고 확인
#pprint.pprint(KisUS.GetBalance())
pprint.pprint(KisKR.GetBalance())

#통합 증거금용 잔고 확인
#pprint.pprint(Common.GetBalanceKrwTotal())

print("                                     ")
print("------------------------------------")
print("                                     ")
'''
#내 보유 주식 리스트 확인
pprint.pprint(KisKR.GetMyStockList())



print("                                     ")
print("------------------------------------")
print("                                     ")

'''
stock_code = "005930" #애플 종목코드

current_price = KisKR.GetCurrentPrice(stock_code)

#애플의 현재 가격 
print(current_price)


print("                                     ")
print("------------------------------------")
print("                                     ")



#애플 1주 현재가로 지정가 매수
pprint.pprint(KisKR.MakeBuyLimitOrder(stock_code,1,current_price))

print("                                     ")
print("------------------------------------")
print("                                     ")



#시장가는 없는데 시장가 효과로 매수하려면???

buy_price = current_price * 1.1

#애플 2주를 현재가보다 10%나 높은금액에 매수하겠다고 주문을 넣으면??
pprint.pprint(KisKR.MakeBuyLimitOrder(stock_code,2,buy_price))
#바로 주문이 체결되는데 시장가로 체결되는걸 볼 수 있음

print("                                     ")
print("------------------------------------")
print("                                     ")


#모의 계좌는 지연 체결이 되며 3초정도 기다렸다고 주문이 완전히 체결된다는 보장은 없어요!!
time.sleep(3.0)



sell_price = current_price * 1.1

#애플 1주 10%위에 지정가 매도 주문
pprint.pprint(KisKR.MakeSellLimitOrder(stock_code,1,sell_price))

print("                                     ")
print("------------------------------------")
print("                                     ")





sell_price = current_price * 0.9

#애플 1주 10% 아래에 지정가 매도 주문을 넣으면???
pprint.pprint(KisKR.MakeSellLimitOrder(stock_code,1,sell_price))
#바로 주문이 체결되는데 시장가로 체결되는걸 볼 수 있음

print("                                     ")
print("------------------------------------")
print("                                     ")


#모의 계좌는 지연 체결이 되며 3초정도 기다렸다고 주문이 완전히 체결된다는 보장은 없어요!!
time.sleep(3.0)


#전체 주문리스트에서 현재 오픈된 주문을 가져온다
pprint.pprint(KisKR.GetOrderList("","ALL","OPEN"))

print("                                     ")
print("------------------------------------")
print("                                     ")

##미체결 모두 취소
time.sleep(5.0)
pprint.pprint(KisKR.CancelAllOrders("","ALL"))

print("                                     ")
print("---------미체결 전량취소완료----------")
print("                                     ")


##보유주식 모두 시장가매도
time.sleep(7.0)
pprint.pprint(KisKR.SellAllStock())

print("                                     ")
print("---------잔고 전량매도완료------------")
print("                                     ")

'''
#########################################################################################################

'''

print("                                     ")
print("-----------삼성 전자 일봉 -------------")
print("                                     ")

#삼성전자의 일봉 정보를 100개까지 가져올 수 있다
pprint.pprint(KisKR.GetOhlcv("005930","D"))

print("                                     ")
print("-----------삼성 전자 월봉 -------------")
print("                                     ")


pprint.pprint(KisKR.GetOhlcv("005930","M"))

print("                                     ")
print("-----------삼성 전자 년봉 -------------")
print("                                     ")


pprint.pprint(KisKR.GetOhlcv("005930","Y"))



print("                                     ")
print("----------애플 일봉---------------")
print("                                     ")


#애플의 일봉 정보를 100개까지 가져올 수 있다
pprint.pprint(KisUS.GetOhlcv("AAPL","D"))



print("                                     ")
print("----------애플 월봉---------------")
print("                                     ")


pprint.pprint(KisUS.GetOhlcv("AAPL","M"))


print("                                     ")
print("----------애플 년봉---------------")
print("                                     ")
print(" 이건 가져올 수 없음 ")
#영상과는 다르게 미국주식의 경우 년봉은 가져올 수 없어요
#내부적으로 수정주가(액면분할 반영)를 가져오도록 API를 변경했기 때문이예요 (해당 API가 년봉 미지원)
#pprint.pprint(KisUS.GetOhlcv("AAPL","Y"))
'''
'''

print("                                     ")
print("--------TQQQ는 한투에 없다 -------------")
print("                                     ")



pprint.pprint(KisUS.GetOhlcv("TQQQ","D"))




print("                                     ")
print("----------삼성전자 일봉 가져오기--------------")
print("                                     ")

print(" 한투 ")
pprint.pprint(KisKR.GetOhlcv("005930","D"))

print(" FinanceDataReader ")

pprint.pprint(Common.GetOhlcv1("KR","005930"))

print(" Yahoo ")

pprint.pprint(Common.GetOhlcv2("KR","005930"))





print("                                     ")
print("----------애플 일봉 가져오기--------------")
print("                                     ")

print(" 한투 ")
pprint.pprint(KisUS.GetOhlcv("AAPL","D"))

print(" FinanceDataReader ") 
# 22년 10월 24일 현재 FinanceDataReader가 사용하는 인베스팅 닷컴의 크롤링이 막힌 상태입니다.
# https://github.com/financedata-org/FinanceDataReader/issues/166 여기를 참고하세요!
# https://github.com/financedata-org/FinanceDataReader/wiki/Release-Note-0.9.50 이 버전으로 해결이 되며 아래 라인이 만약에 에러가 나면
# sudo pip3 install --upgrade finance-datareader 로 업데이트 해주세요!
pprint.pprint(Common.GetOhlcv1("US","AAPL"))

print(" Yahoo ")

pprint.pprint(Common.GetOhlcv2("US","AAPL"))
'''

#pprint.pprint(Common.GetOhlcv("KR","005930"))
#pprint.pprint(Common.GetOhlcv("US","TQQQ"))


############################################################################################################################
# 종목 코드에 맞는 종목 이름 불러오기

'''

KoreaStockList = list()
#파일 경로입니다.
korea_file_path = "/Users/TY/Documents/Class101/KrStockCodeList.json"

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(korea_file_path, 'r') as json_file:
        KoreaStockList = json.load(json_file)

except Exception as e:
    print("Exception by First")
    
    
for stock_code in KoreaStockList:
    print(stock_code, KisKR.GetStockName(stock_code))

'''

####################################################################################################

'''
TargetStockList = list()
#파일 경로입니다.
korea_file_path = "/Users/TY/Documents/Class101/KrStockDataList.json"

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(korea_file_path, 'r') as json_file:
        TargetStockList = json.load(json_file)

except Exception as e:
    print("Exception by First")


print("TotalStockCodeCnt: " , len(TargetStockList))


df = pd.DataFrame(TargetStockList)

df = df[df.StockMarketCap >= 50.0].copy()
df = df[df.StockDistName != "금융"].copy()
df = df[df.StockDistName != "외국증권"].copy()



df = df.sort_values(by="StockMarketCap")
pprint.pprint(df)

print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

pprint.pprint(df[0:20])

'''


####################################################################################################

'''

stockcode = "224060"

url = "https://finance.naver.com/item/main.naver?code=" + stockcode
dfs = pd.read_html(url,encoding='euc-kr')

#pprint.pprint(dfs[4])

data_dict = dfs[4]


data_keys = list(data_dict.keys())

for key in data_keys:
    if stockcode in key:
        print(key)
        print(data_dict[key][5]) #매출액
        print(data_dict[key][6]) #영업이익
        print(data_dict[key][8]) #영업이익증가율
        print(data_dict[key][11]) #ROE
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$")


'''

#############################################################################################



'''
#코스닥 지수 확인
for index_v in stock.get_index_ticker_list(market='KOSDAQ'): #KOSPI 지수도 확인 가능!
    print(index_v, stock.get_index_ticker_name(index_v))

print("-----------------------------------------------------------------")

#코스피 지수 확인
for index_v in stock.get_index_ticker_list(market='KOSPI'): #KOSPI 지수도 확인 가능!
    print(index_v, stock.get_index_ticker_name(index_v))

'''


#################################################################################################

stock_code = "069500"

CurrentPrice = KisKR.GetCurrentPrice(stock_code)

print("-------------------------------------")
Nav = KisKR.GetETF_Nav(stock_code)
print("-------------------------------------")
FarRate = ((CurrentPrice-Nav) / Nav) * 100.0


#최근 괴리율 절대값들의 평균
print("-------------------------------------")
AvgGap = KisKR.GetETFGapAvg(stock_code)
print("-------------------------------------")

print("#######################################")

print("ETF NAV: " , Nav," 현재가:", CurrentPrice, " 괴리율:",FarRate , " 괴리율 절대값 평균:", AvgGap)


#맨 마지막에 True를 넣으면 잔고상황 반영한 수량으로 주문이 들어갑니다
KisKR.MakeBuyLimitOrder(stock_code,10,KisKR.GetCurrentPrice(stock_code))


####### 영상엔 없지만 아래 함수를 사용해 주문자동시스템에서 주문취소 및 시스템내 삭제가 가능합니다 ####
#주문 아이디에 해당하는 주문 취소 및 자동시스템에서 주문 삭제 예시 
Common.DelAutoLimitOrder('REAL2MY_PENSIONKR2612209125200000432650959421015785.93')

#봇 이름에 해당하는 모든 주문 취소 및 자동시스템에서 주문 삭제 예시 
Common.AllDelAutoLimitOrder("MY_PENSION")





