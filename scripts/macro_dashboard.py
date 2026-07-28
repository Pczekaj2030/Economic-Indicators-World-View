
# part 3
import requests
pd.set_option('display.float_format', '{:.0f}'.format)
question = input("Would You like a Market Breath? y/n")

url = 'https://www.slickcharts.com/sp500'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/50.0.2661.102 Safari/537.36'}
result = r.get(url, headers=headers)
hist_start_date='2000-01-01'
if question == 'y':
    print('ok')
    sp500_df   = get_index_constituents_fmp("sp500", API_KEY)

    #nasdaq_df  = get_index_constituents_fmp("nasdaq", API_KEY
    sp500_df_list = sp500_df['symbol'].to_list()
    tickers = sp500_df_list
    sp500_tickers = sp500_df_list

    

    #extend_list=tickers.append('^GSPC')
    sp500_scraped=pd.DataFrame(yf.download(tickers, start=f'{hist_start_date}', end=f'{today}')['Close'])
    sp500_scraped.isna().any()
    sp500_scraped.loc[:,sp500_scraped.isna().any()]
    df_sp500=pd.DataFrame(sp500_scraped.stack().round(2))
    df_sp500['Ave 50']=df_sp500.groupby(level=1)[0].transform(lambda x: x.rolling(50).mean())
    df_sp500['Ave 200']=df_sp500.groupby(level=1)[0].transform(lambda x: x.rolling(200).mean())
    df_sp500.rename(columns={0:'Adj Close'}, inplace=True)
   
    
    df_sp500['Above 50']= df_sp500.apply(lambda x: 1 if (x['Adj Close'] > x['Ave 50']) else 0, axis = 1)
    df_sp500['Above 200']= df_sp500.apply(lambda x:1 if (x['Adj Close'] > x['Ave 200']) else 0, axis = 1)
    ma_50_pct=(df_sp500.groupby(level=0)['Above 50'].sum()/len(sp500_tickers))*100#df_sp500.groupby(level=0)['Above 50'].count()
    ma_200_pct=(df_sp500.groupby(level=0)['Above 200'].sum()/len(sp500_tickers))*100
    df_sp500_breath=pd.concat([ma_50_pct[200:],ma_200_pct[200:]], axis=1).round(2)
   
    
    df_sp500_breath.sort_index(ascending=False, inplace=True)
    df_sp500_breath['Spread']=(df_sp500_breath['Above 50']/df_sp500_breath['Above 200']).round(2)


    sp_500_daily=pd.DataFrame(yf.download("^GSPC",start=f'{hist_start_date}', end=f'{today}')['Close'])
    #tickers=si.tickers_ftse100(include_company_data=True)
    #ftse_tickers=tickers['Ticker'].values
    #ftse_lsx_ready=[]
    #for ticker in ftse_tickers:
    #    x=ticker + '.L'
    
    #ftse_lsx_ready.append(x)

    #ftse_100=pd.DataFrame(yf.download(ftse_lsx_ready, start=f'{hist_start_date}', end=f'{today}')['Close'])
    #ftse=pd.DataFrame(ftse_100.stack().round(2))
    #ftse['Ave 50']=ftse.groupby(level=1)[0].transform(lambda x: x.rolling(50).mean())
    #ftse['Ave 200']=ftse.groupby(level=1)[0].transform(lambda x: x.rolling(200).mean())
    #ftse.rename(columns={0:'Adj Close'}, inplace=True)
    #ftse['Above 50']= ftse.apply(lambda x: 1 if (x['Adj Close'] > x['Ave 50']) else 0, axis = 1)
    #ftse['Above 200']= ftse.apply(lambda x:1 if (x['Adj Close'] > x['Ave 200']) else 0, axis = 1)
    #ma_50_pct=(ftse.groupby(level=0)['Above 50'].sum()/len(ftse_lsx_ready))*100 #df_sp500.groupby(level=0)['Above 50'].count()
    #ma_200_pct=(ftse.groupby(level=0)['Above 200'].sum()/len(ftse_lsx_ready))*100
    
    
    #ftse_breath=pd.concat([ma_50_pct[200:],ma_200_pct[200:]], axis=1).round(2)
    #ftse_breath.sort_index(ascending=False, inplace=True)
    #ftse_breath['Spread']=(ftse_breath['Above 50']/ftse_breath['Above 200']).round(2)
    #ftse_index=pd.DataFrame(yf.download("^FTSE",start=f'{hist_start_date}', end=f'{today}')['Close'])
    #df_ftse_100=pd.concat([ftse_index,ftse_breath],axis=1)
    #df_ftse_100.sort_index(ascending=False, inplace=True)



    dow_jones = get_index_constituents_fmp("dowjones", API_KEY)
    dow_jones_list = dow_jones['symbol'].to_list()
    dow_jones_stocks=pd.DataFrame(yf.download(dow_jones_list, start=f'{hist_start_date}', end=f'{today}')['Close'])
    dow_jones_stocks=pd.DataFrame(dow_jones_stocks.stack().round(2))
    dow_jones_stocks['Ave 50']=dow_jones_stocks.groupby(level=1)[0].transform(lambda x: x.rolling(50).mean())
    dow_jones_stocks['Ave 200']=dow_jones_stocks.groupby(level=1)[0].transform(lambda x: x.rolling(200).mean())
    dow_jones_stocks.rename(columns={0:'Adj Close'}, inplace=True)
    dow_jones_stocks['Above 50']= dow_jones_stocks.apply(lambda x: 1 if (x['Adj Close'] > x['Ave 50']) else 0, axis = 1)
    dow_jones_stocks['Above 200']= dow_jones_stocks.apply(lambda x:1 if (x['Adj Close'] > x['Ave 200']) else 0, axis = 1)
    dow_ma_50_pct=(dow_jones_stocks.groupby(level=0)['Above 50'].sum()/len(dow_jones))*100 #df_sp500.groupby(level=0)['Above 50'].count()
    dow_ma_200_pct=(dow_jones_stocks.groupby(level=0)['Above 200'].sum()/len(dow_jones))*100
    dow_breath=pd.concat([dow_ma_50_pct[200:],dow_ma_200_pct[200:]], axis=1).round(2)
    dow_breath.sort_index(ascending=False, inplace=True)
    dow_breath['Spread']=(dow_breath['Above 50']/dow_breath['Above 200']).round(2)
    dow_industrial_index=pd.DataFrame(yf.download("^DJI",start=f'{hist_start_date}', end=f'{today}')['Close'])
    dow_industrial_full=pd.concat([dow_industrial_index,dow_breath],axis=1)
    df_500_finish=pd.concat([sp_500_daily,df_sp500_breath],axis=1)

    breadth(df_500_finish,'S&P 500 Index','SP500 Breadth 50 and 200 Moving Averages')
    breadth(dow_industrial_full,'Dow Industrial Index','Dow industrial Index Breadth 50 and 200 Moving Averages')
   #breadth(df_ftse_100,'FTSE Index','FTSE Breadth 50 and 200 Moving Averages')
    breath_monthly = df_sp500_breath.resample('MS').last()


