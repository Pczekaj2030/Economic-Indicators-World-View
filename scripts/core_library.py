# Part 1: Core Library Imports and Custom Analytics Functions
import datetime
import os
import re
import shutil
import sys
import textwrap
import time
import warnings
xml_etree_ET = __import__("xml.etree.ElementTree", fromlist=["ET"])

import fredapi
from fredapi import Fred
import matplotlib.pyplot as plt
import nltk
from nltk.tokenize import sent_tokenize
import numpy as np
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import psutil
import requests
import requests as r
from bs4 import BeautifulSoup
from scipy.cluster import hierarchy
from scipy.signal import savgol_filter
from scipy.stats import pearsonr, zscore
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from tqdm import tqdm
from urllib.request import Request, urlopen
from yahoo_fin import stock_info as si
import yfinance as yf

from datetime import timedelta, date
from dotenv import load_dotenv
from io import BytesIO
from IPython.core.pylabtools import figsize
from IPython.display import display, HTML
import wget

# Load environment variables securely from a local .env file
load_dotenv()
API_KEY_gov = os.getenv("API_KEY_gov")
k = os.getenv("k")
fred_key = os.getenv("api_key_fred")
API_KEY = os.getenv("API_KEY")

# Initialize API clients safely
fred = Fred(api_key=fred_key) if fred_key else None

# Load reference files using secure relative paths in the data/ folder
correlation_df = pd.read_parquet("data/correlation_by_ticker.parquet")
top_corr = pd.read_parquet("data/ticker_vs_usa_correlation.parquet")
path = "data/USA DATA GOOGLE.xlsx"
path_dist = "data/Distribution.csv"
path_spreads = "data/Spread Distribution.csv"

top_corr = top_corr[[col for col in top_corr.columns if 'close' not in col.lower().strip()]]
df = top_corr.reset_index()
long_corr = df.melt(id_vars='Ticker', var_name='Indicator', value_name='Correlation')

BASE_URL = "https://financialmodelingprep.com/api/v3/"
CONGRESS = 119

def get_bill_description(bill_input):
    bill_input = str(bill_input).strip().lower()
    if bill_input.startswith('s'):
        bill_type = "s"
        bill_number = re.sub(r'\D', '', bill_input)
    else:
        bill_type = "hr"
        bill_number = re.sub(r'\D', '', bill_input)

    url = f"https://api.congress.gov/v3/bill/{CONGRESS}/{bill_type}/{bill_number}/summaries?api_key={API_KEY_gov}&format=json"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            summaries = data.get('summaries', [])
            if summaries:
                raw_text = summaries[-1].get('text', 'No text available.')
                return re.sub('<[^<]+?>', '', raw_text)
            else:
                return f"Summary for {bill_type.upper()} {bill_number} is pending in the API."
        else:
            return f"API Error {response.status_code} for {bill_type.upper()} {bill_number}."
    except Exception as e:
        return f"Request failed: {str(e)}"

def get_index_constituents_fmp(index: str, api_key: str) -> pd.DataFrame:
    endpoints = {
        "sp500": "sp500_constituent",
        "dowjones": "dowjones_constituent",
        "nasdaq": "nasdaq_constituent",
    }
    if index not in endpoints:
        raise ValueError(f"Unsupported index: {index}. Choose from {list(endpoints.keys())}")

    url = f"https://financialmodelingprep.com/api/v3/{endpoints[index]}?apikey={api_key}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data)
    if df.empty:
        return df

    cols = [c for c in ['symbol','name','sector','subSector','headQuarter','dateFirstAdded','cik'] if c in df.columns]
    return df[cols]

def breadth_above_mas(tickers: list[str], hist_start_date: str, today: str, index_symbol: str) -> pd.DataFrame:
    if not tickers:
        raise ValueError("Empty tickers list.")

    px = yf.download(tickers, start=hist_start_date, end=today, group_by='ticker')['Close']
    if isinstance(px, pd.Series):
        px = px.to_frame()

    ma50  = px.rolling(50, min_periods=1).mean()
    ma200 = px.rolling(200, min_periods=1).mean()

    above50  = (px > ma50).astype(int)
    above200 = (px > ma200).astype(int)

    n_members = len([c for c in px.columns if isinstance(c, str)])

    pct_above50  = (above50.sum(axis=1)  / n_members * 100).round(2)
    pct_above200 = (above200.sum(axis=1) / n_members * 100).round(2)

    idx_close = yf.download(index_symbol, start=hist_start_date, end=today)['Close'].rename('Index Close')

    out = pd.concat(
        [idx_close, pct_above50.rename('Above 50'), pct_above200.rename('Above 200')],
        axis=1
    ).dropna()

    out['Spread'] = (out['Above 50'] / out['Above 200']).replace([pd.NA, pd.NaT, pd.inf], pd.NA).astype(float).round(2)
    out = out.sort_index(ascending=False)
    return out

def add_yield_curve_slope_to_usa(usa, usa_yield_curve_monthly):
    maturities = {
        'USA 1M Note': 1/12, 'USA 3M Note': 0.25, 'USA 6M Note': 0.5,
        'USA 1Y Note': 1, 'USA 2Y Note': 2, 'USA 3Y Note': 3,
        'USA 5Y Note': 5, 'USA 7Y Note': 7, 'USA 10Y Note': 10,
        'USA 20Y Note': 20, 'USA 30Y Note': 30
    }

    cols_present = [col for col in maturities if col in usa_yield_curve_monthly.columns]
    x = np.array([maturities[col] for col in cols_present]).reshape(-1, 1)

    slopes = []
    for _, row in usa_yield_curve_monthly.iterrows():
        y = row[cols_present].values.astype(float)
        if np.isnan(y).any():
            slopes.append(np.nan)
            continue
        model = LinearRegression().fit(x, y)
        slopes.append(model.coef_[0])

    usa_yield_curve_monthly = usa_yield_curve_monthly.copy()
    usa_yield_curve_monthly['Yield_Curve_Slope'] = slopes

    usa = usa.merge(
        usa_yield_curve_monthly[['Yield_Curve_Slope']],
        left_index=True, right_index=True, how='left'
    )
    return usa

