# -*- coding: utf-8 -*-


import KIS_Common as Common

import requests
import json


from datetime import datetime
from pytz import timezone

import pprint
import time


import pandas as pd


#시장이 열렸는지 여부 체크! #토요일 일요일은 확실히 안열리니깐 제외! 
def IsMarketOpen():


    now_time = datetime.now(timezone('America/New_York'))
    pprint.pprint(now_time)

    date_week = now_time.weekday()

    IsOpen = False

    #주말은 무조건 장이 안열리니 False 리턴!
    if date_week == 5 or date_week == 6:  
        IsOpen = False
    else:
        #현지시간 기준 9시 반부터 4시
        if now_time.hour >= 9 and now_time.hour <= 15:
            IsOpen = True

            if now_time.hour == 9 and now_time.minute < 30:
                IsOpen = False

            if now_time.hour == 15 and now_time.minute > 50:
                IsOpen = False

    #평일 장 시간이어도 공휴일같은날 장이 안열린다. 그래서 1번 더 체크!!
    if IsOpen == True:


        print("Time is OK... but one more checked!!!")

        result = ""

        try:

            #가상 계좌면 메세지 통일을 위해 실계좌에서 가짜 주문 취소 주문을 넣는다!
            if Common.GetNowDist() == "VIRTUAL":

                Common.SetChangeMode("REAL")
                result = CancelModifyOrder('AAPL','0','1','1',"CANCEL","CHECK")
                Common.SetChangeMode("VIRTUAL")

            else:
                result = CancelModifyOrder('AAPL','0','1','1',"CANCEL","CHECK")

        except Exception as e:
            print("EXCEPTION ",e)


        #장운영시간이 아니라고 리턴되면 장이 닫힌거다!
        if result == "APBK0918" or result == "APBK0919":

            print("Market is Close!!")
            return False

        #원주문 없다는 에러코드가 리턴되면 장이 열린거고
        else:


            if result == "EGW00123":
                print("Token is failed...So You need Action!!")

                
            print("Market is Open!!")
            return True
    else:

        print("Time is NO!!!")        
        return False


#price_pricision 호가 단위에 맞게 변형해준다. 지정가 매매시 사용
def PriceAdjust(price):
    
    return round(float(price),2)


#환율 리턴!
def GetExrt():

    time.sleep(0.2)
    
    PATH = "/uapi/overseas-stock/v1/trading/inquire-present-balance"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"

    TrId = "CTRP6504R"
    if Common.GetNowDist() == "VIRTUAL":
         TrId = "VTRP6504R"


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
        "WCRC_FRCR_DVSN_CD" : "02",
        'NATN_CD': '840', 
        'TR_MKET_CD': '00', 
        'INQR_DVSN_CD': '00'
    }

    # 호출
    res = requests.get(URL, headers=headers, params=params)
    #pprint.pprint(res.json())

    if res.status_code == 200 and res.json()["rt_cd"] == '0':

        result = res.json()['output2']

        Rate = 1200

        for data in result:
            if data['crcy_cd'] == "USD":
                Rate = data['frst_bltn_exrt']
                break

        return Rate
       
    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return None


#미국 주식 주간 / 야간 여부를 리턴 하는 함수!
def GetDayOrNight():

    time.sleep(0.2)
    
    PATH = "uapi/overseas-stock/v1/trading/dayornight"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"

    # 헤더 설정
    headers = {"Content-Type":"application/json", 
            "authorization": f"Bearer {Common.GetToken(Common.GetNowDist())}",
            "appKey":Common.GetAppKey(Common.GetNowDist()),
            "appSecret":Common.GetAppSecret(Common.GetNowDist()),
            "tr_id":"JTTT3010R"}

    params = {
    }

    # 호출
    res = requests.get(URL, headers=headers, params=params)

    if res.status_code == 200 and res.json()["rt_cd"] == '0':
        return res.json()['output']['PSBL_YN']
    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return None



