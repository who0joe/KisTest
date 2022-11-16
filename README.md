# KisTest

1. 환경설정
    - AWS(리눅스)와 local PC를 FileZilla를 이용해서 통신
    - line_alert 라이브러리 설치
    - Crontab을 이용해서 정해진 시간에 작동.
    
2. KIS_MakeToken.py 실행
    - myStockInfo.yaml 파일에 정보를 읽고 Crontab 하루 한번 실행 설정.
    
3. 기본 메소드
    1. KIS_Common.py
        - 계좌설정(REAL / VIRTUAL)
        - FDR 크롤링 ( GetOhlcv1)
        - Yahoo 크롤링 (GetOhlcv2)
        - 최종 시세 데이터 (GetOhlcv)
        - 기술적지표 (GetMA, GetRSI, GetBB, GetMACD ,GetIC,GetStoch )
    2. KIS_API_Helper .py
        - 장이 열렸는지 확인 (ISMarketOpen)
        - 내 잔고 확인 (GetBalance)
        - 내 보유 주식 리스트 확인 (GetMyStockList)
        - 현재가 확인 (GetCurrentPrice)
        - 지정가 매수/매도 주문 (MakeBuyLimitOrder / MakeSellLimitOrder)
        - 주문내역 확인 (GetOrderList)
        - 미체결 모두 취소 (CancelAllOrder)
        - 보유주식 모두 청산 (SellAllStock)
        - 캔들데이터 불러오기 (GetOhlcv)