def plot_usa_indicators(df, columns, from_year=None, title="Selected USA Indicators"):
    if from_year is not None:
        df = df[df.index >= pd.to_datetime(f"{from_year}-01-01")]

    fig = go.Figure()
    for col in columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df[col], mode='lines', name=col,
            hovertemplate=f"%{{x}}<br>{col}: %{{y:.2f}}<extra></extra>"
        ))
    fig.update_layout(
        title=title, height=1000, template="plotly_dark",
        margin=dict(l=20, r=20, t=60, b=40),
        yaxis=dict(title="Indicator Value")
    )
    fig.show()

# Global runtime definitions
url = 'https://www.slickcharts.com/sp500'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
hist_start_date = '2000-01-01'
warnings.simplefilter("ignore")

memory_info = psutil.virtual_memory()
memory_usage_mb = memory_info.used / (1024 * 1024)

today = datetime.date.today()
this_year = today.year
this_month = today.month
next_month = this_month + 1

if next_month == 13:
    next_year = this_year + 1
    next_month_date = f'{next_year}-01-01'
else:
    next_month_date = f'{this_year}-{next_month}-01'

last_monday = today - datetime.timedelta(days=today.weekday())
current_week_start = str(last_monday)
current_year_start = f'{this_year}-01-01'
current_year_end = str(today)
current_month_date = f'{this_year}-{this_month}-01'

if this_month in range(1, 4):
    quarter_start, quarter_end = f'{this_year}-01-01', f'{this_year}-03-31'
elif this_month in range(4, 7):
    quarter_start, quarter_end = f'{this_year}-04-01', f'{this_year}-06-30'
elif this_month in range(7, 10):
    quarter_start, quarter_end = f'{this_year}-07-01', f'{this_year}-09-30'
else:
    quarter_start, quarter_end = f'{this_year}-10-01', f'{this_year}-12-31'

func = lambda s: 'STRING' if isinstance(s, str) else 'FLOAT'
plt.style.use("ggplot")
pd.set_option("display.precision", 3)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

target_cumulative_probability = 25

def breadth(df, index_name, title):
    column = df.columns[0]
    trace1 = go.Scatter(x=df.index, y=df[column], yaxis="y1", line={'color': 'gainsboro'}, name=f'{index_name}')
    trace2 = go.Scatter(x=df.index, y=df['Above 50'], yaxis="y2", line={'color': '#fb8b1e'}, name='Stocks Above 50')
    trace3 = go.Scatter(x=df.index, y=df['Above 200'], yaxis="y3", line={'color': '#a02837'}, name='Stocks Above 200')

    data = [trace1, trace2, trace3]
    layout = go.Layout(
        yaxis3=dict(domain=[0, 0.25]),
        legend=dict(traceorder="normal"),
        yaxis=dict(domain=[0.5, 1]),
        yaxis2=dict(domain=[0.25, 0.5]),
        height=1000,
        template='plotly_dark',
        title=f'{title}'
    )

    fig = go.Figure(data=data, layout=layout)
    fig.update_layout(yaxis={'side': 'right'}, yaxis2={'side': 'right'}, yaxis3={'side': 'right'})
    return fig.show()

def eps_q(api_key, stock):
    assert stock is not None
    stock = stock.strip().upper()
    url = f"{BASE_URL}function=EARNINGS&symbol={stock}&apikey={api_key}"
    item = r.get(url)
    data = item.json()
    return pd.json_normalize(data['quarterlyEarnings'])

def px_eps_chart(stock, time):
    stock_returns = pd.DataFrame(yf.download(f'{stock}', period='max', interval='1mo')['Close'])
    stock_returns['Q on Q'] = stock_returns.pct_change(1).round(2)
    long = pd.DataFrame(yf.download(stock, period='max', interval='1mo')['Adj Close'])
    long.rename(columns={'Adj Close': f'{stock} Close'}, inplace=True)
    long[f'{stock} Returns'] = long.pct_change(1).round(2)
    long[f'{stock} Y on Y'] = long[f'{stock} Close'].pct_change(12).round(2)
    long_quarter = long[f'{stock} Close'].to_frame()
    long_quarter.drop(long_quarter.index[long_quarter.index.month.isin([1, 2, 4, 5, 7, 8, 10, 11])], inplace=True)
    long_quarter[f'{stock} Returns'] = long_quarter.pct_change(1).round(2)
    
    ticker_q = eps_q(k, stock)
    ticker_q.rename(columns={'fiscalDateEnding': 'Fiscal Ending', 'reportedDate': 'Report Date', 'reportedEPS': 'Reported Eps', 'estimatedEPS': 'Estimated Eps', 'surprise': 'Suprise', 'surprisePercentage': 'Suprise pct'}, inplace=True)
    ticker_q.replace('None', 0, inplace=True)
    
    reported_eps = ticker_q[['Fiscal Ending', 'Reported Eps']].copy()
    reported_eps.index.name = f'{stock}'
    reported_eps = reported_eps.astype({'Reported Eps': 'float'})
    reported_eps['Q on Q'] = reported_eps['Reported Eps'].pct_change(periods=-1).round(2)
    reported_eps['Y on Y'] = reported_eps['Reported Eps'].pct_change(periods=-4).round(2)
    reported_eps.sort_index(ascending=False, inplace=True)
    reported_eps.reset_index(inplace=True)
    reported_eps.index = reported_eps['Fiscal Ending']
    reported_eps.drop(columns=['Fiscal Ending', f'{stock}'], inplace=True)
    
    reported_eps.index = pd.to_datetime(reported_eps.index)
    result = reported_eps.groupby(reported_eps.index.month).mean()
    result.sort_values(by=['Reported Eps'], ascending=False, inplace=True)
    
    new_df = reported_eps.loc[f'{time}':]
    stock_returns = stock_returns.loc[f'{time}':'2022']
    
    fig_eps = px.bar(new_df, y=new_df['Reported Eps'], text='Reported Eps', title=f'{stock} Reported Eps Quarterly', color="Reported Eps", height=500, template='plotly_dark')
    fig_q = px.bar(new_df, y=new_df['Reported Eps'], text='Q on Q', title=f'{stock} Percentage Q on Q Eps ', color="Reported Eps", height=500, template='plotly_dark')
    fig_y = px.bar(new_df, y=new_df['Reported Eps'], text='Y on Y', title=f'{stock} Percentage Y on Y  Quarterly Eps ', color="Reported Eps", height=500, template='plotly_dark')
    fig_returns = px.bar(long_quarter, y=long_quarter[f'{stock} Returns'], text=f'{stock} Returns', title=f'{stock} Stock Price Returns', color=f'{stock} Returns', height=500, template='plotly_dark')
    
    fig_returns.update_traces(marker_color='#298f2b', textposition='outside')
    fig_returns.update_layout(xaxis={'side': 'bottom'}, yaxis={'side': 'right'})
    
    return fig_returns.show(), fig_eps.show(), display(result)

