plot_eu_gdp_q= pd.DataFrame(fred.get_series('CPMNACSCAB1GQEU272020',frequency ='q',))
row__eu_gdp_q = formatting(plot_eu_gdp_q,'EU GDP Billions',4)
# Assuming 'plot_usa_gdp_q' is already created and formatted
plot_eu_gdp_q['EU GDP QonQ'] = plot_eu_gdp_q['EU GDP Billions'].pct_change()

# Calculate annualized quarter-on-quarter growth
plot_eu_gdp_q['EU GDP QonQ Annualized'] = ((1 + plot_eu_gdp_q['EU GDP QonQ']) ** 4 - 1) * 100

europe_path='data/main_indicators_nace2.xlsx'
europe_part_1=pd.read_excel(path, sheet_name='EU')
europe_part_1.set_index('Date',inplace=True)
t.sleep(1)
europe_cpi_yy=pd.DataFrame(fred.get_series('EA19CPALTT01GYM'))
row_europe_cpi= formatting_pct(europe_cpi_yy,'CPI Y on Y',12)
t.sleep(1)
europe_ppi_yy=pd.DataFrame(fred.get_series('EA19PIEAMP01GYM'))
row_europe_ppi= formatting_pct(europe_ppi_yy,'PPI Y on Y',12)
europe_cbbs=pd.DataFrame(fred.get_series('ECBASSETSW',frequency='m'))
row_europe_cbbs= formatting_pct(europe_cbbs,'Euro CBBS',12)

europe_path='data/europe_esi/main_indicators_nace2.xlsx'
plot_europe_all=pd.read_excel(europe_path, sheet_name='MONTHLY')
plot_europe_all.set_index('Unnamed: 0', inplace=True)
plot_europe_all.index=pd.to_datetime(plot_europe_all.index)
plot_europe_all.index.name='Date'
leng=len(plot_europe_all)
data=pd.date_range('1985-01-01',periods=leng, freq='MS')
plot_europe_all.index=pd.to_datetime(data)
plot_europe_all.drop(['Unnamed: 1','Unnamed: 9','Unnamed: 17','Unnamed: 25','Unnamed: 33','Unnamed: 41','Unnamed: 49','Unnamed: 57','Unnamed: 65','Unnamed: 73','Unnamed: 81',
                     'Unnamed: 89','Unnamed: 97','Unnamed: 105','Unnamed: 113','Unnamed: 121','Unnamed: 129','Unnamed: 137','Unnamed: 145','Unnamed: 153','Unnamed: 161','Unnamed: 169',
                     'Unnamed: 177','Unnamed: 185','Unnamed: 193','Unnamed: 201','Unnamed: 209','Unnamed: 217','Unnamed: 225','Unnamed: 233','Unnamed: 241','Unnamed: 249','Unnamed: 257','Unnamed: 265',
                     'Unnamed: 273','UK.INDU','UK.SERV','UK.CONS','UK.RETA','UK.BUIL','UK.ESI','UK.EEI'], axis=1,inplace=True)


plot_europe_esi=plot_europe_all[['EU.ESI','EA.ESI','BE.ESI','BG.ESI','CZ.ESI','DK.ESI','DE.ESI','EE.ESI','IE.ESI','EL.ESI','ES.ESI','FR.ESI','HR.ESI','IT.ESI','CY.ESI','LV.ESI','LT.ESI','LU.ESI','HU.ESI','MT.ESI',
                                              'NL.ESI','AT.ESI','PL.ESI','PT.ESI','RO.ESI','SI.ESI','SK.ESI','FI.ESI','SE.ESI','ME.ESI','MK.ESI','AL.ESI','RS.ESI','TR.ESI']]

nr_countries=len(plot_europe_esi.columns.to_list())
plot_europe_esi_diff=plot_europe_esi.diff(1)
plot_europe_esi_diff=plot_europe_esi_diff.T
df_europe_neg=pd.DataFrame(plot_europe_esi_diff[plot_europe_esi_diff < 0 ].count())
df_europe_neg.rename(columns={0:'Slowing'}, inplace=True)
df_europe_pos=pd.DataFrame(plot_europe_esi_diff[plot_europe_esi_diff > 0 ].count())
df_europe_pos.rename(columns={0:'Growing'}, inplace=True)
df_europe_eval=pd.concat([df_europe_pos,df_europe_neg],axis=1)
df_europe_eval['Percentage']=df_europe_eval['Growing']/(df_europe_eval['Growing']+df_europe_eval['Slowing'])
df_europe_eval.drop(['Growing','Slowing'], axis=1, inplace=True)
plot_europe_eval=df_europe_eval.round(2)
#df_europe_eval.style.format("{:.1%}")




europe_part_1 = pd.DataFrame(europe_part_1)
europe_cbbs   = pd.DataFrame(europe_cbbs)
plot_europe_all = pd.DataFrame(plot_europe_all)

# Combine them side by side
plot_europe_all = pd.concat([europe_part_1, europe_cbbs, plot_europe_all], axis=1)

# Replace zeros
if 'EU Consumer' in plot_europe_all.columns:
    plot_europe_all['EU Consumer'] = plot_europe_all['EU Consumer'].replace(0, 0.01)

# Calculate YoY % change (12-month)
yy_europe_list = []
names_europe_list = []

for col in plot_europe_all.columns:
    # Only process numeric columns
    if pd.api.types.is_numeric_dtype(plot_europe_all[col]):
        item = plot_europe_all[col].pct_change(12)
        yy_europe_list.append(item)
        names_europe_list.append(f"{col} YonY")

# Combine back into one DataFrame
plot_europe_yy = pd.concat(yy_europe_list, axis=1)
plot_europe_yy.columns = names_europe_list

plot_europe_yy=pd.DataFrame(yy_europe_list)
plot_europe_yy=plot_europe_yy.T
plot_europe_yy.columns=names_europe_list

europe=pd.concat([plot_europe_all,plot_europe_yy,plot_eu_gdp_q],axis=1)
europe_diff=plot_europe_all.diff(1)
europe_diff.sort_index(ascending=False, inplace=True)
europe_diff.drop(columns=['EU M2 Supply'], inplace=True) # this was removed 'Euro CBBS'
europe_diff_tr=europe_diff['2000':].T



plot_europe_vis=pd.concat([europe_part_1,plot_europe_all[['EU.ESI','EA.ESI','DE.ESI','FR.ESI','IT.ESI','ES.ESI','NL.ESI','SE.ESI','PL.ESI','BE.ESI','AT.ESI','EL.ESI']]],axis=1)
plot_europe_vis.drop(columns='EU M2 Supply',inplace=True)
plot_europe_vis.sort_index(ascending=False, inplace=True)
plot_europe_vis_tr=plot_europe_vis['2000':].T
#del plot_europe_all,plot_europe_yy


###########
europe_yony=europe[['EU PMI YonY','EU Consumer YonY','EU ZEW YonY','DE.ZEW YonY','EU.ESI YonY','EA.ESI YonY','BE.ESI YonY','BG.ESI YonY','DK.ESI YonY','DE.ESI YonY','ES.ESI YonY','FR.ESI YonY','IT.ESI YonY','NL.ESI YonY']]
europe_yony.sort_index(ascending=False,inplace=True)


