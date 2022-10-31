# -*- coding: utf-8 -*-
import KIS_Common as Common


import requests
import json


from datetime import datetime
from pytz import timezone

import pprint
import math
import time


import pandas as pd


#시장이 열렸는지 여부 체크! #토요일 일요일은 확실히 안열리니깐 제외! 
def IsMarketOpen():


    now_time = datetime.now(timezone('Asia/Seoul'))
    pprint.pprint(now_time)

    date_week = now_time.weekday()

    IsOpen = False

    #주말은 무조건 장이 안열리니 False 리턴!
    if date_week == 5 or date_week == 6:  
        IsOpen = False
    else:
        #9시 부터 3시 반
        if now_time.hour >= 9 and now_time.hour <= 15:
            IsOpen = True

            if now_time.hour == 15 and now_time.minute > 20:
                IsOpen = False

    #평일 장 시간이어도 공휴일같은날 장이 안열린다.
    if IsOpen == True:

        print("Time is OK... but one more checked!!!")

        result = ""

        try:
            #가상 계좌면 메세지 통일을 위해 실계좌에서 가짜 주문 취소 주문을 넣는다!
            if Common.GetNowDist() == "VIRTUAL":

                Common.SetChangeMode("REAL")
                result = MakeSellLimitOrder("069500",1,1,"CHECK")
                Common.SetChangeMode("VIRTUAL")

            else:
                result = MakeSellLimitOrder("069500",1,1,"CHECK")

        except Exception as e:
            print("EXCEPTION ",e)



        #장운영시간이 아니라고 리턴되면 장이 닫힌거다!
        if result == "APBK0918" or result == "APBK0919":
            print("Market is Close!!")
            
            return False
        #아니라면 열린거다
        else:

            if result == "EGW00123":
                print("Token is failed...So You need Action!!")

            print("Market is Open!!")
            return True

    else:

        print("Time is NO!!!")     
           
        return False


#price_pricision 호가 단위에 맞게 변형해준다. 지정가 매매시 사용
def PriceAdjust(price, stock_code):
    #호가를 직접 구해서 개선!!!
    hoga = GetHoga(stock_code)

    adjust_price = math.floor(price / hoga) * hoga
    
    return adjust_price




    

#나의 계좌 잔고!
def GetBalance():

    time.sleep(0.2)

    PATH = "uapi/domestic-stock/v1/trading/inquire-balance"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"

    TrId = "TTTC8434R"
    if Common.GetNowDist() == "VIRTUAL":
         TrId = "VTTC8434R"


    # 헤더 설정
    headers = {"Content-Type":"application/json", 
            "authorization": f"Bearer {Common.GetToken(Common.GetNowDist())}",
            "appKey":Common.GetAppKey(Common.GetNowDist()),
            "appSecret":Common.GetAppSecret(Common.GetNowDist()),
            "tr_id": TrId,
            "custtype": "P"}

    params = {
        "CANO": Common.GetAccountNo(Common.GetNowDist()),
        "ACNT_PRDT_CD" : Common.GetPrdtNo(Common.GetNowDist()),
        "AFHR_FLPR_YN" : "N",
        "OFL_YN": "",
        "INQR_DVSN": "02",
        "UNPR_DVSN": "01",
        "FUND_STTL_ICLD_YN" : "N",
        "FNCG_AMT_AUTO_RDPT_YN" : "N",
        "PRCS_DVSN" : "01",
        "CTX_AREA_FK100" : "",
        "CTX_AREA_NK100" : ""
    }

    # 호출
    res = requests.get(URL, headers=headers, params=params)
    #pprint.pprint(res.json())
    if res.status_code == 200 and res.json()["rt_cd"] == '0':

        result = res.json()['output2'][0]
        #pprint.pprint(result)

        balanceDict = dict()
        #주식 총 평가 금액
        balanceDict['StockMoney'] = float(result['scts_evlu_amt'])
        #평가 손익 금액
        balanceDict['StockRevenue'] = float(result['evlu_pfls_smtl_amt'])
        
        
            
        #총 평가 금액
        balanceDict['TotalMoney'] = float(result['tot_evlu_amt'])

        #예수금이 아예 0이거나 총평가금액이랑 주식평가금액이 같은 상황일때는.. 좀 이상한 특이사항이다 풀매수하더라도 1원이라도 남을 테니깐
        #퇴직연금 계좌에서 tot_evlu_amt가 제대로 반영이 안되는 경우가 있는데..이때는 전일 총평가금액을 가져오도록 한다!
        if float(result['dnca_tot_amt']) == 0 or balanceDict['TotalMoney'] == balanceDict['StockMoney']:
            #장이 안열린 상황을 가정 
            #if IsMarketOpen() == False:
            balanceDict['TotalMoney'] = float(result['bfdy_tot_asst_evlu_amt'])


        #예수금 총금액 (즉 주문가능현금)
        balanceDict['RemainMoney'] = float(balanceDict['TotalMoney']) - float(balanceDict['StockMoney'])#result['dnca_tot_amt']
        
        #그래도 아직도 남은 금액이 0이라면 dnca_tot_amt 예수금 항목에서 정보를 가지고 온다
        if balanceDict['RemainMoney'] == 0:
            balanceDict['RemainMoney'] = float(result['dnca_tot_amt'])
            


        return balanceDict

    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return res.json()["msg_cd"]
    

