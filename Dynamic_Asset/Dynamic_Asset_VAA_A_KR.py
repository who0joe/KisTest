# -*- coding: utf-8 -*-

import KIS_Common as Common
import KIS_API_Helper_KR as KisKR
import time
import json
import pprint

import line_notify as line_alert



#계좌 선택.. "VIRTUAL" 는 모의 계좌!
Common.SetChangeMode("VIRTUAL") #REAL or VIRTUAL



#시간 정보를 읽는다
time_info = time.gmtime()
#년월 문자열을 만든다 즉 2022년 9월이라면 2022_9 라는 문자열이 만들어져 strYM에 들어간다!
strYM = str(time_info.tm_year) + "_" + str(time_info.tm_mon)
print("ym_st: " , strYM)



#포트폴리오 이름
PortfolioName = "동적자산배분전략_VAA_A"


'''

# VAA_A전략
위험자산(지수) , 안전자산(채권)으로 나누고, 모든 자산의 모멘텀 점수를 계산한다.

1개월 수익률 X 12
3개월 수익률 X 4
6개월 수익률 X 2
12개월 수익률 X 1
위의 식을 다 더하면 모멘텀 점수가 된다.

모든 위험 자산의 모멘텀 점수가 양수이면 모멘텀 점수가 가장 높은 자산에 포트폴리오의 100%를 투자하고,
위험 자산 중 모멘텀 점수가 음수이면 포트폴리오의 100%를 점수가 가장 안전 자산에 투자한다.

다음 달 최종 거래일까지 포지션 유지한다


'''


#####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################

#전제는 크롭탭에 주말 빼고 우리나라 시간 아침10시 정각에 해당 봇이 돈다고 가정!
# 0 1 1-7 * 1-5 python3 /Users/TY/Documents/class101/Dynamic_Asset/Dynamic_Asset_VAA_A_KR.py 

#리밸런싱이 가능한지 여부를 판단!
Is_Rebalance_Go = False


#파일에 저장된 년월 문자열 (ex> 2022_9)를 읽는다
YMDict = dict()

#파일 경로입니다.
static_asset_tym_file_path = "/Users/TY/Documents/class101/Dynamic_Asset/Dynamic_Asset_VAA_A_KR.json"
try:
    with open(static_asset_tym_file_path, 'r') as json_file:
        YMDict = json.load(json_file)

except Exception as e:
    print("Exception by First")


#만약 키가 존재 하지 않는다 즉 아직 한번도 매매가 안된 상태라면
if YMDict.get("ym_st") == None:

    #리밸런싱 가능! (리밸런싱이라기보다 첫 매수해야 되는 상황!)
    Is_Rebalance_Go = True
    
#매매가 된 상태라면! 매매 당시 혹은 리밸런싱 당시 년월 정보(ex> 2022_9) 가 들어가 있다.
else:
    #그럼 그 정보랑 다를때만 즉 달이 바뀌었을 때만 리밸런싱을 해야 된다
    if YMDict['ym_st'] != strYM:
        #리밸런싱 가능!
        Is_Rebalance_Go = True


#강제 리밸런싱 수행!
#Is_Rebalance_Go = True





#마켓이 열렸는지 여부~!
IsMarketOpen = KisKR.IsMarketOpen()

if IsMarketOpen == True:
    print("Market Is Open!!!!!!!!!!!")
    #영상엔 없지만 리밸런싱이 가능할때만 내게 메시지를 보내자!
    # if Is_Rebalance_Go == True:
        # line_alert.SendMessage(PortfolioName + " (" + strYM + ") 장이 열려서 포트폴리오 리밸런싱 가능!!")
else:
    print("Market Is Close!!!!!!!!!!!")
    #영상엔 없지만 리밸런싱이 가능할때만 내게 메시지를 보내자!
    # if Is_Rebalance_Go == True:
        # line_alert.SendMessage(PortfolioName + " (" + strYM + ") 장이 닫혀서 포트폴리오 리밸런싱 불가능!!")





#####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################



#####################################################################################################################################

#계좌 잔고를 가지고 온다!
Balance = KisKR.GetBalance()
#####################################################################################################################################