europe_1 = europe.copy()
# Valid GDP countries + region prefixes
valid_prefixes = ['EA.', 'EU.', 'DE.', 'FR.', 'IT.', 'ES.', 'NL.', 'SE.', 'PL.', 'BE.', 'AT.', 'EL.','EU PMI','EA.ESI YonY', 'EU.ESI YonY', 'DE.ESI YonY', 'FR.ESI YonY', 'IT.ESI YonY', 'ES.ESI YonY', 'NL.ESI YonY', 'SE.ESI YonY', 'PL.ESI YonY', 'BE.ESI YonY', 'AT.ESI YonY', 'EL.ESI YonY'
 'EU NPMI',
 'EU Consumer',
 'EU ZEW',
 'EU M2 Supply',
 'DE.ZEW',
 'Euro CBBS',
 'EU PMI YonY',
 #'EU NPMI YonY',
 'EU Consumer YonY',
 'EU ZEW YonY',
 'EU M2 Supply YonY',
 'DE.ZEW YonY',
 'Euro CBBS YonY',    ]

# Filter columns that start with any of the valid prefixes
filtered_cols = [col for col in europe_1.columns if any(col.startswith(prefix) for prefix in valid_prefixes)]

# Apply the filter
europe_df = europe_1[filtered_cols]
# Substrings to match in column names
columns_to_drop = ['SERV YonY', 'CONS YonY', 'RETA YonY', 'BUIL YonY','EEI YonY','INDU YonY']

# Drop any column that contains one of those substrings
europe_df = europe_df[[col for col in europe_df.columns if not any(sub in col for sub in columns_to_drop)]]







# Uk
small_constant=1
uk_cpi_link = Request('https://www.ons.gov.uk/generator?format=csv&uri=/economy/inflationandpriceindices/timeseries/d7bt/mm23')
uk_cpi_link.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0')
uk_cpi = urlopen(uk_cpi_link)
uk_cpi = pd.read_csv(uk_cpi)
uk_cpi.set_index('Title',inplace=True)
uk_cpi.rename(columns={'CPI INDEX 00: ALL ITEMS 2015=100':'CPI'},inplace=True)
uk_cpi_index=uk_cpi.index.get_loc('1988 JAN')
uk_cpi=uk_cpi[uk_cpi_index:]
uk_cpi_len=len(uk_cpi)
new_date=pd.date_range('1988-01-01',periods=uk_cpi_len, freq='MS')
uk_cpi.index=new_date
uk_cpi['CPI']=uk_cpi['CPI'].astype('float')
uk_unemp_link = Request('https://www.ons.gov.uk/generator?format=csv&uri=/employmentandlabourmarket/peoplenotinwork/unemployment/timeseries/mgsx/lms')
uk_unemp_link.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0')
uk_unemp = urlopen(uk_unemp_link)
uk_unemp = pd.read_csv(uk_unemp)
uk_unemp.set_index('Title',inplace=True)
uk_unemp_index=uk_unemp.index.get_loc('1971 FEB')
uk_unemp=uk_unemp[uk_unemp_index:]
uk_unemp.rename(columns={'Unemployment rate (aged 16 and over, seasonally adjusted): %':'Unemployed'},inplace=True)
uk_unemp_len=len(uk_unemp)
date_uk_unemp=pd.date_range('1971-02-01',periods=uk_unemp_len,freq='MS')
uk_unemp.index=date_uk_unemp
uk_unemp['Unemployed']=uk_unemp['Unemployed'].astype('float')
uk_part_1=pd.read_excel(path,sheet_name='UK')
uk_part_1.set_index('Date',inplace=True)

plot_uk_gdp_q= pd.DataFrame(fred.get_series('NGDPRSAXDCGBQ',frequency ='q',))
row__uk_gdp_q = formatting(plot_uk_gdp_q,'UK GDP Billions',4)
# Assuming 'plot_usa_gdp_q' is already created and formatted
plot_uk_gdp_q['UK GDP QonQ'] = plot_uk_gdp_q['UK GDP Billions'].pct_change()

# Calculate annualized quarter-on-quarter growth
plot_uk_gdp_q['UK GDP QonQ Annualized'] = ((1 + plot_uk_gdp_q['UK GDP QonQ']) ** 4 - 1) * 100

uk=pd.concat([uk_part_1,uk_cpi,uk_unemp,plot_uk_gdp_q],axis=1)
uk_yy_list=[]
names_uk_list=[]


uk['UK GFK'] = uk['UK GFK'].replace(0, 0.1)
uk_yy_list=[]
names_uk_list=[]
# Calculate the year-on-year change with a small constant added to denominator only when denominator is not zero or -1




uk_yy_list = []
names_uk_list = []
for col in uk.columns:
    denominator = uk[col].shift(12)
    denominator_zero_or_negative = (denominator == 0) | (denominator == -1)
    item = uk[col].pct_change(12)
    item[~denominator_zero_or_negative] /= (denominator[~denominator_zero_or_negative] + small_constant)
    uk_yy_list.append(item)
    names_uk_list.append(f'{col} YonY')

uk_yy = pd.DataFrame(uk_yy_list).T
uk_yy.columns = names_uk_list
uk = pd.concat([uk, uk_yy], axis=1)


# Ensure the main DataFrame (uk) index is timezone-aware
if uk.index.tz is None:
    uk.index = uk.index.tz_localize("UTC")  # Localize to UTC if naive
else:
    uk.index = uk.index.tz_convert("UTC")   # Convert to UTC if already timezone-aware

# Ensure 'UK NPMI' index is timezone-aware
if uk['UK NPMI'].index.tz is None:
    uk['UK NPMI'].index = uk['UK NPMI'].index.tz_localize("UTC")
else:
    uk['UK NPMI'].index = uk['UK NPMI'].index.tz_convert("UTC")

# Ensure 'UK PMI' index is timezone-aware
if uk['UK PMI'].index.tz is None:
    uk['UK PMI'].index = uk['UK PMI'].index.tz_localize("UTC")
else:
    uk['UK PMI'].index = uk['UK PMI'].index.tz_convert("UTC")

# Now, safely add them
uk['UK COMPOSITE'] = (uk['UK NPMI'] + uk['UK PMI'])/2
uk.index = uk.index.tz_convert(None)  # Remove timezone from UK 




plot_nfib =  pd.read_excel(path,sheet_name='SMB')
row_nfib = formatting(plot_nfib ,'SMB',12)
plot_nfib.set_index('Date', inplace=True)
plot_nfib.index = pd.to_datetime(plot_nfib.index, format='%Y/%m/%d', errors='coerce')

plot_pmi=pd.read_excel(path, sheet_name='PMI')
plot_pmi.set_index('Date', inplace=True)
plot_npmi=pd.read_excel(path, sheet_name='NPMI')
plot_npmi.set_index('Date', inplace=True)
plot_umcsi=pd.read_csv('http://www.sca.isr.umich.edu/files/tbmiccice.csv')
plot_umcsi=plot_umcsi[92:]
len_umcsi=len(plot_umcsi)
date=pd.date_range('1978-01-01', periods=len_umcsi, freq='MS')
plot_umcsi.index=date
plot_umcsi.drop(columns=['Month','YYYY','ICC'], inplace=True)
plot_umcsi['UMCSI']=plot_umcsi['ICE']
plot_umcsi.drop(columns='ICE', inplace=True)
row_umcsi_m=formatting(plot_umcsi,'UMCSI',12)