try:
    from scipy.signal import savgol_filter
except ImportError:
    savgol_filter = None

def px_chart(
    df, time, indicator, title_name, line_color,
    height=600, top_value=0.2, bottom_value=-0.2,
    annotations_top=None, annotations_bottom=None,
    arrow_offset_x=0, arrow_offset_y=40,
    smooth="No", smooth_window=12, smooth_poly=3,
):
    _df = df[[indicator]].copy()
    _df.index = pd.to_datetime(_df.index)
    _df = _df[~_df.index.isna()]
    
    if _df.index.duplicated().any():
        _df = _df.groupby(_df.index).mean()
        
    _df = _df.sort_index().dropna(how="all")

    plot_col = indicator
    label_suffix = ""

    if smooth == "Yes" and savgol_filter is not None:
        smoothed_col = f"{indicator}_Smoothed"
        s = pd.to_numeric(_df[indicator], errors="coerce")
        clean_s = s.interpolate(method='linear').ffill().bfill()
        
        n = clean_s.shape[0]
        if n >= 7:
            w = min(smooth_window, n if n % 2 == 1 else n - 1)
            w = max(5, w if w % 2 == 1 else w - 1)
            _df[smoothed_col] = savgol_filter(clean_s, window_length=w, polyorder=min(smooth_poly, w-2))
            plot_col = smoothed_col
            label_suffix = " (Smoothed)"

    try:
        plot_slice = _df.loc[str(time):, [plot_col]].dropna()
    except Exception:
        plot_slice = _df[[plot_col]].dropna()

    fig = px.line(
        plot_slice, x=plot_slice.index, y=plot_col,
        title=f"<b>{title_name}</b>{label_suffix}", 
        height=height, template="plotly_dark",
    )
    
    fig.update_traces(line_color=line_color, line_width=2.5)
    fig.update_layout(
        xaxis_title="", yaxis={"side": "right", "title": ""},
        margin=dict(l=10, r=10, t=50, b=10), hovermode="x unified"
    )
    
    fig.add_hline(y=top_value, line_dash="dash", line_color="red", opacity=0.4)
    fig.add_hline(y=bottom_value, line_dash="dash", line_color="green", opacity=0.4)

    def _apply_annos(annos, color_bg, direction):
        if not annos: return
        for x, text in annos:
            try:
                ts = pd.to_datetime(x)
                if ts in _df.index:
                    val = _df.at[ts, plot_col]
                    fig.add_annotation(
                        x=ts, y=val, text=text, showarrow=True, arrowhead=2,
                        ax=arrow_offset_x, ay=-arrow_offset_y if direction=="top" else arrow_offset_y,
                        bgcolor=color_bg, font=dict(color="white", size=12),
                        borderpad=4, bordercolor="rgba(255,255,255,0.3)"
                    )
            except: continue

    _apply_annos(annotations_top, "rgba(200, 50, 50, 0.7)", "top")
    _apply_annos(annotations_bottom, "rgba(50, 150, 50, 0.7)", "bottom")

    series_24 = plot_slice[plot_col].tail(24)
    if not series_24.empty:
        table_label = f"{indicator}{label_suffix}"
        cols = series_24.index.strftime('%Y-%m-%d')
        section = pd.DataFrame([series_24.values], index=[table_label], columns=cols)
        
        if section.columns.duplicated().any():
            section = section.loc[:, ~section.columns.duplicated()]

        styled = section.style.background_gradient(axis=1, cmap="PiYG").format("{:.2f}")
        display(fig)
        display(styled)
    else:
        display(fig)

    return None

def px_chart_bar(df, time, indicator, title_name, line_color):
    score = len(df) - 24
    table = df.sort_index(ascending=True, inplace=True)
    table_tr = df.iloc[score:].T
    section = table_tr.loc[[indicator]]

    fig = px.bar(df.loc[f'{time}':], x=df.loc[f'{time}':].index, y=indicator, title=title_name, height=500, template='plotly_dark')
    fig.update_traces(marker_color=f'{line_color}')
    fig.update_layout(xaxis_title="Date", xaxis={'side': 'bottom'}, yaxis={'side': 'right'})
    return fig.show(), display(section.style.background_gradient(axis=None, cmap='PiYG').format({0: '{:.2%}', 2: func}, precision=2, na_rep=''))

def px_chart_bar_visual(df, time, indicator, title_name, line_color, column_name, height=800):
    score = len(df) - 24
    table = df.sort_index(ascending=True, inplace=True)
    table_tr = df.iloc[score:].T
    section = table_tr.loc[[indicator]]

    fig = px.bar(df.loc[f'{time}':], x=df.loc[f'{time}':].index, y=indicator, text=f'{column_name}', title=title_name, height=height, template='plotly_dark')
    fig.update_traces(marker_color=f'{line_color}', textposition='outside')
    fig.update_layout(xaxis_title="Date", xaxis={'side': 'bottom'}, yaxis={'side': 'right'})
    return fig.show(), display(section.style.background_gradient(axis=None, cmap='PiYG').format({0: '{:.2%}', 2: func}, precision=2, na_rep=''))