#한국 보유 주식 리스트!
def GetMyStockList():

    

    PATH = "uapi/domestic-stock/v1/trading/inquire-balance"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"

    TrId = "TTTC8434R"
    if Common.GetNowDist() == "VIRTUAL":
         TrId = "VTTC8434R"
         
         
    StockList = list()
    
    DataLoad = True
    
    SeqKey = ""

    count = 0

    #드물지만 보유종목이 아주 많으면 한 번에 못가져 오므로 SeqKey를 이용해 연속조회를 하기 위한 반복 처리 
    while DataLoad:



        time.sleep(0.2)
        # 헤더 설정
        headers = {"Content-Type":"application/json", 
                "authorization": f"Bearer {Common.GetToken(Common.GetNowDist())}",
                "appKey":Common.GetAppKey(Common.GetNowDist()),
                "appSecret":Common.GetAppSecret(Common.GetNowDist()),
                "tr_id": TrId,
                "custtype": "P"}

        params = {
            "CANO": Common.GetAccountNo(Common.GetNowDist()),
            "ACNT_PRDT_CD" : Common.GetPrdtNo(Common.GetNowDist()),
            "AFHR_FLPR_YN" : "N",
            "OFL_YN": "",
            "INQR_DVSN": "02",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN" : "N",
            "FNCG_AMT_AUTO_RDPT_YN" : "N",
            "PRCS_DVSN" : "01",
            "CTX_AREA_FK100" : "",
            "CTX_AREA_NK100" : SeqKey
        }

        # 호출
        res = requests.get(URL, headers=headers, params=params)
        
        
        
        if res.status_code == 200 and res.json()["rt_cd"] == '0':
                
            SeqKey = res.json()['ctx_area_nk100'].strip()
            if SeqKey != "":
                print("CTX_AREA_NK100: ", SeqKey)
                
            if SeqKey == "":
                DataLoad = False
            
                
            ResultList = res.json()['output1']
            #pprint.pprint(ResultList)



            for stock in ResultList:
                #잔고 수량이 0 이상인것만
                if int(stock['hldg_qty']) > 0:

                    StockInfo = dict()
                    
                    StockInfo["StockCode"] = stock['pdno']
                    StockInfo["StockName"] = stock['prdt_name']
                    StockInfo["StockAmt"] = stock['hldg_qty']
                    StockInfo["StockAvgPrice"] = stock['pchs_avg_pric']
                    StockInfo["StockOriMoney"] = stock['pchs_amt']
                    StockInfo["StockNowMoney"] = stock['evlu_amt']
                    StockInfo["StockNowPrice"] = stock['prpr']
                # StockInfo["StockNowRate"] = stock['fltt_rt'] #등락률인데 해외 주식에는 없어서 통일성을 위해 여기도 없앰 ㅎ
                    StockInfo["StockRevenueRate"] = stock['evlu_pfls_rt']
                    StockInfo["StockRevenueMoney"] = stock['evlu_pfls_amt']
                    
                    StockList.append(StockInfo)



        else:
            print("Error Code : " + str(res.status_code) + " | " + res.text)
            #return res.json()["msg_cd"]

            if res.json()["msg_cd"] == "EGW00123":
                DataLoad = False

            count += 1
            if count > 10:
                DataLoad = False
    
    return StockList