plot_umcsi_inflation=pd.read_csv('http://www.sca.isr.umich.edu/files/tbmpx1px5.csv')
len_umcsi_inflation=len(plot_umcsi_inflation)
date=pd.date_range('1978-01-01', periods=len_umcsi_inflation, freq='MS')
plot_umcsi_inflation.drop(columns=['Month','YYYY','PX5_MD'],inplace=True)
plot_umcsi_inflation.rename(columns={'PX_MD':'UMCSI inf EXP'},inplace=True)
plot_umcsi_inflation.index=date
row_umcsi_m_inflation=formatting(plot_umcsi_inflation,'UMCSI inf EXP',12)
plot_bp_m = pd.DataFrame(fred.get_series('PERMIT'))                        # Permit-Issuing Total Places Monthly
row_bp_m = formatting(plot_bp_m,'B Permits',12)
t.sleep(1)
plot_b_starts_m = pd.DataFrame(fred.get_series('HOUST'))                        # Permit-Issuing Total Places Monthly
row_b_starts_m = formatting(plot_b_starts_m,'B Starts',12)
t.sleep(1)
plot_2Y_yield = pd.DataFrame(fred.get_series('DGS2',frequency='m'))  # Treasury Securities at 2-Year Constant Maturity, Quoted on an Investment Basis (DGS2)
row_2Y_yield = formatting_pct(plot_2Y_yield ,'2 Year Note',12)
t.sleep(1)
plot_10Y_yield=pd.DataFrame(fred.get_series('DGS10',frequency='m'))     # 10-Year Treasury Constant Maturity
row_10Y_yield=formatting(plot_10Y_yield,'10 Year Note',12)

t.sleep(1)
# weekly items Usa
plot_10Y2Y_w = pd.DataFrame(fred.get_series('T10Y2Y', frequency='w'))      # 10-Year Treasury Constant Maturity Minus 2-Year Treasury Constant Maturity Weekly
row_10Y2Y_w=formatting(plot_10Y2Y_w,'T10Y2Y w',12)
t.sleep(1)
plot_10Y3M_w= pd.DataFrame(fred.get_series('T10Y3M',  frequency='w'))      # 10-Year Treasury Constant Maturity Minus 3-Month Treasury Constant Maturity Weekly
row_10y3M_w=formatting(plot_10Y3M_w,'T10Y3M w',12)

plot_cbbs = pd.DataFrame(fred.get_series('WALCL',frequency='m'))                       # Assets: Total Assets: Total Assets (Less Eliminations from Consolidation): Wednesday Level Weekly
row_usa_cbbs=formatting(plot_cbbs,'Usa CBBS',12)
t.sleep(1)
plot_cbbs_weekly = pd.DataFrame(fred.get_series('WALCL',frequency='w'))                       # Assets: Total Assets: Total Assets (Less Eliminations from Consolidation): Wednesday Level Weekly
row_usa_cbbs=formatting(plot_cbbs_weekly,'Usa CBBS',52)
#plot_cbbs_weekly.rename(columns={0:'Usa CBBS'}, inplace=True)
plot_cbbs_weekly['Usa CBBS Y on Y Weekly']=plot_cbbs_weekly.pct_change(52).round(2)
plot_cbbs_weekly['Usa CBBS Change Weekly']=(plot_cbbs_weekly['Usa CBBS'].pct_change(1)*100).round(3)
t.sleep(1)
plot_treasury_weekly = pd.DataFrame(fred.get_series('TREAST',frequency='w'))                       # Assets: Total Assets: Total Assets (Less Eliminations from Consolidation): Wednesday Level Weekly
row_usa_treasury=formatting(plot_treasury_weekly,'TREASURY FED',52)
#plot_cbbs_weekly.rename(columns={0:'Usa CBBS'}, inplace=True)
plot_treasury_weekly['USA Treasury Y on Y Weekly']=plot_treasury_weekly.pct_change(52).round(2)
plot_treasury_weekly['USA Treasury Change Weekly']=(plot_treasury_weekly['TREASURY FED'].pct_change(1)*100).round(3)
t.sleep(1)
plot_banks_dep_w=pd.DataFrame(fred.get_series('DPSACBW027SBOG',frequency='w'))
row_banks_dep=formatting(plot_banks_dep_w,'Usa Bank Dep',52)
#plot_banks_dep_w.rename(columns={0:'Usa Bank Dep'}, inplace=True)
plot_banks_dep_w['Usa Bank Dep Y on Y Weekly']=plot_banks_dep_w.pct_change(52).round(2)
plot_banks_dep_w['Usa Bank Dep Change Weekly']=(plot_banks_dep_w['Usa Bank Dep'].pct_change(1)*100).round(3)
t.sleep(1)
# Corporate Bonds
plot_corp_bond_aaa_d=pd.DataFrame(fred.get_series('BAMLC0A1CAAAEY',frequency='d'))
row_corp_bond_aaa_d=formatting(plot_corp_bond_aaa_d,'Usa AAA Corp Bond',365)

plot_corp_bond_aaa_m=pd.DataFrame(fred.get_series('BAMLC0A1CAAAEY',frequency='m'))
row_corp_bond_aaa_m=formatting(plot_corp_bond_aaa_m,'Usa AAA Corp Bond',12)
t.sleep(1)
plot_corp_bond_bbb_d=pd.DataFrame(fred.get_series('BAMLC0A4CBBBEY',frequency='d'))
row_corp_bond_bbb_d=formatting(plot_corp_bond_bbb_d,'Usa BBB Corp Bond',365)

plot_corp_bond_bbb_m=pd.DataFrame(fred.get_series('BAMLC0A4CBBBEY',frequency='m'))
row_corp_bond_bbb_m=formatting(plot_corp_bond_bbb_m,'Usa BBB Corp Bond',12)
t.sleep(1)
plot_corp_bond_ccc_d=pd.DataFrame(fred.get_series('BAMLH0A3HYCEY',frequency='d'))
row_corp_bond_ccc_d=formatting(plot_corp_bond_ccc_d,'Usa CCC Corp Bond',365)
plot_corp_bond_ccc_m=pd.DataFrame(fred.get_series('BAMLH0A3HYCEY',frequency='m'))
row_corp_bond_ccc_m=formatting(plot_corp_bond_ccc_m,'Usa CCC Corp Bond',12)
t.sleep(1)
plot_corp_bond_aaa_vs_ccc_m = pd.concat([plot_corp_bond_aaa_m, plot_corp_bond_ccc_m], axis=1).dropna()
plot_corp_bond_aaa_m = plot_corp_bond_aaa_vs_ccc_m.iloc[:, 0]
plot_corp_bond_ccc_m = plot_corp_bond_aaa_vs_ccc_m.iloc[:, 1]
plot_corp_bond_aaa_vs_ccc_m = (plot_corp_bond_aaa_m - plot_corp_bond_ccc_m).to_frame()
plot_corp_bond_aaa_vs_ccc_m.rename(columns={plot_corp_bond_aaa_vs_ccc_m.columns[0]: "USA Corp Bond AAA-CCC"}, inplace=True)

plot_banks_dep_m=pd.DataFrame(fred.get_series('DPSACBW027SBOG',frequency='m'))
row_banks_dep_m=formatting(plot_banks_dep_m,'Usa Bank Dep',12)
t.sleep(1)
plot_m2 = pd.DataFrame(fred.get_series('WM2NS',frequency='m'))                         # M2 on a monthly bases weekly end of the month
row_usa_m2 = formatting_pct(plot_m2,'M2 Supply',12)

plot_10Y2Y_m= pd.DataFrame(fred.get_series('T10Y2Y', frequency='m'))         # 10-Year Treasury Constant Maturity Minus 2-Year Treasury Constant Maturity
plot_10Y2Y_m.rename(columns={0:'10Y-2Y'}, inplace=True)
t.sleep(1)
plot_usa_gdp_q = pd.DataFrame(fred.get_series('GDPC1')) 
plot_usa_gdp_q['USA GDP Q'] = (plot_usa_gdp_q.pct_change(1))*100