# Assuming 'usa_yield_curve_tr_chart' contains the data and the new 'Last Week' column
fig = px.line(
    usa_yield_curve_tr_chart,
    x=usa_yield_curve_tr_chart.index,
    y=['Today', 'Last Week', '3 Months Ago', '6 Months Ago'],
    markers=True,
    height=800,  # Increased height by 200px
    title='United States Yield Curve'
)

# Updating layout to resemble the chart style
fig.update_layout(
    template='plotly_dark',
    xaxis_title="Time to Maturity",
    yaxis=dict(
        side='right',
        title="% Yield (Annualized)"
    ),
    legend_title="Time Periods",
    font=dict(size=14),
    autosize=True  # Enable autosizing for width
)

# Update lines for visibility based on time period
line_styles = {
    'Today': {'opacity': 1.0, 'line_width': 3},
    'Last Week': {'opacity': 0.8, 'line_width': 2.5},
    '3 Months Ago': {'opacity': 0.6, 'line_width': 2},
    '6 Months Ago': {'opacity': 0.3, 'line_width': 1.5}
}

for trace in fig.data:
    time_period = trace.name
    if time_period in line_styles:
        trace.update(
            opacity=line_styles[time_period]['opacity'],
            line=dict(width=line_styles[time_period]['line_width'])
        )
        # Add data labels for each point
        trace.update(
            text=[f"{y:.2f}" for y in trace.y],
            textposition="top center",
            mode="markers+lines+text"
        )

# Add annotations to the chart
fig.add_annotation(
    x=7,  # Adjust based on where you want the annotation
    y=5.6,  # Adjust to the appropriate y-value for the annotation
    text="When longer-term yields are going higher, Preference for higher risk assets -> Economic Expansion",
    showarrow=False,
    font=dict(size=12, color="Green"),
    align="left",
    bordercolor="white",
    borderwidth=1,
    borderpad=4,
    bgcolor="rgba(0,0,0,0.7)"
)

fig.add_annotation(
    x=7,  # Adjust based on where you want the annotation
    y=5.4,  # Adjust to the appropriate y-value for the annotation
    text="When longer-term yields are going down, short-term yields going up -> Economic Contraction",
    showarrow=False,
    font=dict(size=12, color="red"),
    align="left",
    bordercolor="white",
    borderwidth=1,
    borderpad=4,
    bgcolor="rgba(0,0,0,0.7)"
)

# Show the figure
fig.show()

# --- 1. DOWNLOAD & ALIGN S&P 500 ---
spx_full = yf.download("^GSPC", start="1949-01-01")
spx_quarterly = spx_full['Close'].resample('QE').last().pct_change() * 100
spx_quarterly.index = spx_quarterly.index.to_period('Q').to_timestamp()

# --- 2. JOIN WITH GDP DATA ---
# Ensure columns are named exactly as you expect for the join
gdp_col = plot_usa_gdp_q[['Usa GDP QonQ']]
spx_col = pd.DataFrame(spx_quarterly)
spx_col.columns = ['^GSPC']

# Join and clean up the 'Modern Era' (1950+)
macro_comparison_df = pd.concat([gdp_col, spx_col], axis=1, join='inner').dropna()
macro_comparison_df = macro_comparison_df[macro_comparison_df.index >= '1950-01-01']

# --- 3. ADD MACRO INDICATORS (CRITICAL: DO THIS BEFORE SORTING) ---
macro_comparison_df['USA_GDP'] = (macro_comparison_df['Usa GDP QonQ'] > 0).astype(int)
macro_comparison_df['USA_SPX'] = (macro_comparison_df['^GSPC'] > 0).astype(int)