############################################################################################################################################################

#국내 주식현재가 시세
def GetCurrentPrice(stock_code):
    time.sleep(0.2)

    PATH = "uapi/domestic-stock/v1/quotations/inquire-price"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"

    # 헤더 설정
    headers = {"Content-Type":"application/json", 
            "authorization": f"Bearer {Common.GetToken(Common.GetNowDist())}",
            "appKey":Common.GetAppKey(Common.GetNowDist()),
            "appSecret":Common.GetAppSecret(Common.GetNowDist()),
            "tr_id":"FHKST01010100"}

    params = {
        "FID_COND_MRKT_DIV_CODE":"J",
        "FID_INPUT_ISCD": stock_code
    }

    # 호출
    res = requests.get(URL, headers=headers, params=params)
    #pprint.pprint(res.json())

    if res.status_code == 200 and res.json()["rt_cd"] == '0':
        return int(res.json()['output']['stck_prpr'])
    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return res.json()["msg_cd"]


#국내 주식 호가 단위!
def GetHoga(stock_code):
    time.sleep(0.2)

    PATH = "uapi/domestic-stock/v1/quotations/inquire-price"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"

    # 헤더 설정
    headers = {"Content-Type":"application/json", 
            "authorization": f"Bearer {Common.GetToken(Common.GetNowDist())}",
            "appKey":Common.GetAppKey(Common.GetNowDist()),
            "appSecret":Common.GetAppSecret(Common.GetNowDist()),
            "tr_id":"FHKST01010100"}

    params = {
        "FID_COND_MRKT_DIV_CODE":"J",
        "FID_INPUT_ISCD": stock_code
    }

    # 호출
    res = requests.get(URL, headers=headers, params=params)
    #pprint.pprint(res.json())

    if res.status_code == 200 and res.json()["rt_cd"] == '0':
        return int(res.json()['output']['aspr_unit'])
    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return res.json()["msg_cd"]






############################################################################################################################################################
#시장가 주문하기!
def MakeBuyMarketOrder(stockcode, amt):
    
    try:
        #매수 가능한수량으로 보정
        amt = AdjustPossibleAmt(stockcode, amt, "MARKET")

    except Exception as e:
        print("Exception")


    time.sleep(0.2)

    TrId = "TTTC0802U"
    if Common.GetNowDist() == "VIRTUAL":
         TrId = "VTTC0802U"


    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"
    data = {
        "CANO": Common.GetAccountNo(Common.GetNowDist()),
        "ACNT_PRDT_CD" : Common.GetPrdtNo(Common.GetNowDist()),
        "PDNO": stockcode,
        "ORD_DVSN": "01",
        "ORD_QTY": str(int(amt)),
        "ORD_UNPR": "0"
    }
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {Common.GetToken(Common.GetNowDist())}",
        "appKey":Common.GetAppKey(Common.GetNowDist()),
        "appSecret":Common.GetAppSecret(Common.GetNowDist()),
        "tr_id": TrId,
        "custtype":"P",
        "hashkey" : Common.GetHashKey(data)
    }
    res = requests.post(URL, headers=headers, data=json.dumps(data))

    if res.status_code == 200 and res.json()["rt_cd"] == '0':

        order = res.json()['output']

        OrderInfo = dict()
        

        OrderInfo["OrderNum"] = order['KRX_FWDG_ORD_ORGNO']
        OrderInfo["OrderNum2"] = order['ODNO']
        OrderInfo["OrderTime"] = order['ORD_TMD'] 



        return OrderInfo
    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return res.json()["msg_cd"]
        

