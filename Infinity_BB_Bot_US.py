import KIS_Common as Common
import KIS_API_Helper_US as KisUS
import json
import pprint
import line_alert 

Common.SetChangeMode("VIRTUAL")



BOT_NAME = Common.GetNowDist() + "_InfinityBbBot"

#투자할 종목!
TargetStockList = ['TSLA','AAPL','GOOG','AMZN','SBUX']


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
############# 해당 전략으로 매수한 종목 데이터 리스트 ####################
InfinityBbDataList = list()
#파일 경로입니다.
bot_file_path = "/var/autobot/UsStock_" + BOT_NAME + ".json"

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(bot_file_path, 'r') as json_file:
        InfinityBbDataList = json.load(json_file)

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
InvestRate = 0.1 # 10%로 일단 설정

#기준이 되는 내 총 평가금액에서 투자비중을 곱해서 나온 포트폴리오에 할당된 돈!!
TotalMoney = float(Balance['TotalMoney']) * InvestRate

#각 종목당 투자할 금액! 리스트의 종목 개수로 나눈다!
StockMoney = TotalMoney / len(TargetStockList)
print("TotalMoney:", str(format(round(TotalMoney), ',')))
print("StockMoney:", str(format(round(StockMoney), ',')))

#분할된 투자금!
StMoney = StockMoney / 10.0 #10분할!

print("StMoney:", str(format(round(StMoney), ',')))