def px_chart_neg(df, time, indicator, title_name, line_color):
    score = len(df) - 24
    table = df.sort_index(ascending=True, inplace=True)
    table_tr = df.iloc[score:].T
    section = table_tr.loc[[indicator]]

    fig = px.line(df.loc[f'{time}':], x=df.loc[f'{time}':].index, y=indicator, title=title_name, height=500, template='plotly_dark')
    fig.update_traces(line_color=f'{line_color}')
    fig.update_layout(xaxis_title="Date", xaxis={'side': 'bottom'}, yaxis={'side': 'right'})
    return fig.show(), display(section.style.background_gradient(axis=None, cmap='PiYG_r').format({0: '{:.2%}', 2: func}, precision=2, na_rep=''))

def px_chart_bar_neg(df, time, indicator, title_name, line_color):
    score = len(df) - 24
    table = df.sort_index(ascending=True, inplace=True)
    table_tr = df.iloc[score:].T
    section = table_tr.loc[[indicator]]

    fig = px.bar(df.loc[f'{time}':], x=df.loc[f'{time}':].index, y=indicator, title=title_name, height=500, template='plotly_dark')
    fig.update_traces(marker_color=f'{line_color}')
    fig.update_layout(xaxis_title="Date", xaxis={'side': 'bottom'}, yaxis={'side': 'right'})
    return fig.show(), display(section.style.background_gradient(axis=None, cmap='PiYG_r').format({0: '{:.2%}', 2: func}, precision=2, na_rep=''))

def px_chart_bar_visual_neg(df, time, indicator, title_name, line_color, column_name):
    score = len(df) - 24
    table = df.sort_index(ascending=True, inplace=True)
    table_tr = df.iloc[score:].T
    section = table_tr.loc[[indicator]]

    fig = px.bar(df.loc[f'{time}':], x=df.loc[f'{time}':].index, y=indicator, text=f'{column_name}', title=title_name, height=500, template='plotly_dark')
    fig.update_traces(marker_color=f'{line_color}', textposition='outside')
    fig.update_layout(xaxis_title="Date", xaxis={'side': 'bottom'}, yaxis={'side': 'right'})
    return fig.show(), display(section.style.background_gradient(axis=None, cmap='PiYG_r').format({0: '{:.2%}', 2: func}, precision=2, na_rep=''))

def retuns(table):
    table["Returns"] = (table['Close'] - table['Open']) / table['Open']

def color_negative_red(val):
    color = 'green' if val > 0 else 'red'
    return f'color: {color}'

def formatting(data, name, freq_):
    freq = freq_ * (-1)
    df = pd.DataFrame(data)
    df.rename(columns={0: f'{name}'}, inplace=True)
    data.rename(columns={0: f'{name}'}, inplace=True)
    df.sort_index(ascending=False, inplace=True)
    df[f'{name} pct'] = df[f'{name}'].pct_change(-1)
    df[f'{name} YonY'] = df[f'{name}'].pct_change(freq)
    mean = df[f'{name} pct'].mean()
    
    df.index.names = ['Date']
    df['Date'] = pd.to_datetime(df.index)
    df['Date'] = df['Date'].dt.to_period('D')
    df.set_index(df['Date'], drop=True, inplace=True)
    df.drop(columns=['Date'], inplace=True)
    df.sort_index(ascending=False, inplace=True)
    data = df.T
    one_y = data.iloc[0:1, [0, 1, 2, 4, 5, 6, 7, 8, 9]]
    
    indicators = pd.concat([one_y.reset_index(drop=True)], axis=1)
    indicators.index = [f'{name}']
    return indicators

def formatting_pct(data, name, freq_):
    freq = freq_ * (-1)
    df = pd.DataFrame(data)
    df.rename(columns={0: f'{name}'}, inplace=True)
    data.rename(columns={0: f'{name}'}, inplace=True)
    df.sort_index(ascending=False, inplace=True)
    df[f'{name} pct'] = df[f'{name}'].pct_change(-1)
    df[f'{name} YonY'] = df[f'{name}'].pct_change(freq)
    mean = df[f'{name} pct'].mean()
    df_series_mean = pd.DataFrame({'Series Ave': [mean]})

    df.index.names = ['Date']
    df['Date'] = pd.to_datetime(df.index)
    df['Date'] = df['Date'].dt.to_period('D')
    df.set_index(df['Date'], drop=True, inplace=True)
    df.drop(columns=['Date'], inplace=True)
    data = df.T
    one_y = data.iloc[2:3, [0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12]]

    indicators = pd.concat([df_series_mean, one_y.reset_index(drop=True)], axis=1)
    indicators.index = [f'{name}']
    return indicators

def chances(prob, pct_description, value):
    prob.drop(['Bin Values1', 'Frequency', 'Probabilities %'], axis=1, inplace=True)
    prob.insert(0, "Bin Values", pct_description, True)
    sorted_cum = prob.loc[prob['Probability'] <= value]
    df_prob_part = pd.DataFrame(sorted_cum.sort_values(by=['Probability'], ascending=False))
    df_prob_part.reset_index(drop=True, inplace=True)
    return df_prob_part.iloc[0:1]

def describe(df):
    df_mean = pd.DataFrame(df.describe())
    df_mean_t = df_mean.T
    df_mean_t.rename(columns={"std": "Std", "min": "Min", "max": "Max"}, inplace=True)
    df_mean_t.rename(index={'Returns': 0}, inplace=True)
    return (df_mean_t[['Std', 'Min', 'Max']] * 100).round(2)

def avgreturn(df):
    pos_sorted_values, neg_sorted_values = [], []
    for value in df:
        if value > 0:
            pos_sorted_values.append(value)
        elif value < 0:
            neg_sorted_values.append(value)
            
    neg_returns = pd.DataFrame(neg_sorted_values)
    neg_mean = neg_returns[0].mean() if not neg_returns.empty else 0
    
    pos_returns = pd.DataFrame(pos_sorted_values)
    pos_mean = pos_returns[0].mean() if not pos_returns.empty else 0
    
    return pos_mean, neg_mean