#시장가 매도하기!
def MakeSellMarketOrder(stockcode, amt):

    time.sleep(0.2)

    TrId = "TTTC0801U"
    if Common.GetNowDist() == "VIRTUAL":
         TrId = "VTTC0801U"


    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"
    data = {
        "CANO": Common.GetAccountNo(Common.GetNowDist()),
        "ACNT_PRDT_CD" : Common.GetPrdtNo(Common.GetNowDist()),
        "PDNO": stockcode,
        "ORD_DVSN": "01",
        "ORD_QTY": str(int(amt)),
        "ORD_UNPR": "0",
    }
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {Common.GetToken(Common.GetNowDist())}",
        "appKey":Common.GetAppKey(Common.GetNowDist()),
        "appSecret":Common.GetAppSecret(Common.GetNowDist()),
        "tr_id":TrId,
        "custtype":"P",
        "hashkey" : Common.GetHashKey(data)
    }
    res = requests.post(URL, headers=headers, data=json.dumps(data))

    if res.status_code == 200 and res.json()["rt_cd"] == '0':

        order = res.json()['output']

        OrderInfo = dict()
        

        OrderInfo["OrderNum"] = order['KRX_FWDG_ORD_ORGNO']
        OrderInfo["OrderNum2"] = order['ODNO']
        OrderInfo["OrderTime"] = order['ORD_TMD'] 


        return OrderInfo
    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return res.json()["msg_cd"]


#지정가 주문하기!
def MakeBuyLimitOrder(stockcode, amt, price, ErrLog="YES"):
    
    
    try:
        #매수 가능한수량으로 보정
        amt = AdjustPossibleAmt(stockcode, amt, "LIMIT")

    except Exception as e:
        print("Exception")




    time.sleep(0.2)

    TrId = "TTTC0802U"
    if Common.GetNowDist() == "VIRTUAL":
         TrId = "VTTC0802U"


    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"
    data = {
        "CANO": Common.GetAccountNo(Common.GetNowDist()),
        "ACNT_PRDT_CD" : Common.GetPrdtNo(Common.GetNowDist()),
        "PDNO": stockcode,
        "ORD_DVSN": "00",
        "ORD_QTY": str(int(amt)),
        "ORD_UNPR": str(PriceAdjust(price,stockcode)),
    }
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {Common.GetToken(Common.GetNowDist())}",
        "appKey":Common.GetAppKey(Common.GetNowDist()),
        "appSecret":Common.GetAppSecret(Common.GetNowDist()),
        "tr_id": TrId,
        "custtype":"P",
        "hashkey" : Common.GetHashKey(data)
    }
    res = requests.post(URL, headers=headers, data=json.dumps(data))

    if res.status_code == 200 and res.json()["rt_cd"] == '0':

        order = res.json()['output']

        OrderInfo = dict()
        

        OrderInfo["OrderNum"] = order['KRX_FWDG_ORD_ORGNO']
        OrderInfo["OrderNum2"] = order['ODNO']
        OrderInfo["OrderTime"] = order['ORD_TMD'] 



        return OrderInfo

    else:
        if ErrLog == "YES":
            print("Error Code : " + str(res.status_code) + " | " + res.text)
        return res.json()["msg_cd"]
        

#지정가 매도하기!
def MakeSellLimitOrder(stockcode, amt, price, ErrLog="YES"):

    time.sleep(0.2)

    TrId = "TTTC0801U"
    if Common.GetNowDist() == "VIRTUAL":
         TrId = "VTTC0801U"


    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"
    data = {
        "CANO": Common.GetAccountNo(Common.GetNowDist()),
        "ACNT_PRDT_CD" : Common.GetPrdtNo(Common.GetNowDist()),
        "PDNO": stockcode,
        "ORD_DVSN": "00",
        "ORD_QTY": str(int(amt)),
        "ORD_UNPR": str(PriceAdjust(price,stockcode)),
    }
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {Common.GetToken(Common.GetNowDist())}",
        "appKey":Common.GetAppKey(Common.GetNowDist()),
        "appSecret":Common.GetAppSecret(Common.GetNowDist()),
        "tr_id":TrId,
        "custtype":"P",
        "hashkey" : Common.GetHashKey(data)
    }
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    
    if res.status_code == 200 and res.json()["rt_cd"] == '0':

        order = res.json()['output']

        OrderInfo = dict()
        

        OrderInfo["OrderNum"] = order['KRX_FWDG_ORD_ORGNO']
        OrderInfo["OrderNum2"] = order['ODNO']
        OrderInfo["OrderTime"] = order['ORD_TMD'] 



        return OrderInfo
    else:
        if ErrLog == "YES":
            print("Error Code : " + str(res.status_code) + " | " + res.text)
        return res.json()["msg_cd"]