'''-------통합 증거금 사용자는 아래 코드도 사용할 수 있습니다! -----------'''
#통합증거금 계좌 사용자 분들중 만약 미국계좌랑 통합해서 총자산을 계산 하고 포트폴리오 비중에도 반영하고 싶으시다면 아래 코드를 사용하시면 되고 나머지는 동일합니다!!!
#Balance = Common.GetBalanceKrwTotal()

'''-----------------------------------------------------------'''
#####################################################################################################################################




print("--------------내 보유 잔고---------------------")

pprint.pprint(Balance)

print("--------------------------------------------")
#총 평가금액에서 해당 봇에게 할당할 총 금액비율 1.0 = 100%  0.5 = 50%
InvestRate = 0.5

#기준이 되는 내 총 평가금액에서 투자비중을 곱해서 나온 포트폴리오에 할당된 돈!!
TotalMoney = float(Balance['TotalMoney']) * InvestRate

print("총 포트폴리오에 할당된 투자 가능 금액 : ", format(round(TotalMoney), ','))
'''

ETF찾기 참고 : https://blog.naver.com/zacra/222867823600
참고로 아시겠지만 ETF의 종목코드는 직접 검색하셔서 알아 내셔야 합니다!


공격형 자산 :

미국주식      TIGER 미국 S&P 500 "360750"
선진국 주식     KODEX 선진국 MSCI World "251350"
개발도상국 주식   ARIRANG 신흥국 MSCI(합성 H) "195980"
미국혼합채권    KODEX 200 미국채혼합 "284430"

안전 자산:

미국회사채      ARIRANG 미국장기우량회사채 "332620"
미국단기국채    TIGER 미국달러단기채권액티브 "329750"
미국중기국채    KODEX 단기채권 "153130"



'''

##########################################################

#투자 주식 리스트
MyPortfolioList = list()


asset1 = dict()
asset1['stock_code'] = "360750"       #종목코드
asset1['stock_type'] = "RISK"         #공격형(RISK) 자산인지 안전형(SAFE) 자산인지 여부
asset1['stock_momentum_score'] = 0    #모멘텀 스코어
asset1['stock_rebalance_amt'] = 0     #리밸런싱 해야 되는 수량


MyPortfolioList.append(asset1)



asset2 = dict()
asset2['stock_code'] = "251350"
asset2['stock_type'] = "RISK"         
asset2['stock_momentum_score'] = 0    
asset2['stock_rebalance_amt'] = 0


MyPortfolioList.append(asset2)



asset3 = dict()
asset3['stock_code'] = "195980"
asset3['stock_type'] = "RISK"         
asset3['stock_momentum_score'] = 0    
asset3['stock_rebalance_amt'] = 0


MyPortfolioList.append(asset3)



asset4 = dict()
asset4['stock_code'] = "284430"
asset4['stock_type'] = "RISK"         
asset4['stock_momentum_score'] = 0    
asset4['stock_rebalance_amt'] = 0

MyPortfolioList.append(asset4)





asset5 = dict()
asset5['stock_code'] = "332620"
asset5['stock_type'] = "SAFE"         
asset5['stock_momentum_score'] = 0    
asset5['stock_rebalance_amt'] = 0


MyPortfolioList.append(asset5)

asset6 = dict()
asset6['stock_code'] = "329750"
asset6['stock_type'] = "SAFE"         
asset6['stock_momentum_score'] = 0    
asset6['stock_rebalance_amt'] = 0


MyPortfolioList.append(asset6)

asset7 = dict()
asset7['stock_code'] = "153130"
asset7['stock_type'] = "SAFE"         
asset7['stock_momentum_score'] = 0    
asset7['stock_rebalance_amt'] = 0


MyPortfolioList.append(asset7)





##########################################################

print("--------------내 보유 주식---------------------")
#그리고 현재 이 계좌에서 보유한 주식 리스트를 가지고 옵니다!
MyStockList = KisKR.GetMyStockList()
pprint.pprint(MyStockList)
print("--------------------------------------------")
##########################################################