# --- 4. THE BEAUTIFUL CALCULATION ---
total_n = len(macro_comparison_df)
probs = macro_comparison_df.value_counts(['USA_GDP', 'USA_SPX'], normalize=True) * 100

p_11 = probs.get((1, 1), 0)  # Boom
p_00 = probs.get((0, 0), 0)  # Reality Check
p_01 = probs.get((0, 1), 0)  # Hallucination
p_10 = probs.get((1, 0), 0)  # Profit Taking / Panic

print(f"--- 1950-2026 Macro Outcome Probabilities ---")
print(f"Total History: {total_n} Quarters")
print("-" * 45)
print(f"✅ (1,1) Boom (Both Up):               {p_11:.2f}%")
print(f"❌ (0,0) Reality Check (Both Down):     {p_00:.2f}%")
print(f"🚀 (0,1) Hallucination (GDP Down, SPX Up): {p_01:.2f}%")
print(f"📉 (1,0) Profit Taking (GDP Up, SPX Down): {p_10:.2f}%")
print("-" * 45)

# Conditional Probability Logic
gdp_up_df = macro_comparison_df[macro_comparison_df['USA_GDP'] == 1]
profit_taking_chance = (len(gdp_up_df[gdp_up_df['USA_SPX'] == 0]) / len(gdp_up_df)) * 100
print(f"Chance of 'Profit Taking' if GDP is positive: {profit_taking_chance:.2f}%")

# --- 5. SORT & TRANSPOSE FOR THE DASHBOARD VIEW ---
# Ascending=False ensures 2026 is the very first column in the transpose
macro_comparison_df_sorted = macro_comparison_df.sort_index(ascending=False)
macro_comparison_tr = macro_comparison_df_sorted.T
display(
    macro_comparison_tr.iloc[:, :48]  # Select the first 36 columns
    .style
    .background_gradient(axis=1, cmap='RdYlGn')
    .format("{:.0f}")
)
indicator_vs_stock_bar(stock_gspc_monthly['^GSPC Y on Y'],"^SKEW")
plot_price_and_returns("^SKEW", start_date="2015-01-01")


px_chart(plot_mmf_fred_q,1976,'Total MMF FRED Y on Y','Money Market Flow Total Quarterly Y on Y','#E57E00',top_value=0.55,bottom_value=-0.3,annotations_bottom=[('2009-04-01', 'Cycle begins to Acquire, Rent , Employment Transoport, Lease, Finance, Manage ,Travel')],annotations_top=[('2004-02-01','Where is the cycle?  to Acquire, Rent , Employment Transoport, Lease, Finance, Manage ,Travel')])

time=2002
px_chart(usa,2016,'Yield_Curve_Slope','A stronger USD often coincides with higher interest rates, improving net interest margins for banks and insurers','#E87722',
         
        top_value=0.15,bottom_value=-0.1,annotations_top=[('2021-05-01','PMI Topping Yields and Market expect FED Rate cycle to begin' )
                                                 ],annotations_bottom=[('2023-07-01',' Market expect Lowering cycle PMI YonY Trought')
          ])
px_chart(usa_yields_monthly,2010,'Curvature_Z','Yet anohter reminder of the Yield curve implication','#ffffff',
         top_value=1,bottom_value=-2,annotations_top=[('2019-06-01','🟢 Market wil beging to belive IR cuts but the market might colapse before that then you ok' )],
         annotations_bottom=[('2018-02-01','🔴 So at this level waht is ususlaly happenning is FED will Hike depending on CPI')],smooth = 'Yes')

px_chart_bar_neg(usa,1990,'Usa IR','United States Interest Rate','#577d70')
px_chart(usa,1997,'USA Corp Bond AAA-CCC',' I think this represents how smart money is thinking what FED will do. when going up less chance of future cuts','#E87722',top_value=-5,bottom_value=-16,annotations_top=[('2014-07-01','Smart money sells AAA and buys CCC Higher IR condition' ),
                                                                                                                                                                                                          ('2021-06-01','Market expectation higher Rates')],annotations_bottom=[('2016-02-01',' Trup took office lowered taxes for corpo'),
                                                                                                                                                                                                          ('2022-10-01','Market Expects Lowering cycle with SP 500 Breath')])
indicator_vs_indicator(usa['UMCSI inf EXP'],usa['CPI inc YonY'])

px_chart_bar_neg(plot_treasury_weekly,2007,'TREASURY FED','Total U.S. Fed Treasury Holdings from 2002','#E57E00')

px_chart(plot_treasury_weekly,2007,'USA Treasury Y on Y Weekly','Total U.S. Fed Treasury Holdings Y on Y','#E57E00')

px_chart_bar_visual(plot_cbbs_weekly,2021,'Usa CBBS Y on Y Weekly',' USA Central Bank Balance Sheet Weekly on Y on Y','#e0af60','Usa CBBS Change Weekly', height = 700)
#px_chart(plot_banks_dep_w,time,'Usa Bank Dep Y on Y Weekly','USA Bank Deposit','#E57E00',top_value=0.1,bottom_value=-0.05,annotations_bottom=[('2023-02-01', ' things could be easing from now wait for breath and skew flush and load EPS growth'),('2016-03-01','Trump gets nomination for President')],annotations_top=[('2003-12-01','Remember index might go down but IJH like Etfs might be flat or negative')])



indicator_vs_indicator(usa['10 Year Note'],usa['CPI ex YonY'])

