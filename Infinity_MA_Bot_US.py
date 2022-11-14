import KIS_Common as Common
import KIS_API_Helper_US as KisUS
import json
import pprint
import line_alert 

Common.SetChangeMode("VIRTUAL")



BOT_NAME = Common.GetNowDist() + "_InfinityMaBot"

#투자할 종목!
TargetStockList = ['TQQQ','SOXL']




#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
############# 해당 전략으로 매수한 종목 데이터 리스트 ####################
InfinityMaDataList = list()
#파일 경로입니다.
bot_file_path = "/Users/TY/Documents/class101/UsStock_" + BOT_NAME + ".json"

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(bot_file_path, 'r') as json_file:
        InfinityMaDataList = json.load(json_file)

except Exception as e:
    print("Exception by First")
################################################################
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#


#계좌 잔고를 가지고 온다!
Balance = KisUS.GetBalance()



print("--------------내 보유 잔고---------------------")

pprint.pprint(Balance)

print("--------------------------------------------")
#총 평가금액에서 해당 봇에게 할당할 총 금액비율 1.0 = 100%  0.5 = 50%
InvestRate = 0.4

#기준이 되는 내 총 평가금액에서 투자비중을 곱해서 나온 포트폴리오에 할당된 돈!!
TotalMoney = float(Balance['TotalMoney']) * InvestRate

#각 종목당 투자할 금액! 리스트의 종목 개수로 나눈다!
StockMoney = TotalMoney / len(TargetStockList)
print("TotalMoney:", str(format(round(TotalMoney), ',')))
print("StockMoney:", str(format(round(StockMoney), ',')))

#분할된 투자금!
StMoney = StockMoney / 50.0

print("StMoney:", str(format(round(StMoney), ',')))



#########################-트레일링스탑 적용-#######################
TraillingStopRate = 0.01 #1%기준으로 트레일링 스탑!




print("--------------내 보유 주식---------------------")
#그리고 현재 이 계좌에서 보유한 주식 리스트를 가지고 옵니다!
MyStockList = KisUS.GetMyStockList()
pprint.pprint(MyStockList)
print("--------------------------------------------")
    

#마켓이 열렸는지 여부~!
IsMarketOpen = KisUS.IsMarketOpen()