print("--------------리밸런싱 수량 계산 ---------------------")



print("-------------- 모멘텀 스코어 계산 ---------------------")

#모멘텀 스코어 구하기! 
for stock_info in MyPortfolioList:
    
    
    stock_code = stock_info['stock_code']
    print(KisKR.GetStockName(stock_code), "....")

    df = Common.GetOhlcv("KR",stock_code,250)

    Now_Price = df['close'][-1] #현재가
    #Now_Price = KisKR.GetCurrentPrice(stock_code)

    One_Price = df['close'][-20] #한달 전
    Three_Price = df['close'][-60] #3달전
    Six_Price = df['close'][-120] #6달전
    Twelve_Price = df['close'][-240] #1년전

    print(stock_code, Now_Price, One_Price, Three_Price, Six_Price, Twelve_Price)

    # 12*1개월 수익률, 4*3개월 수익률, 2*6개월 수익률, 1*12개월 수익률의 합!!
    MomentumScore = (((Now_Price - One_Price) / One_Price) * 12.0) + (((Now_Price - Three_Price) / Three_Price) * 4.0) + (((Now_Price - Six_Price) / Six_Price) * 2.0) + (((Now_Price - Twelve_Price) / Twelve_Price) * 1.0)

    stock_info['stock_momentum_score'] = MomentumScore

    #pprint.pprint(stock_info)




print("-------------- 공격 자산인지 안전 자산인지 결정 ---------------------")

RiskList = list() #공격 자산 리스트
SafeList = list() #안전 자산 리스트

#공격자산에 투자할지 안전자산에 투자할지 정하기!
IsPossibleRiskInvest = True

for stock_info in MyPortfolioList:

    pprint.pprint(stock_info)

    #공격 자산인데 
    if stock_info['stock_type'] == "RISK":
        #모멘텀 스코어가 마이너스다? 그럼 False로!!!
        if stock_info['stock_momentum_score'] < 0:
            IsPossibleRiskInvest = False

        RiskList.append(stock_info)

    else:

        SafeList.append(stock_info)


#최종 선택된 자산의 종목 코드가 들어간다!
PickStockCode = ""

#공격자산중 가장 모멘텀 점수가 높은 거를 픽한다
if IsPossibleRiskInvest == True:
    print("RISK Sort!")

    data = sorted(RiskList, key=lambda stock_info: (stock_info['stock_momentum_score']), reverse= True)
    pprint.pprint(data)

    PickStockCode = data[0]['stock_code']


#안전자산중 가장 모멘텀 점수가 낮은거를 픽한다!
else:
    print("SAFE Sort!")
    
    data = sorted(SafeList, key=lambda stock_info: (stock_info['stock_momentum_score']), reverse= True)
    pprint.pprint(data)

    PickStockCode = data[0]['stock_code']







strResult = "-- 현재 포트폴리오 상황 --\n"

#매수된 자산의 총합!
total_stock_money = 0