t.sleep(1)
plot_10Y3M_m= pd.DataFrame(fred.get_series('T10Y3M',  frequency='m'))      # 10-Year Treasury Constant Maturity Minus 2-Year Treasury Constant Maturity 
plot_10Y3M_m.rename(columns={0:'10Y-3M'}, inplace=True)
t.sleep(1)
plot_oil_usa=pd.DataFrame(fred.get_series('DCOILWTICO',frequency='m'))  # Crude Oil
row_oil_usa=formatting(plot_oil_usa,'Usa Oil',12)
plot_gas_gallon = pd.DataFrame(fred.get_series('GASREGW',frequency='m')) 
row_gas_gallon = formatting_pct(plot_gas_gallon,'Gas / Gallon',12)                     
t.sleep(1)
plot_copper= pd.DataFrame(fred.get_series('PCOPPUSDM',frequency='m'))
row_copper=formatting(plot_copper,'Copper',12)
plot_cpi_inc = pd.DataFrame(fred.get_series('CPIAUCSL')) 
row_cpi_inc = formatting_pct(plot_cpi_inc,'CPI inc',12)
t.sleep(1)
plot_cpi_ex = pd.DataFrame(fred.get_series('CPILFESL'))                    # Consumer Price Index for All Urban Consumers: All Items Less Food and Energy in U.S. City Average
row_cpi_ex = formatting_pct(plot_cpi_ex,'CPI ex',12)
plot_ppi_inc = pd.DataFrame(fred.get_series('WPSFD49207'))
row_ppi_inc = formatting_pct(plot_ppi_inc,'PPI inc',12)
t.sleep(1)
plot_ppi_ex = pd.DataFrame(fred.get_series('WPSFD4131'))                   # Producer Price Index by Commodity: Final Demand: Finished Goods Less Foods and Energy
row_ppi_ex = formatting_pct(plot_ppi_ex,'PPI ex',12)
t.sleep(1)
plot_job_claims_w= pd.DataFrame(fred.get_series('ICSA'))                   # Initial Jobless Claims Weekly
row_job_claims_w = formatting_pct(plot_job_claims_w,'Jobless Claims',12)
plot_jobless_claims = pd.DataFrame(fred.get_series('ICSA',frequency ='m'))
row_jobless_claims = formatting(plot_jobless_claims,'Usa Jobless Claims',12)
t.sleep(1)
plot_nfp_all = pd.DataFrame(fred.get_series('PAYEMS'))      # All Employees, Total Nonfarm First Fri of the Month
row_nfp_all = formatting_pct(plot_nfp_all,'NFProll',12)

plot_nfp_all['NFPR DIFF'] = plot_nfp_all['NFProll'].diff()
plot_job_open = pd.DataFrame(fred.get_series('JTSJOL'))                    # Job Openings: Total Nonfarm
row_job_open = formatting_pct(plot_job_open,'Open Jobs',12)

t.sleep(1)
plot_dur_g_new_ord_value_ship = pd.DataFrame(fred.get_series('AMDMVS')) 
row_dur_g_new_ord_value_ship = formatting_pct(plot_dur_g_new_ord_value_ship,'DG Value of Shipments',12)
t.sleep(1)


plot_dur_g_new_ord_customer_goods = pd.DataFrame(fred.get_series('ACDGNO')) 
row_dur_g_new_ord_customer_goods = formatting_pct(plot_dur_g_new_ord_customer_goods,'DG Consumer Goods',12)
t.sleep(1)
plot_dur_g_new_ord_customer_goods_ex_transport = pd.DataFrame(fred.get_series('ADXTNO')) 
row_dur_g_new_ord_customer_goods_ex_transport = formatting_pct(plot_dur_g_new_ord_customer_goods_ex_transport,'DG Consumer Goods Ex Transp',12)
plot_dur_g_new_ord_customer_goods_ex_defense = pd.DataFrame(fred.get_series('ADXDNO')) 
row_dur_g_new_ord_customer_goods_ex_defense = formatting_pct(plot_dur_g_new_ord_customer_goods_ex_defense,'DG Consumer Goods Ex Defense',12)
t.sleep(1)

plot_dur_g_new_ord_manufacturing_unfill  = pd.DataFrame(fred.get_series('AMTUNO')) 
row_dur_g_new_ord_manufacturing_unfill = formatting_pct(plot_dur_g_new_ord_manufacturing_unfill,'DG Manufacturing UFilled Orders',12)


plot_dur_g_new_ord_machinery  = pd.DataFrame(fred.get_series('A33SNO')) 
row_dur_g_new_ord_machinery = formatting_pct(plot_dur_g_new_ord_machinery,'DG Machinery',12)
t.sleep(1)
plot_dur_g_new_ord_computer_elec_products  = pd.DataFrame(fred.get_series('A34SNO')) 
row_dur_g_new_ord_computer_elec_products = formatting_pct(plot_dur_g_new_ord_computer_elec_products,'DG Computer and Elec',12)
plot_dur_g_new_ord_fab_metal = pd.DataFrame(fred.get_series('A32SNO')) 
row_dur_g_new_ord_fab_metal = formatting_pct(plot_dur_g_new_ord_fab_metal,'DG Fab metal',12)
t.sleep(1)
plot_dur_g_new_ord_primary_metal = pd.DataFrame(fred.get_series('A31SNO')) 
row_dur_g_new_ord_primary_metal = formatting_pct(plot_dur_g_new_ord_primary_metal,'DG Primary metal',12)

plot_dur_g_new_ord_transportation = pd.DataFrame(fred.get_series('A36SNO')) 
row_dur_g_new_ord_transportation = formatting_pct(plot_dur_g_new_ord_transportation,'DG Transportation Equ',12)

t.sleep(1)
plot_pce_goods = pd.DataFrame(fred.get_series('DGDSRC1')) 
row_pce_goods = formatting_pct(plot_pce_goods,'PCE Goods',12)
plot_pce_services = pd.DataFrame(fred.get_series('PCES')) 
row_pce_services = formatting_pct(plot_pce_services,'PCE Services',12)
t.sleep(1)
plot_pce_durable_goods = pd.DataFrame(fred.get_series('PCEDG')) 
row_pce_durable_goods = formatting_pct(plot_pce_durable_goods,'PCE Durable Goods',12)
plot_pce_non_durable_goods = pd.DataFrame(fred.get_series('PCEND')) 
row_pce_non_durable_goods = formatting_pct(plot_pce_non_durable_goods,'PCE Non Durable Goods',12)

t.sleep(1)
plot_vehicle_parts=pd.DataFrame(fred.get_series('IPG3361T3S',frequency='m')) 
row_vehicle_parts=formatting(plot_vehicle_parts,' IP Motor Vehicles and Parts',12)
plot_indu_pro = pd.DataFrame(fred.get_series('IPMAN'))                     # Industrial Production: Manufacturing (NAICS)
row_indu_pro = formatting_pct(plot_indu_pro,'Indu Prodction',12)
t.sleep(1)
plot_oil_gas = pd.DataFrame(fred.get_series('IPG211S', frequency='m'))
row_oil_gas = formatting(plot_oil_gas, 'IP Oil and Gas Extraction', 12)

# Point 3: Utilities (Electric Power Generation)
plot_utilities = pd.DataFrame(fred.get_series('IPUTIL', frequency='m'))
row_utilities = formatting(plot_utilities, 'IP Utilities (Electric Power)', 12)
t.sleep(1)
# Point 4: Chemicals
plot_chemicals = pd.DataFrame(fred.get_series('IPG325S', frequency='m'))
row_chemicals = formatting(plot_chemicals, 'IP Chemicals', 12)
t.sleep(1)
# Point 5: Machinery
plot_machinery = pd.DataFrame(fred.get_series('IPG333S', frequency='m'))
row_machinery = formatting(plot_machinery, 'IP Machinery', 12)
t.sleep(1)