px_chart_bar_visual(plot_10Y2Y_w,2018,'T10Y2Y w','Weekly 10 Year - 2 Year Yields','#fb8b1e','T10Y2Y w',height = 700)


px_chart_bar_visual(plot_10Y3M_w,2018,'T10Y3M w','Weekly 10 Year - 3 Months Yield since 1985','#57b023','T10Y3M w',height = 700)

px_chart_bar_visual(usa,2000,'10Y-3M','Monthly 10 Year - 3 Months Yield since 1985','#57b023','10Y-3M',height = 700)

px_chart_bar_visual(usa,1985,'10Y-2Y','Monthly 10 Year - 2 Year Yield since 1985','#fb8b1e','10Y-2Y',height = 700)

px_chart_bar_visual(usa,1985,'M2 Supply YonY','Usa Money Supply Monthly Y on Y','#5DADE2','M2 Supply',height = 700)

px_chart_bar_neg(usa,1978,'Spread 2Y/10Y','Monthly Spread 2Y/10Y since 1978','#fb8b1e')

indicator_vs_indicator_smoothed_future(usa['Usa GDP QonQ Annualized'],usa['PMI'])
indicator_vs_stock_bar(usa['PMI YonY']['2005':],"^GSPC")
px_chart(usa,1950,'PMI','United States PMI Index','#E57E00',top_value=60,bottom_value=40,annotations_top=[('1994-04-01', 'Business cycle Top Economy on fire CPI as welll FED will step in')],annotations_bottom=[('1991-03-01','Economy to expand XLB then jobs CX TECH Low rates')])#fa6969



px_chart(usa,time,'PMI YonY','United States PMI Index Y on Y Change 10 Year value will follow and Yield should fall','#66B5E5',top_value=0.25,bottom_value=-0.2,annotations_top=[('2021-05-01', 'FED will rise IR as Inflation too high'),('2010-01-01', 'Business cycle Top FED will step in')],annotations_bottom = [
    ('2023-02-01', 'Expected condition easing of IR'),
    ('2020-03-01', 'Long Everything Cycnical'),# February 2023 annotation
    ('2009-01-01', 'Bottom after 2008-2009 Crisis')  # Another annotation
],smooth='Yes')


px_chart(usa,1995,'PMI_Spread_NewOrders_Inv','🟢 Demand accelerating — inventories lean → factories ramp up → early-cycle rally in industrials, semiconductors, raw materials ','#E87722',top_value=15,bottom_value=0,annotations_top=
         [('2018-01-01','🔴 Inventories piling up → Factories built too much → they’ll slow production → EPS falls in cyclicals' )],
         annotations_bottom=[('2024-09-01','🟢 Demand accelerating early-cycle rally in industrials, semiconductors, raw materials')])

px_chart(usa,1970,'PMI_Spread_Backlog_Inv','“Are order backlogs growing faster than inventories? Factories have future work secured, giving pricing power and margin expansion”,Equipment makers,metal producers,industrial suppliers','#E87722',
         top_value=7,bottom_value=-5,annotations_top=[('2018-06-01','🔴 No → Inventories are building faster Or Topping → orders drying up, future production slows, margins compress.' ),('2021-06-01','future production slows, margins compress.' )],
         annotations_bottom=[('2012-10-01','🟢 Yes → Production demand is still strong or recovering, factories have work lined up, pricing power improves, EPS expands.')], smooth = 'Yes' )


px_chart(usa,time,'PMI New Orders','United States PMI New Orders Index','#E57E00',top_value=65,bottom_value=45,annotations_top=[('2014-01-01', 'SELL FDX , OIL GBX And watch it may not happen It took Another 12 M ')],annotations_bottom=[('2011-06-01','XLI , FDX, RAIL GBX SEMIS, A lot of things ')])
px_chart(usa,time,'PMI New Orders YonY','United States PMI New Orders Y On Y Index','#66B5E5',top_value=0.2,bottom_value=-0.25,annotations_top=[('2014-01-01', 'SELL FDX , OIL GBX And watch it may not happen It took Another 12 M ')],annotations_bottom=[('2011-06-01','XLI , FDX, RAIL GBX SEMIS, A lot of things ')],smooth='Yes')


px_chart(usa,1955,'PMI_Spread_Orders_Exports','“Does the world still want U.S. products — and the dollars that come with them?”','#E87722',top_value=8,bottom_value=-5,annotations_top=
         [('1998-02-01','Rising export momentum = overheating → inflation risk builds → policy tightening ahead.🚢 Export-heavy cyclicals' ),('2014-10-01','Semis after strong run: NVDA, TXN, AMAT.' )],
         annotations_bottom=[('2001-03-01','Central banks are likely near the end of tightening, liquidity will turn supportive.')], smooth = 'Yes' )

px_chart(usa,time,'PMI Inputs','United States PMI Inputs Index','#E57E00',top_value=65,bottom_value=45.2,annotations_top=[('2014-05-01', 'SELL FDX , OIL GBX And watch it may not happen It took Another 12 M ')],annotations_bottom=[('2011-11-01','XLI , FDX, RAIL GBX SEMIS, A lot of things ')])
px_chart(usa,time,'PMI Inputs YonY','United States PMI Inputs Y On Y Index','#66B5E5',top_value=0.2,bottom_value=-0.2,annotations_top=[('2014-05-01', 'SELL FDX , OIL GBX And watch it may not happen It took Another 12 M ')],annotations_bottom=[('2011-11-01','XLI , FDX, RAIL GBX SEMIS, A lot of things ')],smooth='Yes')

