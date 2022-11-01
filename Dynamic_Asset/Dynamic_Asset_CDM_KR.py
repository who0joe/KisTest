# -*- coding: utf-8 -*-

import KIS_Common as Common
import KIS_API_Helper_KR as KisKR
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
PortfolioName = "동적자산배분전략_CDM"




#####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################

#전제는 크롭탭에 주말 빼고 우리나라 시간 아침10시 정각에 해당 봇이 돈다고 가정!
# 0 1 1-7 * 1-5 python3 /Users/TY/Documents/class101/Dynamic_Asset/Dynamic_Asset_CDM_KR.py 

#리밸런싱이 가능한지 여부를 판단!
Is_Rebalance_Go = False


#파일에 저장된 년월 문자열 (ex> 2022_9)를 읽는다
YMDict = dict()

#파일 경로입니다.
static_asset_tym_file_path = "/Users/TY/Documents/class101/Dynamic_Asset/Dynamic_Asset_CDM_KR.json"
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
    
else:
    print("Market Is Close!!!!!!!!!!!")
   


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


주식      TIGER 미국S&P500 "360750" or KODEX 선진국MSCI World "251350"
채권   ARIRANG 미국장기우량회사채 "332620" or TIGER 단기선진하이일드(합성 H) "182490"
부동산    KODEX 다우존스미국리츠(H) "352560" or TIGER 미국MSCI리츠(합성 H) "182480"
불경기    KODEX 200미국채혼합 "284430" or KINDEX KRX금현물 "411060"

비교할 단기채 --> TIGER 미국달러단기채권액티브 "329750" 