# usa Interest Rate
plot_usa_rate = pd.DataFrame(fred.get_series('DFF', frequency='m'))
row_usa_rate=formatting(plot_usa_rate,'Usa IR',12)
plot_gbp_usd= pd.DataFrame(fred.get_series('DEXUSUK',frequency='m'))
row_gbp_usd=formatting(plot_gbp_usd,'GBP_USD',12)
t.sleep(1)
plot_eur_usd=pd.DataFrame(fred.get_series('DEXUSEU',frequency='m')) # EUR/USD
row_eur_usd=formatting(plot_eur_usd,'EUR_USD',12)
plot_gas=pd.DataFrame(fred.get_series('PNGASUSUSDM',frequency='m')) # Natural Gas
row_gas=formatting(plot_gas,'N Gas',12)
t.sleep(1)
plot_dxy=pd.DataFrame(fred.get_series('RTWEXBGS',frequency='m')) # DXY
row_dxy=formatting(plot_dxy,'DXY',12)
plot_aluminum=pd.DataFrame(fred.get_series('PALUMUSDM',frequency='m')) # Aluminum
row_aluminum=formatting(plot_aluminum,'Aluminum',12)

t.sleep(1)
# incorporate weeky data 
usa_1_month_bond=pd.DataFrame(fred.get_series('DGS1MO',frequency='w'))
row_usa_1_month_bond=formatting(usa_1_month_bond,'USA 1M Note',52)

usa_3_month_bond=pd.DataFrame(fred.get_series('DGS3MO',frequency='w'))
row_usa_3_month_bond=formatting(usa_3_month_bond,'USA 3M Note',52)
t.sleep(1)
usa_6_month_bond=pd.DataFrame(fred.get_series('DGS6MO',frequency='w'))
row_usa_6_month_bond=formatting(usa_6_month_bond,'USA 6M Note',52)



usa_1_year_bond=pd.DataFrame(fred.get_series('DGS1',frequency='w'))
row_usa_1_year_bond=formatting(usa_1_year_bond,'USA 1Y Note',52)
t.sleep(1)
usa_2_year_bond=pd.DataFrame(fred.get_series('DGS2',frequency='w'))
row_usa_2_year_bond=formatting(usa_2_year_bond,'USA 2Y Note',52)

usa_3_year_bond=pd.DataFrame(fred.get_series('DGS3',frequency='w'))
row_usa_3_year_bond=formatting(usa_3_year_bond,'USA 3Y Note',52)
t.sleep(1)
usa_5_year_bond=pd.DataFrame(fred.get_series('DGS5',frequency='w'))
row_usa_5_year_bond=formatting(usa_5_year_bond,'USA 5Y Note',52)

usa_7_year_bond=pd.DataFrame(fred.get_series('DGS7',frequency='w'))
row_usa_7_year_bond=formatting(usa_7_year_bond,'USA 7Y Note',52)
t.sleep(1)
usa_10_year_bond=pd.DataFrame(fred.get_series('DGS10',frequency='w'))
row_usa_10_year_bond=formatting(usa_10_year_bond,'USA 10Y Note',52)

usa_20_year_bond=pd.DataFrame(fred.get_series('DGS20',frequency='w'))
row_usa_20_year_bond=formatting(usa_20_year_bond,'USA 20Y Note',52)
t.sleep(1)
usa_30_year_bond=pd.DataFrame(fred.get_series('DGS30',frequency='w'))
row_usa_30_year_bond=formatting(usa_30_year_bond,'USA 30Y Note',52)
usa_yield_curve=pd.concat([usa_1_month_bond['USA 1M Note'],usa_3_month_bond['USA 3M Note'],usa_6_month_bond['USA 6M Note'],
                           usa_1_year_bond['USA 1Y Note'],usa_2_year_bond['USA 2Y Note'],usa_3_year_bond['USA 3Y Note'],usa_5_year_bond['USA 5Y Note'],usa_7_year_bond['USA 7Y Note'],usa_10_year_bond['USA 10Y Note'],usa_20_year_bond['USA 20Y Note'],usa_30_year_bond['USA 30Y Note']],axis=1)

# Resample to month-end frequency using last available value in the month
usa_yield_curve_monthly = usa_yield_curve.resample('ME').last()

plot_usa_gdp_q= pd.DataFrame(fred.get_series('GDP',frequency ='q',))
row__usa_gdp_q = formatting(plot_usa_gdp_q,'Usa GDP Billions',4)
# Assuming 'plot_usa_gdp_q' is already created and formatted
plot_usa_gdp_q['Usa GDP QonQ'] = plot_usa_gdp_q['Usa GDP Billions'].pct_change()

# Calculate annualized quarter-on-quarter growth
plot_usa_gdp_q['Usa GDP QonQ Annualized'] = ((1 + plot_usa_gdp_q['Usa GDP QonQ']) ** 4 - 1) * 100


plot_total_const_m=pd.DataFrame(fred.get_series('TTLCONS',frequency='m'))
row_total_const_m=formatting(plot_total_const_m,'USA_Construction Spending',12)
t.sleep(1)
plot_consumer_credit_m=pd.DataFrame(fred.get_series('TOTALSL',frequency='m'))
row_consumer_credit_m=formatting(plot_consumer_credit_m,'USA_Cons_Credit_Out',12)
plot_savings_m=pd.DataFrame(fred.get_series('PSAVERT',frequency='m'))
row_savnigs_m=formatting(plot_savings_m,'USA_Savings_usa',12)
t.sleep(1)



zinc=pd.DataFrame(fred.get_series('PZINCUSDM',frequency='m')) 
row_zinc=formatting(zinc,'Zinc',12)

usa_yield_curve.sort_index(ascending=False, inplace=True)
usa_yield_curve=usa_yield_curve.head(500)
usa_yield_curve_tr=usa_yield_curve.T
usa_yield_curve_tr.dropna(axis=1, how='all', inplace=True)
usa_yield_curve_tr_0mo_past=usa_yield_curve_tr.columns.to_list()[0]
usa_yield_curve_tr_1week_past=usa_yield_curve_tr.columns.to_list()[1]
usa_yield_curve_tr_3mo_past=usa_yield_curve_tr.columns.to_list()[13]
usa_yield_curve_tr_6mo_past=usa_yield_curve_tr.columns.to_list()[26]
usa_yield_curve_tr_9mo_past=usa_yield_curve_tr.columns.to_list()[39]
usa_yield_curve_tr_12mo_past=usa_yield_curve_tr.columns.to_list()[52]
usa_yield_curve_tr_chart=usa_yield_curve_tr.reindex(columns=[usa_yield_curve_tr_0mo_past,usa_yield_curve_tr_1week_past,usa_yield_curve_tr_3mo_past,usa_yield_curve_tr_6mo_past,usa_yield_curve_tr_9mo_past,usa_yield_curve_tr_12mo_past])
usa_yield_curve_tr.style.background_gradient(axis=1,cmap='RdYlGn').format("{:.5}")






plot_mmf_fred_q = pd.DataFrame(fred.get_series('MMMFFAQ027S', frequency='q'))
plot_mmf_fred_q.columns = ['Total MMF FRED']
plot_mmf_fred_q.index = pd.date_range(start=plot_mmf_fred_q.index.min(), periods=len(plot_mmf_fred_q), freq='QS')
plot_mmf_fred_q['Total MMF FRED Y on Y'] = plot_mmf_fred_q['Total MMF FRED'].pct_change(4).round(3)

