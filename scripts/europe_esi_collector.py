# Once a month script to collect and process European ESI data
import datetime
import shutil
import requests as r
import wget
import pandas as pd



# Dynamic or parameterized link (adjust base folder suffix as required by EU naming conventions)

                                                                                                            # chage this date to 07 then 08 ect europe economic indicators realse dates changes so keep checking it at the end of the month
link_europe_esi = "https://ec.europa.eu/economy_finance/db_indicators/surveys/documents/series/nace2_ecfin_2606/all_surveys_total_sa_nace2.zip"

# Download the zip file using relative path
europe_zip_download = wget.download(link_europe_esi, "all_surveys_total_sa_nace2.zip")

# Unpack archive to a relative local directory
unzip_europe = shutil.unpack_archive(europe_zip_download, "europe_esi_data")
europe_path = "europe_esi_data/main_indicators_nace2.xlsx"

# Load and process data
plot_europe_all = pd.read_excel(europe_path, sheet_name="MONTHLY")
plot_europe_all.set_index("Unnamed: 0", inplace=True)
plot_europe_all.index = pd.to_datetime(plot_europe_all.index)
plot_europe_all.index.name = "Date"

leng = len(plot_europe_all)
data = pd.date_range("1985-01-01", periods=leng, freq="MS")
plot_europe_all.index = pd.to_datetime(data)

# Drop unnecessary columns safely
columns_to_drop = [
    "Unnamed: 1",
    "Unnamed: 9",
    "Unnamed: 17",
    "Unnamed: 25",
    "Unnamed: 33",
    "Unnamed: 41",
    "Unnamed: 49",
    "Unnamed: 57",
    "Unnamed: 65",
    "Unnamed: 73",
    "Unnamed: 81",
    "Unnamed: 89",
    "Unnamed: 97",
    "Unnamed: 105",
    "Unnamed: 113",
    "Unnamed: 121",
    "Unnamed: 129",
    "Unnamed: 137",
    "Unnamed: 145",
    "Unnamed: 153",
    "Unnamed: 161",
    "Unnamed: 169",
    "Unnamed: 177",
    "Unnamed: 185",
    "Unnamed: 193",
    "Unnamed: 201",
    "Unnamed: 209",
    "Unnamed: 217",
    "Unnamed: 225",
    "Unnamed: 233",
    "Unnamed: 241",
    "Unnamed: 249",
    "Unnamed: 257",
    "Unnamed: 265",
    "Unnamed: 273",
    "UK.INDU",
    "UK.SERV",
    "UK.CONS",
    "UK.RETA",
    "UK.BUIL",
    "UK.ESI",
    "UK.EEI",
]
plot_europe_all.drop(columns=columns_to_drop, inplace=True, errors="ignore")

# Filter core European ESI columns
plot_europe_esi = plot_europe_all[
    [
        "EU.ESI",
        "EA.ESI",
        "BE.ESI",
        "BG.ESI",
        "CZ.ESI",
        "DK.ESI",
        "DE.ESI",
        "EE.ESI",
        "IE.ESI",
        "EL.ESI",
        "ES.ESI",
        "FR.ESI",
        "HR.ESI",
        "IT.ESI",
        "CY.ESI",
        "LV.ESI",
        "LT.ESI",
        "LU.ESI",
        "HU.ESI",
        "MT.ESI",
        "NL.ESI",
        "AT.ESI",
        "PL.ESI",
        "PT.ESI",
        "RO.ESI",
        "SI.ESI",
        "SK.ESI",
        "FI.ESI",
        "SE.ESI",
        "ME.ESI",
        "MK.ESI",
        "AL.ESI",
        "RS.ESI",
        "TR.ESI",
    ]
]

nr_countries = len(plot_europe_esi.columns.to_list())
plot_europe_esi_diff = plot_europe_esi.diff(1)
plot_europe_esi.tail(4)