#현재 평가금액 기준으로 각 자산이 몇 주씩 매수해야 되는지 계산한다 (포트폴리오 비중에 따라) 이게 바로 리밸런싱 목표치가 됩니다.
for stock_info in MyPortfolioList:

    #내주식 코드
    stock_code = stock_info['stock_code']
    #매수할 자산 보유할 자산의 비중은 100%니깐 1.0으로 세팅
    stock_target_rate = 1.0

    #현재가!
    CurrentPrice = KisKR.GetCurrentPrice(stock_code)



    stock_name = ""
    stock_amt = 0 #수량
    stock_avg_price = 0 #평단
    stock_eval_totalmoney = 0 #총평가금액!
    stock_revenue_rate = 0 #종목 수익률
    stock_revenue_money = 0 #종목 수익금

 

    #내가 보유한 주식 리스트에서 매수된 잔고 정보를 가져온다
    for my_stock in MyStockList:
        if my_stock['StockCode'] == stock_code:
            stock_name = my_stock['StockName']
            stock_amt = int(my_stock['StockAmt'])
            stock_avg_price = float(my_stock['StockAvgPrice'])
            stock_eval_totalmoney = float(my_stock['StockNowMoney'])
            stock_revenue_rate = float(my_stock['StockRevenueRate'])
            stock_revenue_money = float(my_stock['StockRevenueMoney'])

            break


    print("#####" , KisKR.GetStockName(stock_code) ," stock_code: ", stock_code)


    #주식의 총 평가금액을 더해준다
    total_stock_money += stock_eval_totalmoney

    #현재 비중
    stock_now_rate = 0

    #잔고에 있는 경우 즉 이미 매수된 주식의 경우
    if stock_amt > 0:


        stock_now_rate = round((stock_eval_totalmoney / TotalMoney),3)

        print("---> NowRate:", round(stock_now_rate * 100.0,2), "%")



        # 선택된 자산이라면 100% 몰빵이니깐 유지하면 된다. 
        # 아래의 리밸런싱 로직을 타도록 내비둔 이유는 내 계좌 잔고가 늘어났다면(금액 추가 투입 등) 추가로 매수해야 되는 수량이 생길 수 있다.
        if PickStockCode == stock_code:

                
            #목표한 비중가 다르다면!!
            if stock_now_rate != stock_target_rate:


                #갭을 구한다!!!
                GapRate = stock_target_rate - stock_now_rate


                #그래서 그 갭만큼의 금액을 구한다
                GapMoney = TotalMoney * abs(GapRate) 
                #현재가로 나눠서 몇주를 매매해야 되는지 계산한다
                GapAmt = GapMoney / CurrentPrice

                #수량이 1보다 커야 리밸러싱을 할 수 있다!! 즉 그 전에는 리밸런싱 불가 
                if GapAmt >= 1.0:

                    GapAmt = int(GapAmt)

                    #갭이 음수라면! 비중이 더 많으니 팔아야 되는 상황!!!
                    if GapRate < 0:

                        #팔아야 되는 상황에서는 현재 주식수량에서 매도할 수량을 뺀 값이 1주는 남아 있어야 한다
                        #그래야 포트폴리오 상에서 아예 사라지는 걸 막는다!
                        if stock_amt - GapAmt >= 1:
                            stock_info['stock_rebalance_amt'] = -GapAmt

                    #갭이 양수라면 비중이 더 적으니 사야되는 상황!
                    else:  
                        stock_info['stock_rebalance_amt'] = GapAmt


        #선택된 자산이 아니라면 전 수량 다 팔아야 한다
        else:
            stock_info['stock_rebalance_amt'] = -stock_amt



    #잔고에 없는 경우
    else:

        #선택된 최종 자산이라면 100% 풀 매수 (stock_target_rate가 1.0 100%인걸 기억하자)
        if PickStockCode == stock_code:
            
            print("---> NowRate: 0%")

            #잔고가 없다면 첫 매수다! 비중대로 매수할 총 금액을 계산한다 
            BuyMoney = TotalMoney * stock_target_rate


            #매수할 수량을 계산한다!
            BuyAmt = int(BuyMoney / CurrentPrice)

            #포트폴리오에 들어간건 일단 무조건 1주를 사주자... 아니라면 아래 2줄 주석처리
        # if BuyAmt <= 0:
            #    BuyAmt = 1

            stock_info['stock_rebalance_amt'] = BuyAmt
            

        #선택된 최종 자산이 아니라면 아무것도 안하면 된다!
        else:
            print("Do nothing")
        

        
        
        
    #라인 메시지랑 로그를 만들기 위한 문자열 
    line_data =  (">> " + KisKR.GetStockName(stock_code) + "(" + stock_code + ") << \n비중: " + str(round(stock_now_rate * 100.0,2)) + "/" + str(round(stock_target_rate * 100.0,2)) 
    + "% \n수익: " + str(format(round(stock_revenue_money), ',')) + "("+ str(round(stock_revenue_rate,2)) 
    + "%) \n총평가금액: " + str(format(round(stock_eval_totalmoney), ',')) 
    + "\n리밸런싱수량: " + str(stock_info['stock_rebalance_amt']) + "\n----------------------\n")

    #만약 아래 한번에 보내는 라인메시지가 짤린다면 아래 주석을 해제하여 개별로 보내면 됩니다
    #if Is_Rebalance_Go == True:
    #    line_alert.SendMessage(line_data)
    strResult += line_data