usa_yield_curve_tr_chart.rename(columns={usa_yield_curve_tr_0mo_past:'Today',usa_yield_curve_tr_1week_past:'Last Week',usa_yield_curve_tr_3mo_past:'3 Months Ago',usa_yield_curve_tr_6mo_past:'6 Months Ago',usa_yield_curve_tr_9mo_past:'9 Months Ago',usa_yield_curve_tr_12mo_past:'12 Months Ago'}, inplace=True)


plot_usa_unemployment_rate=pd.DataFrame(fred.get_series('UNRATE',frequency='m'))
row_usa_unemployment_rate=formatting(plot_usa_unemployment_rate,'Usa Unemployment Rate',12)




def make_index_unique(df):
    df = df.copy()
    df = df[~df.index.duplicated(keep='first')]
    return df


plot_pmi=pd.read_excel(path, sheet_name='PMI')
plot_pmi.set_index('Date', inplace=True)
plot_npmi=pd.read_excel(path, sheet_name='NPMI')
plot_npmi.set_index('Date', inplace=True)



#plot_gscpi,

dataframes = [
    plot_2Y_yield, plot_10Y_yield, plot_10Y2Y_m, plot_10Y3M_m, plot_pmi, plot_npmi,
    plot_umcsi, plot_umcsi_inflation, plot_bp_m, plot_b_starts_m, plot_cpi_inc,
    plot_cpi_ex, plot_ppi_inc, plot_ppi_ex, plot_indu_pro, plot_nfp_all['NFPR DIFF'],
    plot_job_open, plot_usa_rate, plot_cbbs, plot_m2, plot_oil_usa, plot_gas,
    plot_gas_gallon, plot_copper, plot_aluminum, plot_dxy, plot_gbp_usd, plot_eur_usd,
     plot_banks_dep_m, plot_vehicle_parts, zinc, plot_pce_goods,
    plot_pce_services, plot_pce_durable_goods, plot_pce_non_durable_goods,
    plot_jobless_claims, plot_usa_gdp_q, plot_corp_bond_aaa_m, plot_corp_bond_bbb_m,
    plot_corp_bond_aaa_vs_ccc_m, plot_nfib, plot_oil_gas, plot_dur_g_new_ord_value_ship,
    plot_dur_g_new_ord_customer_goods, plot_dur_g_new_ord_customer_goods_ex_transport,
    plot_dur_g_new_ord_customer_goods_ex_defense, plot_dur_g_new_ord_manufacturing_unfill,
    plot_dur_g_new_ord_machinery, plot_dur_g_new_ord_computer_elec_products,
    plot_dur_g_new_ord_fab_metal, plot_dur_g_new_ord_primary_metal,
    plot_dur_g_new_ord_transportation, plot_utilities, plot_chemicals, plot_machinery,
    plot_usa_unemployment_rate,plot_total_const_m,plot_consumer_credit_m,plot_savings_m,
]

# Clean each DataFrame’s index
dataframes = [make_index_unique(df) if isinstance(df, pd.DataFrame) else make_index_unique(df.to_frame()) for df in dataframes]

# Concatenate
usa = pd.concat(dataframes, axis=1)



usa['G-S'] = (plot_pce_goods['PCE Goods']-plot_pce_services['PCE Services'])

usa.sort_index(ascending=True,inplace=True)

usa_yy_list=[]
names_usa_list=[]
usa["PMI_Spread_NewOrders_Inv"] = usa["PMI New Orders"] - usa["PMI Inventories"]
usa["PMI_Spread_Backlog_Inv"] = usa["PMI Backlog of Orders"] - usa["PMI Inventories"]
usa["PMI_Spread_Supplier_Inv"] = usa["PMI Supplier Deliveries"] - usa["PMI Inventories"]
usa["PMI_Spread_Orders_Exports"] = usa["PMI New Orders"] - usa["PMI New Export Orders"]
usa["PMI_Spread_Consumption_Inputs"] = usa["PMI Consumption"] - usa["PMI Inputs"]

# Core NPMI Spreads
usa["NPMI_Spread_NewOrders_Inv"] = usa["NPMI New Orders"] - usa["NPMI Inventories"]
usa["NPMI_Spread_Backlog_Inv"] = usa["NPMI Backlog of Orders"] - usa["NPMI Inventories"]
usa["NPMI_Spread_Supplier_Inv"] = usa["NPMI Supplier Deliveries"] - usa["NPMI Inventories"]

# Optional / secondary NPMI spreads
usa["NPMI_Spread_Orders_Exports"] = usa["NPMI New Orders"] - usa["NPMI New Export Orders"]
usa["NPMI_Spread_Consumption_Inputs"] = usa["NPMI Business Activity"] - usa["NPMI Inputs"]

for col in usa.columns:
    item = usa[col].pct_change(12)
    usa_yy_list.append(item)
    names_usa_list.append(f'{col} YonY')
    

usa_yy=pd.DataFrame(usa_yy_list)
usa_yy = usa_yy
usa_yy=usa_yy.T
usa_yy.columns=names_usa_list
usa=pd.concat([usa,usa_yy],axis=1)
usa
usa['PPI - CPI']=usa['PPI inc YonY']-usa['CPI inc YonY']
usa['Spread 2Y/10Y']=(usa['2 Year Note']/usa['10 Year Note']).round(2)
usa.sort_index(ascending=True,inplace=True)
usa = usa.apply(lambda x: x.tz_localize(None) if x.dtype == 'datetime64[ns, UTC]' else x)







stock_gspc_quarterly=pd.DataFrame(yf.download("^GSPC", period='max', interval='3mo')['Close']).round(2)
stock_gspc_quarterly.rename(columns={'Close':'^GSPC'}, inplace=True)
stock_gspc_quarterly['Returns']=stock_gspc_quarterly.pct_change(1).round(2)

stock_gspc_monthly=pd.DataFrame(yf.download("^GSPC",period='max', interval='1mo')['Close']).round(2)
stock_gspc_monthly.rename(columns={'Close':'^GSPC'}, inplace=True)
stock_gspc_monthly['Returns']=stock_gspc_monthly['^GSPC'].pct_change(1).round(2)
stock_gspc_monthly['^GSPC Y on Y']=stock_gspc_monthly['^GSPC'].pct_change(12).round(2)
stock_gspc_daily=pd.DataFrame(yf.download("^GSPC",start='2016-01-01',end=f'{today}', interval='1d')['Close']).round(2)
stock_gspc_daily.rename(columns={'Close':'^GSPC'}, inplace=True)
df_usa_leading=usa[['PMI','NPMI','UMCSI','B Permits','PMI New Orders','PMI Consumption','PMI Inputs','PMI Prices','PMI Customers Inventories','NPMI Business Activity','NPMI New Orders','NPMI Prices']].round(2)

df_usa_leading.sort_index(ascending=False, inplace=True)
df_usa_leading_tr=df_usa_leading[:-610].T # around 1998
########################
usa_current_indi = pd.concat([
        usa['DG Value of Shipments'],
    usa['DG Transportation Equ'],
    usa['DG Computer and Elec'],
    usa['DG Consumer Goods'],
    usa['DG Consumer Goods Ex Transp'],
    usa['DG Consumer Goods Ex Defense'],
    usa['DG Fab metal'],
    usa['DG Primary metal'],
    usa['DG Machinery'],
    usa['DG Manufacturing UFilled Orders']
],axis = 1)
usa_current_indi.sort_index(ascending=False, inplace=True)
usa_current_indi_tr = usa_current_indi[:-650].T