#보유한 주식을 모두 시장가 매도하는 극단적 함수 
def SellAllStock():
    StockList = GetMyStockList()

    #시장가로 모두 매도 한다
    for stock_info in StockList:
        pprint.pprint(MakeSellMarketOrder(stock_info['StockCode'],stock_info['StockAmt']))







#매수 가능한지 체크 하기!
def CheckPossibleBuyInfo(stockcode, price, type):

    time.sleep(0.2)

    PATH = "uapi/domestic-stock/v1/trading/inquire-psbl-order"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"

    TrId = "TTTC8908R"
    if Common.GetNowDist() == "VIRTUAL":
         TrId = "VTTC8908R"

    type_code = "00" #지정가
    if type.upper() == "MAREKT":
        type_code = "01"



    # 헤더 설정
    headers = {"Content-Type":"application/json", 
            "authorization": f"Bearer {Common.GetToken(Common.GetNowDist())}",
            "appKey":Common.GetAppKey(Common.GetNowDist()),
            "appSecret":Common.GetAppSecret(Common.GetNowDist()),
            "tr_id": TrId,
            "custtype": "P"}

    params = {
        "CANO": Common.GetAccountNo(Common.GetNowDist()),
        "ACNT_PRDT_CD" : Common.GetPrdtNo(Common.GetNowDist()),
        "PDNO" : stockcode,
        "ORD_UNPR": str(PriceAdjust(price,stockcode)),
        "ORD_DVSN": type_code,
        "CMA_EVLU_AMT_ICLD_YN" : "N",
        "OVRS_ICLD_YN" : "N"
    }

    # 호출
    res = requests.get(URL, headers=headers, params=params)

    if res.status_code == 200 and res.json()["rt_cd"] == '0':

        result = res.json()['output']
#        pprint.pprint(result)

        CheckDict = dict()

        CheckDict['RemainMoney'] = result['ord_psbl_cash']
        CheckDict['MaxAmt'] = result['max_buy_qty']

        return CheckDict

    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return res.json()["msg_cd"]


#매수 가능한수량으로 보정
def AdjustPossibleAmt(stockcode, amt ,type):
    NowPrice = GetCurrentPrice(stockcode)

    data = CheckPossibleBuyInfo(stockcode,NowPrice,type)

    MaxAmt = int(data['MaxAmt'])

    if MaxAmt <= int(amt):
        print("!!!!!!!!!!!!MaxAmt Over!!!!!!!!!!!!!!!!!!")
        return MaxAmt
    else:
        print("!!!!!!!!!!!!Amt OK!!!!!!!!!!!!!!!!!!")
        return int(amt)




############################################################################################################################################################