px_chart(usa,time,'PMI Consumption','United States PMI Consumption Index','blanchedalmond',top_value=65,bottom_value=45.2,annotations_top=[('2014-05-01', 'SELL FDX , OIL GBX And watch it may not happen It took Another 12 M ')],annotations_bottom=[('2011-11-01','XLI , FDX, RAIL GBX SEMIS, A lot of things ')])
px_chart(usa,time,'PMI Consumption YonY','United States PMI Consumption Y on Y Index','blanchedalmond',top_value=0.2,bottom_value=-0.25,annotations_top=[('2014-05-01', 'SELL FDX , OIL GBX And watch it may not happen It took Another 12 M ')],annotations_bottom=[('2009-01-01','XLI , FDX, RAIL GBX SEMIS, A lot of things ')],smooth='Yes')

        
px_chart(usa,time,'B Permits','United States building Permits','#94f7da')
px_chart(usa,time,'B Permits YonY','United States B Permits Y on Y Smothed Change ','#C76E00',top_value=0.25,bottom_value=-0.2,annotations_top=[('2021-05-01', 'FED will rise IR Short Home , wood anything realated'),('2012-09-01', 'Business cycle Top FED will step in')],annotations_bottom = [
    ('2023-02-01', 'Expected condition easing of IR'),
    ('2020-03-01', 'Long Everything Cycnical and housing'),# February 2023 annotation
    ('2009-01-01', 'Housein market Boom')  # Another annotation
],smooth='Yes')


time = '1990'
px_chart(usa,time,'UMCSI','Usa UMCSI Consumer Expectation Index ','blanchedalmond',top_value=65,bottom_value=90,annotations_bottom=[('1998-10-01', 'This is GDP at 3 % ')],annotations_top=[('1992-01-01','                                                                   Below 70 GDP 0 %')])
px_chart(usa[:-1],1978,'UMCSI YonY','Usa Consumer Expectation Y onY Index','#bf826f',top_value=0.25,bottom_value=-0.25,annotations_top=[('1994-09-01', 'This is GDP at 3 % ')],annotations_bottom=[('2001-11-01',' Below 70 GDP 0 %')],smooth='Yes')


url = 'http://www.sca.isr.umich.edu/'
response = r.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    richnote_div = soup.find('div', id='richnote')

    if richnote_div:
        commentary = richnote_div.get_text(strip=True, separator="<br><br>")
        
        # Define font size here (e.g., 20px or 150%)
        font_size = "30px"
        
        html_output = f"""
        <div style="font-size:{font_size}; line-height:1.6;">
            {commentary}
        </div>
        """
        display(HTML(html_output))
    else:
        print("No 'richnote' section found.")
else:
    print(f"Failed to retrieve content: Status Code {response.status_code}")




px_chart_neg(usa,1978,'UMCSI inf EXP','United States Consumer Inflation Expectation Index','#2f5899')
years_4=2018
time=2002


time = '2002'
px_chart(usa,time,'NPMI','Usa NPMI Service Index ',' #E57E00',top_value=60,bottom_value=50,annotations_bottom=[('2009-04-01', 'Cycle begins to Acquire, Rent , Employment Transoport, Lease, Finance, Manage ,Travel')],annotations_top=[('2004-02-01','Where is the cycle?  to Acquire, Rent , Employment Transoport, Lease, Finance, Manage ,Travel')])
px_chart(usa[:-1],2002,'NPMI YonY','Usa NPMI Services Y onY Index',' #E57E00',top_value=0.1,bottom_value=-0.15,annotations_bottom=[('2009-05-01', 'Cycle begins to Acquire, Rent , Employment Transoport, Lease, Finance, Manage ,Travel')],annotations_top=[('2004-04-01','Where is the cycle?  to Acquire, Rent , Employment Transoport, Lease, Finance, Manage ,Travel')],smooth='Yes')


time = '2002'
px_chart(usa,time,'NPMI Business Activity','Usa NPMI Business Activity Index ',' #008080',top_value=65,bottom_value=50,annotations_bottom=[('2009-04-01', 'Cycle begins to Acquire, Rent , Employment Transoport, Lease, Finance, Manage ,Travel')],annotations_top=[('2004-02-01','Where is the cycle?  to Acquire, Rent , Employment Transoport, Lease, Finance, Manage ,Travel')])
px_chart(usa[:-1],2002,'NPMI Business Activity YonY','Usa NPMI Business Activity Y on Y Index',' #008080',top_value=0.25,bottom_value=-0.2,annotations_bottom=[('2009-05-01', 'Cycle begins to Acquire, Rent , Employment Transoport, Lease, Finance, Manage ,Travel')],annotations_top=[('2004-04-01','Where is the cycle?  to Acquire, Rent , Employment Transoport, Lease, Finance, Manage ,Travel')],smooth='Yes')

px_chart(usa,time,'NPMI New Orders','Usa NPMI New Orders Index ','#E57E00',top_value=65,bottom_value=50,annotations_bottom=[('2009-04-01', 'Cycle begins to Acquire, Rent , Employment Transoport, Lease, Finance, Manage ,Travel')],annotations_top=[('2004-02-01','Where is the cycle?  to Acquire, Rent , Employment Transoport, Lease, Finance, Manage ,Travel')])
px_chart(usa[:-1],2002,'NPMI New Orders YonY','Usa NPMI New Orders Y onY Index','#fefefe',top_value=0.25,bottom_value=-0.2,annotations_bottom=[('2008-12-01', 'Cycle begins to Acquire, Rent , Employment Transoport, Lease, Finance, Manage ,Travel')],annotations_top=[('2004-04-01','Where is the cycle?  to Acquire, Rent , Employment Transoport, Lease, Finance, Manage ,Travel')],smooth='Yes')


