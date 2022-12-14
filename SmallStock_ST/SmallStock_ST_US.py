import KIS_Common as Common
import KIS_API_Helper_US as KisUS
import json
import pandas as pd
import pprint
import time
import line_alert



#계좌 선택.. "VIRTUAL" 는 모의 계좌!
Common.SetChangeMode("VIRTUAL") #REAL or VIRTUAL


BOT_NAME = Common.GetNowDist() + "_SmallQuant_US"


#시간 정보를 읽는다
time_info = time.gmtime()
#년월 문자열을 만든다 즉 2022년 9월이라면 2022_9 라는 문자열이 만들어져 strYM에 들어간다!
strYM = str(time_info.tm_year) + "_" + str(time_info.tm_mon)
print("ym_st: " , strYM)



#포트폴리오 이름
PortfolioName = "소형주퀀트_전략US"




#####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################


#전제는 크롭탭에 주말 빼고 UTC 0시 기준 16시/ 우리나라 시간 새벽1시 정각에 해당 봇이 돈다고 가정!
# 0 16 * * 1-5 python3 /var/autobot/Static_Asset_US.py 




#리밸런싱이 가능한지 여부를 판단!
Is_Rebalance_Go = False


#파일에 저장된 년월 문자열 (ex> 2022_9)를 읽는다
YMDict = dict()

#파일 경로입니다.
asset_tym_file_path = "/var/autobot/UsSmallStockST_YM" + BOT_NAME + ".json"

try:
    with open(asset_tym_file_path, 'r') as json_file:
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
    #영상엔 없지만 리밸런싱이 가능할때만 내게 메시지를 보내자!
    if Is_Rebalance_Go == True:
       line_alert.SendMessage(PortfolioName + " (" + strYM + ") 장이 열려서 포트폴리오 리밸런싱 가능!!")
else:
    print("Market Is Close!!!!!!!!!!!")
    #영상엔 없지만 리밸런싱이 가능할때만 내게 메시지를 보내자!
    if Is_Rebalance_Go == True:
       line_alert.SendMessage(PortfolioName + " (" + strYM + ") 장이 닫혀서 포트폴리오 리밸런싱 불가능!!")





#####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################



#계좌 잔고를 가지고 온다!
Balance = KisUS.GetBalance()


print("--------------내 보유 잔고---------------------")

pprint.pprint(Balance)

print("--------------------------------------------")
#총 평가금액에서 해당 봇에게 할당할 총 금액비율 1.0 = 100%  0.5 = 50%
InvestRate = 0.1

#기준이 되는 내 총 평가금액에서 투자비중을 곱해서 나온 포트폴리오에 할당된 돈!!
TotalMoney = float(Balance['TotalMoney']) * InvestRate

print("총 포트폴리오에 할당된 투자 가능 금액 : $", TotalMoney)



###################################################################################
###################################################################################
###################################################################################

TargetStockList = list()
#파일 경로입니다.
us_file_path = "/var/autobot/UsStockDataList.json"

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(us_file_path, 'r') as json_file:
        TargetStockList = json.load(json_file)

except Exception as e:
    print("Exception by First")


print("TotalStockCodeCnt: " , len(TargetStockList))


df = pd.DataFrame(TargetStockList)

df['PER_rank'] = df['StockPER'].rank()
df['PBR_rank'] = df['StockPBR'].rank()
df['EV_EBITDA_rank'] = df['StockEV_EBITDA'].rank()
df['ROE_rank'] = df['StockROE'].rank(ascending=False)

df['TOTAL_SCORE'] = df['EV_EBITDA_rank']*3.0 + df['PBR_rank']*2.0 + df['PER_rank']*1.0 + df['ROE_rank']



df = df[df.StockMarketCap >= 5000000.0].copy() 
df = df[df.StockDistName != "Financial Services"].copy()


df = df[df.StockPER >= 1.0].copy()
df = df[df.StockPBR >= 0.2].copy()

df = df[df.StockOperatingMargin > 0].copy()
df = df[df.StockProfitMargin > 0].copy()

df = df[df.StockEPS > 0].copy()



df = df.sort_values(by="StockMarketCap")



#시총 상위 20%중에 PER낮은거순으로 20개?
df = df[0:int(float(len(df))*0.2)].copy()
pprint.pprint(df)


df = df.sort_values(by="TOTAL_SCORE")


print("----------------------------------------")
pprint.pprint(df)

print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

#Final20List -> FinalTopList로 변수명 변경
FinalTopList = list()