#미국 잔고! 달러로 리턴할건지 원화로 리턴할건지!
def GetBalance(st = "USD"):

    time.sleep(0.2)
    
    PATH = "uapi/overseas-stock/v1/trading/inquire-present-balance"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"

    TrId = "CTRP6504R"
    if Common.GetNowDist() == "VIRTUAL":
         TrId = "VTRP6504R"


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
        "WCRC_FRCR_DVSN_CD" : "02",
        'NATN_CD': '840', 
        'TR_MKET_CD': '00', 
        'INQR_DVSN_CD': '00'
    }

    # 호출
    res = requests.get(URL, headers=headers, params=params)
    #pprint.pprint(res.json())



    if res.status_code == 200 and res.json()["rt_cd"] == '0':

        result = res.json()['output2']

        #실시간 주식 상태가 반영이 안되서 주식 정보를 직접 읽어서 계산!
        MyStockList = GetMyStockList(st)
        
        StockOriMoneyTotal = 0
        StockNowMoneyTotal = 0
        
        for stock in MyStockList:
            #pprint.pprint(stock)
            StockOriMoneyTotal += float(stock['StockOriMoney'])
            StockNowMoneyTotal += float(stock['StockNowMoney'])
            
            #print("--", StockNowMoneyTotal, StockOriMoneyTotal)
            
            
        balanceDict = dict()
        balanceDict['RemainMoney'] = 0

        Rate = 1200


        if st == "USD":


            for data in result:
                if data['crcy_cd'] == "USD":
                    #예수금 총금액 (즉 주문가능 금액)
                    balanceDict['RemainMoney'] = float(data['frcr_dncl_amt_2']) - float(data['frcr_buy_amt_smtl']) + float(data['frcr_sll_amt_smtl']) #모의계좌는 0으로 나온다 이유는 모르겠음!
                    Rate = data['frst_bltn_exrt']
                    break


            result = res.json()['output3']

            #임시로 모의 계좌 잔고가 0으로 
            if Common.GetNowDist() == "VIRTUAL" and float(balanceDict['RemainMoney']) == 0:

                #주식 총 평가 금액
                balanceDict['StockMoney'] = StockNowMoneyTotal#(float(result['evlu_amt_smtl_amt']) / float(Rate))
                #평가 손익률
                balanceDict['StockRevenue'] = float(StockNowMoneyTotal) - float(StockOriMoneyTotal) #round((float(StockNowMoneyTotal)/float(StockOriMoneyTotal) - 1.0) * 100.0,2) #(float(result['evlu_amt_smtl_amt']) - float(result['pchs_amt_smtl_amt'])) / float(Rate)
                
                balanceDict['RemainMoney'] = (float(result['frcr_evlu_tota']) / float(Rate))
                
                #총 평가 금액
                balanceDict['TotalMoney'] = float(balanceDict['StockMoney']) + float(balanceDict['RemainMoney'])
                


            else:


                #주식 총 평가 금액
                balanceDict['StockMoney'] = StockNowMoneyTotal#(float(result['evlu_amt_smtl_amt']) / float(Rate))
                #평가 손익률
                balanceDict['StockRevenue'] = float(StockNowMoneyTotal) - float(StockOriMoneyTotal) #round((float(StockNowMoneyTotal)/float(StockOriMoneyTotal) - 1.0) * 100.0,2)#(float(result['evlu_amt_smtl_amt']) - float(result['pchs_amt_smtl_amt'])) / float(Rate)
                
                #총 평가 금액
                balanceDict['TotalMoney'] = float(balanceDict['StockMoney']) + float(balanceDict['RemainMoney'])


        else:

            for data in result:
                if data['crcy_cd'] == "USD":
                    Rate = data['frst_bltn_exrt']
                    #예수금 총금액 (즉 주문가능현금)
                    balanceDict['RemainMoney'] = (float(data['frcr_dncl_amt_2']) - float(data['frcr_buy_amt_smtl']) + float(data['frcr_sll_amt_smtl'])) * float(Rate)
                    #balanceDict['RemainMoney'] = data['frcr_evlu_amt2'] #모의계좌는 0으로 나온다 이유는 모르겠음!
                    
                    break

            #print("balanceDict['RemainMoney'] ", balanceDict['RemainMoney'] )

            result = res.json()['output3']

            #임시로 모의 계좌 잔고가 0으로 나오면 
            if Common.GetNowDist() == "VIRTUAL" and float(balanceDict['RemainMoney']) == 0:
                

  
                #주식 총 평가 금액
                balanceDict['StockMoney'] = StockNowMoneyTotal#result['evlu_amt_smtl_amt']
                #평가 손익 금액
                balanceDict['StockRevenue'] = float(StockNowMoneyTotal) - float(StockOriMoneyTotal)  #round((float(StockNowMoneyTotal)/float(StockOriMoneyTotal) - 1.0) * 100.0,2)#float(result['evlu_amt_smtl_amt']) - float(result['pchs_amt_smtl_amt'])

                balanceDict['RemainMoney'] =  float(result['frcr_evlu_tota'])

                #총 평가 금액
                balanceDict['TotalMoney'] = float(balanceDict['StockMoney']) + float(balanceDict['RemainMoney'])
                
            else:


                #주식 총 평가 금액
                balanceDict['StockMoney'] = StockNowMoneyTotal#result['evlu_amt_smtl_amt']
                #평가 손익 금액
                balanceDict['StockRevenue'] = float(StockNowMoneyTotal) - float(StockOriMoneyTotal) #round((float(StockNowMoneyTotal)/float(StockOriMoneyTotal) - 1.0) * 100.0,2)#float(result['evlu_amt_smtl_amt']) - float(result['pchs_amt_smtl_amt'])
                #총 평가 금액
                balanceDict['TotalMoney'] = float(balanceDict['StockMoney']) + float(balanceDict['RemainMoney'])

        #print("RATE: ", Rate)

        return balanceDict
       

    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return None
    
