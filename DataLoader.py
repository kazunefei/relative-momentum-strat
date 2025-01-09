import yfinance as yf
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas_market_calendars as mcal

class DataLoader:
    def __init__(self):
        self.DATE_TD = dt.today()
        self.DATE_FYA = self.DATE_TD - relativedelta(years = 5)
        self.DATE_ONEYEARAGO = self.DATE_TD - relativedelta(years = 1)
        self.CALENDAR = mcal.get_calendar('NYSE')
        self.SCHEDULE = self.CALENDAR.schedule(start_date = self.DATE_FYA, end_date = self.DATE_TD)
        
    def get_securities_data(self, ticker1, ticker2):
        ticker1_data = yf.download(ticker1, start = self.DATE_FYA, end = self.DATE_TD)
        ticker2_data = yf.download(ticker2, start = self.DATE_FYA, end = self.DATE_TD)
        
        ticker1_data = ticker1_data[ticker1_data.index.weekday < 5]
        ticker2_data = ticker2_data[ticker2_data.index.weekday < 5]
        
        ticker1_data = ticker1_data[ticker1_data.index.isin(self.SCHEDULE.index)]
        ticker2_data = ticker2_data[ticker2_data.index.isin(self.SCHEDULE.index)]
        
        ticker1_close = ticker1_data['Close']
        ticker2_close = ticker2_data['Close']
        
        merged_data = ticker1_close.merge(ticker2_close, on = 'Date')
        
        return merged_data
    
    def get_tbill(self):
        t_bill = yf.Ticker('^IRX')
        hist = t_bill.history(period="1d")
        THREE_MO_TBILL = (hist["Close"].iloc[-1])/100 
        
        return THREE_MO_TBILL  