##########################################################

print("--------------리밸런싱 해야 되는 수량-------------")

data_str = "\n" + PortfolioName + "\n" +  strResult + "\n포트폴리오할당금액: " + str(format(round(TotalMoney), ',')) + "\n매수한자산총액: " + str(format(round(total_stock_money), ',') )

#결과를 출력해 줍니다!
print(data_str)

#영상엔 없지만 리밸런싱이 가능할때만 내게 메시지를 보내자!
# if Is_Rebalance_Go == True:
    # line_alert.SendMessage(data_str)
    
#만약 위의 한번에 보내는 라인메시지가 짤린다면 아래 주석을 해제하여 개별로 보내면 됩니다
#if Is_Rebalance_Go == True:
#    line_alert.SendMessage("\n포트폴리오할당금액: " + str(format(round(TotalMoney), ',')) + "\n매수한자산총액: " + str(format(round(total_stock_money), ',') ))




print("--------------------------------------------")

##########################################################


#리밸런싱이 가능한 상태여야 하고 매수 매도는 장이 열려있어야지만 가능하다!!!
if Is_Rebalance_Go == True and IsMarketOpen == True:

    # line_alert.SendMessage(PortfolioName + " (" + strYM + ") 리밸런싱 시작!!")

    print("------------------리밸런싱 시작  ---------------------")
    #이제 목표치에 맞게 포트폴리오를 조정하면 되는데
    #매도를 해야 돈이 생겨 매수를 할 수 있을 테니
    #먼저 매도를 하고
    #그 다음에 매수를 해서 포트폴리오를 조정합니다!

    print("--------------매도 (리밸런싱 수량이 마이너스인거)---------------------")

    for stock_info in MyPortfolioList:

        #내주식 코드
        stock_code = stock_info['stock_code']
        rebalance_amt = stock_info['stock_rebalance_amt']

        #리밸런싱 수량이 마이너스인 것을 찾아 매도 한다!
        if rebalance_amt < 0:
                    
            #일반계좌 개인연금(저축)계좌에서는 이 함수를 사용합니다
            pprint.pprint(KisKR.MakeSellMarketOrder(stock_code,abs(rebalance_amt)))
            
            #퇴직연금 IRP 계좌에서는 아래 함수를 사용합니다.
            #pprint.pprint(KisKR.MakeSellMarketOrderIRP(stock_code,abs(rebalance_amt)))


    print("--------------------------------------------")


    #3초 정도 쉬어준다
    time.sleep(3.0)



    print("--------------매수 ---------------------")

    for stock_info in MyPortfolioList:

        #내주식 코드
        stock_code = stock_info['stock_code']
        rebalance_amt = stock_info['stock_rebalance_amt']

        #리밸런싱 수량이 플러스인 것을 찾아 매수 한다!
        if rebalance_amt > 0:
                    
            #일반계좌 개인연금(저축)계좌에서는 이 함수를 사용합니다
            pprint.pprint(KisKR.MakeBuyMarketOrder(stock_code,rebalance_amt))
            
            #퇴직연금 IRP 계좌에서는 아래 함수를 사용합니다.
            #pprint.pprint(KisKR.MakeBuyMarketOrderIRP(stock_code,rebalance_amt))


    print("--------------------------------------------")

    #########################################################################################################################
    #첫 매수던 리밸런싱이던 매매가 끝났으면 이달의 리밸런싱은 끝이다. 해당 달의 년달 즉 22년 9월이라면 '2022_9' 라는 값을 파일에 저장해 둔다! 
    #파일에 저장하는 부분은 여기가 유일!!!!
    YMDict['ym_st'] = strYM
    with open(static_asset_tym_file_path, 'w') as outfile:
        json.dump(YMDict, outfile)
    #########################################################################################################################
        
    #line_alert.SendMessage(PortfolioName + " (" + strYM + ") 리밸런싱 완료!!")
    print("------------------리밸런싱 끝---------------------")