#미국 보유 주식 리스트 
def GetMyStockList(st = "USD"):


    time.sleep(0.2)
    

    PATH = "uapi/overseas-stock/v1/trading/inquire-balance"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"


    StockList = list()
    
    for i in range(1,4):

        try_market = "NASD"

        if i == 2:
            try_market = "NYSE"
        elif i == 3:
            try_market = "AMEX"
        else:
            try_market = "NASD"

        


        TrId = "JTTT3012R"
        if Common.GetNowDist() == "VIRTUAL":
            TrId = "VTTT3012R"

        if GetDayOrNight() == 'N':
            TrId = "TTTS3012R"
            if Common.GetNowDist() == "VIRTUAL":
                TrId = "VTTS3012R"


        
        DataLoad = True
        
        SeqKey = ""

        #드물지만 보유종목이 아주 많으면 한 번에 못가져 오므로 SeqKey를 이용해 연속조회를 하기 위한 반복 처리 
        while DataLoad:
                
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
                "OVRS_EXCG_CD" : try_market,
                "TR_CRCY_CD": "USD",
                "CTX_AREA_FK200" : "",
                "CTX_AREA_NK200" : SeqKey
            }

            # 호출
            res = requests.get(URL, headers=headers, params=params)
            #pprint.pprint(res.json())

            if res.status_code == 200 and res.json()["rt_cd"] == '0':

                SeqKey = res.json()['ctx_area_nk200'].strip()
                if SeqKey != "":
                    print("CTX_AREA_NK200: ", SeqKey)
                
                if SeqKey == "":
                    DataLoad = False
                

                ResultList = res.json()['output1']
                #pprint.pprint(ResultList)



                for stock in ResultList:
                    #잔고 수량이 0 이상인것만
                    if int(stock['ovrs_cblc_qty']) > 0:

                        StockInfo = dict()
                        
                        StockInfo["StockCode"] = stock['ovrs_pdno']
                        StockInfo["StockName"] = stock['ovrs_item_name']
                        StockInfo["StockAmt"] = stock['ovrs_cblc_qty']

                        if st == "USD":

                            StockInfo["StockAvgPrice"] = stock['pchs_avg_pric']
                            StockInfo["StockOriMoney"] = stock['frcr_pchs_amt1']
                            StockInfo["StockNowMoney"] = stock['ovrs_stck_evlu_amt']
                            StockInfo["StockNowPrice"] = stock['now_pric2']
                            StockInfo["StockRevenueMoney"] = stock['frcr_evlu_pfls_amt']

                        else:

                            time.sleep(0.2)
                            Rate = GetExrt()
                            
                            StockInfo["StockAvgPrice"] = float(stock['pchs_avg_pric']) * float(Rate)
                            StockInfo["StockOriMoney"] = float(stock['frcr_pchs_amt1']) * float(Rate)
                            StockInfo["StockNowMoney"] = float(stock['ovrs_stck_evlu_amt']) * float(Rate)
                            StockInfo["StockNowPrice"] = float(stock['now_pric2']) * float(Rate)
                            StockInfo["StockRevenueMoney"] = float(stock['frcr_evlu_pfls_amt']) * float(Rate)



                        StockInfo["StockRevenueRate"] = stock['evlu_pfls_rt']
                        
                        Is_Duple = False
                        for exist_stock in StockList:
                            if exist_stock["StockCode"] == StockInfo["StockCode"]:
                                Is_Duple = True
                                break
                                

                        if Is_Duple == False:
                            StockList.append(StockInfo)



            else:
                print("Error Code : " + str(res.status_code) + " | " + res.text)
                # return None
           
        
    return StockList
        



