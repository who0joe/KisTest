import KIS_Common as Common

import KIS_API_Helper_US as KisUS
import KIS_API_Helper_KR as KisKR
import time
import json
import pprint
import random

SELL_LIMIT_DATE = 0
BUY_LIMIT_DATE = 1

Common.SetChangeMode('VIRTUAL') 

IsKRMarketOpen = False
IsUSMarketOpen = False

try:

    IsKRMarketOpen = KisKR.IsMarketOpen() 
    IsUSMarketOpen = KisUS.IsMarketOpen() 

except Exception as e:

    Common.SetChangeMode('REAL') 
    IsKRMarketOpen = KisKR.IsMarketOpen() 
    IsUSMarketOpen = KisUS.IsMarketOpen() 



#시간 정보를 읽는다
time_info = time.gmtime()


bot_path_file_path = "/Users/TY/Documents/class101/BotOrderListPath.json"

#각 봇 별로 들어가 있는 자동 주문 리스트!!!
BotOrderPathList = list()
try:
    with open(bot_path_file_path, 'r') as json_file:
        BotOrderPathList = json.load(json_file)

except Exception as e:
    print("Exception by First")


time.sleep(random.random()*0.01)
#주문감시 데이터가 있는 모든 봇을 순회하며 처리한다!!
for botOrderPath in BotOrderPathList:

    print("----->" , botOrderPath)

    AutoOrderList = list()

    try:
        with open(botOrderPath, 'r') as json_file:
            AutoOrderList = json.load(json_file)

    except Exception as e:
        print("Exception by First")



    for AutoLimitData in AutoOrderList:

        try:

            Common.SetChangeMode(AutoLimitData['NowDist']) 

            print("$$$$$$$$$$$$$$$$$$CHECK$$$$$$$$$$$$$$$$$$")
            pprint.pprint(AutoLimitData)

            if AutoLimitData['IsDone'] == 'N':
                #KR일 경우
                if AutoLimitData['Area'] == "KR":
                    
                    if IsKRMarketOpen == True:

                    
                        GapAmt = 0


                        MyKRStockList = KisKR.GetMyStockList()
                        stock_amt = 0
                        for my_stock in MyKRStockList:
                            if my_stock['StockCode'] == AutoLimitData['StockCode']:
                                stock_amt = int(my_stock['StockAmt'])
                                print(my_stock['StockName'], stock_amt)
                                break


                        GapAmt = abs(AutoLimitData['TargetAmt'] - stock_amt)

                        Is_Except = False
                        try:

                            #주문리스트를 읽어 온다!
                            OrderList = KisKR.GetOrderList(AutoLimitData['StockCode'])

                            print(len(OrderList) , " <--- Order OK!!!!!!")
                            

                            for OrderInfo in OrderList:
                                if OrderInfo['OrderNum'] == AutoLimitData['OrderNum'] and float(OrderInfo["OrderNum2"]) == float(AutoLimitData['OrderNum2']):
                                    #현재 주문이 취소된 상태이다!
                                    if OrderInfo["OrderSatus"] == "Close" or AutoLimitData['IsCancel'] == 'Y':
                                        #그런데 미체결 수량이 있다!
                                        if OrderInfo["OrderAmt"] != OrderInfo["OrderResultAmt"]:
                                            #그 수량 만큼 지정가 주문을 걸어준다!
                                            GapAmt = abs(OrderInfo["OrderResultAmt"] - OrderInfo["OrderAmt"])
                                            
                                            if AutoLimitData['OrderAmt'] < 0:
                                                GapAmt *= -1
                                        else:
                                            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>Order Done<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                                            #미체결 수량이 없다면 완료!!!
                                            AutoLimitData['IsDone'] = 'Y'
                                            with open(botOrderPath, 'w') as outfile:
                                                json.dump(AutoOrderList, outfile)
                                    break

                        except Exception as e:
                            Is_Except = True
                            print("Exception", e)


                        if Is_Except == True:


                            #종목의 현재 잔고 수량과 비교해 맞는지 체크한다.
                            #연금의 경우 종목당 주문이 1개일 것이기 때문에 유효 하다!
                            
                            if AutoLimitData['TargetAmt'] != stock_amt:
                                
                                #최초 주문이 0보다 작은 매도 주문이었다면 -1로!
                                if AutoLimitData['OrderAmt'] < 0:
                                    GapAmt *= -1
                            else:
                                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>Order Done<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                                #미체결 수량이 없다면 완료!!!
                                AutoLimitData['IsDone'] = 'Y'
                                with open(botOrderPath, 'w') as outfile:
                                    json.dump(AutoOrderList, outfile)

                        OrderOk = "OK"
                        if int(AutoLimitData['OrderNum2']) == 0:
                            AutoLimitData['IsCancel'] = 'Y'
                            OrderOk = "NO"

                        str_msg = AutoLimitData["Id"] + KisKR.GetStockName(AutoLimitData['StockCode']) + " 현재주식잔고: " +  str(stock_amt) + " 주문수량:" +  str(AutoLimitData["OrderAmt"]) + " 남은주문수량:" + str(GapAmt) + " 주문들어갔는지:" + str(OrderOk)
                       
                        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                        print(str_msg)
                        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

                        if GapAmt != 0:
                            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>Order Fail<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                            
                            if AutoLimitData['IsCancel'] == 'Y':


                                print(">>>>>>>>>>>>>>>>>>>>> GOGO ORDER >>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                                #if OrderOk == "NO":
                                #    line_alert.SendMessage(str_msg)
                                #else:
                                #    line_alert.SendMessage(AutoLimitData['Id'] + " 가 날이 지나 취소된 주문인데 미체결 수량이 남아 있어 추가 주문이 들어갑니다! ")
                                    
                                OrderData = None

                                MAX_LIMIT_DATE = BUY_LIMIT_DATE
                                if GapAmt < 0:
                                    MAX_LIMIT_DATE = SELL_LIMIT_DATE

                                try:
                                        
                                    if MAX_LIMIT_DATE <= AutoLimitData['TryCnt']:

                                        if MAX_LIMIT_DATE + 1 <= AutoLimitData['TryCnt']:

                                            #사야된다
                                            if GapAmt > 0:

                                                OrderData = KisKR.MakeBuyMarketOrder(AutoLimitData['StockCode'],abs(GapAmt))
                                            #팔아야 된다!
                                            else:
                                                OrderData = KisKR.MakeSellMarketOrder(AutoLimitData['StockCode'],abs(GapAmt))

                                        else:



                                            #사야된다
                                            if GapAmt > 0:
                                                OrderData = KisKR.MakeBuyLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),KisKR.GetCurrentPrice(AutoLimitData['StockCode']))
            
                                            #팔아야 된다!
                                            else:
                                                OrderData = KisKR.MakeSellLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),KisKR.GetCurrentPrice(AutoLimitData['StockCode']))

                                    else:
                                        
                                        #사야된다
                                        if GapAmt > 0:
                                            OrderData = KisKR.MakeBuyLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),AutoLimitData['TargetPrice'])
                                            
                                        #팔아야 된다!
                                        else:
                                            OrderData = KisKR.MakeSellLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),AutoLimitData['TargetPrice'])
                                        
                                
                                    
                                    AutoLimitData['OrderNum'] = OrderData["OrderNum"]
                                    AutoLimitData['OrderNum2'] = OrderData["OrderNum2"]   
                                    AutoLimitData['OrderTime'] = OrderData["OrderTime"]   

                                    #실제 주문이 들어갔을 경우에만!
                                    if int(AutoLimitData['OrderNum2']) != 0:
                                        #그리고 이전 주문이 정상적으로 들어간 경우에만 카운팅!!!
                                        if OrderOk == "OK":
                                            AutoLimitData['TryCnt'] += 1
                                            
                                        AutoLimitData['IsCancel'] = 'N'  


                                except Exception as e:
                                    print("Fail..", e)
                                    #line_alert.SendMessage("주문 실패" + str(e))

                                    AutoLimitData['OrderNum'] = 0
                                    AutoLimitData['OrderNum2'] = 0
                                    AutoLimitData['OrderTime'] = Common.GetNowDateStr(AutoLimitData['Area'])  + str(time_info.tm_hour) + str(time_info.tm_min) + str(time_info.tm_sec) 




                                with open(botOrderPath, 'w') as outfile:
                                    json.dump(AutoOrderList, outfile)
                    else:
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>Order Cancel<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                        #장이 안열렸으면 취소처리!
                        AutoLimitData['IsCancel'] = 'Y'
                        with open(botOrderPath, 'w') as outfile:
                            json.dump(AutoOrderList, outfile)
                #US일 경우
                else:
                    print("")
                    if IsUSMarketOpen == True:
                        print("")

                        GapAmt = 0


                        MyUSStockList = KisUS.GetMyStockList()
                        stock_amt = 0
                        for my_stock in MyUSStockList:
                            if my_stock['StockCode'] == AutoLimitData['StockCode']:
                                stock_amt = int(my_stock['StockAmt'])
                                break            

                        GapAmt = abs(AutoLimitData['TargetAmt'] - stock_amt)            

                        Is_Except = False
                        try:
                            #주문리스트를 읽어 온다!
                            OrderList = KisUS.GetOrderList(AutoLimitData['StockCode'])

                            print(len(OrderList) , " <--- Order OK!!!!!!")
                            

                            for OrderInfo in OrderList:
                                if OrderInfo['OrderNum'] == AutoLimitData['OrderNum'] and float(OrderInfo["OrderNum2"]) == float(AutoLimitData['OrderNum2']):
                                    pprint.pprint(OrderInfo)
                                    #현재 주문이 취소된 상태이다!
                                    if OrderInfo["OrderSatus"] == "Close" or AutoLimitData['IsCancel'] == 'Y':
                                        #그런데 미체결 수량이 있다!
                                        if OrderInfo["OrderAmt"] != OrderInfo["OrderResultAmt"]:
                                            #그 수량 만큼 지정가 주문을 걸어준다!
                                            GapAmt = abs(OrderInfo["OrderResultAmt"] - OrderInfo["OrderAmt"])
                                            
                                            if AutoLimitData['OrderAmt'] < 0:
                                                GapAmt *= -1
                                        else:
                                            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>Order Done<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                                            #미체결 수량이 없다면 완료!!!
                                            AutoLimitData['IsDone'] = 'Y'
                                            with open(botOrderPath, 'w') as outfile:
                                                json.dump(AutoOrderList, outfile)
                                    break

                        except Exception as e:
                            Is_Except = True
                            print("Exception ORDER!", e)


                        if Is_Except == True:
                            #종목의 현재 잔고 수량과 비교해 맞는지 체크한다.
                            #연금의 경우 종목당 주문이 1개일 것이기 때문에 유효 하다!



                            if AutoLimitData['TargetAmt'] != stock_amt:
                                
                                #최초 주문이 0보다 작은 매도 주문이었다면 -1로!
                                if AutoLimitData['OrderAmt'] < 0:
                                    GapAmt *= -1
                            else:
                                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>Order Done<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                                #미체결 수량이 없다면 완료!!!
                                AutoLimitData['IsDone'] = 'Y'
                                with open(botOrderPath, 'w') as outfile:
                                    json.dump(AutoOrderList, outfile)

                        OrderOk = "OK"
                        if int(AutoLimitData['OrderNum2']) == 0:
                            AutoLimitData['IsCancel'] = 'Y'
                            OrderOk = "NO"

                        str_msg = AutoLimitData["Id"] +  AutoLimitData['StockCode'] + " 현재주식잔고: " +  str(stock_amt) + " 주문수량:" +  str(AutoLimitData["OrderAmt"]) + " 남은주문수량:" + str(GapAmt) + " 주문들어갔는지:" + str(OrderOk)
                        
                        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                        print(str_msg)
                        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")


                        if GapAmt != 0:

                            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>Order Fail<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

                            if AutoLimitData['IsCancel'] == 'Y':

                                print(">>>>>>>>>>>>>>>>>>>>> GOGO ORDER >>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                                #if OrderOk == "NO":
                                #    line_alert.SendMessage(str_msg)
                                #else:
                                #    line_alert.SendMessage(AutoLimitData['Id'] + " 가 날이 지나 취소된 주문인데 미체결 수량이 남아 있어 추가 주문이 들어갑니다! ")
                                    
                                OrderData = None

                                try:

                                    MAX_LIMIT_DATE = BUY_LIMIT_DATE
                                    if GapAmt < 0:
                                        MAX_LIMIT_DATE = SELL_LIMIT_DATE


                                    if MAX_LIMIT_DATE <= AutoLimitData['TryCnt']:

                                        if MAX_LIMIT_DATE + 1 <= AutoLimitData['TryCnt']:
                                            #사야된다
                                            if GapAmt > 0:
                                                OrderData = KisUS.MakeBuyLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),KisUS.GetCurrentPrice(AutoLimitData['StockCode'])*1.1)
            
                                            #팔아야 된다!
                                            else:
                                                OrderData = KisUS.MakeSellLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),KisUS.GetCurrentPrice(AutoLimitData['StockCode'])*0.9)
                                        else:

                                            #사야된다
                                            if GapAmt > 0:
                                                OrderData = KisUS.MakeBuyLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),KisUS.GetCurrentPrice(AutoLimitData['StockCode']))
            
                                            #팔아야 된다!
                                            else:
                                                OrderData = KisUS.MakeSellLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),KisUS.GetCurrentPrice(AutoLimitData['StockCode']))

                                    else:

                                        #사야된다
                                        if GapAmt > 0:
                                            OrderData = KisUS.MakeBuyLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),AutoLimitData['TargetPrice'])
                                            
                                        #팔아야 된다!
                                        else:
                                            OrderData = KisUS.MakeSellLimitOrder(AutoLimitData['StockCode'],abs(GapAmt),AutoLimitData['TargetPrice'])
                                            
                                    AutoLimitData['OrderNum'] = OrderData["OrderNum"]
                                    AutoLimitData['OrderNum2'] = OrderData["OrderNum2"]   
                                    AutoLimitData['OrderTime'] = OrderData["OrderTime"]   

                                    #실제 주문이 들어갔을 경우에만!
                                    if int(AutoLimitData['OrderNum2']) != 0:
                                        #그리고 이전 주문이 정상적으로 들어간 경우에만 카운팅!!!
                                        if OrderOk == "OK":
                                            AutoLimitData['TryCnt'] += 1

                                        AutoLimitData['IsCancel'] = 'N'  
                                    
                                except Exception as e:
                                    print("Fail..", e)
                                    #line_alert.SendMessage("주문 실패" + str(e))
                                    AutoLimitData['OrderNum'] = 0
                                    AutoLimitData['OrderNum2'] = 0
                                    AutoLimitData['OrderTime'] = Common.GetNowDateStr(AutoLimitData['Area'])  + str(time_info.tm_hour) + str(time_info.tm_min) + str(time_info.tm_sec) 



                                with open(botOrderPath, 'w') as outfile:
                                    json.dump(AutoOrderList, outfile)

                    else:
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>Order Cancel<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                        #장이 안열렸으면 취소처리!
                        AutoLimitData['IsCancel'] = 'Y'
                        with open(botOrderPath, 'w') as outfile:
                            json.dump(AutoOrderList, outfile)

            else:
                #완료가 된 주문이라면 취소가 된 주문이기도 하다!
                if AutoLimitData['IsDone'] == 'Y':
                    AutoLimitData['IsCancel'] = 'Y'

                    with open(botOrderPath, 'w') as outfile:
                        json.dump(AutoOrderList, outfile)

        except Exception as e:
            print("Exception by First")





    #10일이나 지난 주문은 무조건 삭제처리한다.. 보통 완료처리 되거나 취소처리 된 상태! (주문은 1일동안만 유효하므로..)
    AutoOrderList = list()

    try:
        with open(botOrderPath, 'r') as json_file:
            AutoOrderList = json.load(json_file)

    except Exception as e:
        print("Exception by First")

    print("---DELETE Logic Start---")
    for AutoLimitData in AutoOrderList:
        #print("---")
       # print(int(AutoLimitData['DelDate']), int(Common.GetNowDateStr(AutoLimitData['Area'],"NONE")))
        if int(AutoLimitData['DelDate']) < int(Common.GetNowDateStr(AutoLimitData['Area'],"NONE")):
            AutoOrderList.remove(AutoLimitData)

    with open(botOrderPath, 'w') as outfile:
        json.dump(AutoOrderList, outfile)

    print("---DELETE Logic End---")




print("------------------------------------------------------------")
print("----------------------RESULT--------------------------------")
print("------------------------------------------------------------")


#주문감시 데이터가 있는 모든 봇을 순회하며 처리한다!!
for botOrderPath in BotOrderPathList:

    print("##################################")
    print("-------------->" , botOrderPath)
    print("##################################")

    AutoOrderList = list()

    try:
        with open(botOrderPath, 'r') as json_file:
            AutoOrderList = json.load(json_file)

    except Exception as e:
        print("Exception by First")


    for AutoLimitData in AutoOrderList:

        try:

            Common.SetChangeMode(AutoLimitData['NowDist']) 

            print("                                  ")
            pprint.pprint(AutoLimitData)

            if AutoLimitData['Area'] == "KR":
                print(KisKR.GetStockName(AutoLimitData['StockCode']))
            print("---->", AutoLimitData['StockCode'], ' IsCancel', AutoLimitData['IsCancel'],' IsDone' , AutoLimitData['IsDone'] )
            
            print("                                  ")

        except Exception as e:
            print("Exception", e)


print("------------------------------------------------------------")
print("------------------------------------------------------------")
print("------------------------------------------------------------")