#장이 열렸을 때!
if IsMarketOpen == True:


    #투자할 종목을 순회한다!
    for stock_code in TargetStockList:

        #주식(ETF) 정보~
        stock_name = ""
        stock_amt = 0 #수량
        stock_avg_price = 0 #평단
        stock_eval_totalmoney = 0 #총평가금액!
        stock_revenue_rate = 0 #종목 수익률
        stock_revenue_money = 0 #종목 수익금


        #매수된 상태라면 정보를 넣어준다!!!
        for my_stock in MyStockList:
            if my_stock['StockCode'] == stock_code:
                stock_name = my_stock['StockName']
                stock_amt = int(my_stock['StockAmt'])
                stock_avg_price = float(my_stock['StockAvgPrice'])
                stock_eval_totalmoney = float(my_stock['StockNowMoney'])
                stock_revenue_rate = float(my_stock['StockRevenueRate'])
                stock_revenue_money = float(my_stock['StockRevenueMoney'])

                break
                

        #현재가
        CurrentPrice = KisUS.GetCurrentPrice(stock_code)

            
        #종목 데이터
        PickStockInfo = None

        #저장된 종목 데이터를 찾는다
        for StockInfo in InfinityMaDataList:
            if StockInfo['StockCode'] == stock_code:
                PickStockInfo = StockInfo
                break

        #PickStockInfo 이게 없다면 매수되지 않은 처음 상태이거나 이전에 손으로 매수한 종목인데 해당 봇으로 돌리고자 할 때!
        if PickStockInfo == None:
            #잔고가 없다 즉 처음이다!!!
            if stock_amt == 0:

                InfinityDataDict = dict()
                
                InfinityDataDict['StockCode'] = stock_code #종목 코드
                InfinityDataDict['Round'] = 0    #현재 회차
                InfinityDataDict['IsReady'] = 'Y' #하루에 한번 체크하고 매수등의 처리를 하기 위한 플래그

                InfinityDataDict['S_WaterAmt'] = 0 #물탄 수량!
                InfinityDataDict['S_WaterLossMoney'] = 0 #물탄 수량을 팔때 손해본 금액

                InfinityDataDict['TrallingPrice'] = 0 #트레일링 추적할 가격
                InfinityDataDict['IsTralling'] = 'N' #트레일링 시작 여부

                InfinityMaDataList.append(InfinityDataDict) #데이터를 추가 한다!


                msg = stock_code + " 이평무한매수봇 첫 시작!!!!"
                print(msg) 
                line_alert.SendMessage(msg) 
                
            #데이터가 없는데 잔고가 있다? 이미 이 봇으로 트레이딩 하기전에 매수된 종목!
            else:
                print("Exist")

                InfinityDataDict = dict()
                
                InfinityDataDict['StockCode'] = stock_code #종목 코드
                InfinityDataDict['Round'] = int(stock_eval_totalmoney / StMoney)    #현재 회차 - 매수된 금액을 50분할된 단위 금액으로 나누면 회차가 나온다!
                InfinityDataDict['IsReady'] = 'Y' #하루에 한번 체크하고 매수등의 처리를 하기 위한 플래그

                InfinityDataDict['S_WaterAmt'] = 0 #물탄 수량!
                InfinityDataDict['S_WaterLossMoney'] = 0 #물탄 수량을 팔때 손해본 금액


                InfinityDataDict['TrallingPrice'] = 0 #트레일링 추적할 가격
                InfinityDataDict['IsTralling'] = 'N' #트레일링 시작 여부

                InfinityMaDataList.append(InfinityDataDict) #데이터를 추가 한다!


                msg = stock_code + " 기존에 매수한 종목을 이평무한매수봇으로 변경해서 트레이딩 첫 시작!!!! " + str(InfinityDataDict['Round']) + "회차로 세팅 완료!"
                print(msg) 
                line_alert.SendMessage(msg) 

            #파일에 저장
            with open(bot_file_path, 'w') as outfile:
                json.dump(InfinityMaDataList, outfile)
                

        #이제 데이터(InfinityMaDataList)는 확실히 있을 테니 본격적으로 트레이딩을 합니다!
        for StockInfo in InfinityMaDataList:

            if StockInfo['StockCode'] == stock_code:

                #1회차 이상 매수된 상황이라면 익절 조건을 체크해서 익절 처리 해야 한다!
                if StockInfo['Round'] > 0 :


                    #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
                    #########################-트레일링스탑 적용-#######################
                    #트레일링 스탑이 시작되었다면 이전에 저장된 값 대비 트레일링 스탑 비중만큼 떨어졌다면 스탑!
                    #아니라면 고점 갱신해줍니다!!
                    if StockInfo['IsTralling'] == 'Y':

                        #스탑할 가격을 구합니다.
                        StopPrice = StockInfo['TrallingPrice'] * (1.0 - TraillingStopRate)

                        #스탑할 가격보다 작아졌다면
                        if CurrentPrice <= StopPrice:

                            #현재가보다 아래에 매도 주문을 넣음으로써 시장가로 매도효과!
                            pprint.pprint(KisUS.MakeSellLimitOrder(stock_code,stock_amt,CurrentPrice*0.9))


                            msg = stock_code + " 이평무한매수봇 모두 팔아서 수익확정!!!!  [" + str(stock_revenue_money) + "] 수익 조으다! (현재 [" + str(StockInfo['Round']) + "] 라운드까지 진행되었고 모든 수량 매도 처리! )"
                            print(msg) 
                            line_alert.SendMessage(msg) 

                            #전량 매도 모두 초기화! 
                            StockInfo['TrallingPrice'] = 0
                            StockInfo['IsTralling'] = 'N' 
                            StockInfo['Round'] = 0
                            StockInfo['IsReady'] = 'N' #익절한 날은 매수 안하고 즐기자!
                            StockInfo['S_WaterAmt'] = 0 #물탄 수량 초기화 
                            StockInfo['S_WaterLossMoney'] = 0 #물탄 수량을 팔때 손해본 금액 초기화!

                            #파일에 저장
                            with open(bot_file_path, 'w') as outfile:
                                json.dump(InfinityMaDataList, outfile)

                        #현재가가 이전에 저장된 가격보다 높아졌다면 고점 갱신!!!
                        if StockInfo['TrallingPrice'] < CurrentPrice:

                            StockInfo['TrallingPrice'] = CurrentPrice

                            #파일에 저장
                            with open(bot_file_path, 'w') as outfile:
                                json.dump(InfinityMaDataList, outfile)

                    #트레일링 스탑 아직 시작 안됨!
                    else:

                        #목표 수익률을 구한다! 
                        '''
                        1회 :  10% + 1%
                        10회  8.5% + 1%
                        20회  7%
                        30회  5.5%
                        40회 : 4%
                        '''
                        TargetRate = (10.0 - StockInfo['Round']*0.15) / 100.0

                        #현재총평가금액은 물타기 손실금액을 반영한게 아니다.
                        #손실액이 현재 평가금액 대비 비중이 얼마인지 체크한다. 
                        PlusRate = StockInfo['S_WaterLossMoney'] / stock_eval_totalmoney

                        #그래서 목표수익률이랑 손실액을 커버하기 위한 수익률을 더해준다! + 트레일링 스탑 기준도 더해서 수익 확보!
                        FinalRate = TargetRate + PlusRate + TraillingStopRate

                        print("TargetRate:", TargetRate , "+ PlusRate:" ,PlusRate , "  -> FinalRate:" , FinalRate)
                        #수익화할 가격을 구한다!
                        RevenuePrice = stock_avg_price + (1.0 + FinalRate) 

                        #목표한 수익가격보다 현재가가 높다면 익절처리할 순간이다!
                        if CurrentPrice >= RevenuePrice:
                            
                            if stock_amt == 1:
                                    

                                #현재가보다 아래에 매도 주문을 넣음으로써 시장가로 매도효과!
                                pprint.pprint(KisUS.MakeSellLimitOrder(stock_code,stock_amt,CurrentPrice*0.9))


                                msg = stock_code + " 이평무한매수봇 모두 팔아서 수익확정!!!!  [" + str(stock_revenue_money) + "] 수익 조으다! (현재 [" + str(StockInfo['Round']) + "] 라운드까지 진행되었고 모든 수량 매도 처리! )"
                                print(msg) 
                                line_alert.SendMessage(msg) 

                                #전량 매도 모두 초기화! 
                                StockInfo['TrallingPrice'] = 0
                                StockInfo['IsTralling'] = 'N' 
                                StockInfo['Round'] = 0
                                StockInfo['IsReady'] = 'N' #익절한 날은 매수 안하고 즐기자!
                                StockInfo['S_WaterAmt'] = 0 #물탄 수량 초기화 
                                StockInfo['S_WaterLossMoney'] = 0 #물탄 수량을 팔때 손해본 금액 초기화!

                                #파일에 저장
                                with open(bot_file_path, 'w') as outfile:
                                    json.dump(InfinityMaDataList, outfile)

                                
                            else:

                                #절반은 바로 팔고 절반은 트레일링 스탑으로 처리한다!!!
                                HalfAmt = int(stock_amt * 0.5)

                                #절반만 팝니다!!!!!
                                pprint.pprint(KisUS.MakeSellLimitOrder(stock_code,HalfAmt,CurrentPrice*0.9))


                                msg = stock_code + " 이평무한매수봇 절반 팔아서 수익확정!!!!  [" + str(stock_revenue_money) + "] 수익 조으다! (현재 [" + str(StockInfo['Round']) + "] 라운드까지 진행되었고 절반 익절 후 트레일링 스탑 시작!!)"
                                print(msg) 
                                line_alert.SendMessage(msg) 

                                StockInfo['TrallingPrice'] = CurrentPrice
                                StockInfo['IsTralling'] = 'Y' #트레일링 스탑 시작!

                                #파일에 저장
                                with open(bot_file_path, 'w') as outfile:
                                    json.dump(InfinityMaDataList, outfile)



                #매수는 장이 열렸을 때 1번만 해야 되니깐! 안의 로직을 다 수행하면 N으로 바꿔준다! 그리고 트레일링 스탑이 진행중이라면 추가매수하지 않는다!
                if StockInfo['IsReady'] == 'Y' and StockInfo['IsTralling'] =='N':



                    #50분할된 투자금이 현재가격보다 작다면..투자금이 너무 작다!
                    if CurrentPrice > StMoney:

                        msg = stock_code + " 현재 50분할된 투자금보다 현재가가 높아서 전략을 제대로 수행 못해요!  자금을 투자비중이나늘리세요!"
                        print(msg)   
                        line_alert.SendMessage(msg) 



                    #캔들 데이터를 읽는다
                    df = Common.GetOhlcv("US",stock_code, 50)

                    #5일 이평선
                    Ma5_before3 = Common.GetMA(df,5,-4)
                    Ma5_before = Common.GetMA(df,5,-3)
                    Ma5 = Common.GetMA(df,5,-2)

                    print("MA5",Ma5_before3, "->", Ma5_before, "-> ",Ma5)

                    #20일 이평선
                    Ma20_before = Common.GetMA(df,20,-3)
                    Ma20 = Common.GetMA(df,20,-2)

                    print("MA20", Ma20_before, "-> ",Ma20)

                    #양봉 캔들인지 여부
                    IsUpCandle = False

                    #시가보다 종가가 크다면 양봉이다
                    if df['open'][-2] <= df['close'][-2]:
                        IsUpCandle = True

                    print("IsUpCandle : ", IsUpCandle)




                            
                    #40회를 넘었다면! 풀매수 상태이다!
                    if StockInfo['Round'] > 40:
                        #그런데 애시당초 후반부는 5일선이 증가추세일때만 매매 하므로 5일선이 하락으로 바뀌었다면 이때 손절처리를 한다
                        if Ma5_before > Ma5:
                            #절반을 손절처리 한다

                            HalfAmt = int(stock_amt * 0.5)

                            #절반만 팝니다!!!!!
                            pprint.pprint(KisUS.MakeSellLimitOrder(stock_code,HalfAmt,CurrentPrice*0.9))

                            StockInfo['Round'] = 21 #라운드는 절반을 팔았으니깐 21회로 초기화

                            #단 현재 수익금이 마이너스 즉 손실 상태라면 손실 금액을 저장해 둔다!
                            if stock_revenue_money < 0:
                                #손실 금액에서 매도수량/보유수량 즉 예로 10개보유 하고 현재 -100달러인데 5개를 파는 거라면 실제 확정 손실금은 -100 * (5/10)이 니깐~
                                LossMoney = abs(stock_revenue_money) * (float(StockInfo['S_WaterAmt']) / float(HalfAmt))
                                StockInfo['S_WaterLossMoney'] += LossMoney

                                msg = stock_code + " 40회가 소진되어 절반 손절합니다! 약 [" + str(LossMoney) + "] 확정손실이 나서 기록했으며 누적 손실은 [" + str(StockInfo['S_WaterLossMoney']) + "] 입니다"
                                print(msg) 
                                line_alert.SendMessage(msg) 

                            #이 경우는 이득 본 경우다! 목표 %에 못 도달했지만 수익권이긴 한 상태.
                            else:

                                #이득본 금액도 계산해보자
                                RevenuMoney = abs(stock_revenue_money) * (float(StockInfo['S_WaterAmt']) / float(HalfAmt))

                                #혹시나 저장된 손실본 금액이 있다면 줄여 준다! (빠른 탈출을 위해)
                                if StockInfo['S_WaterLossMoney'] > 0:
                                    StockInfo['S_WaterLossMoney'] -= RevenuMoney #저 데이터는 손실금을 저장하는 곳이니 빼준다

                                    #수익금을 뺐더니 손실금이 음수라면 0으로 처리해 준다!
                                    if StockInfo['S_WaterLossMoney'] < 0:
                                        StockInfo['S_WaterLossMoney'] = 0


                                msg = stock_code + " 40회가 소진되어 절반 매도합니다! 약 [" + str(RevenuMoney) + "] 확정 수익이 났네요!"
                                print(msg) 
                                line_alert.SendMessage(msg) 


                    '''
                    
                    1~10회:

                    무조건 삽니다

                    11~20회 :

                    5일선 위에 있을 때만!

                    21~30회 :

                    5일선 위에 있고 이전봉이 양봉일때만

                    30~40회 :

                    5일선 위에 있고 이전봉이 양봉이고 
                    5일선 증가, 20일선이 증가했다!

                    '''

                    IsBuyGo = False #매수 하는지!

                    #라운드에 따라 매수 조건이 다르다!
                    if StockInfo['Round'] <= 10:

                        #여기는 무조건 매수
                        IsBuyGo = True

                    elif StockInfo['Round'] <= 20:

                        #현재가가 5일선 위에 있을 때만 매수
                        if Ma5 < CurrentPrice:
                            IsBuyGo = True

                    elif StockInfo['Round'] <= 30:

                        #현재가가 5일선 위에 있고 이전 봉이 양봉일 때만 매수
                        if Ma5 < CurrentPrice and IsUpCandle == True:
                            IsBuyGo = True

                    elif StockInfo['Round'] <= 40:

                        #현재가가 5일선 위에 있고 이전 봉이 양봉일때 그리고 5일선, 20일선 둘다 증가추세에 있을 때만 매수
                        if Ma5 < CurrentPrice and IsUpCandle == True and Ma5_before < Ma5 and Ma20_before < Ma20:
                            IsBuyGo = True



                    #한 회차 매수 한다!!
                    if IsBuyGo == True:

                        StockInfo['Round'] += 1 #라운드 증가!

                        BuyAmt = int(StMoney / CurrentPrice)
                        
                        #1주보다 적다면 투자금이나 투자비중이 작은 상황인데 일단 1주는 매수하게끔 처리 하자!
                        if BuyAmt < 1:
                            BuyAmt = 1

                        #시장가 주문을 넣는다!
                        #현재가보다 위에 매수 주문을 넣음으로써 시장가로 매수!
                        pprint.pprint(KisUS.MakeBuyLimitOrder(stock_code,BuyAmt,CurrentPrice*1.1))


                        msg = stock_code + " 이평무한매수봇 " + str(StockInfo['Round']) + "회차 매수 완료!"
                        print(msg) 
                        line_alert.SendMessage(msg) 





                    ####################################################################################
                    ################## 위 정규 매수 로직과는 별개로 특별 물타기 로직을 체크하고 제어한다! #############

                    #이평선이 꺾여서 특별히 물탄 경우 수량이 0이 아닐꺼고 즉 여기는  물을 탄 상태이다!
                    if StockInfo['S_WaterAmt'] != 0:

                        #그렇다면 하루가 지났다는 이야기니깐 해당 수량 만큼 무조건 매도 한다!

                        #현재가보다 아래에 매도 주문을 넣음으로써 시장가로 매도효과!
                        pprint.pprint(KisUS.MakeSellLimitOrder(stock_code,StockInfo['S_WaterAmt'],CurrentPrice*0.9))

                        #단 현재 수익금이 마이너스 즉 손실 상태라면 손실 금액을 저장해 둔다!
                        if stock_revenue_money < 0:
                            #손실 금액에서 매도수량/보유수량 즉 예로 10개보유 하고 현재 -100달러인데 3개를 파는 거라면 실제 확정 손실금은 -100 * (3/10)이 니깐~
                            LossMoney = abs(stock_revenue_money) * (float(StockInfo['S_WaterAmt']) / float(stock_amt))
                            StockInfo['S_WaterLossMoney'] += LossMoney

                            msg = stock_code + " 평단을 확 낮추기 위한 이평무한매수봇 물탄지 하루가 지나 그 수량만큼 매도합니다! 약 [" + str(LossMoney) + "] 확정손실이 나서 기록했으며 누적 손실은 [" + str(StockInfo['S_WaterLossMoney']) + "] 입니다"
                            print(msg) 
                            line_alert.SendMessage(msg) 

                        #이 경우는 이득 본 경우다!
                        else:

                            #이득본 금액도 계산해보자
                            RevenuMoney = abs(stock_revenue_money) * (float(StockInfo['S_WaterAmt']) / float(stock_amt))

                            #혹시나 저장된 손실본 금액이 있다면 줄여 준다! (빠른 탈출을 위해)
                            if StockInfo['S_WaterLossMoney'] > 0:
                                StockInfo['S_WaterLossMoney'] -= RevenuMoney #저 데이터는 손실금을 저장하는 곳이니 빼준다

                                #수익금을 뺐더니 손실금이 음수라면 0으로 처리해 준다!
                                if StockInfo['S_WaterLossMoney'] < 0:
                                    StockInfo['S_WaterLossMoney'] = 0


                            msg = stock_code + " 평단을 확 낮추기 위한 이평무한매수봇 물탄지 하루가 지나 그 수량만큼 매도합니다! 약 [" + str(RevenuMoney) + "] 확정 수익이 났네요!"
                            print(msg) 
                            line_alert.SendMessage(msg) 

                        StockInfo['S_WaterAmt'] = 0 #팔았으니 0으로 초기화!

                        
                    #평단 낮추기위한 물타기 미진행!
                    else:
                        # 20선밑에 5일선이 있는데 5일선이 위로 꺾여을 때
                        if Ma5 < Ma20 and Ma5_before3 > Ma5_before and Ma5_before < Ma5:

                            '''

                            매수할 회차 = 현재 회차 / 4 + 1

                            '''
                            #즉 10분할 남은 수량을 회차비중별로 차등 물을 탄다
                            #만약 현재 4회차 진입에 이 상황을 만났다면 2분할을 물을 타주고
                            #만약 현재 38회차 진입에 이 상황을 만났다면 10분할로 물을 타줘서
                            #평단을 확확 내려 줍니다!

                            BuyRound = int(StockInfo['Round']/4) + 1 #물탈 회수

                            BuyAmt = int((StMoney * BuyRound) / CurrentPrice) #물탈 수량을 구한다!
                            
                            if BuyAmt < 1:
                                BuyAmt = 1


                            StockInfo['S_WaterAmt'] = BuyAmt

                            #시장가 주문을 넣는다!
                            #현재가보다 위에 매수 주문을 넣음으로써 시장가로 매수!
                            pprint.pprint(KisUS.MakeBuyLimitOrder(stock_code,BuyAmt,CurrentPrice*1.1))

                            msg = stock_code + " 이평선이 위로 꺾였어요! 평단을 확 낮추기 위한 이평무한매수봇 물을 탑니다!! [" + str(BuyRound) + "] 회차 만큼의 수량을 추가 했어요!"
                            print(msg) 
                            line_alert.SendMessage(msg) 

                    #########################################################################################
                    #########################################################################################


                    #위 로직 완료하면 N으로 바꿔서 오늘 매수는 안되게 처리!
                    StockInfo['IsReady'] = 'N' # 영상에선 제가 실수를 ==이 아니라 =가 맞습니다!

                    #파일에 저장
                    with open(bot_file_path, 'w') as outfile:
                        json.dump(InfinityMaDataList, outfile)
                        
                            
                break

else:

        
    #장이 끝나고 다음날 다시 매수시도 할수 있게 Y로 바꿔줍니당!
    for StockInfo in InfinityMaDataList:
        StockInfo['IsReady'] = 'Y' # 영상에선 제가 실수를 ==이 아니라 =가 맞습니다!


    #파일에 저장
    with open(bot_file_path, 'w') as outfile:
        json.dump(InfinityMaDataList, outfile)
        
        
pprint.pprint(InfinityMaDataList)