# -*- coding: utf-8 -*-

import KIS_Common as Common
import KIS_API_Helper_US as KisUS
import time
import json
import pprint


#계좌 선택.. "VIRTUAL" 는 모의 계좌!
Common.SetChangeMode("VIRTUAL") #REAL or VIRTUAL



#시간 정보를 읽는다
time_info = time.gmtime()
#년월 문자열을 만든다 즉 2022년 9월이라면 2022_9 라는 문자열이 만들어져 strYM에 들어간다!
strYM = str(time_info.tm_year) + "_" + str(time_info.tm_mon)
print("ym_st: " , strYM)



#포트폴리오 이름
PortfolioName = "동적자산배분전략_DAA"




#####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################

#전제는 크롭탭에 주말 빼고 UTC 0시 기준 16시/ 우리나라 시간 새벽1시 정각에 해당 봇이 돈다고 가정!
# 0 16 1-7 * 1-5 python3 /Users/TY/Documents/class101/Dynamic_Asset/Dynamic_Asset_DAA_US.py 


#리밸런싱이 가능한지 여부를 판단!
Is_Rebalance_Go = False


#파일에 저장된 년월 문자열 (ex> 2022_9)를 읽는다
YMDict = dict()

#파일 경로입니다.
static_asset_tym_file_path = "/Users/TY/Documents/class101/Dynamic_Asset/Dynamic_Asset_DAA_US.json"
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
IsMarketOpen = KisUS.IsMarketOpen()

if IsMarketOpen == True:
    print("Market Is Open!!!!!!!!!!!")
   
else:
    print("Market Is Close!!!!!!!!!!!")
    





#####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################


#계좌 잔고를 가지고 온다!
Balance = KisUS.GetBalance()


print("--------------내 보유 잔고---------------------")

pprint.pprint(Balance)

print("--------------------------------------------")
#총 평가금액에서 해당 봇에게 할당할 총 금액비율 1.0 = 100%  0.5 = 50%
InvestRate = 0.04

#기준이 되는 내 총 평가금액에서 투자비중을 곱해서 나온 포트폴리오에 할당된 돈!!
TotalMoney = float(Balance['TotalMoney']) * InvestRate

print("총 포트폴리오에 할당된 투자 가능 금액 : $", TotalMoney)


'''

공격형 자산 :

미국대형주          SPY
나스닥             QQQ
미국소형주(러셀 2000) IWM
유럽주식             VGK
일본주식              EWJ
개발도상국주식       EEM 
미국리츠            VNQ
금               GLD
원자재            DBC
하이일드            HYG
회사채              LQD
미국장기채            TLT


안전 자산:

미국회사채      LQD
미국중기국채    IEF
미국단기국채    SHY



카나리아 자산
개발도상국주식 EEM 
미국총채권    AGG  


'''

##########################################################

#위험 자산 투자시 상위 몇 개를 투자할지
RiskAssetCnt = 6


#투자 주식 리스트
MyPortfolioList = list()


asset1 = dict()
asset1['stock_code'] = "SPY"          #종목코드
asset1['stock_type'] = "RISK"         #공격형(RISK) 자산인지 안전형(SAFE) 자산인지 카나리아(BIRD) 자산인지 여부
asset1['stock_momentum_score'] = 0    #모멘텀 스코어
asset1['stock_target_rate'] = 0   #포트폴리오 목표 비중
asset1['stock_rebalance_amt'] = 0     #리밸런싱 해야 되는 수량
MyPortfolioList.append(asset1)

asset2 = dict()
asset2['stock_code'] = "QQQ"
asset2['stock_type'] = "RISK"         
asset2['stock_momentum_score'] = 0    
asset2['stock_target_rate'] = 0   
asset2['stock_rebalance_amt'] = 0
MyPortfolioList.append(asset2)

asset3 = dict()
asset3['stock_code'] = "IWM"
asset3['stock_type'] = "RISK"         
asset3['stock_momentum_score'] = 0    
asset3['stock_target_rate'] = 0   
asset3['stock_rebalance_amt'] = 0
MyPortfolioList.append(asset3)

asset4 = dict()
asset4['stock_code'] = "VGK"
asset4['stock_type'] = "RISK"         
asset4['stock_momentum_score'] = 0    
asset4['stock_target_rate'] = 0   
asset4['stock_rebalance_amt'] = 0
MyPortfolioList.append(asset4)

asset5 = dict()
asset5['stock_code'] = "EWJ"
asset5['stock_type'] = "RISK"         
asset5['stock_momentum_score'] = 0    
asset5['stock_target_rate'] = 0   
asset5['stock_rebalance_amt'] = 0
MyPortfolioList.append(asset5)