df_usa_pct_change = pd.concat([
    usa['CPI inc YonY'],
    usa['PPI inc YonY'],
    usa['PPI - CPI'],
    usa['UMCSI inf EXP'] / 100,  # Ensuring proper division
    usa['Indu Prodction YonY'],
    usa['2 Year Note'] / 100,
    usa['Usa IR'] / 100,
    usa['10 Year Note'] / 100,
], axis=1)


df_usa_pct_change.sort_index(ascending=False, inplace=True)
df_usa_pct_change_tr=df_usa_pct_change[:-650].T

world_all=pd.concat([usa,europe['EU PMI YonY'],europe['EU PMI'],europe['EU Consumer'],europe['EU Consumer YonY'],europe['DE.ZEW'],
                     europe['DE.ZEW YonY'],europe['EU ZEW'],europe['EU ZEW YonY'],europe['EA.ESI'],europe['EA.ESI YonY'],europe['EU M2 Supply YonY'],uk,],axis=1)


# better version

# leading indicators from the world put in to one df and y on y applied for next stage
usa_db_diff=pd.concat([plot_pmi,plot_npmi,plot_umcsi,plot_bp_m,plot_m2,plot_oil_usa,plot_gas,plot_gas_gallon,
               plot_copper,plot_aluminum,plot_dxy,plot_gbp_usd,plot_eur_usd,plot_europe_vis,uk['UK PMI'],uk['UK NPMI'],uk['UK GFK'],uk['UK M Approvals']],axis=1)

new_world_all=world_all[['2 Year Note YonY',
 '10 Year Note YonY',
 '10Y-2Y YonY',
 '10Y-3M YonY',
 'PMI YonY',
 'PMI New Orders YonY',
 'PMI Production YonY',
 'PMI Employment YonY',
 'PMI Supplier Deliveries YonY',
 'PMI Inventories YonY',
 'PMI Customers Inventories YonY',
 'PMI Prices YonY',
 'PMI Backlog of Orders YonY',
 'PMI New Export Orders YonY',
 'PMI Imports YonY',
 'PMI Consumption YonY',
 'PMI Inputs YonY',
 'NPMI YonY',
 'NPMI Business Activity YonY',
 'NPMI New Orders YonY',
 'NPMI Employment YonY',
 'NPMI Supplier Deliveries YonY',
 'NPMI Inventories YonY',
 'NPMI Prices YonY',
 'NPMI Backlog of Orders YonY',
 'NPMI New Export Orders YonY',
 'NPMI Imports YonY',
 'NPMI Inventory Sentiment YonY',
 'NPMI Inputs YonY',
 'UMCSI YonY',
 'UMCSI inf EXP YonY',
 'B Permits YonY',
 'B Starts YonY',
 'Usa CBBS YonY',
 'M2 Supply YonY',
 'EU PMI',
 'EU PMI YonY',
 #'EU NPMI YonY',
 'EU Consumer',
 'DE.ZEW',
 'DE.ZEW YonY',
 'EU ZEW',
 'EU ZEW YonY',
 'EA.ESI',
 'EA.ESI YonY',
 'EU M2 Supply YonY',
 'UK PMI',
 'UK NPMI',
 'UK GFK',
 'UK M Approvals YonY',
 'UK PMI YonY',
 'UK NPMI YonY'

]]



usa_exp = usa[['2 Year Note',
 '10 Year Note',
 '10Y-2Y',
 '10Y-3M',
 'PMI',
 'PMI New Orders',
 'PMI Production',
 'PMI Employment',
 'PMI Supplier Deliveries',
 'PMI Inventories',
 'PMI Customers Inventories',
 'PMI Prices',
 'PMI Backlog of Orders',
 'PMI New Export Orders',
 'PMI Imports',
 'PMI Consumption',
 'PMI Inputs',
 'NPMI',
 'NPMI Business Activity',
 'NPMI New Orders',
 'NPMI Employment',
 'NPMI Supplier Deliveries',
 'NPMI Inventories',
 'NPMI Prices',
 'NPMI Backlog of Orders',
 'NPMI New Export Orders',
 'NPMI Imports',
 'NPMI Inventory Sentiment',
 'NPMI Inputs',
 'UMCSI',
 'UMCSI inf EXP',
 'B Permits',
 'B Starts',
 'CPI inc',
 'CPI ex',
 'PPI inc',
 'PPI ex',
 'Indu Prodction',
 'NFPR DIFF',
 'Open Jobs',
 'Usa IR',
 'Usa CBBS',
 'M2 Supply',
 'Usa Oil',
 'N Gas',
 'Gas / Gallon',
 'Copper',
 'Aluminum',
 'DXY',
 'GBP_USD',
 'EUR_USD',
 #'GSCPI',
 'Usa Bank Dep',
 ' IP Motor Vehicles and Parts',
 'Zinc',
 'PCE Goods',
 'PCE Services',
 'PCE Durable Goods',
 'PCE Non Durable Goods',
 'Usa Jobless Claims',
 'Usa GDP Billions',
 'Usa GDP QonQ',
 'Usa GDP QonQ Annualized',
 'Usa AAA Corp Bond',
 'Usa BBB Corp Bond',
 'USA Corp Bond AAA-CCC',
 'SMB',
 'SMB Employment',
 'SMB Capital',
 'SMB Inventories',
 'SMB Economy',
 'SMB Sales',
 'SMB FIJI',
 'SMB Construction',
 'SMB Manufacturing',
 'SMB Transportation',
 'SMB Wholesale',
 'SMB Retail',

 'IP Oil and Gas Extraction',
 'DG Value of Shipments',
 'DG Consumer Goods',
 'DG Consumer Goods Ex Transp',
 'DG Consumer Goods Ex Defense',
 'DG Manufacturing UFilled Orders',
 'DG Machinery',
 'DG Computer and Elec',
 'DG Fab metal',
 'DG Primary metal',
 'DG Transportation Equ',
 'IP Utilities (Electric Power)',
 'IP Chemicals',
 'IP Machinery',
 'G-S',
 '2 Year Note YonY',
 '10 Year Note YonY',
 '10Y-2Y YonY',
 '10Y-3M YonY',
 'PMI YonY',
 'PMI New Orders YonY',
 'PMI Production YonY',
 'PMI Employment YonY',
 'PMI Supplier Deliveries YonY',
 'PMI Inventories YonY',
 'PMI Customers Inventories YonY',
 'PMI Prices YonY',
 'PMI Backlog of Orders YonY',
 'PMI New Export Orders YonY',
 'PMI Imports YonY',
 'PMI Consumption YonY',
 'PMI Inputs YonY',
 'NPMI YonY',
 'NPMI Business Activity YonY',
 'NPMI New Orders YonY',
 'NPMI Employment YonY',
 'NPMI Supplier Deliveries YonY',
 'NPMI Inventories YonY',
 'NPMI Prices YonY',
 'NPMI Backlog of Orders YonY',
 'NPMI New Export Orders YonY',
 'NPMI Imports YonY',
 'NPMI Inventory Sentiment YonY',
 'NPMI Inputs YonY',
 'UMCSI YonY',
 'UMCSI inf EXP YonY',
 'B Permits YonY',
 'B Starts YonY',
 'CPI inc YonY',
 'CPI ex YonY',
 'PPI inc YonY',
 'PPI ex YonY',
 'Indu Prodction YonY',
 'NFPR DIFF YonY',
 'Open Jobs YonY',
 'Usa IR YonY',
 'Usa CBBS YonY',
 'M2 Supply YonY',
 'Usa Oil YonY',
 'N Gas YonY',
 'Gas / Gallon YonY',
 'Copper YonY',
 'Aluminum YonY',
 'DXY YonY',
 'GBP_USD YonY',
 'EUR_USD YonY',
# 'GSCPI YonY',
 'Usa Bank Dep YonY',
 ' IP Motor Vehicles and Parts YonY',
 'Zinc YonY',
 'PCE Goods YonY',
 'PCE Services YonY',
 'PCE Durable Goods YonY',
 'PCE Non Durable Goods YonY',
 'Usa Jobless Claims YonY',
 'Usa GDP Billions YonY',
 'Usa GDP QonQ YonY',
 'Usa GDP QonQ Annualized YonY',
 'Usa AAA Corp Bond YonY',
 'Usa BBB Corp Bond YonY',
 'USA Corp Bond AAA-CCC YonY',
 'SMB YonY',
 'SMB Employment YonY',
 'SMB Capital YonY',
 'SMB Inventories YonY',
 'SMB Economy YonY',
 'SMB Sales YonY',
 'SMB FIJI YonY',
 'SMB Construction YonY',
 'SMB Manufacturing YonY',
 'SMB Transportation YonY',
 'SMB Wholesale YonY',
 'SMB Retail YonY',

 'IP Oil and Gas Extraction YonY',
 'DG Value of Shipments YonY',
 'DG Consumer Goods YonY',
 'DG Consumer Goods Ex Transp YonY',
 'DG Consumer Goods Ex Defense YonY',
 'DG Manufacturing UFilled Orders YonY',
 'DG Machinery YonY',
 'DG Computer and Elec YonY',
 'DG Fab metal YonY',
 'DG Primary metal YonY',
 'DG Transportation Equ YonY',
 'IP Utilities (Electric Power) YonY',
 'IP Chemicals YonY',
 'IP Machinery YonY',
 'G-S YonY',
 'PPI - CPI',
 'Spread 2Y/10Y',
 'PMI_Spread_NewOrders_Inv',
 'PMI_Spread_Backlog_Inv','PMI_Spread_Supplier_Inv','PMI_Spread_Orders_Exports','PMI_Spread_Consumption_Inputs','PMI_Spread_NewOrders_Inv YonY',
     'PMI_Spread_Backlog_Inv YonY','PMI_Spread_Supplier_Inv YonY','PMI_Spread_Orders_Exports YonY','PMI_Spread_Consumption_Inputs YonY','NPMI_Spread_NewOrders_Inv','NPMI_Spread_Backlog_Inv',
     'NPMI_Spread_Supplier_Inv','NPMI_Spread_Orders_Exports','NPMI_Spread_Consumption_Inputs']]