def dist_chart(df, b):
    count, b_e = np.histogram(df, b)
    df.plot(kind='hist', figsize=(18, 6), bins=b, edgecolor='white', alpha=0.6, xticks=b_e, color=['darkblue'])
    current_values = plt.gca().get_xticks()
    plt.gca().set_xticklabels(['{:,.0%}'.format(x) for x in current_values])
    plt.grid(color='grey', linestyle='-', linewidth=0.25)

def diff(df, df_daily_open):
    last_period_close = df[0]
    current_price = df_daily_open[0]
    df_pct_diff = (current_price - last_period_close) / last_period_close
    return pd.DataFrame([df_pct_diff])

def cumprob(df, bins):
    categories = pd.cut(df['Returns'], bins)
    value_count = pd.DataFrame(pd.value_counts(categories))
    value_count.reset_index(inplace=True)
    value_count.rename(columns={'index': 'Bin Values1', 'Returns': 'Frequency'}, inplace=True)
    value_count.sort_values(by='Bin Values1', ascending=True, inplace=True)
    value_count['Probabilities %'] = (value_count['Frequency'] / len(df['Returns'])).round(5)
    value_count['Probability'] = (100 * (value_count['Frequency'].cumsum() / value_count['Frequency'].sum())).round(2)
    return value_count

def current_spread_real(l_daily, s_daily, df, df2, period):
    l_daily.sort_index(ascending=False, inplace=True)
    s_daily.sort_index(ascending=False, inplace=True)
    current_price = l_daily['Close'].iloc[0] / s_daily['Close'].iloc[0]
    last_period_close = df['Open'].iloc[0] / df2['Open'].iloc[0]
    df_pct_diff = (current_price - last_period_close) / last_period_close
    df_pct_diff_str = f"{df_pct_diff:.2%}"
    res_df = pd.DataFrame([df_pct_diff_str])
    res_df.rename(columns={0: f'{period}'}, inplace=True)
    return res_df

def find_element_in_list(element):
    df_dist = pd.read_csv(path_dist)
    df_dist.rename(columns={'Unnamed: 0': 'Asset'}, inplace=True)
    df_dist.set_index('Asset', inplace=True)
    try:
        return df_dist.loc[[element]]
    except KeyError:
        return None

def spread_fetch_or_new(element):
    spreads_hist = pd.read_csv(path_spreads)
    spreads_hist.rename(columns={'Unnamed: 0': 'Asset'}, inplace=True)
    spreads_hist.set_index('Asset', inplace=True)
    try:
        return spreads_hist.loc[[element]]
    except KeyError:
        return None

def spread_hist_distribution_fresh(name):
    x = name.split("/", 1)
    long, short = x[0], x[1]

    long_daily = yf.download(long, start="1990-01-01", interval='1d')
    short_daily = yf.download(short, start="1990-01-01", interval='1d')
    long_weekly = yf.download(long, start="1990-01-01", interval='1wk')
    short_weekly = yf.download(short, start="1990-01-01", interval='1wk')
    long_monthly = yf.download(long, start="1990-01-01", interval='1mo')
    short_monthly = yf.download(short, start="1990-01-01", interval='1mo')

    long_close_daily = long_daily.xs('Close', axis=1, level=0)[long]
    short_close_daily = short_daily.xs('Close', axis=1, level=0)[short]
    long_close_weekly = long_weekly.xs('Close', axis=1, level=0)[long]
    short_close_weekly = short_weekly.xs('Close', axis=1, level=0)[short]
    long_close_monthly = long_monthly.xs('Close', axis=1, level=0)[long]
    short_close_monthly = short_monthly.xs('Close', axis=1, level=0)[short]

    spread_daily = long_close_daily / short_close_daily
    spread_weekly = long_close_weekly / short_close_weekly
    spread_monthly = long_close_monthly / short_close_monthly

    df_spread_daily = pd.DataFrame(spread_daily, columns=[name])
    df_spread_weekly = pd.DataFrame(spread_weekly, columns=[name])
    df_spread_monthly = pd.DataFrame(spread_monthly, columns=[name])

    df_spread_daily['Returns'] = df_spread_daily[name].pct_change(1)
    df_spread_weekly['Returns'] = df_spread_weekly[name].pct_change(1)
    df_spread_monthly['Returns'] = df_spread_monthly[name].pct_change(1)

    daily_avg = avgreturn(df_spread_daily['Returns'])
    weekly_avg = avgreturn(df_spread_weekly['Returns'])
    monthly_avg = avgreturn(df_spread_monthly['Returns'])

    spread_daily_stats = pd.DataFrame({'Daily Pos': [f"{daily_avg[0]:.2%}"], 'Daily Neg': [f"{daily_avg[1]:.2%}"]})
    spread_weekly_stats = pd.DataFrame({'Weekly Pos': [f"{weekly_avg[0]:.2%}"], 'Weekly Neg': [f"{weekly_avg[1]:.2%}"]})
    spread_monthly_stats = pd.DataFrame({'Monthly Pos': [f"{monthly_avg[0]:.2%}"], 'Monthly Neg': [f"{monthly_avg[1]:.2%}"]})

    spread_quarterly = spread_monthly.resample('BQS', label='right').last()
    spread_quarterly_df = pd.DataFrame(spread_quarterly, columns=[name])
    spread_quarterly_df['Returns'] = spread_quarterly_df[name].pct_change(1)
    quarterly_avg = avgreturn(spread_quarterly_df['Returns'])
    spread_quarterly_stats = pd.DataFrame({'Quarterly Pos': [f"{quarterly_avg[0]:.2%}"], 'Quarterly Neg': [f"{quarterly_avg[1]:.2%}"]})

    spread_stats = pd.concat([spread_daily_stats, spread_weekly_stats, spread_monthly_stats, spread_quarterly_stats], axis=1)
    spread_stats.index = [name]
    return spread_stats