asset6 = dict()
asset6['stock_code'] = "EEM"
asset6['stock_type'] = "RISK"         
asset6['stock_momentum_score'] = 0    
asset6['stock_target_rate'] = 0   
asset6['stock_rebalance_amt'] = 0
MyPortfolioList.append(asset6)

asset7 = dict()
asset7['stock_code'] = "VNQ"
asset7['stock_type'] = "RISK"         
asset7['stock_momentum_score'] = 0    
asset7['stock_target_rate'] = 0   
asset7['stock_rebalance_amt'] = 0
MyPortfolioList.append(asset7)

asset8 = dict()
asset8['stock_code'] = "GLD"
asset8['stock_type'] = "RISK"         
asset8['stock_momentum_score'] = 0    
asset8['stock_target_rate'] = 0   
asset8['stock_rebalance_amt'] = 0
MyPortfolioList.append(asset8)

asset9 = dict()
asset9['stock_code'] = "DBC"
asset9['stock_type'] = "RISK"         
asset9['stock_momentum_score'] = 0    
asset9['stock_target_rate'] = 0   
asset9['stock_rebalance_amt'] = 0
MyPortfolioList.append(asset9)

asset10 = dict()
asset10['stock_code'] = "HYG"
asset10['stock_type'] = "RISK"         
asset10['stock_momentum_score'] = 0   
asset10['stock_target_rate'] = 0    
asset10['stock_rebalance_amt'] = 0
MyPortfolioList.append(asset10)

asset11 = dict()
asset11['stock_code'] = "LQD"
asset11['stock_type'] = "RISK"         
asset11['stock_momentum_score'] = 0    
asset11['stock_target_rate'] = 0   
asset11['stock_rebalance_amt'] = 0
MyPortfolioList.append(asset11)

asset12 = dict()
asset12['stock_code'] = "TLT"
asset12['stock_type'] = "RISK"         
asset12['stock_momentum_score'] = 0    
asset12['stock_target_rate'] = 0   
asset12['stock_rebalance_amt'] = 0
MyPortfolioList.append(asset12)



asset13 = dict()
asset13['stock_code'] = "SHY"
asset13['stock_type'] = "SAFE"         
asset13['stock_momentum_score'] = 0   
asset13['stock_target_rate'] = 0    
asset13['stock_rebalance_amt'] = 0
MyPortfolioList.append(asset13)

asset14 = dict()
asset14['stock_code'] = "IEF"
asset14['stock_type'] = "SAFE"         
asset14['stock_momentum_score'] = 0    
asset14['stock_target_rate'] = 0   
asset14['stock_rebalance_amt'] = 0
MyPortfolioList.append(asset14)

asset15 = dict()
asset15['stock_code'] = "LQD"
asset15['stock_type'] = "SAFE"         
asset15['stock_momentum_score'] = 0   
asset15['stock_target_rate'] = 0    
asset15['stock_rebalance_amt'] = 0
MyPortfolioList.append(asset15)





asset16 = dict()
asset16['stock_code'] = "EEM"
asset16['stock_type'] = "BIRD"         
asset16['stock_momentum_score'] = 0    
asset16['stock_target_rate'] = 0   
asset16['stock_rebalance_amt'] = 0
MyPortfolioList.append(asset16)

asset17 = dict()
asset17['stock_code'] = "AGG"
asset17['stock_type'] = "BIRD"         
asset17['stock_momentum_score'] = 0    
asset17['stock_target_rate'] = 0   
asset17['stock_rebalance_amt'] = 0
MyPortfolioList.append(asset17)




##########################################################

print("--------------내 보유 주식---------------------")
#그리고 현재 이 계좌에서 보유한 주식 리스트를 가지고 옵니다!
MyStockList = KisUS.GetMyStockList()
pprint.pprint(MyStockList)
print("--------------------------------------------")
##########################################################




print("--------------리밸런싱 계산 ---------------------")


print("-------------- 모멘텀 스코어 계산 ---------------------")