px_chart(usa,time,'SMB','Usa Small businnes Index NFBI','#E57E00',top_value=110,bottom_value=90,annotations_bottom=[('2009-04-01', 'SP500 and Rus2000 corr over 0.45 Be creative in your longs'),('2016-03-01','Trump gets nomination for President')],annotations_top=[('2003-12-01','Remember index might go down but IJH like Etfs might be flat or negative')])
px_chart(usa[:-1],2002,'SMB YonY','Usa Small busines Index NFBI YonY Index','#fefefe',top_value=0.07,bottom_value=-0.05,annotations_bottom=[('2009-04-01', 'SP500 and Rus2000 corr over 0.45 Be creative in your longs IJH like ETS (check holdings) Positive out preforming SP500')],annotations_top=[('2004-02-01','Remember index might go down but IJH like Etfs might be flat or negative,')],smooth='Yes')

px_chart(usa[:-1].round(3),1950,'PPI inc YonY','Producer Price Index Y on Y since 1950','burlywood',top_value=0.05,bottom_value=-0.03,annotations_top=[('1989-05-01','These are extreams FED will tightening policy')],
        annotations_bottom=[('1964-06-01','These are extreams FED WIll step in possible cuts , GAS , OIL Ect (HES, APA high corr)')],smooth='Yes'
)
px_chart(usa[:-1].round(3),1950,'CPI inc YonY','Consumer Price Index Y on Y since 1950','burlywood',top_value=0.06,bottom_value=0,annotations_top=[('1990-12-01','These are extreams FED will tightening policy')],
        annotations_bottom=[('1986-10-01','FED Policy to loose Cut rates create growth,')]
)
px_chart(usa[:-1].round(3),1950,'PPI - CPI','Producer Price Index - Consumer Price Index since 1950','burlywood',top_value=0.02,bottom_value=-0.04,annotations_top=[('1974-11-01','If PPI > CPI  Short Discount retailers, Long luxury or strong brand')],
        annotations_bottom=[('1986-07-01','If PPI > CPI  Short Discount retailers, Long luxury or strong brand, or financials')]
)

px_chart(usa[:-1],1973,'IP Chemicals YonY','Usa Industrial Production Chemicals YonY','#fefefe',top_value=0.07,bottom_value=-0.05,annotations_bottom=[('2009-03-01', 'DD a simple stock went 4X in a year Good Luck for a time like this')],
         annotations_top=[('2005-03-01',"DD did'd go up X times just normal moves")],smooth='Yes')

px_chart(usa[:-1],1973,'IP Machinery YonY','Usa Industrial Production Machinery YonY','#fefefe',top_value=0.11,bottom_value=-0.09,annotations_bottom=[('2009-06-01', 'XLI like Full power in steps but PMI Index ahead')],
         annotations_top=[('1993-12-01','Always remember Top for index might not mean top for a specific stock NEXT 2 Years Flat Catapilar example')]),#smooth='Yes')

px_chart(usa[:-1],1950,'PMI Employment','Usa PMI Employment Index','#ff991c',top_value=58,bottom_value=40,annotations_bottom=[('2009-06-01', 'To be filled')],
         annotations_top=[('1984-01-01','Always remember Top for index might not mean top for a specific stock')])#,smooth='Yes')

px_chart(usa[:-1],1950,'PMI Employment YonY','Usa PMI Employment Y onY Smoothed Index','#fefefe',top_value=0.25,bottom_value=-0.2,annotations_bottom=[('2008-12-01', 'Cycle begins to Acquire, Rent , Employment Transoport, Lease, Finance, Manage ,Travel')],annotations_top=[('2004-04-01','Where is the cycle?  to Acquire, Rent , Employment Transoport, Lease, Finance, Manage ,Travel')],smooth='Yes')
px_chart(usa,1970,'USA_Savings_usa YonY','“How much money is US consumer saving vs Year ago ?”','#ffffff',top_value=0.2,bottom_value=-0.5,annotations_top=[('2009-01-01','🟢 Consumer starting to spend meaning PMI and earnigs to explode' )],annotations_bottom=[('2005-06-01','🔴 In Jun 2005 (2 Years before Recesion) consumer slowy started saving meaning less cash more worry')],smooth = 'Yes')
px_chart(usa,1970,'USA_Cons_Credit_Out YonY','“The Heartbeat of the US Consumer since 1970”','#ffffff',top_value=0.07,bottom_value=-0.01,annotations_top=[('2006-04-01','🔴 this makrs tops for additional borrowings Like Big ticket items' ),('2022-02-01','🔴 This was top for PMI and FED will hike baddly' )],annotations_bottom=[('1975-07-01','🟢 When they are not borrowing FED will lower otherwise Stagflation'),('2020-12-01','🟢 Market Crashed for 3 months before rates where slashed')],smooth = 'Yes')
px_chart(usa,time,'Open Jobs','Usa Number Of Jobs Openings in Millions ','#E57E00',top_value=65,bottom_value=50,annotations_bottom=[('2009-04-01', 'Cycle begins to Acquire, Rent , Employment Transoport, Lease, Finance, Manage ,Travel')],annotations_top=[('2004-02-01','Where is the cycle?  to Acquire, Rent , Employment Transoport, Lease, Finance, Manage ,Travel')])
px_chart(usa[:-1],2002,'Open Jobs YonY','Usa Number Of Jobs Openings Y on Y Smoothed','#fefefe',top_value=0.25,bottom_value=-0.2,annotations_bottom=[('2008-12-01', 'Cycle begins to Acquire, Rent , Employment Transoport, Lease, Finance, Manage ,Travel')],annotations_top=[('2004-04-01','Where is the cycle?  to Acquire, Rent , Employment Transoport, Lease, Finance, Manage ,Travel')],smooth='Yes')
column =['Open Jobs']

