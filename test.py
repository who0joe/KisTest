import KIS_Common as Common
import KIS_API_Helper_US as KisUS
#import KIS_API_Helper_KR as KisKR

import pprint
import time

#통합증거금을 사용하시는 분은 강의 영상을 잘 봐주세요!!

#REAL 실계좌 VIRTUAL 모의 계좌
Common.SetChangeMode("VIRTUAL") 


#현재 장이 열렸는지 여부
if KisUS.IsMarketOpen() == True:
    print("Maket is Open!!")
else:
    print("Maket is Closed!!")


'''
print("                                     ")
print("------------------------------------")
print("                                     ")


#내 잔고 확인
pprint.pprint(KisUS.GetBalance())
#pprint.pprint(KisKR.GetBalance())

#통합 증거금용 잔고 확인
#pprint.pprint(Common.GetBalanceKrwTotal())

print("                                     ")
print("------------------------------------")
print("                                     ")

#내 보유 주식 리스트 확인
pprint.pprint(KisUS.GetMyStockList())



print("                                     ")
print("------------------------------------")
print("                                     ")


stock_code = "AAPL" #애플 종목코드

current_price = KisUS.GetCurrentPrice(stock_code)

#애플의 현재 가격 
print(current_price)


print("                                     ")
print("------------------------------------")
print("                                     ")



#애플 1주 현재가로 지정가 매수
pprint.pprint(KisUS.MakeBuyLimitOrder(stock_code,1,current_price))

print("                                     ")
print("------------------------------------")
print("                                     ")



#시장가는 없는데 시장가 효과로 매수하려면???

buy_price = current_price * 1.1

#애플 2주를 현재가보다 10%나 높은금액에 매수하겠다고 주문을 넣으면??
pprint.pprint(KisUS.MakeBuyLimitOrder(stock_code,2,buy_price))
#바로 주문이 체결되는데 시장가로 체결되는걸 볼 수 있음

print("                                     ")
print("------------------------------------")
print("                                     ")


#모의 계좌는 지연 체결이 되며 3초정도 기다렸다고 주문이 완전히 체결된다는 보장은 없어요!!
time.sleep(3.0)



sell_price = current_price * 1.1

#애플 1주 10%위에 지정가 매도 주문
pprint.pprint(KisUS.MakeSellLimitOrder(stock_code,1,sell_price))

print("                                     ")
print("------------------------------------")
print("                                     ")





sell_price = current_price * 0.9

#애플 1주 10% 아래에 지정가 매도 주문을 넣으면???
pprint.pprint(KisUS.MakeSellLimitOrder(stock_code,1,sell_price))
#바로 주문이 체결되는데 시장가로 체결되는걸 볼 수 있음

print("                                     ")
print("------------------------------------")
print("                                     ")


#모의 계좌는 지연 체결이 되며 3초정도 기다렸다고 주문이 완전히 체결된다는 보장은 없어요!!
time.sleep(3.0)


#전체 주문리스트에서 현재 오픈된 주문을 가져온다
pprint.pprint(KisUS.GetOrderList("","ALL","OPEN"))

print("                                     ")
print("------------------------------------")
print("                                     ")

'''

##추가

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




pprint.pprint(Common.GetOhlcv("KR","005930"))
pprint.pprint(Common.GetOhlcv("US","TQQQ"))