#모든 자산의 모멘텀 스코어 구하기! 
for stock_info in MyPortfolioList:
    print("....")
    stock_code = stock_info['stock_code']

    df = Common.GetOhlcv("US",stock_code)

    '''
    Now_Price = df['close'][-1] #현재가
    One_Price = df['close'][-20] #한달 전
    Three_Price = df['close'][-60] #3달전
    Six_Price = df['close'][-120] #6달전
    Twelve_Price = df['close'][-240] #1년전
    '''

    Now_Price = Common.GetCloseData(df,-1) #현재가
    One_Price = Common.GetCloseData(df,-20) #한달 전
    Three_Price = Common.GetCloseData(df,-60) #3달전
    Six_Price = Common.GetCloseData(df,-120) #6달전
    Twelve_Price = Common.GetCloseData(df,-240) #1년전


    print(stock_code, Now_Price, One_Price, Three_Price, Six_Price, Twelve_Price)

    # 12*1개월 수익률, 4*3개월 수익률, 2*6개월 수익률, 1*12개월 수익률의 합!!
    MomentumScore = (((Now_Price - One_Price) / One_Price) * 12.0) + (((Now_Price - Three_Price) / Three_Price) * 4.0) + (((Now_Price - Six_Price) / Six_Price) * 2.0) + (((Now_Price - Twelve_Price) / Twelve_Price) * 1.0)

    stock_info['stock_momentum_score'] = MomentumScore

    print(stock_code," -> MomentumScore: ",MomentumScore)






print("-------------- 투자 자산과 비중 결정 ---------------------")

RiskList = list() #공격 자산 리스트
SafeList = list() #안전 자산 리스트

#카나리아 자산이 
BirdAssetMinusCnt = 0

for stock_info in MyPortfolioList:

    pprint.pprint(stock_info)

    #카나리아 자산인데 
    if stock_info['stock_type'] == "BIRD":
        #모멘텀 스코어가 마이너스다? 그럼 숫자를 증가시켜주자!
        if stock_info['stock_momentum_score'] < 0:
            BirdAssetMinusCnt += 1

    elif stock_info['stock_type'] == "RISK":

        RiskList.append(stock_info)

    elif stock_info['stock_type'] == "SAFE":

        SafeList.append(stock_info)





#안전 자산 중 가장 모멘텀 스코어가 높은거 1개를 구한다!
Safedata = sorted(SafeList, key=lambda stock_info: (stock_info['stock_momentum_score']), reverse= True)
pprint.pprint(Safedata)

#이곳에는 안전자산중 수익률이 가장 높은거 1개 들어간다!
SafeTopStockCode = Safedata[0]['stock_code']



#위험 자산 중 가장 모멘텀 스코어가 높은 상위 6개를 구한다.
Riskdata = sorted(RiskList, key=lambda stock_info: (stock_info['stock_momentum_score']), reverse= True)
pprint.pprint(Riskdata)

#이 리스트에는 위험 자산중 수익률이 가장 높은거 6개 들어간다!
RiskSafeTopStockCodeList = list()

for i in range(0,RiskAssetCnt):
    RiskSafeTopStockCodeList.append(Riskdata[i]['stock_code'])





###############################
#최종 투자해야 자산 코드 리스트!!
FinalSelectedList = list()
###############################

for stock_info in MyPortfolioList:

    stock_code = stock_info['stock_code']

    #100% 안전자산에 투자
    if BirdAssetMinusCnt == 2:

        if stock_info['stock_type'] == "SAFE":
            #가장 수익률 높은 안전자산이랑 코드가 같다면 최종 선택된 자산!
            if stock_code == SafeTopStockCode:
                FinalSelectedList.append(stock_code) #최종 선택에 넣어준다!
                stock_info['stock_target_rate'] = 100.0 #비중은 100%이다 


    #50%는 공격 50%는 안전
    elif BirdAssetMinusCnt == 1:

        if stock_info['stock_type'] == "RISK":
            #가장 수익률 높은 위험자산 6개의 리스트에 포함이 되어 있다면!
            if Common.CheckStockCodeInList(RiskSafeTopStockCodeList,stock_code) == True:
                FinalSelectedList.append(stock_code) #최종 선택에 넣어준다!
                stock_info['stock_target_rate'] = 50.0 / float(RiskAssetCnt) #비중은 50% / 6이다 


        if stock_info['stock_type'] == "SAFE":
            #가장 수익률 높은 안전자산이랑 코드가 같다면 최종 선택된 자산!
            if stock_code == SafeTopStockCode:
                FinalSelectedList.append(stock_code) #최종 선택에 넣어준다!
                stock_info['stock_target_rate'] = 50.0 #비중은 50%이다 



    #100% 공격자산에 투자
    elif BirdAssetMinusCnt == 0:

        if stock_info['stock_type'] == "RISK":
            #가장 수익률 높은 위험자산 6개의 리스트에 포함이 되어 있다면!
            if Common.CheckStockCodeInList(RiskSafeTopStockCodeList,stock_code) == True:
                FinalSelectedList.append(stock_code) #최종 선택에 넣어준다!
                stock_info['stock_target_rate'] = 100.0 / float(RiskAssetCnt) #비중은 100% / 6이다 

    