def spread_now_chart(name, start_date=None):
    x = name.split("/", 1)
    long_name, short_name = x[0], x[1]

    start = start_date if start_date else "2000-01-01"
    long = yf.download(long_name, start=start, interval='1d')
    short = yf.download(short_name, start=start, interval='1d')

    long_close = long.xs('Close', axis=1, level=0)[long_name]
    short_close = short.xs('Close', axis=1, level=0)[short_name]

    spread_ = long_close / short_close
    plot_spread = pd.DataFrame(spread_, columns=[name])

    plot_spread['Returns'] = plot_spread[name].pct_change(1)
    plot_spread['AVG 20'] = plot_spread[name].rolling(window=20).mean()
    plot_spread['AVG 60'] = plot_spread[name].rolling(window=60).mean()
    plot_spread['AVG 252'] = plot_spread[name].rolling(window=252).mean()

    ytd = plot_spread['Returns'][f'{current_year_start}':].cumsum().iloc[-1]
    quarter = plot_spread['Returns'][f'{quarter_start}':].cumsum().iloc[-1]
    monthly = plot_spread['Returns'][f'{current_month_date}':].cumsum().iloc[-1]

    if last_monday == today:
        weekly = pd.DataFrame([0], columns=['Weekly'], index=[name])
    else:
        w_val = plot_spread['Returns'][f'{current_week_start}':].cumsum().iloc[-1]
        weekly = pd.DataFrame([w_val], columns=['Weekly'], index=[name])

    ytd_df = pd.DataFrame([ytd], columns=['Y to Date'], index=[name])
    quarter_df = pd.DataFrame([quarter], columns=['Quarter'], index=[name])
    monthly_df = pd.DataFrame([monthly], columns=['Monthly'], index=[name])

    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, subplot_titles=(f'{name} from {start}',), row_heights=[1], vertical_spacing=0.01)
    fig.add_trace(go.Scatter(x=plot_spread.index, y=plot_spread[name], mode='lines', name='Spread', line=dict(color='firebrick')), row=1, col=1)
    fig.add_trace(go.Scatter(x=plot_spread.index, y=plot_spread['AVG 20'], mode='lines', name='AVG 20', line=dict(color='lightblue')), row=1, col=1)
    fig.add_trace(go.Scatter(x=plot_spread.index, y=plot_spread['AVG 60'], mode='lines', name='AVG 60', line=dict(color='lightslategrey')), row=1, col=1)
    fig.add_trace(go.Scatter(x=plot_spread.index, y=plot_spread['AVG 252'], mode='lines', name='AVG 252', line=dict(color='coral')), row=1, col=1)
    
    fig.update_layout(height=1100, template='plotly_dark', legend_title="Legend", margin=dict(l=40, r=40, t=40, b=40))
    fig.update_yaxes(title_text="Spread", row=1, col=1, showgrid=True)
    
    spread_dist = spread_hist_distribution_fresh(name)
    stock_stats = pd.concat([ytd_df['Y to Date'], spread_dist['Quarterly Pos'], quarter_df['Quarter'], spread_dist['Quarterly Neg'], spread_dist['Monthly Pos'], monthly_df['Monthly'], spread_dist['Monthly Neg'], spread_dist['Weekly Pos'], weekly['Weekly'], spread_dist['Weekly Neg']], axis=1)

    return fig.show(), display(stock_stats.style.background_gradient(axis=1, cmap='PiYG').format('{:.2%}', subset=['Y to Date', 'Quarter', 'Monthly', 'Weekly']))

def y_on_y(target, col_name):
    new_value = pd.DataFrame()
    new_value[f'{col_name} Y on Y'] = target.loc[:, [col_name]].pct_change(12)
    return new_value

def indicator_vs_indicator(indi_1_name, indi_2_name):
    indicator_1_name = indi_1_name.name
    indicator_2_name = indi_2_name.name

    if indi_1_name.index.tz is None and indi_2_name.index.tz is not None:
        indi_1_name.index = indi_1_name.index.tz_localize(indi_2_name.index.tz)
    elif indi_1_name.index.tz is not None and indi_2_name.index.tz is None:
        indi_2_name.index = indi_2_name.index.tz_localize(indi_1_name.index.tz)

    indi_vs_indi = pd.concat([indi_1_name, indi_2_name], axis=1).dropna()
    indi_vs_indi_corr_extra = indi_vs_indi.corr()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=indi_vs_indi.index, y=indi_vs_indi[f'{indicator_1_name}'], name=f'{indicator_1_name} (R2)', line={'color': 'white'}), secondary_y=True)
    fig.add_trace(go.Scatter(x=indi_vs_indi.index, y=indi_vs_indi[f'{indicator_2_name}'], name=f'{indicator_2_name} (L1)', line={'color': '#fb8b1e'}), secondary_y=False)
    
    fig.update_layout(
        title_text=f'{indicator_1_name} vs {indicator_2_name} with correlation score {indi_vs_indi_corr_extra.iloc[0,1].round(3)}',
        font_color="#FFFFFF", height=800, template='plotly_dark'
    )
    fig.update_yaxes(title_text=f'{indicator_1_name} vs {indicator_2_name}', secondary_y=False)
    return fig.show()

def indicator_vs_indicator_future(indi_1_name, indi_2_name):
    indicator_1_name = indi_1_name.name
    indicator_2_name = indi_2_name.name

    if indi_1_name.index.tz is None and indi_2_name.index.tz is not None:
        indi_1_name.index = indi_1_name.index.tz_localize(indi_2_name.index.tz)
    elif indi_1_name.index.tz is not None and indi_2_name.index.tz is None:
        indi_2_name.index = indi_2_name.index.tz_localize(indi_1_name.index.tz)

    indi_vs_indi = pd.concat([indi_1_name, indi_2_name], axis=1)
    allowed_months = [1, 4, 7, 10]
    indi_vs_indi = indi_vs_indi[indi_vs_indi.index.month.isin(allowed_months)]
    indi_vs_indi_corr_extra = indi_vs_indi.corr()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=indi_vs_indi.index, y=indi_vs_indi[f'{indicator_1_name}'], name=f'{indicator_1_name} (R2)', line={'color': 'white'}), secondary_y=True)
    fig.add_trace(go.Scatter(x=indi_vs_indi.index, y=indi_vs_indi[f'{indicator_2_name}'], name=f'{indicator_2_name} (L1)', line={'color': '#fb8b1e'}), secondary_y=False)
    
    fig.update_layout(
        title_text=f'{indicator_1_name} vs {indicator_2_name} with correlation score {indi_vs_indi_corr_extra.iloc[0, 1].round(3)}',
        font_color="#FFFFFF", height=800, template='plotly_dark'
    )
    fig.update_yaxes(title_text=f'{indicator_1_name} vs {indicator_2_name}', secondary_y=False)
    return fig.show()

