import json
import pandas as pd
import pprint




TargetStockList = list()
#파일 경로입니다.
korea_file_path = "/Users/TY/Documents/class101/KrStockDataList.json"

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(korea_file_path, 'r') as json_file:
        TargetStockList = json.load(json_file)

except Exception as e:
    print("Exception by First")


print("TotalStockCodeCnt: " , len(TargetStockList))


df = pd.DataFrame(TargetStockList)
pprint.pprint(df)

#ROE ROA GP/A를 포괄한다고 치자! 
#물론 새로운 KIS_Make_StockData_KR을 통해 미리 크롤링해놨다면 이 부분은 필요 없다 주석처리!!
df['StockROE'] = df['StockEPS'] / df['StockBPS'] * 100.0

#새로운 KIS_Make_StockData_KR을 통해 미리 크롤링해놨다면 영업이익(StockOperProfit)도 사용가능!
#df['OPER_PROFIT_rank'] = df['StockOperProfit'].rank()
df['PER_rank'] = df['StockPER'].rank()
df['PBR_rank'] = df['StockPBR'].rank()
df['ROE_rank'] = df['StockROE'].rank(ascending=False)

df['PER_ROE_SCORE'] = df['PER_rank'] + df['ROE_rank']


df = df[df.StockMarketCap >= 50.0].copy()
df = df[df.StockDistName != "금융"].copy()
df = df[df.StockDistName != "외국증권"].copy()

#영상엔 없지만 이렇게 영업이익 0 초과를 필터할 수 있다! (새로운 KIS_Make_StockData_KR을 통해 미리 크롤링해놨다면)
#df = df[df.StockOperProfit > 0].copy()

df = df[df.StockEPS > 0].copy()
df = df[df.StockBPS > 0].copy()
df = df[df.StockPER >= 1.0].copy()
df = df[df.StockPBR >= 0.2].copy()




#ascending=False 시총 높은 순으로
df = df.sort_values(by="StockMarketCap", ascending=False)
#df = df.sort_values(by=["StockMarketCap","ROE_rank"])
pprint.pprint(df)




#시총 상위 20%중에 PER낮은거순으로 20개?
df = df[0:int(float(len(df))*0.2)].copy()
pprint.pprint(df)




df = df.sort_values(by="PER_ROE_SCORE")
pprint.pprint(df)




TopCnt = 20
NowCnt = 0

for idx, row in df.iterrows():
    
    if NowCnt < TopCnt:

        print("-----------------------------------")
        print(row['StockName'])
        print("시총: ", row['StockMarketCap'])
        print("현재가 : ", row['StockNowPrice'])
        print("EPS(주당 순이익) : ", row['StockEPS'])
        print("BPS(주당 순자산(-부채))) : ", row['StockBPS'])
        print("PER(현재가 / 주당 순자산) : ", row['StockPER'])
        print("PBR(현재가 / 주당 순자산) : ", row['StockPBR'])
        print("ROE(EPS / BPS), ROA, GP/A 등 : ", row['StockROE'])

        print("PER순위 : ", row['PER_rank'])
        print("PBR순위 : ", row['PBR_rank'])
        print("ROE순위: ", row['ROE_rank'])
        print("-----------------------------------")


        NowCnt += 1