############################################################################################################################################################




#미국 주식현재가 시세
def GetCurrentPriceOri(market, stock_code):

    time.sleep(0.2)
    
    PATH = "uapi/overseas-price/v1/quotations/price"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"



    # 헤더 설정
    headers = {"Content-Type":"application/json", 
            "authorization": f"Bearer {Common.GetToken(Common.GetNowDist())}",
            "appKey":Common.GetAppKey(Common.GetNowDist()),
            "appSecret":Common.GetAppSecret(Common.GetNowDist()),
            "tr_id":"HHDFS00000300"}

    params = {
        "AUTH": "",
        "EXCD":market.upper(),
        "SYMB":stock_code,
    }

    # 호출
    res = requests.get(URL, headers=headers, params=params)
    pprint.pprint(res.json())

    if res.status_code == 200 and res.json()["rt_cd"] == '0':
        return float(res.json()['output']['last'])
    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return None


#미국의 나스닥,뉴욕거래소, 아멕스를 뒤져서 있는 증권의 현재가를 가지고 옵니다!
def GetCurrentPrice(stock_code):

    time.sleep(0.2)
    
    PATH = "uapi/overseas-price/v1/quotations/price"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"

    for i in range(1,4):

        try_market = "NAS"

        if i == 2:
            try_market = "NYS"
        elif i == 3:
            try_market = "AMS"
        else:
            try_market = "NAS"




        # 헤더 설정
        headers = {"Content-Type":"application/json", 
                "authorization": f"Bearer {Common.GetToken(Common.GetNowDist())}",
                "appKey":Common.GetAppKey(Common.GetNowDist()),
                "appSecret":Common.GetAppSecret(Common.GetNowDist()),
                "tr_id":"HHDFS00000300"}

        params = {
            "AUTH": "",
            "EXCD":try_market,
            "SYMB":stock_code,
        }

        # 호출
        res = requests.get(URL, headers=headers, params=params)

        if res.status_code == 200 and res.json()["rt_cd"] == '0':

            if res.json()['output']['last'] == '':
               #print(try_market, " is Failed.. Next market.. ")
                time.sleep(0.2)
                continue # 다음 시도를 한다!
            else:
                #print(try_market, " is Succeed!! ")
                return float(res.json()['output']['last'])

        else:
            print("Error Code : " + str(res.status_code) + " | " + res.text)
            break

    return None




############################################################################################################################################################