def indicator_vs_indicator_smoothed_future(indi_1, indi_2):
    if indi_1.index.tzinfo or indi_2.index.tzinfo:
        indi_1.index = indi_1.index.tz_localize(None)
        indi_2.index = indi_2.index.tz_localize(None)

    indicator_1_name = indi_1.name if indi_1.name else "Indicator_1"
    indicator_2_name = indi_2.name if indi_2.name else "Indicator_2"

    indi_vs_indi = pd.concat([indi_1, indi_2], axis=1)
    allowed_months = [1, 4, 7, 10]
    indi_vs_indi = indi_vs_indi[indi_vs_indi.index.month.isin(allowed_months)]
    indi_vs_indi_corr_extra = indi_vs_indi.corr()

    for column in indi_vs_indi.columns:
        smoothed_column_name = column + '_Smoothed'
        if smoothed_column_name not in indi_vs_indi.columns:
            clean_data = indi_vs_indi[column].dropna()
            if len(clean_data) >= 12 and savgol_filter is not None:
                indi_vs_indi.loc[clean_data.index, smoothed_column_name] = savgol_filter(clean_data, window_length=12, polyorder=3)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=indi_vs_indi.index, y=indi_vs_indi[f'{indicator_1_name}_Smoothed'], name=f'{indicator_1_name}_Smoothed (R2)', line={'color': 'white'}), secondary_y=True)
    fig.add_trace(go.Scatter(x=indi_vs_indi.index, y=indi_vs_indi[f'{indicator_2_name}_Smoothed'], name=f'{indicator_2_name}_Smoothed (L1)', line={'color': '#fb8b1e'}), secondary_y=False)
    
    fig.update_layout(
        title_text=f'{indicator_1_name}_Smoothed vs {indicator_2_name}_Smoothed with correlation score {indi_vs_indi_corr_extra.iloc[0,-1].round(2)}',
        font_color="#FFFFFF", height=800, template='plotly_dark'
    )
    fig.update_yaxes(title_text=f'{indicator_1_name} vs {indicator_2_name}', secondary_y=False)
    return fig.show()

def stock_metrics_monthly(ticker, bin_labels_monthly, target_cumulative_probability):
    data = yf.download(ticker, interval='1mo')
    data['Monthly_Return'] = data['Close'].pct_change() * 100
    custom_values = [i * 2.5 for i in range(-12, 13)]
    
    bin_counts, _ = np.histogram(data['Monthly_Return'], bins=custom_values)
    total_occurrences = bin_counts.sum()
    probabilities_monthly = (bin_counts / total_occurrences) * 100
    cumulative_probabilities_monthly = np.cumsum(probabilities_monthly)
    
    df_monthly = pd.DataFrame({
        'Occurrences': bin_counts,
        'Probability (%)': probabilities_monthly.round(2),
        'Cumulative Probability (%)': cumulative_probabilities_monthly.round(2),
    })
    
    df_monthly.index = bin_labels_monthly
    df_monthly.reset_index(inplace=True)
    df_monthly.rename(columns={'index': 'Monthly Range'}, inplace=True)
    
    closest_row = df_monthly[df_monthly['Cumulative Probability (%)'] >= target_cumulative_probability].head(1)
    closest_row.index = pd.Index([ticker], name='')
    
    positive_returns = data[data['Monthly_Return'] > 0]
    ave_positive_return = positive_returns['Monthly_Return'].mean()
    negative_returns = data[data['Monthly_Return'] < 0]
    ave_negative_return = negative_returns['Monthly_Return'].mean()
    
    data['High-Low'] = data['High'] - data['Low']
    data['High-Close'] = np.abs(data['High'] - data['Close'].shift())
    data['Low-Close'] = np.abs(data['Low'] - data['Close'].shift())
    data['TR'] = data[['High-Low', 'High-Close', 'Low-Close']].max(axis=1)
    atr_9_months = data['TR'].rolling(window=9).mean().iloc[-1]
    
    additional_metrics = {
        'Average Neg (%)': ave_negative_return.round(2) if not np.isnan(ave_negative_return) else 0,
        'Average Pos (%)': ave_positive_return.round(2) if not np.isnan(ave_positive_return) else 0,
        'ATR 9 Months (%)': atr_9_months.round(2) if not np.isnan(atr_9_months) else 0
    }
    additional_metrics_df = pd.DataFrame(additional_metrics, index=[ticker])
    
    current_month = pd.Timestamp.now().month
    current_year = pd.Timestamp.now().year
    current_month_data = data[(data.index.month == current_month) & (data.index.year == current_year)]
    
    if current_month_data.empty:
        return None

    open_price = current_month_data['Open'].iloc[0]
    close_price = current_month_data['Close'].iloc[-1]
    monthly_return = (((close_price - open_price) / open_price) * 100).round(2)
    result_df = pd.DataFrame({'Monthly Return (%)': [monthly_return]}, index=[ticker])

    closest_row = pd.concat([
        closest_row['Monthly Range'],
        closest_row['Occurrences'],
        additional_metrics_df['Average Pos (%)'],
        result_df['Monthly Return (%)'],
        additional_metrics_df['Average Neg (%)'],
        additional_metrics_df['ATR 9 Months (%)']
    ], axis=1)
    
    return closest_row

