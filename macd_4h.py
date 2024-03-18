import pandas as pd
from ta.trend import MACD
import warnings

warnings.filterwarnings("ignore")


def macd_run(df):
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
        return "Buy"
    elif df_final.iloc[-1].signal == "Sell" and df_final.iloc[-2].signal == "Buy":
        return "Sell"
    else: return "NA"