TopCnt = 20
NowCnt = 0

for idx, row in df.iterrows():
    
    stockcode = row['StockCode']
    print(stockcode)


    if NowCnt < TopCnt:
        
        IsOk = False
        #현재가!
        try:
            #현재가를 가져올수 있는지 체크 
            CurrentPrice = KisUS.GetCurrentPrice(stockcode)
            
            CurrentPrice = float(CurrentPrice)*1.0
            
            #거래량이 있는지 
            ohlcv = Common.GetOhlcv("US",stockcode,10)
            
            if int(ohlcv['volume'][-2]) == 0:
                IsOk = False
            else: 
                IsOk = True

        except Exception as e:
            IsOk = False
            print("Exception by First")

        if IsOk == True:
            FinalTopList.append(row.to_dict())
            NowCnt += 1

        
    else:
        break



pprint.pprint(FinalTopList)
###################################################################################
###################################################################################
###################################################################################




#전략에 투자되거나 투자할 주식 리스트
MyPortfolioList = list()

#종목 개수 20개.
StockCnt = len(FinalTopList)


#오늘 뽑은 조건에 맞는 주식들.. 
for PickStock in FinalTopList:
    
    stock = dict()
    stock['stock_code'] = PickStock['StockCode']         #종목코드
    stock['stock_target_rate'] = 100.0 / float(StockCnt)    #포트폴리오 목표 비중
    stock['stock_rebalance_amt'] = 0     #리밸런싱 해야하는 수량

    MyPortfolioList.append(stock)





#소형주 퀀트전략으로 투자하고 있는 주식 종목코드 리스트를 저장할 파일 
USSmallStockSTList = list()
#파일 경로입니다.
small_stock_file_path = "/var/autobot/UsSmallStockSTList.json"

try:
    with open(small_stock_file_path, 'r') as json_file:
        USSmallStockSTList = json.load(json_file)

except Exception as e:
    print("Exception by First")


#이전에 투자했던 종목들...
print("-----Prev--------")
pprint.pprint(USSmallStockSTList)
print("-----------------")


#이전에 뽑아서 저장된 주식들....오늘 뽑은 것과 중복되지 않는 것을 뽑아낸다. 이는 시총 하위 순에서 밀려난 것으로 비중 0으로 모두 팔아줘야 한다!
for AlReadyHasStock in USSmallStockSTList:

    #오늘 뽑은 주식과 비교해서..
    Is_Duple = False
    for exist_stock in MyPortfolioList:
        if exist_stock["stock_code"] == AlReadyHasStock['StockCode']:
            Is_Duple = True
            break
            
    #중복되지 않은 것만 넣어둔다. 비중은 0%이다!!!!
    if Is_Duple == False:

        stock = dict()
        stock['stock_code'] = AlReadyHasStock['StockCode']         #종목코드
        stock['stock_target_rate'] = 0    #포트폴리오 목표 비중
        stock['stock_rebalance_amt'] = 0     #리밸런싱 해야하는 수량
        print("Old Stock...",stock)

        MyPortfolioList.append(stock)





#현재 체크해야할 투자 종목들..
pprint.pprint(MyPortfolioList)




##########################################################

print("--------------내 보유 주식---------------------")
#그리고 현재 이 계좌에서 보유한 주식 리스트를 가지고 옵니다!
MyStockList = KisUS.GetMyStockList()
pprint.pprint(MyStockList)
print("--------------------------------------------")
##########################################################



print("--------------리밸런싱 수량 계산 ---------------------")

strResult = "-- 현재 포트폴리오 상황 --\n"

#매수된 자산의 총합!
total_stock_money = 0