#주문 리스트를 얻어온다! 종목 코드, side는 ALL or BUY or SELL, 상태는 OPEN or CLOSE
def GetOrderList(stockcode = "", side = "ALL", status = "ALL", limit = 5):
    
    time.sleep(0.2)
    
    TrId = "TTTC8001R"
    if Common.GetNowDist() == "VIRTUAL":
         TrId = "VTTC8001R"

    sell_buy_code = "00"
    if side.upper() == "BUY":
        sell_buy_code = "02"
    elif side.upper() == "SELL":
        sell_buy_code = "01"
    else:
        sell_buy_code = "00"

    status_code= "00"
    if status.upper() == "OPEN":
        status_code = "02"
    elif status.upper() == "CLOSE":
        status_code = "01"
    else:
        status_code = "00"


    PATH = "uapi/domestic-stock/v1/trading/inquire-daily-ccld"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"
    

    params = {
        "CANO": Common.GetAccountNo(Common.GetNowDist()),
        "ACNT_PRDT_CD": Common.GetPrdtNo(Common.GetNowDist()),
        "INQR_STRT_DT": Common.GetFromNowDateStr("KR","NONE", -limit),
        "INQR_END_DT": Common.GetNowDateStr("KR"),
        "SLL_BUY_DVSN_CD": sell_buy_code,
        "INQR_DVSN": "00",
        "PDNO": stockcode,
        "CCLD_DVSN": status_code,
        "ORD_GNO_BRNO": "",
        "ODNO": "",
        "INQR_DVSN_3": "00",
        "INQR_DVSN_1": "",
        "INQR_DVSN_2": "",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": "",

    }
    
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {Common.GetToken(Common.GetNowDist())}",
        "appKey":Common.GetAppKey(Common.GetNowDist()),
        "appSecret":Common.GetAppSecret(Common.GetNowDist()),
        "tr_id": TrId,
        "custtype":"P",
        "hashkey" : Common.GetHashKey(params)
    }

    res = requests.get(URL, headers=headers, params=params) 
    #pprint.pprint(res.json())
    
    if res.status_code == 200 and res.json()["rt_cd"] == '0':

        ResultList = res.json()['output1']

        OrderList = list()
        #pprint.pprint(ResultList)

        for order in ResultList:
            #잔고 수량이 0 이상인것만


            OrderInfo = dict()
            
            OrderInfo["OrderStock"] = order['pdno']
            OrderInfo["OrderStockName"] = order['prdt_name']

            #주문 구분
            if order['ord_dvsn_cd'] == "00":
                OrderInfo["OrderType"] = "Limit"
            else:
                OrderInfo["OrderType"] = "Market"

            #주문 사이드
            if order['sll_buy_dvsn_cd'] == "01":
                OrderInfo["OrderSide"] = "Sell"
            else:
                OrderInfo["OrderSide"] = "Buy"

            #주문 상태
            if float(order['ord_qty']) - (float(order['tot_ccld_qty']) + float(order['cncl_cfrm_qty'])) == 0:
                OrderInfo["OrderSatus"] = "Close"
            else:
                OrderInfo["OrderSatus"] = "Open"



            if Common.GetNowDateStr("KR") != order['ord_dt']: 
                OrderInfo["OrderSatus"] = "Close"     


            #주문 수량~
            OrderInfo["OrderAmt"] = order['ord_qty']


            #주문넘버..
            OrderInfo["OrderNum"] = order['ord_gno_brno']
            OrderInfo["OrderNum2"] = order['odno']

            #아직 미체결 주문이라면 주문 단가를
            if OrderInfo["OrderSatus"] == "Open":

                OrderInfo["OrderAvgPrice"] = order['ord_unpr']

            #체결된 주문이면 평균체결금액을!
            else:

                OrderInfo["OrderAvgPrice"] = order['avg_prvs']


            OrderInfo["OrderIsCancel"] = order['cncl_yn'] #주문 취소 여부!
            OrderInfo['OrderMarket'] = "KOR" #마켓인데 미국과 통일성을 위해!

            OrderInfo["OrderDate"] = order['ord_dt']
            OrderInfo["OrderTime"] = order['ord_tmd'] 

            Is_Ok = False
            
            if status == "ALL":
                Is_Ok = True
            else:
                if status.upper()  == OrderInfo["OrderSatus"].upper() :
                    Is_Ok = True


            if Is_Ok == True:
                Is_Ok = False

                if side.upper() == "ALL":
                    Is_Ok = True
                else:
                    if side.upper() == OrderInfo["OrderSide"].upper():
                        Is_Ok = True


            if Is_Ok == True:
                if stockcode != "":
                    if stockcode.upper() == OrderInfo["OrderStock"].upper():
                        OrderList.append(OrderInfo)
                else:

                    OrderList.append(OrderInfo)



        return OrderList

    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return res.json()["msg_cd"]