px_chart(usa,2003,'Usa Unemployment Rate','Usa Unemployment rate in % ','#E57E00',top_value=10,bottom_value=3.3,annotations_top=[('2019-06-01', 'Cycle on all cylinders FED might step in no direction, but check inflation')],annotations_bottom=[('2007-08-01','Unemplyment picks Up plus Deflation Recesion might come in Lowering cycle next 2 Years ')],smooth='No')

time_4  = '2000'

usa.loc['2020-04-01', 'NFPR DIFF'] = -800
usa.loc['2020-05-01', 'NFPR DIFF'] = 1000
usa.loc['2020-06-01', 'NFPR DIFF'] = 900
usa.loc['2020-07-01', 'NFPR DIFF'] = 750
usa.loc['2020-08-01', 'NFPR DIFF'] = 850
usa.loc['2020-03-01', 'NFPR DIFF'] = -400
px_chart(usa,1990,'NFPR DIFF','Usa Non Farm Payroll Jobs added to the economy 200-250 USA GDP Growth 2.5%','#E87722',top_value=330,bottom_value=-212,annotations_bottom=[('2018-10-01', 'This is not a bottom just referece'),
                                                                                                                                   ('2009-03-01','GFC Bottom of Stock Market'),
                                                                                                                                   ('2001-11-01','Dot.com Bubble')],#smooth='Yes',
         annotations_top=[('2005-04-01','At This rate USA GDP might be growing @ 4%  Q on Q so Fed might step in' ),('2024-11-01','2 months before collapse')])

px_chart(usa,2021,'NFPR DIFF','Usa Non Farm Payroll Jobs added to the economy 200-250 USA GDP Growth 2.5%','#E87722',bottom_value=220,top_value=100,annotations_top=[('2021-05-01','At This rate 6.4% GDP ,PMI TOP so Fed might step in' ),('2022-11-01','This rate 3.8% GDP' ),('2023-11-01','This rate 2.5% GDP' )],smooth='Yes')


indicator_vs_indicator_smoothed_future(usa['NFPR DIFF'],usa['PMI Employment'])
px_chart(df_europe_eval,1985,'Percentage','Percentage of European countries experiencing ESI growth','#E87722',top_value=0.7,bottom_value=0.3,annotations_bottom=[('1990-11-01', 'This is not a bottom just referece of Boom for possible Europe Business Cycle'),
                                                                                                                                   ('2008-11-01','GFC'),
                                                                                                                                   ('2011-09-01','September 9/11'),
                                                                                                                                   ('2001-07-01','Dot.com Bubble')],
         annotations_top=[('1999-08-01','This is not a Top just referece of Bust§ for possible End of Europe Business Cycle' )],smooth='Yes')

px_chart(europe,2008,'EU PMI','Europe PMI Index','#E87722',top_value=60,bottom_value=44,annotations_bottom=[('2009-03-01','GFC'),('2020-05-01','COVID 19')],                                                                                                            
         annotations_top=[('2018-01-01','This is not a Top just referece of Bust for possible End of Europe Business Cycle' )])#,smooth='Yes')


px_chart(europe,2008,'EU PMI YonY','Europe PMI Index YonY','#FFFFFF',top_value=0.2,bottom_value=-0.2,annotations_top=[('2014-05-01','This is not a Top just referece For next few Years flat to up not short But Chances of 15% Short' )])

px_chart(europe,1995,'EA.CONS','Europe Consumer Sentiment Index From ESI ','#E87722',top_value=0,bottom_value=-25,annotations_bottom=[
                                                                                                                                   ('2009-05-01','GFC'),
                                                                                                                                   ('2020-06-01','COVID 19 3 Months later then US')],                                                                                                            
         annotations_top=[('2018-01-01','This is not a Top just referece of Bust for possible End of Europe Business Cycle' )])#,smooth='Yes')

px_chart(europe,1999,'EU ZEW','ZEW Economic Sentiment Indicator Index Above 0.6 corr to ^STOXX50E,^STOXX, ^GDAXI,^FCHI','#E87722',top_value=60,bottom_value=-25,annotations_bottom=[
                                                                                                                                   ('2012-01-01','DAX,CAC40, STOXX Europe 600 Get to work')],                                                                                                     
         annotations_top=[('2014-03-01','This is not a Top just referece of Bust for possible End of Europe Business Cycle Or world ')])#,smooth='Yes')


