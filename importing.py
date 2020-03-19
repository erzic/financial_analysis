# import libraries
from datetime import datetime
import lxml
from lxml import html
import requests
import numpy as np
import pandas as pd

symbol = 'GOOGL'

url_bs = 'https://finance.yahoo.com/quote/' + symbol + '/balance-sheet?p=' + symbol
url_is = 'https://finance.yahoo.com/quote/' + symbol + '/financials?p=' + symbol
url_cf = 'https://finance.yahoo.com/quote/' + symbol + '/cash-flow?p='+ symbol

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Pragma': 'no-cache',
    'Referrer': 'https://google.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}

def get_table(url):
    # Fetch the page that we're going to parse, using the request headers defined above
    page = requests.get(url, headers)

    # Parse the page with LXML, so that we can start doing some XPATH queries
    # to extract the data that we want
    tree = html.fromstring(page.content)

    # Smoke test that we fetched the page by fetching and displaying the H1 element
    tree.xpath("//h1/text()")
    table_rows = tree.xpath("//div[contains(@class, 'D(tbr)')]")

    # Ensure that some table rows are found; if none are found, then it's possible
    # that Yahoo Finance has changed their page layout, or have detected
    # that you're scraping the page.
    assert len(table_rows) > 0

    parsed_rows = []

    for table_row in table_rows:
        parsed_row = []
        el = table_row.xpath("./div")

        none_count = 0

        for rs in el:
            try:
                (text,) = rs.xpath('.//span/text()[1]')
                parsed_row.append(text)
            except ValueError:
                parsed_row.append(np.NaN)
                none_count += 1

        if (none_count < 4):
            parsed_rows.append(parsed_row)

    df = pd.DataFrame(parsed_rows)
    df_org = df
    
    df = pd.DataFrame(parsed_rows)
    df = df.set_index(0) # Set the index to the first column: 'Period Ending'.
    df = df.transpose() # Transpose the DataFrame, so that our header contains the account names

    # Rename the "Breakdown" column to "Date"
    cols = list(df.columns)
    cols[0] = 'Date'
    df = df.set_axis(cols, axis='columns', inplace=False)
    df_rot = df
    return df_org, df_rot



# get Balance Sheet 
BS_orginal, BS_transpose = get_table(url_bs)

# get Income Statement 
IS_orginal, IS_transpose = get_table(url_is)


# get Cash Flow
CF_orginal, CF_transpose = get_table(url_cf)

print(BS_orginal.head())

BS_transpose = BS_orginal.T
IS_transpose = IS_orginal.T
CF_transpose = CF_orginal.T
BS_transpose.to_excel("E:/Datos/google_bs.xlsx")
IS_transpose.to_excel("E:/Datos/google_is.xlsx")
CF_transpose.to_excel("E:/Datos/google_cf.xlsx")