#주문 취소/수정 함수
def CancelModifyOrder(stockcode, order_num1 , order_num2 , order_amt , order_price, mode = "CANCEL" ,order_type = "LIMIT" , order_dist = "NONE"):


    time.sleep(0.2)

    TrId = "TTTC0803U"
    if Common.GetNowDist() == "VIRTUAL":
         TrId = "VTTC0803U"

    #마켓 주문을 취소하거나 정정할 순 없는데? 일단 있으니깐 
    order_type = "00"
    if order_type.upper() == "MARKET":
        order_type = "01"

    mode_type = "02"
    if mode.upper() == "MODIFY":
        mode_type = "01"



    PATH = "uapi/domestic-stock/v1/trading/order-rvsecncl"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"
    data = {

        "CANO": Common.GetAccountNo(Common.GetNowDist()),
        "ACNT_PRDT_CD": Common.GetPrdtNo(Common.GetNowDist()),
        "KRX_FWDG_ORD_ORGNO": order_num1,
        "ORGN_ODNO": order_num2,
        "ORD_DVSN": order_type,
        "RVSE_CNCL_DVSN_CD": mode_type,
        "ORD_QTY": str(order_amt),
        "ORD_UNPR": str(PriceAdjust(order_price,stockcode)),
        "QTY_ALL_ORD_YN": "N"

    }
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {Common.GetToken(Common.GetNowDist())}",
        "appKey":Common.GetAppKey(Common.GetNowDist()),
        "appSecret":Common.GetAppSecret(Common.GetNowDist()),
        "tr_id": TrId,
        "custtype":"P",
        "hashkey" : Common.GetHashKey(data)
    }

    res = requests.post(URL, headers=headers, data=json.dumps(data))
    
    if res.status_code == 200 and res.json()["rt_cd"] == '0':

        order = res.json()['output']

        OrderInfo = dict()
        

        OrderInfo["OrderNum"] = order['KRX_FWDG_ORD_ORGNO']
        OrderInfo["OrderNum2"] = order['ODNO']
        OrderInfo["OrderTime"] = order['ORD_TMD'] 


        return OrderInfo
    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return res.json()["msg_cd"]



#모든 주문을 취소하는 함수
def CancelAllOrders(stockcode = "", side = "ALL"):

    OrderList = GetOrderList(stockcode,side)

    for order in OrderList:
        if order['OrderSatus'].upper() == "OPEN":
            pprint.pprint(CancelModifyOrder(order['OrderStock'],order['OrderNum'],order['OrderNum2'],order['OrderAmt'],order['OrderAvgPrice']))




############################################################################################################################################################
    
#p_code -> D:일, W:주, M:월, Y:년
def GetOhlcv(stock_code,p_code):

    time.sleep(0.2)

    PATH = "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"



    # 헤더 설정
    headers = {"Content-Type":"application/json", 
            "authorization": f"Bearer {Common.GetToken(Common.GetNowDist())}",
            "appKey":Common.GetAppKey(Common.GetNowDist()),
            "appSecret":Common.GetAppSecret(Common.GetNowDist()),
            "tr_id":"FHKST03010100"}

    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": stock_code,
        "FID_INPUT_DATE_1": Common.GetFromNowDateStr("KR","NONE",-36500),
        "FID_INPUT_DATE_2": Common.GetNowDateStr("KR"),
        "FID_PERIOD_DIV_CODE": p_code,
        "FID_ORG_ADJ_PRC": "0"
    }

    # 호출
    res = requests.get(URL, headers=headers, params=params)

    if res.status_code == 200 and res.json()["rt_cd"] == '0':

        ResultList = res.json()['output2']


        df = list()


        if len(pd.DataFrame(ResultList)) > 0:

            OhlcvList = list()


            for ohlcv in ResultList:
                
                if len(ohlcv) == 0:
                    continue

                OhlcvData = dict()

                try:
                    if ohlcv['stck_oprc'] != "":
                        
                        OhlcvData['Date'] = ohlcv['stck_bsop_date']
                        OhlcvData['open'] = float(ohlcv['stck_oprc'])
                        OhlcvData['high'] = float(ohlcv['stck_hgpr'])
                        OhlcvData['low'] = float(ohlcv['stck_lwpr'])
                        OhlcvData['close'] = float(ohlcv['stck_clpr'])
                        OhlcvData['volume'] = float(ohlcv['acml_vol'])
                        OhlcvData['value'] = float(ohlcv['acml_tr_pbmn'])

                        OhlcvList.append(OhlcvData)
                except Exception as e:
                    print("E:", e)
                    
            if len(OhlcvList) > 0:
                        
                df = pd.DataFrame(OhlcvList)
                df = df.set_index('Date')

                df = df.sort_values(by="Date")
                df.insert(6,'change',(df['close'] - df['close'].shift(1)) / df['close'].shift(1))
                    
                df[[ 'open', 'high', 'low', 'close', 'volume', 'change']] = df[[ 'open', 'high', 'low', 'close', 'volume', 'change']].apply(pd.to_numeric)



        return df
    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return res.json()["msg_cd"]