print("----FINAL SELECTED ASSET!-----")
pprint.pprint(FinalSelectedList)
print("-----------------------------")





strResult = "-- 현재 포트폴리오 상황 --\n"

#매수된 자산의 총합!
total_stock_money = 0

#현재 평가금액 기준으로 각 자산이 몇 주씩 매수해야 되는지 계산한다 (포트폴리오 비중에 따라) 이게 바로 리밸런싱 목표치가 됩니다.
for stock_info in MyPortfolioList:

    #내주식 코드
    stock_code = stock_info['stock_code']
    #매수할 자산 보유할 자산의 비중을 넣어준다!
    stock_target_rate = float(stock_info['stock_target_rate']) / 100.0


    #기준이 된 카나리아 자산 ETF는 아무것도 안한다
    if stock_info['stock_type'] == "BIRD":
        continue



    #현재가!
    CurrentPrice = KisUS.GetCurrentPrice(stock_code)


    
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

    print("##### stock_code: ", stock_code)

    #주식의 총 평가금액을 더해준다
    total_stock_money += stock_eval_totalmoney

    #현재 비중
    stock_now_rate = 0

    #잔고에 있는 경우 즉 이미 매수된 주식의 경우
    if stock_amt > 0:


        stock_now_rate = round((stock_eval_totalmoney / TotalMoney),3)

        print("---> NowRate:", round(stock_now_rate * 100.0,2), "%")

        #최종 선택된 자산리스트에 포함되어 있다면 비중대로 보유해야 한다! 리밸린싱!
        if Common.CheckStockCodeInList(FinalSelectedList,stock_code) == True:


            #목표한 비중이 다르다면!! stock_target_rate 는 100%
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

        #최종 선택된 자산리스트에 포함되어 있다면 비중대로 매수해야 한다!
        if Common.CheckStockCodeInList(FinalSelectedList,stock_code) == True:

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
    line_data =  (">> " + stock_code + " << \n비중: " + str(round(stock_now_rate * 100.0,2)) + "/" + str(round(stock_target_rate * 100.0,2)) 
    + "% \n수익: $" + str(stock_revenue_money) + "("+ str(round(stock_revenue_rate,2)) 
    + "%) \n총평가금액: $" + str(round(stock_eval_totalmoney,2)) 
    + "\n리밸런싱수량: " + str(stock_info['stock_rebalance_amt']) + "\n----------------------\n")

    #만약 아래 한번에 보내는 라인메시지가 짤린다면 아래 주석을 해제하여 개별로 보내면 됩니다
   
    strResult += line_data



##########################################################

print("--------------리밸런싱 해야 되는 수량-------------")

data_str = "\n" + PortfolioName + "\n" +  strResult + "\n포트폴리오할당금액: $" + str(round(TotalMoney,2)) + "\n매수한자산총액: $" + str(round(total_stock_money,2))

#결과를 출력해 줍니다!
print(data_str)

#영상엔 없지만 리밸런싱이 가능할때만 내게 메시지를 보내자!
#if Is_Rebalance_Go == True:
#    line_alert.SendMessage(data_str)
    


print("--------------------------------------------")

##########################################################


#리밸런싱이 가능한 상태여야 하고 매수 매도는 장이 열려있어야지만 가능하다!!!
if Is_Rebalance_Go == True and IsMarketOpen == True:


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
                    
            #현재가!
            CurrentPrice = KisUS.GetCurrentPrice(stock_code)

            #현재가보다 아래에 매도 주문을 넣음으로써 시장가로 매도
            CurrentPrice *= 0.9
            pprint.pprint(KisUS.MakeSellLimitOrder(stock_code,abs(rebalance_amt),CurrentPrice))

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
                    
            #현재가!
            CurrentPrice = KisUS.GetCurrentPrice(stock_code)


            #현재가보다 위에 매수 주문을 넣음으로써 시장가로 매수
            CurrentPrice *= 1.1
            pprint.pprint(KisUS.MakeBuyLimitOrder(stock_code,rebalance_amt,CurrentPrice))


    print("--------------------------------------------")

    #########################################################################################################################
    #첫 매수던 리밸런싱이던 매매가 끝났으면 이달의 리밸런싱은 끝이다. 해당 달의 년달 즉 22년 9월이라면 '2022_9' 라는 값을 파일에 저장해 둔다! 
    #파일에 저장하는 부분은 여기가 유일!!!!
    YMDict['ym_st'] = strYM
    with open(static_asset_tym_file_path, 'w') as outfile:
        json.dump(YMDict, outfile)
    #########################################################################################################################
        
  
    print("------------------리밸런싱 끝---------------------")