#미국 지정가 주문하기!
def MakeBuyLimitOrderOri(stockcode, amt, price, market):

    try:
        #가상 계좌는 미지원
        if Common.GetNowDist() != "VIRTUAL":
            #매수 가능한수량으로 보정
            amt = AdjustPossibleAmt(stockcode, amt)

    except Exception as e:
        print("Exception")

    


    time.sleep(0.2)

    TrId = "JTTT1002U"
    if Common.GetNowDist() == "VIRTUAL":
         TrId = "VTTT1002U"


    PATH = "uapi/overseas-stock/v1/trading/order"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"
    data = {

        "CANO": Common.GetAccountNo(Common.GetNowDist()),
        "ACNT_PRDT_CD": Common.GetPrdtNo(Common.GetNowDist()),
        "OVRS_EXCG_CD": market.upper(),
        "PDNO": stockcode,
        "ORD_DVSN": "00",
        "ORD_QTY": str(int(amt)),
        "OVRS_ORD_UNPR": str(PriceAdjust(price)),
        "ORD_SVR_DVSN_CD": "0"

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
        return None
        
#미국 지정가 주문하기!
def MakeSellLimitOrderOri(stockcode, amt, price, market):

    time.sleep(0.2)

    TrId = "JTTT1006U"
    if Common.GetNowDist() == "VIRTUAL":
         TrId = "VTTT1001U"



    PATH = "uapi/overseas-stock/v1/trading/order"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"
    data = {

        "CANO": Common.GetAccountNo(Common.GetNowDist()),
        "ACNT_PRDT_CD": Common.GetPrdtNo(Common.GetNowDist()),
        "OVRS_EXCG_CD": market.upper(),
        "PDNO": stockcode,
        "ORD_DVSN": "00",
        "ORD_QTY": str(int(amt)),
        "OVRS_ORD_UNPR": str(PriceAdjust(price)),
        "ORD_SVR_DVSN_CD": "0"

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
        return None

#미국 지정가 주문하기! 마켓을 모를 경우 자동으로 뒤져서!
def MakeBuyLimitOrder(stockcode, amt, price):

    try:
        #가상 계좌는 미지원
        if Common.GetNowDist() != "VIRTUAL":
            #매수 가능한수량으로 보정
            amt = AdjustPossibleAmt(stockcode, amt)

    except Exception as e:
        print("Exception")


    

    time.sleep(0.2)
    
    TrId = "JTTT1002U"
    if Common.GetNowDist() == "VIRTUAL":
         TrId = "VTTT1002U"

    market = GetMarketCodeUS(stockcode)

    PATH = "uapi/overseas-stock/v1/trading/order"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"
    data = {

        "CANO": Common.GetAccountNo(Common.GetNowDist()),
        "ACNT_PRDT_CD": Common.GetPrdtNo(Common.GetNowDist()),
        "OVRS_EXCG_CD": market,
        "PDNO": stockcode,
        "ORD_DVSN": "00",
        "ORD_QTY": str(int(amt)),
        "OVRS_ORD_UNPR": str(PriceAdjust(price)),
        "ORD_SVR_DVSN_CD": "0"

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
        return None
        
#미국 지정가 주문하기! 마켓을 모를 경우 자동으로 뒤져서!
def MakeSellLimitOrder(stockcode, amt, price):

    time.sleep(0.2)
    
    TrId = "JTTT1006U"
    if Common.GetNowDist() == "VIRTUAL":
         TrId = "VTTT1001U"


    market = GetMarketCodeUS(stockcode)

    PATH = "uapi/overseas-stock/v1/trading/order"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"
    data = {

        "CANO": Common.GetAccountNo(Common.GetNowDist()),
        "ACNT_PRDT_CD": Common.GetPrdtNo(Common.GetNowDist()),
        "OVRS_EXCG_CD": market,
        "PDNO": stockcode,
        "ORD_DVSN": "00",
        "ORD_QTY": str(int(amt)),
        "OVRS_ORD_UNPR": str(PriceAdjust(price)),
        "ORD_SVR_DVSN_CD": "0"

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
        return None

#미국의 나스닥,뉴욕거래소, 아멕스를 뒤져서 있는 해당 주식의 거래소 코드를 리턴합니다!!
def GetMarketCodeUS(stock_code):

    time.sleep(0.2)
        
    PATH = "uapi/overseas-price/v1/quotations/price"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"

    for i in range(1,4):

        try_market = "NAS"

        if i == 2:
            try_market = "NYS"
        elif i == 3:
            try_market = "AMS"
        else:
            try_market = "NAS"




        # 헤더 설정
        headers = {"Content-Type":"application/json", 
                "authorization": f"Bearer {Common.GetToken(Common.GetNowDist())}",
                "appKey":Common.GetAppKey(Common.GetNowDist()),
                "appSecret":Common.GetAppSecret(Common.GetNowDist()),
                "tr_id":"HHDFS00000300"}

        params = {
            "AUTH": "",
            "EXCD":try_market,
            "SYMB":stock_code,
        }

        # 호출
        res = requests.get(URL, headers=headers, params=params)

        if res.status_code == 200 and res.json()["rt_cd"] == '0':

            if res.json()['output']['last'] == '':
                #print(try_market, " is Failed.. Next market.. ")
                time.sleep(0.2)
                continue # 다음 시도를 한다!
            else:
                #print(try_market, " is Succeed!! ")

                if try_market == "NYS":
                    return "NYSE"
                elif try_market == "AMS":
                    return "AMEX"
                else:
                    return "NASD"

        else:
            print("Error Code : " + str(res.status_code) + " | " + res.text)
            break

    return None




#보유한 주식을 모두 매도하는 극단적 함수 
def SellAllStock():
    StockList = GetMyStockList()

    #시장가로 모두 매도 한다
    for stock_info in StockList:
        pprint.pprint(MakeSellLimitOrder(stock_info['StockCode'],stock_info['StockAmt'],stock_info['StockAvgPrice']))



#매수 가능한지 체크 하기!
def CheckPossibleBuyInfo(stockcode, price):

    time.sleep(0.2)

    PATH = "uapi/overseas-stock/v1/trading/inquire-psamount"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"

    TrId = "TTTS3007R"
    if GetDayOrNight() == 'N':
        TrId = "JTTT3007R"



    market = GetMarketCodeUS(stockcode)

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
        "OVRS_EXCG_CD" : market,
        "OVRS_ORD_UNPR": str(PriceAdjust(price)),
        "ITEM_CD" : stockcode
    }

    # 호출
    res = requests.get(URL, headers=headers, params=params)

    if res.status_code == 200 and res.json()["rt_cd"] == '0':

        result = res.json()['output']
        pprint.pprint(result)

        CheckDict = dict()

        CheckDict['RemainMoney'] = result['ord_psbl_frcr_amt']
        CheckDict['MaxAmt'] = result['max_ord_psbl_qty']

        return CheckDict

    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return res.json()["msg_cd"]


#매수 가능한수량으로 보정
def AdjustPossibleAmt(stockcode, amt):
    NowPrice = GetCurrentPrice(stockcode)

    data = CheckPossibleBuyInfo(stockcode,NowPrice)
    
    if str(data) == "MCA00124" or str(data) == "OPSQ0002":
        return int(amt)
    else:
        
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
    
    TrId = "JTTT3001R"
    if Common.GetNowDist() == "VIRTUAL":
         TrId = "VTTS3035R" # VTTT3001R #야간은 미지원...으앙! 어쩌라공~~

    if GetDayOrNight() == 'N':
        TrId = "TTTS3035R"
        if Common.GetNowDist() == "VIRTUAL":
            TrId = "VTTS3035R"

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


    PATH = "uapi/overseas-stock/v1/trading/inquire-ccnl"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"
    
    print("stockcode - >" , stockcode)

    params = {
        "CANO": Common.GetAccountNo(Common.GetNowDist()),
        "ACNT_PRDT_CD": Common.GetPrdtNo(Common.GetNowDist()),
        "PDNO": stockcode,
        "ORD_STRT_DT": Common.GetFromNowDateStr("US","NONE", -limit),
        "ORD_END_DT": Common.GetNowDateStr("US"),
        "SLL_BUY_DVSN": sell_buy_code,
        "CCLD_NCCS_DVSN": status_code,
        "OVRS_EXCG_CD": "",
        "SORT_SQN": "",
        "ORD_DT": "",
        "ORD_GNO_BRNO": "",
        "ODNO": "",
        "CTX_AREA_FK200": "",
        "CTX_AREA_NK200": "",

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

        ResultList = res.json()['output']

        

        OrderList = list()


        for order in ResultList:
            #잔고 수량이 0 이상인것만

            OrderInfo = dict()
            
            OrderInfo["OrderStock"] = order['pdno']
            OrderInfo["OrderStockName"] = order['prdt_name']

            #주문 구분
            OrderInfo["OrderType"] = "Limit"
   

            #주문 사이드
            if order['sll_buy_dvsn_cd'] == "01":
                OrderInfo["OrderSide"] = "Sell"
            else:
                OrderInfo["OrderSide"] = "Buy"


            if (float(order['ft_ord_qty']) - float(order['ft_ccld_qty'])) == 0 or order['prcs_stat_name'] == "완료":
                OrderInfo["OrderSatus"] = "Close"
            else:
                OrderInfo["OrderSatus"] = "Open"

            #주문정보 날짜가 다르다.
            if Common.GetNowDateStr("KR") != order['ord_dt']: 
                #그런데 전날이다!
                if Common.GetFromNowDateStr("KR","NONE",-1) == order['ord_dt']:
                    if int(order['ord_tmd']) < 203000: #10시30분00초 보다 작다
                        OrderInfo["OrderSatus"] = "Close"     
                else:
                    OrderInfo["OrderSatus"] = "Close"   #전날도 아니면 무조건 취소가 되었을 터!



            #주문 수량~
            OrderInfo["OrderAmt"] = order['ft_ord_qty']


            #주문넘버..
            OrderInfo["OrderNum"] = order['ord_gno_brno']
            OrderInfo["OrderNum2"] = order['odno']

            #아직 미체결 주문이라면 주문 단가를
            if OrderInfo["OrderSatus"] == "Open":

                OrderInfo["OrderAvgPrice"] = order['ft_ord_unpr3']

            #체결된 주문이면 평균체결금액을!
            else:
                if order['ft_ccld_qty'] == '0':
                    OrderInfo["OrderAvgPrice"] = order['ft_ord_unpr3']
                else:
                    OrderInfo["OrderAvgPrice"] = order['ft_ccld_unpr3']

            if order['rvse_cncl_dvsn']  == "02":

                OrderInfo["OrderIsCancel"] = 'Y' 
            else:

                OrderInfo["OrderIsCancel"] = 'N' 
            OrderInfo['OrderMarket'] = order['ovrs_excg_cd'] #마켓인데 미국과 통일성을 위해!

            OrderInfo["OrderDate"] = order['ord_dt']
            OrderInfo["OrderTime"] = order['ord_tmd'] 


            Is_Ok = False
            
            if status == "ALL":
                Is_Ok = True
            else:
                if status == OrderInfo["OrderSatus"].upper():
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
        return None


#주문 취소하거나 종료하기
def CancelModifyOrder(stockcode, order_num , order_amt , order_price, mode = "CANCEL", Errlog="YES"):

    time.sleep(0.2)
    
    TrId = "JTTT1004U"
    if Common.GetNowDist() == "VIRTUAL":
         TrId = "VTTT1004U"


    mode_type = "02"
    if mode.upper() == "MODIFY":
        mode_type = "01"

    market = GetMarketCodeUS(stockcode)


    PATH = "uapi/overseas-stock/v1/trading/order-rvsecncl"
    URL = f"{Common.GetUrlBase(Common.GetNowDist())}/{PATH}"
    data = {

        "CANO": Common.GetAccountNo(Common.GetNowDist()),
        "ACNT_PRDT_CD": Common.GetPrdtNo(Common.GetNowDist()),
        "OVRS_EXCG_CD": market.upper(),
        "PDNO" : stockcode,
        "ORGN_ODNO": str(order_num),
        "RVSE_CNCL_DVSN_CD": mode_type,
        "ORD_QTY": str(order_amt),
        "OVRS_ORD_UNPR": str(PriceAdjust(order_price))

    }

    pprint.pprint(data)

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
        if Errlog == "YES":
            print("Error Code : " + str(res.status_code) + " | " + res.text)
        return res.json()["msg_cd"]



def CancelAllOrders(stockcode = "", side = "ALL"):

    OrderList = GetOrderList(stockcode,side)

    for order in OrderList:
        if order['OrderSatus'].upper() == "OPEN":
            pprint.pprint(CancelModifyOrder(order['OrderStock'],order['OrderNum2'],order['OrderAmt'],order['OrderAvgPrice']))



        

############################################################################################################################################################
    