#단타시 최소 수익 기준 수익률!
StRate = 0.015 #1.5% 


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
        for StockInfo in InfinityBbDataList:
            if StockInfo['StockCode'] == stock_code:
                PickStockInfo = StockInfo
                break

        #PickStockInfo 이게 없다면 매수되지 않은 처음 상태이거나 이전에 손으로 매수한 종목인데 해당 봇으로 돌리고자 할 때!
        if PickStockInfo == None:

            InfinityDataDict = dict()
            
            InfinityDataDict['StockCode'] = stock_code #종목 코드
            InfinityDataDict['IsReady'] = 'Y' #하루에 한번 체크하고 매수등의 처리를 하기 위한 플래그

            #단타칠때 진입지점을 기록할 리스트 4개를 미리 생성!
            DantaList = list()
            
            for i in range(0,4):
                DataDataDict = dict()
                DataDataDict['Id'] = i+1 #아이디
                DataDataDict['EntryPrice'] = 0 #진입가격
                DataDataDict['DantaAmt'] = 0   #단타 수량
                DataDataDict['IsBuy'] = 'N'    #매수 상태인지 여부
                DantaList.append(DataDataDict)

            InfinityDataDict['DantaList'] = DantaList


            InfinityBbDataList.append(InfinityDataDict) #데이터를 추가 한다!


            msg = stock_code + " BB모아봇 첫 시작!!!!"
            print(msg) 
            line_alert.SendMessage(msg) 


            #파일에 저장
            with open(bot_file_path, 'w') as outfile:
                json.dump(InfinityBbDataList, outfile)
                




        #이제 데이터(InfinityBbDataList)는 확실히 있을 테니 본격적으로 트레이딩을 합니다!
        for StockInfo in InfinityBbDataList:

            if StockInfo['StockCode'] == stock_code:

                #먼저 6(장기보유):4(단타) 비중을 맞춰줍니다
                #즉 투자금의 60%는 무조건 보유해야 하니깐 이보다 작을 경우에만 추가매수 합니다!
                LongTermMoney = StMoney * 6.0

                MustHasAmt = int(LongTermMoney / CurrentPrice) #현재 보유해야 되는 수량!
                
                #그 해당 수량보다 현재 잔고가 작다면 그 차액을 매수한다
                if MustHasAmt > stock_amt:

                    GapAmt = MustHasAmt - stock_amt

                    if GapAmt >= 1:

                        #시장가 주문을 넣는다!
                        #현재가보다 위에 매수 주문을 넣음으로써 시장가로 매수!
                        pprint.pprint(KisUS.MakeBuyLimitOrder(stock_code,GapAmt,CurrentPrice*1.1))

                        msg = stock_code + " BB모아봇 60% 비중이 안차서 " + str(GapAmt)+ "개 추가 매수 했어요!"
                        print(msg)  
                        line_alert.SendMessage(msg) 


                #단타로직!
                if StockInfo['IsReady'] == 'Y':
                
                    #캔들 데이터를 읽는다
                    df = Common.GetOhlcv("US",stock_code, 70)

    
                    BB60_2_before = Common.GetBB(df,60,-3)
                    BB60_2 = Common.GetBB(df,60,-2)

                    BB60_1_before = Common.GetBB(df,60,-3,1)
                    BB60_1 = Common.GetBB(df,60,-2,1)

                    print("---------------------------")
                    pprint.pprint(BB60_2_before)
                    pprint.pprint(BB60_1_before)
                    print("---------------------------")
                    pprint.pprint(BB60_2)
                    pprint.pprint(BB60_1)
                    print("---------------------------")


                    Candle_before = df['close'][-3]
                    Candle = df['close'][-2]


                    #양봉 캔들인지 여부
                    IsUpCandle = False

                    #시가보다 종가가 크다면 양봉이다
                    if df['open'][-2] <= df['close'][-2]:
                        IsUpCandle = True

                    print("IsUpCandle : ", IsUpCandle)


                    #5개 라인을 이전봉 양봉으로 상단 돌파 했는지
                    #이전봉 음봉으로 하단 돌파했는지 여부로
                    #단타 매매 결정!

                    IsBuy = False
                    IsSell = False
                    

                    '--------------------------------------------------------------------------------------'
                    #맨위
                    #상향돌파 여부 이전엔 업라인 아래에 있다가 어제 업라인을 돌파했고 양봉이었다!
                    #if Candle_before < BB60_2_before['upper'] and BB60_2['upper'] < Candle and IsUpCandle == True:
                    #    IsBuy = True

                    #하향돌파 여부 이전엔 업라인 위에에 있다가 어제 업라인을 아래로 돌파했고 음봉이었다!
                    if Candle_before > BB60_2_before['upper'] and BB60_2['upper'] > Candle and IsUpCandle == False:
                        IsSell = True
                    '--------------------------------------------------------------------------------------'
                    #위 중간
                    #상향돌파 여부 이전엔 업라인 아래에 있다가 어제 업라인을 돌파했고 양봉이었다!
                    #if Candle_before < BB60_1_before['upper'] and BB60_1['upper'] < Candle and IsUpCandle == True:
                    #    IsBuy = True

                    #하향돌파 여부 이전엔 업라인 위에에 있다가 어제 업라인을 아래로 돌파했고 음봉이었다!
                    if Candle_before > BB60_1_before['upper'] and BB60_1['upper'] > Candle and IsUpCandle == False:
                        IsSell = True

                    '--------------------------------------------------------------------------------------'
                    #중앙선
                    #상향돌파 여부 이전엔 업라인 아래에 있다가 어제 업라인을 돌파했고 양봉이었다!
                    if Candle_before < BB60_1_before['ma'] and BB60_1['ma'] < Candle and IsUpCandle == True:
                        IsBuy = True

                    #하향돌파 여부 이전엔 업라인 위에에 있다가 어제 업라인을 아래로 돌파했고 음봉이었다!
                    if Candle_before > BB60_1_before['ma'] and BB60_1['ma'] > Candle and IsUpCandle == False:
                        IsSell = True
                    '--------------------------------------------------------------------------------------'
                    #아래 중간
                    #상향돌파 여부 이전엔 다운라인 아래에 있다가 어제 다운라인을 돌파했고 양봉이었다!
                    if Candle_before < BB60_1_before['lower'] and BB60_1['lower'] < Candle and IsUpCandle == True:
                        IsBuy = True

                    #하향돌파 여부 이전엔 다운라인 위에에 있다가 어제 다운라인을 아래로 돌파했고 음봉이었다!
                  #  if Candle_before > BB60_1_before['lower'] and BB60_1['lower'] > Candle and IsUpCandle == False:
                   #     IsSell = True
                    '--------------------------------------------------------------------------------------'
                    #맨아래
                    #상향돌파 여부 이전엔 다운라인 아래에 있다가 어제 다운라인을 돌파했고 양봉이었다!
                    if Candle_before < BB60_2_before['lower'] and BB60_2['lower'] < Candle and IsUpCandle == True:
                        IsBuy = True

                    #하향돌파 여부 이전엔 다운라인 위에에 있다가 어제 다운라인을 아래로 돌파했고 음봉이었다!
                    #if Candle_before > BB60_2_before['lower'] and BB60_2['lower'] > Candle and IsUpCandle == False:
                    #    IsSell = True
                    '--------------------------------------------------------------------------------------'

                    IsFull = True #풀매수 상태 구분!
                    for DantaData in list(StockInfo['DantaList']):
                        #아직 매수되지 않은 슬롯을 찾는다!
                        if DantaData['IsBuy'] == 'N':
                            IsFull = False
                            break

                    #상향 돌파 했는데 풀 매수 상태이거나  하향돌파했는데 매도 해야 되는 상황이다!
                    if (IsBuy == True and IsFull == True) or IsSell == True:
 
                        IsDone = False
                        
                        # 지정한 수익률(1.5%)보다 높은 건 다 매도처리 한다!
                        for DantaData in list(StockInfo['DantaList']):
                            if DantaData['IsBuy'] == 'Y':

                                #진입가격에서 1.5%위에 있는 가격을 구한다
                                RevenuePrice = DantaData['EntryPrice'] * (1.0 + StRate)

                                #그 가격보다 현재가가 위에 있다면 매도한다!
                                if RevenuePrice <= CurrentPrice: 

                                    #저장된 단타수량을 매도!
                                    pprint.pprint(KisUS.MakeSellLimitOrder(stock_code,DantaData['DantaAmt'],CurrentPrice*0.9))

                                    msg = stock_code + " BB모아봇 ID:" + str(DantaData['Id']) + " -> ["+str(DantaData['DantaAmt'])+"]개 단타세계관에서 익절로 팔았어요!!!!"
                                    print(msg) 
                                    line_alert.SendMessage(msg) 

                                    #전량 매도 모두 초기화! 
                                    DantaData['IsBuy'] = 'N'
                                    DantaData['EntryPrice'] = 0
                                    DantaData['DantaAmt'] = 0

                                    #파일에 저장
                                    with open(bot_file_path, 'w') as outfile:
                                        json.dump(InfinityBbDataList, outfile)
            
                                    IsDone = True #1개라도 팔았다면 True로 변경!

                                    #상향돌파 한거는 1개만 팔아준다!
                                    if IsBuy == True:
                                        break



                        #팔아야 되는데 못 팔았다? 그런데 풀매수 상태다?
                        if IsSell == True and IsDone == False  and IsFull == True:
                            #1개 손절해서 슬롯을 비워준다!

                            #가장 진입가격이 높은거를 비워준다 진입 가격순으로 정렬해서!
                            PickData = sorted(list(StockInfo['DantaList']), key=lambda stock_info: (stock_info['EntryPrice']), reverse= True)
                            #이곳에는 진입가격 가장높은거의 ID!
                            PickId = PickData[0]['Id']

                            for DantaData in list(StockInfo['DantaList']):
                                if DantaData['Id'] == PickId:

                                    #저장된 단타수량을 매도!
                                    pprint.pprint(KisUS.MakeSellLimitOrder(stock_code,DantaData['DantaAmt'],CurrentPrice*0.9))


                                    msg = stock_code + " BB모아봇 ID:" + str(DantaData['Id']) + " -> ["+str(DantaData['DantaAmt'])+"]개 단타세계관에서 손절로 팔았어요!!!!"
                                    print(msg) 
                                    line_alert.SendMessage(msg) 

                                    #전량 매도 모두 초기화! 
                                    DantaData['IsBuy'] = 'N'
                                    DantaData['EntryPrice'] = 0
                                    DantaData['DantaAmt'] = 0

                                    #파일에 저장
                                    with open(bot_file_path, 'w') as outfile:
                                        json.dump(InfinityBbDataList, outfile)
            
                                    break
                    
                    #
                    else:

                         #매수해야 된다면!
                        if IsBuy == True:
                            
                            
                            for DantaData in list(StockInfo['DantaList']):
                                #아직 매수되지 않은 슬롯을 찾는다!
                                if DantaData['IsBuy'] == 'N':

                                    #발견했다면 매수!
                                    BuyAmt = int(StMoney / CurrentPrice)
                                    
                                    #1주보다 적다면 투자금이나 투자비중이 작은 상황인데 일단 1주는 매수하게끔 처리 하자!
                                    if BuyAmt < 1:
                                        BuyAmt = 1


                                    DantaData['IsBuy'] = 'Y'
                                    DantaData['EntryPrice'] = CurrentPrice #현재가로 진입했다고 가정합니다!
                                    DantaData['DantaAmt'] = BuyAmt

                                    #파일에 저장
                                    with open(bot_file_path, 'w') as outfile:
                                        json.dump(InfinityBbDataList, outfile)
                        
                                    #시장가 주문을 넣는다!
                                    #현재가보다 위에 매수 주문을 넣음으로써 시장가로 매수!
                                    pprint.pprint(KisUS.MakeBuyLimitOrder(stock_code,BuyAmt,CurrentPrice*1.1))


                                    msg = stock_code + " BB모아봇 " + str(BuyAmt) + "개 "  +  str(CurrentPrice) + "가격으로 단타 매수 완료!"
                                    print(msg) 
                                    line_alert.SendMessage(msg) 

                                    break



                    StockInfo['IsReady'] = 'N'

                    #파일에 저장
                    with open(bot_file_path, 'w') as outfile:
                        json.dump(InfinityBbDataList, outfile)
        
else:

        
    #장이 끝나고 다음날 다시 매수시도 할수 있게 Y로 바꿔줍니당!
    for StockInfo in InfinityBbDataList:
        StockInfo['IsReady'] = 'Y' # 영상에선 제가 실수를 ==이 아니라 =가 맞습니다!


    #파일에 저장
    with open(bot_file_path, 'w') as outfile:
        json.dump(InfinityBbDataList, outfile)
        
pprint.pprint(InfinityBbDataList)