px_chart(europe,1996,'EU M2 Supply YonY','Europe M2 Money Supply YonY ','#E87722',top_value=0.11,bottom_value=-0.025)       
px_chart(europe,1985,'EA.ESI','Economic Sentiment Indicator (ESI)','#E87722',top_value=114,bottom_value=90)                                                                                             
px_chart(europe,1985,'EA.ESI YonY','Economic Sentiment Indicator (ESI)','#FFFFFF',top_value=0.15,bottom_value=-0.2,annotations_top=[('2014-05-01','This is not a Top just referece For next few Years flat to up not short But Chances of 15% Short' )],annotations_bottom=[('2009-03-01','^STOXX on the expansion  and work through sectors 0.7 corr')])

px_chart(europe,1985,'EA.INDU','Economic Sentiment Indicator (ESI) in Industrials','#E87722',top_value=7,bottom_value=-13.5,annotations_top=[('2006-12-01','This is not a Top just referece 2 years before GFC' )],annotations_bottom=[('2009-03-01','Industrials in Europe'),
                                                                                                                                                                                                                                      ('2001-11-01','Industrials in Europe'),
                                                                                                                                                                                                                                      ('2012-10-01','Industrials in Europe'),
                                                                                                                                                                                                                                      ('2025-01-01','Industrials in Europe')])
indicator_vs_stock_bar_not_sm(europe['EU ZEW'],"^STOXX")
px_chart(europe,1995,'EA.SERV','Economic Sentiment Indicator (ESI) in Services 30% in ESI','#E87722',top_value=19,bottom_value=-13.5,annotations_top=[('2006-12-01','This is not a Top just referece 2 years before GFC' )],annotations_bottom=[('2009-03-01',' Best Correlations: Financial Services, Travel & Leisure, Retail '),
                                                                                                                                                                                                                          ('2001-11-01','Best Correlations: Financial Services, Travel & Leisure, Retail'),
                                                                                                                                                                                                                                      ('2012-10-01','Best Correlations: Financial Services, Travel & Leisure, Retail'),
                                                                                                                                                                                                                                      ('2025-01-01','Best Correlations: Financial Services, Travel & Leisure, Retail')])

px_chart(europe,1985,'IT.ESI',' Italy ITLMS.MI and Italian names over 0.55 corrolation','#E87722',top_value=112,bottom_value=80,annotations_top=[('2021-06-01','Market expectation higher Rates')],annotations_bottom=[('2020-05-01',' Trup took office lowered taxes for corpo'),('2022-10-01','Market Expects Lowering IR cycle In Europe')])
px_chart(europe,1985,'IT.ESI YonY',' Italy YonY ITLMS.MI','#FFFFFF',top_value=0.2,bottom_value=-0.2,annotations_top=[('2021-06-01','Market expectation higher Rates')],annotations_bottom=[('2022-10-01','Market Expects Lowering IR cycle In Europe')])
px_chart(europe,1985,'DE.ESI',' German Economy DAX ^Mdaxi','#E87722',top_value=112,bottom_value=80,annotations_top=[('2021-09-01','Market expectation higher Rates')])
px_chart(europe,1985,'DE.ESI YonY','From April 2021 TOP Index was in range','#FFFFFF',top_value=0.2,bottom_value=-0.2,annotations_top=[('2021-04-01','Market expectation higher Rates')],annotations_bottom=[('2022-10-01','Market Expects Lowering IR cycle In Europe')])



px_chart(usa,2007,'DXY YonY','A stronger USD often coincides with higher interest rates, improving net interest margins for banks and insurers','#E87722',top_value=0.2,bottom_value=-0.1,annotations_top=[('2015-08-01','A stronger USD makes U.S. exports more expensive abroad and reduces the value of foreign earnings when converted back to dollars.' ),
                                                                                                                                                                                                          ('2022-10-01','If DXY is Falling → Favor multinationals, commodities, and emerging markets.')],annotations_bottom=[('2011-05-01',' Oil is priced in USD. A stronger dollar usually leads to lower crude oil prices, reducing fuel costs for airlines.'),
                                                                                                                                                                                                                                                                                                                             ('2024-09-01',' Favor U.S. domestic stocks, financials, and airlines.')])
px_chart(usa,2007,'GBP_USD YonY','British Pound against USD Percent Chnage Y on Y','#89ab8f')

display(df_usa_leading_tr.style.background_gradient(axis=1,cmap='RdYlGn').format("{:.5}"))

display(df_usa_pct_change_tr.style.background_gradient(axis=1,cmap='RdYlGn_r').format("{:.2%}"))



display(
    usa_current_indi_tr.iloc[:, :48]  # Select the first 36 columns
    .style
    .background_gradient(axis=1, cmap='RdYlGn')
    .format("{:.0f}")
)
#display(df_usa_industries_pmi_tr.style.background_gradient(axis=0,cmap='RdYlGn'))
#display(df_usa_industries_npmi_tr.style.background_gradient(axis=0,cmap='RdYlGn'))
display(plot_europe_vis_tr.style.background_gradient(axis=1,cmap='RdYlGn').format("{:.5}"))
#display(usa_db_diff_yy_tr[:40].style.background_gradient(axis=0,cmap='RdYlGn').format("{:.2}"))
#world_db_yy_diff[:40].style.background_gradient(axis=0,cmap='RdYlGn').format("{:.2}")
#. This give me Secotr and idustry count based on historical preformance of stock price an corrolation to a Q 
print(f"Memory usage: {memory_usage_mb:.2f} MB")
display(leading_europe_std)
display(leading_usa_std)