#현재 평가금액 기준으로 각 자산이 몇 주씩 매수해야 되는지 계산한다 (포트폴리오 비중에 따라) 이게 바로 리밸런싱 목표치가 됩니다.
for stock_info in MyPortfolioList:

    #내주식 코드
    stock_code = stock_info['stock_code']
    stock_target_rate = float(stock_info['stock_target_rate']) / 100.0

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
    print("---> TargetRate:", round(stock_target_rate * 100.0,2) , "%")


    #주식의 총 평가금액을 더해준다
    total_stock_money += stock_eval_totalmoney

    #현재 비중
    stock_now_rate = 0

    #잔고에 있는 경우 즉 이미 매수된 주식의 경우
    if stock_amt > 0:


        stock_now_rate = round((stock_eval_totalmoney / TotalMoney),3)

        print("---> NowRate:", round(stock_now_rate * 100.0,2), "%")
        
        #비중이 0 이면 전량 매도 
        if stock_target_rate == 0:
            stock_info['stock_rebalance_amt'] = -stock_amt
            
        #아니라면 유지 
        else:
                
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

    #잔고에 없는 경우
    else:

        #비중 0 이상이면 비중 만큼 매수 
        if stock_target_rate != 0:
                
            print("---> NowRate: 0%")

            #잔고가 없다면 첫 매수다! 비중대로 매수할 총 금액을 계산한다 
            BuyMoney = TotalMoney * stock_target_rate


            #매수할 수량을 계산한다!
            BuyAmt = int(BuyMoney / CurrentPrice)

            #포트폴리오에 들어간건 일단 무조건 1주를 사주자... 아니라면 아래 2줄 주석처리
        # if BuyAmt <= 0:
            #    BuyAmt = 1

            stock_info['stock_rebalance_amt'] = BuyAmt
        
        
        
    
        
        
    #라인 메시지랑 로그를 만들기 위한 문자열 
    line_data =  (">> " + stock_code + " << \n비중: " + str(round(stock_now_rate * 100.0,2)) + "/" + str(round(stock_target_rate * 100.0,2)) 
    + "% \n수익: $" + str(stock_revenue_money) + "("+ str(round(stock_revenue_rate,2)) 
    + "%) \n총평가금액: $" + str(round(stock_eval_totalmoney,2)) 
    + "\n리밸런싱수량: " + str(stock_info['stock_rebalance_amt']) + "\n----------------------\n")

    #만약 아래 한번에 보내는 라인메시지가 짤린다면 아래 주석을 해제하여 개별로 보내면 됩니다
    if Is_Rebalance_Go == True:
       line_alert.SendMessage(line_data)
    strResult += line_data



##########################################################

print("--------------리밸런싱 해야 되는 수량-------------")

data_str = "\n" + PortfolioName + "\n" +  strResult + "\n포트폴리오할당금액: $" + str(round(TotalMoney,2)) + "\n매수한자산총액: $" + str(round(total_stock_money,2))

#결과를 출력해 줍니다!
print(data_str)

#영상엔 없지만 리밸런싱이 가능할때만 내게 메시지를 보내자!
if Is_Rebalance_Go == True:
   line_alert.SendMessage(data_str)
    
#만약 위의 한번에 보내는 라인메시지가 짤린다면 아래 주석을 해제하여 개별로 보내면 됩니다
if Is_Rebalance_Go == True:
    line_alert.SendMessage("\n포트폴리오할당금액: $" + str(round(TotalMoney,2)) + "\n매수한자산총액: $" + str(round(total_stock_money,2)))









print("--------------------------------------------")

##########################################################


#리밸런싱이 가능한 상태여야 하고 매수 매도는 장이 열려있어야지만 가능하다!!!
if Is_Rebalance_Go == True and IsMarketOpen == True:

    line_alert.SendMessage(PortfolioName + " (" + strYM + ") 리밸런싱 시작!!")

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

            Common.AutoLimitDoAgain(BOT_NAME,"US",stock_code,CurrentPrice,rebalance_amt,"DAY_END")
            

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
            print("stock_code", stock_code)
            #현재가!
            CurrentPrice = KisUS.GetCurrentPrice(stock_code)

            Common.AutoLimitDoAgain(BOT_NAME,"US",stock_code,CurrentPrice,rebalance_amt,"DAY_END")


    print("--------------------------------------------")

    #########################################################################################################################
    #첫 매수던 리밸런싱이던 매매가 끝났으면 이달의 리밸런싱은 끝이다. 해당 달의 년달 즉 22년 9월이라면 '2022_9' 라는 값을 파일에 저장해 둔다! 
    #파일에 저장하는 부분은 여기가 유일!!!!
    YMDict['ym_st'] = strYM
    with open(asset_tym_file_path, 'w') as outfile:
        json.dump(YMDict, outfile)
    #########################################################################################################################
        
    line_alert.SendMessage(PortfolioName + " (" + strYM + ") 리밸런싱 완료!!")


    #########################################################################################################################
    #이전에 확정된 종목 이번에 선정된 것으로 바꿔치기!
    USSmallStockSTList = FinalTopList

    print("-----Now--------")
    pprint.pprint(USSmallStockSTList)

    #파일에 저장!!
    with open(small_stock_file_path, 'w') as outfile:
        json.dump(USSmallStockSTList, outfile)

    print("-----------------")
    #########################################################################################################################

    print("------------------리밸런싱 끝---------------------")

