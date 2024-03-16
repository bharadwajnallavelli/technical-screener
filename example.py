import pandas as pd
import yfinance as yf
from ta.trend import MACD
import warnings
warnings.filterwarnings("ignore")

# MACD stock list for recent buy or sell
macd_buy_list = []
macd_sell_list = []

# Stock List
stock_list = ['CPRT', 'AAPL', 'AMGN', 'CMCSA', 'INTC', 'KLAC', 'PCAR', 'CTAS', 'PAYX', 'LRCX', 'ADSK', 'ROST', 'MNST',
              'MSFT', 'ADBE', 'FAST', 'EA', 'CSCO', 'REGN', 'IDXX', 'VRTX', 'BIIB', 'ODFL', 'QCOM', 'GILD', 'SNPS',
              'SBUX', 'SIRI', 'INTU', 'MCHP', 'ORLY', 'DLTR', 'ASML', 'ANSS', 'TTWO', 'CTSH', 'CSGP', 'NVDA', 'BKNG',
              'ON', 'ISRG', 'MRVL', 'ILMN', 'ADI', 'AEP', 'AMD', 'CDNS', 'CSX', 'HON',
              'MU', 'XEL', 'EXC', 'PEP', 'ROP', 'TXN', 'WBA', 'MDLZ', 'NFLX', 'GOOGL', 'DXCM', 'TMUS', 'MELI', 'AVGO',
              'VRSK', 'FTNT', 'CHTR', 'TSLA', 'NXPI', 'SPLK', 'FANG', 'META', 'PANW', 'WDAY', 'CDW', 'GOOG', 'PYPL',
              'KHC', 'TEAM', 'CCEP', 'BKR', 'MDB', 'ZS', 'PDD', 'MRNA', 'CRWD', 'DDOG', 'AZN', 'LULU', 'CEG', 'GFS',
              'ABNB', 'DASH', 'WBD', 'COST', 'KDP', 'TTD', 'ADP', 'MAR', 'AMZN', 'AMAT', 'GEHC']

# Run through all stocks
for stock_code in stock_list:
    # Download the stock data
    df = yf.download(stock_code, period='6mo', interval='60m', auto_adjust=True, prepost=True, progress=False)
    df_agg = df.groupby(pd.Grouper(freq='4h')).agg({"Open": "first", "High": "max", "Low": "min", "Close": "last"})
    # Remove the NaN rows
    df_final = df_agg.dropna(how='all')
    # Label the dataframe columns
    df_final.columns = ["Open", "High", "Low", "Close"]
    # Calculate the MACD
    c_macd = MACD(close=df_final['Close'], window_fast=12, window_slow=26, window_sign=9)
    # Add it to final df
    df_final['macd_line'] = c_macd.macd()
    df_final['macd_signal'] = c_macd.macd_signal()
    df_final.dropna(inplace=True)


    def condition(row):
        if row['macd_line'] > row['macd_signal']:
            return "Buy"
        elif row['macd_line'] < row['macd_signal']:
            return "Sell"
        else:
            return "Not Sure"


    df_final['signal'] = df_final.apply(condition, axis=1)

    if df_final.iloc[-1].signal == "Buy" and df_final.iloc[-2].signal == "Sell":
        macd_buy_list.append(stock_code)
    elif df_final.iloc[-1].signal == "Sell" and df_final.iloc[-2].signal == "Buy":
        macd_sell_list.append(stock_code)

print("stocks in buy condition", macd_buy_list)
print("stocks in sell condition", macd_sell_list)