def plot_price_and_returns(ticker, start_date="1900-01-01"):
    df_p = yf.download(ticker, period='max')
    if isinstance(df_p.columns, pd.MultiIndex):
        df_p.columns = ['_'.join(col).strip() for col in df_p.columns.values]
        
    close_col = [col for col in df_p.columns if 'Close' in col][0]
    df_p[f'{ticker} Returns'] = df_p[close_col].pct_change() * 100
    df_p = df_p[[close_col, f'{ticker} Returns']].dropna()
    df_p = df_p[df_p.index >= pd.to_datetime(start_date)]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df_p.index, y=df_p[close_col], name="Close Price", line=dict(color='white'), opacity=0.8), secondary_y=False)
    fig.add_trace(go.Bar(x=df_p[df_p[f'{ticker} Returns'] >= 0].index, y=df_p[df_p[f'{ticker} Returns'] >= 0][f'{ticker} Returns'], name="Positive Return (%)", marker_color='green'), secondary_y=True)
    fig.add_trace(go.Bar(x=df_p[df_p[f'{ticker} Returns'] < 0].index, y=df_p[df_p[f'{ticker} Returns'] < 0][f'{ticker} Returns'], name="Negative Return (%)", marker_color='red'), secondary_y=True)

    fig.update_layout(
        barmode='relative', height=1000, template='plotly_dark',
        title=f"{ticker} – Close Price (left) & Daily Returns (bars, right)",
        margin=dict(l=20, r=20, t=60, b=60), legend=dict(x=1.01, y=1)
    )
    fig.update_yaxes(title_text="Close Price", secondary_y=False)
    fig.update_yaxes(title_text="Daily Return (%)", secondary_y=True)
    fig.show()

def detect_unusual_moves(df_input, columns):
    results = []
    for col in columns:
        series = df_input[col].dropna()
        if len(series) < 2:
            continue
        last_val = series.iloc[-1]
        prev_val = series.iloc[-2]
        pct_change = (last_val - prev_val) / prev_val * 100

        full_pct_change = series.pct_change() * 100
        mean = full_pct_change.mean()
        std = full_pct_change.std()
        z_score = (pct_change - mean) / std if std != 0 else np.nan

        freq_1_std = (full_pct_change.abs() > std).sum()
        freq_2_std = (full_pct_change.abs() > 2 * std).sum()
        freq_3_std = (full_pct_change.abs() > 3 * std).sum()

        if pct_change > 0:
            direction = '🟢 Growing'
        elif pct_change < 0:
            direction = '🔻 Slowing'
        else:
            direction = '⏸️ Flat'

        classification = (
            '⚠️ >3 STD' if abs(z_score) > 3 else
            '🔶 >2 STD' if abs(z_score) > 2 else
            '🔷 >1 STD' if abs(z_score) > 1 else
            '✅ Normal'
        )

        results.append({
            'Indicator': col, 'Classification': classification, 'Direction': direction,
            'Last % Change': pct_change, 'Z Score': z_score, '1 STD Band': std,
            '2 STD Band': 2 * std, '3 STD Band': 3 * std,
            'Occurrences >1 STD': freq_1_std, 'Occurrences >2 STD': freq_2_std, 'Occurrences >3 STD': freq_3_std,
        })
    return pd.DataFrame(results)

usa_columns = [
    '2 Year Note', '10 Year Note', 'PMI', 'PMI New Orders', 'PMI Production',
    'PMI Employment', 'PMI Supplier Deliveries', 'PMI Inventories', 'PMI Customers Inventories',
    'PMI Prices', 'PMI Backlog of Orders', 'PMI New Export Orders', 'PMI Imports',
    'PMI Consumption', 'PMI Inputs', 'NPMI', 'NPMI Business Activity', 'NPMI New Orders',
    'NPMI Employment', 'NPMI Supplier Deliveries', 'NPMI Inventories', 'NPMI Prices',
    'NPMI Backlog of Orders', 'NPMI New Export Orders', 'NPMI Imports', 'NPMI Inventory Sentiment',
    'NPMI Inputs', 'UMCSI', 'UMCSI inf EXP', 'B Permits', 'SMB', 'Usa CBBS',
    'M2 Supply', 'Usa Bank Dep', 'Spread 2Y/10Y', 'Yield_Curve_Slope', 'USA_Cons_Credit_Out', 'Usa Unemployment Rate'
]

eu_columns = [
    'EU PMI', 'EU NPMI', 'EU Consumer', 'EU ZEW', 'EU M2 Supply', 'DE.ZEW', 'Euro CBBS',
    'EU.INDU', 'EU.SERV', 'EU.CONS', 'EU.ESI', 'EU.EEI', 'EA.CONS', 'EA.ESI', 'EA.EEI',
    'BE.ESI', 'BG.ESI', 'CZ.ESI', 'DK.ESI', 'DE.ESI', 'EE.ESI', 'IE.ESI', 'EL.ESI',
    'ES.ESI', 'FR.ESI', 'HR.ESI', 'IT.ESI', 'CY.ESI', 'LV.ESI', 'LT.ESI', 'LU.ESI',
    'HU.ESI', 'MT.ESI', 'NL.ESI', 'AT.ESI', 'PL.ESI', 'PT.ESI', 'RO.ESI', 'SI.ESI',
    'SK.ESI', 'FI.ESI', 'SE.ESI', 'ME.ESI', 'MK.ESI', 'AL.ESI', 'RS.ESI', 'TR.ESI'
]

pd.set_option('display.float_format', lambda x: f'{x:.2f}')

print(f'Today is {today}')
print(f'Date for this Monday is {current_week_start}')
print(f'Current Year is {this_year}')
print(f'Current Year Start is {current_year_start}')
print(f'Current Year End is {current_year_end}')
print(f'Current Month as a date is {current_month_date}')
print(f'Next Month as a date is {next_month_date}')
print(f'Current months as a number is {this_month}')
print(f'Next month as a number is {next_month}')
print(f'Quarter Start {quarter_start}')
print(f'Quarter End {quarter_end}')
print(f"Memory usage: {memory_usage_mb:.2f} MB")