tickers = {
    '^GSPC':'SP500',
    '^SKEW': 'SKEW',
    '^MOVE': 'MOVE',
    '^VIX': 'VIX',
    'HYG': 'High Yield Bonds',
    'LQD': 'Investment Grade Bonds',
    'TLT': 'Long Treasuries',
    'IEF': 'Intermediate Treasuries',
    'SHY': 'Short Treasuries'
}




usa_db_diff=new_world_all.copy()
usa_db_yy_list=[]
names_usa_db_list=[]

for col in usa_db_diff.columns:
    item = usa_db_diff[col].pct_change(12)
    usa_db_yy_list.append(item)
    names_usa_db_list.append(f'{col} YonY')
    

usa_db_diff_yy=pd.DataFrame(usa_db_yy_list)
usa_db_diff_yy_tr=usa_db_diff_yy.T
usa_db_diff_yy_tr.columns=names_usa_db_list
usa_db_diff_yy_tr=pd.concat([usa_db_diff_yy_tr,usa['UMCSI inf EXP']],axis=1)
usa_db_diff_yy_tr.sort_index(ascending=False, inplace=True)
usa = usa.apply(lambda x: x.tz_localize(None) if x.dtype == 'datetime64[ns, UTC]' else x)
usa_yield_curve_monthly = usa_yield_curve.resample('MS').first() 
usa = add_yield_curve_slope_to_usa(usa, usa_yield_curve_monthly)
print(f"Memory usage: {memory_usage_mb:.2f} MB")

eu_columns = [c for c in eu_columns if c != "EU NPMI"]
missing = [c for c in eu_columns if c not in europe.columns]
print("Missing columns:", missing)
europe = europe.loc[:, ~europe.columns.duplicated(keep="first")]


bond_dfs_weekly = [
    usa_1_month_bond, usa_3_month_bond, usa_6_month_bond,
    usa_1_year_bond, usa_2_year_bond, usa_3_year_bond,
    usa_5_year_bond, usa_7_year_bond, usa_10_year_bond,
    usa_20_year_bond, usa_30_year_bond
]

# Concatenate along columns (axis=1)
# This aligns them by their Date index automatically
usa_yields_weekly = pd.concat(bond_dfs_weekly, axis=1)
usa_yields_weekly.columns = ['1M', '3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y']
usa_yields_weekly = usa_yields_weekly.dropna()

# --- THE MONTHLY MASTER (Month Start) ---
# 'MS' = Month Start (1st of the month)
# .first() ensures we take the yield from the first trading day
usa_yields_monthly = usa_yields_weekly.resample('MS').first().dropna()


#weekly
scaler_w = StandardScaler()
# Fit and transform the yields
pca_w = PCA(n_components=3)
factors_w = pca_w.fit_transform(scaler_w.fit_transform(usa_yields_weekly))

# Assign Factors
usa_yields_weekly['Level'] = factors_w[:, 0]
usa_yields_weekly['Slope'] = factors_w[:, 1]
usa_yields_weekly['Curvature'] = factors_w[:, 2]

# --- 2. Weekly Z-Score of the MOVE ---
# Window of 52 weeks to see if the MOVE is normal for the year
for factor in ['Level', 'Slope', 'Curvature']:
    weekly_move = usa_yields_weekly[factor].diff()
    usa_yields_weekly[f'{factor}_Move_Z'] = (weekly_move - weekly_move.rolling(52).mean()) / weekly_move.rolling(52).std()


# monthly
# --- 1. Monthly PCA ---
scaler_m = StandardScaler()
pca_m = PCA(n_components=3)
factors_m = pca_m.fit_transform(scaler_m.fit_transform(usa_yields_monthly))

# Assign Factors
usa_yields_monthly['Level'] = factors_m[:, 0]
usa_yields_monthly['Slope'] = factors_m[:, 1]
usa_yields_monthly['Curvature'] = factors_m[:, 2]

# --- 2. Monthly Z-Score (Where are we?) ---
# 24-month window to see if the current curve shape is an "extreme"
for factor in ['Level', 'Slope', 'Curvature']:
    usa_yields_monthly[f'{factor}_Z'] = (usa_yields_monthly[factor] - usa_yields_monthly[factor].rolling(24).mean()) / usa_yields_monthly[factor].rolling(24).std()

# --- 3. Monthly Year-on-Year (YoY Strength) ---
# Absolute change over 12 months
usa_yields_monthly['Level_YoY'] = usa_yields_monthly['Level'].diff(12)
usa_yields_monthly['Slope_YoY'] = usa_yields_monthly['Slope'].diff(12)
usa_yields_monthly['Curvature_YoY'] = usa_yields_monthly['Curvature'].diff(12)


leading_europe_std = detect_unusual_moves(europe,eu_columns)
leading_usa_std = detect_unusual_moves(usa, usa_columns)