'''

##########################################################

##########################################################

#투자 주식 리스트
MyPortfolioList = list()


asset1 = dict()
asset1['stock_code'] = "360750"          #종목코드
asset1['stock_type'] = "STOCK"        #주식(STOCK) 채권(BOND) 리츠(REITS) 불경기(STRESS) 비교단기채(ST) 로 구분!
asset1['stock_momentum_score'] = 0    #모멘텀 스코어
asset1['stock_rebalance_amt'] = 0     #리밸런싱 해야 되는 수량


MyPortfolioList.append(asset1)



asset2 = dict()
asset2['stock_code'] = "251350"
asset2['stock_type'] = "STOCK"         
asset2['stock_momentum_score'] = 0    
asset2['stock_rebalance_amt'] = 0


MyPortfolioList.append(asset2)



asset3 = dict()
asset3['stock_code'] = "332620"
asset3['stock_type'] = "BOND"         
asset3['stock_momentum_score'] = 0    
asset3['stock_rebalance_amt'] = 0


MyPortfolioList.append(asset3)



asset4 = dict()
asset4['stock_code'] = "182490"
asset4['stock_type'] = "BOND"         
asset4['stock_momentum_score'] = 0    
asset4['stock_rebalance_amt'] = 0

MyPortfolioList.append(asset4)



asset5 = dict()
asset5['stock_code'] = "352560"
asset5['stock_type'] = "REITS"         
asset5['stock_momentum_score'] = 0    
asset5['stock_rebalance_amt'] = 0


MyPortfolioList.append(asset5)



asset6 = dict()
asset6['stock_code'] = "182480"
asset6['stock_type'] = "REITS"         
asset6['stock_momentum_score'] = 0    
asset6['stock_rebalance_amt'] = 0

MyPortfolioList.append(asset6)



asset7 = dict()
asset7['stock_code'] = "284430"
asset7['stock_type'] = "STRESS"         
asset7['stock_momentum_score'] = 0    
asset7['stock_rebalance_amt'] = 0


MyPortfolioList.append(asset7)



asset8 = dict()
asset8['stock_code'] = "411060"
asset8['stock_type'] = "STRESS"         
asset8['stock_momentum_score'] = 0    
asset8['stock_rebalance_amt'] = 0

MyPortfolioList.append(asset8)




asset9 = dict()
asset9['stock_code'] = "329750"
asset9['stock_type'] = "ST"         
asset9['stock_momentum_score'] = 0    
asset9['stock_rebalance_amt'] = 0

MyPortfolioList.append(asset9)




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
    
    df = Common.GetOhlcv("KR",stock_code)
    print(len(df))

    #Now_Price = df['close'][-1] #현재가
    #Year_Price = df['close'][-240] #12달전
    
    
    #이렇게 GetCloseData 함수를 이용해서 가져오면 더 안전? 합니다
    #모멘텀 구하는 다른 전략도 아래 함수를 사용하게 바꿔보세요!!
    Now_Price = Common.GetCloseData(df,-1) #현재가
    Year_Price = Common.GetCloseData(df,-240)  #12달전


    # 12개월 수익률 저장!!!
    stock_info['stock_momentum_score'] = (Now_Price - Year_Price) / Year_Price



print("-------------- 투자할 자산을 결정 ---------------------")

#기준이 되는 단기채권 ETF를 구한다!
ST_ETF = None

for stock_info in MyPortfolioList:
    if stock_info['stock_type'] == "ST":
        ST_ETF = stock_info




#########################################

#주식 영역에 해당하는 거를 픽한다!
StockAreaFinal_ETF = None
#채권 영역에 해당하는 거를 픽한다!
BondAreaFinal_ETF = None
#부동산 영역에 해당하는 거를 픽한다!
ReitsAreaFinal_ETF = None
#불경기 영역에 해당하는 거를 픽한다!
StressAreaFinal_ETF = None
#########################################

#투자할 ETF를 선정한다!!!
for stock_info in MyPortfolioList:

    #주식 영역
    if stock_info['stock_type'] == "STOCK":
        #단기 채권 수익률보다 높은 것만
        if ST_ETF['stock_momentum_score'] < stock_info['stock_momentum_score']:
            
            #디폴트 셋팅이 그대로라면 처음 발견된 단기 채권보다 높은 자산!
            if StockAreaFinal_ETF == None:
                StockAreaFinal_ETF = stock_info
            #이미 자산이 들어가 있는데 또 단기 채권 수익률 보다 높은게 들어왔다면 비교해서 큰 것으로 설정한다!
            else:
                #현재와 비교해서 크다면 설정!
                if StockAreaFinal_ETF['stock_momentum_score'] < stock_info['stock_momentum_score']:
                    StockAreaFinal_ETF = stock_info


    #채권 영역
    if stock_info['stock_type'] == "BOND":
        #단기 채권 수익률보다 높은 것만
        if ST_ETF['stock_momentum_score'] < stock_info['stock_momentum_score']:

            #디폴트 셋팅이 그대로라면 처음 발견된 단기 채권보다 높은 자산!
            if BondAreaFinal_ETF == None:
                BondAreaFinal_ETF = stock_info
            #이미 자산이 들어가 있는데 또 단기 채권 수익률 보다 높은게 들어왔다면 비교해서 큰 것으로 설정한다!
            else:
                #현재와 비교해서 크다면 설정!
                if BondAreaFinal_ETF['stock_momentum_score'] < stock_info['stock_momentum_score']:
                    BondAreaFinal_ETF = stock_info





    #부동산 영역
    if stock_info['stock_type'] == "REITS":
        #단기 채권 수익률보다 높은 것만
        if ST_ETF['stock_momentum_score'] < stock_info['stock_momentum_score']:
            #디폴트 셋팅이 그대로라면 처음 발견된 단기 채권보다 높은 자산!
            if ReitsAreaFinal_ETF == None:
                ReitsAreaFinal_ETF = stock_info
            #이미 자산이 들어가 있는데 또 단기 채권 수익률 보다 높은게 들어왔다면 비교해서 큰 것으로 설정한다!
            else:
                #현재와 비교해서 크다면 설정!
                if ReitsAreaFinal_ETF['stock_momentum_score'] < stock_info['stock_momentum_score']:
                    ReitsAreaFinal_ETF = stock_info




    #안전(불황기) 영역
    if stock_info['stock_type'] == "STRESS":
        #단기 채권 수익률보다 높은 것만
        if ST_ETF['stock_momentum_score'] < stock_info['stock_momentum_score']:
            #디폴트 셋팅이 그대로라면 처음 발견된 단기 채권보다 높은 자산!
            if StressAreaFinal_ETF == None:
                StressAreaFinal_ETF = stock_info
            #이미 자산이 들어가 있는데 또 단기 채권 수익률 보다 높은게 들어왔다면 비교해서 큰 것으로 설정한다!
            else:
                #현재와 비교해서 크다면 설정!
                if StressAreaFinal_ETF['stock_momentum_score'] < stock_info['stock_momentum_score']:
                    StressAreaFinal_ETF = stock_info



pprint.pprint(MyPortfolioList)

print("###################PICK ETF#########################")
pprint.pprint(StockAreaFinal_ETF)
pprint.pprint(BondAreaFinal_ETF)
pprint.pprint(ReitsAreaFinal_ETF)
pprint.pprint(StressAreaFinal_ETF)
print("###################PICK ETF#########################")








strResult = "-- 현재 포트폴리오 상황 --\n"

#매수된 자산의 총합!
total_stock_money = 0

#현재 평가금액 기준으로 각 자산이 몇 주씩 매수해야 되는지 계산한다 (포트폴리오 비중에 따라) 이게 바로 리밸런싱 목표치가 됩니다.
for stock_info in MyPortfolioList:

    #내주식 코드
    stock_code = stock_info['stock_code']
    #매수할 자산 보유할 자산의 각 비중은 25%니깐 0.25으로 세팅
    stock_target_rate = 0.25

    #기준이 된 ETF는 아무것도 안한다
    if stock_info['stock_type'] == "ST":
        continue
    
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



    ###########################################################################
    #각 영역별 선택된 보유 자산인지 여부
    SelectedOK = False

    #주식 영역
    if stock_info['stock_type'] == "STOCK":
        #선택된 자산이 있다면! 
        if StockAreaFinal_ETF != None:
            #선택받은 종목이다 그럼 보유한다!
            if stock_code == StockAreaFinal_ETF['stock_code']:
                SelectedOK = True

    #채권 영역
    if stock_info['stock_type'] == "BOND":
        #선택된 자산이 있다면! 
        if BondAreaFinal_ETF != None:
            #선택받은 종목이다 그럼 보유한다!
            if stock_code == BondAreaFinal_ETF['stock_code']:
                SelectedOK = True

    #부동산 영역
    if stock_info['stock_type'] == "REITS":
        #선택된 자산이 있다면! 
        if ReitsAreaFinal_ETF != None:
            #선택받은 종목이다 그럼 보유한다!
            if stock_code == ReitsAreaFinal_ETF['stock_code']:
                SelectedOK = True

    #불경기 영역
    if stock_info['stock_type'] == "STRESS":
        #선택된 자산이 있다면! 
        if StressAreaFinal_ETF != None:
            #선택받은 종목이다 그럼 보유한다!
            if stock_code == StressAreaFinal_ETF['stock_code']:
                SelectedOK = True


    ###########################################################################

    #주식의 총 평가금액을 더해준다
    total_stock_money += stock_eval_totalmoney

    #현재 비중
    stock_now_rate = 0

    #잔고에 있는 경우 즉 이미 매수된 주식의 경우
    if stock_amt > 0:

            
        stock_now_rate = round((stock_eval_totalmoney / TotalMoney),3)

        print("---> NowRate:", round(stock_now_rate * 100.0,2), "%")
        
        #선택된 자산은 유지!!!
        if SelectedOK == True:


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

        #선택된 최종 자산이라면 25% 매수 (stock_target_rate가 0.25 25%인걸 기억하자)
        if SelectedOK == True:
            
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

   
    strResult += line_data



##########################################################

print("--------------리밸런싱 해야 되는 수량-------------")

data_str = "\n" + PortfolioName + "\n" +  strResult + "\n포트폴리오할당금액: " + str(format(round(TotalMoney), ',')) + "\n매수한자산총액: " + str(format(round(total_stock_money), ',') )

#결과를 출력해 줍니다!
print(data_str)


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
        
  
    print("------------------리밸런싱 끝---------------------")

