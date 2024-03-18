import yfinance as yf
import numpy as np
from macd_4h import macd_run


def run_code(stock_list):
    out_squeeze_long = []
    out_squeeze_short = []
    macd_buy = []
    macd_sell = []
    for stock_code in stock_list:
        # get stock prices
        df = yf.download(stock_code, period="1mo", interval="1h", threads=False, prepost=True, progress=False)
        result = macd_run(df)
        if result == "Buy":
            macd_buy.append(stock_code)
        elif result == "Sell":
            macd_sell.append(stock_code)
        # parameter setup
        length = 20
        mult = 2
        length_KC = 20
        mult_KC = 1.5

        # calculate BB
        m_avg = df["Close"].rolling(window=length).mean()
        m_std = df["Close"].rolling(window=length).std(ddof=0)
        df["upper_BB"] = m_avg + mult * m_std
        df["lower_BB"] = m_avg - mult * m_std

        # calculate true range
        df["tr0"] = abs(df["High"] - df["Low"])
        df["tr1"] = abs(df["High"] - df["Close"].shift())
        df["tr2"] = abs(df["Low"] - df["Close"].shift())
        df["tr"] = df[["tr0", "tr1", "tr2"]].max(axis=1)

        # calculate KC
        range_ma = df["tr"].rolling(window=length_KC).mean()
        df["upper_KC"] = m_avg + range_ma * mult_KC
        df["lower_KC"] = m_avg - range_ma * mult_KC

        # calculate bar value
        highest = df["High"].rolling(window=length_KC).max()
        lowest = df["Low"].rolling(window=length_KC).min()
        m1 = (highest + lowest) / 2
        df["value"] = df["Close"] - (m1 + m_avg) / 2
        fit_y = np.array(range(0, length_KC))
        df["value"] = (
            df["value"]
            .rolling(window=length_KC)
            .apply(
                lambda x: np.polyfit(fit_y, x, 1)[0] * (length_KC - 1)
                          + np.polyfit(fit_y, x, 1)[1],
                raw=True,
            )
        )

        # check for 'squeeze'
        df["squeeze_on"] = (df["lower_BB"] > df["lower_KC"]) & (df["upper_BB"] < df["upper_KC"])
        df["squeeze_off"] = (df["lower_BB"] < df["lower_KC"]) & (df["upper_BB"] > df["upper_KC"])

        # buying window for long position:
        # 1. black cross becomes gray (the squeeze is released)
        long_cond1 = (~df["squeeze_off"].iloc[-2]) & df["squeeze_off"].iloc[-1]
        # 2. bar value is positive => the bar is light green k
        long_cond2 = df["value"].iloc[-1] > 0
        enter_long = long_cond1 & long_cond2
        if enter_long:
            out_squeeze_long.append(stock_code)

        # buying window for short position:
        # 1. black cross becomes gray (the squeeze is released)
        short_cond1 = (~df["squeeze_off"].iloc[-2]) & df["squeeze_off"].iloc[-1]
        # 2. bar value is negative => the bar is light red
        short_cond2 = df["value"].iloc[-1] < 0
        enter_short = short_cond1 & short_cond2
        if enter_short:
            out_squeeze_short.append(stock_code)
    return out_squeeze_long, out_squeeze_short, macd_buy, macd_sell
