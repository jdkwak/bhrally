import pandas as pd
import datetime as dt
from collections import Counter
import time
import requests
import json
import argparse

ALPHA_VANTAGE_Q = 'https://www.alphavantage.co/query?'

def get_previous_close(ticker, api_key):
    r = requests.get(ALPHA_VANTAGE_Q+
                     'function='+
                     'GLOBAL_QUOTE'+ 
                     '&symbol='+
                     ticker+ 
                     '&apikey='+
                     api_key)
    if r.ok:
        #return float(r.json()['Global Quote']['08. previous close'])
        return float(r.json()['Global Quote']['05. price'])
    else:
        return 0.0

def get_pnl_string(x, api_key):
    return str(int((get_previous_close(convert_to_alphavan_ticker(x), api_key) / start_price_dict[x] - 1)*10000)/100) + '%'

def convert_to_alphavan_ticker(google_ticker):
    if 'AMS:' in google_ticker:
        return google_ticker.split(':')[1] + '.AS'
    if 'EBR:' in google_ticker:
        return google_ticker.split(':')[1] + '.BR'
    if 'NYSE:' in google_ticker:
        return google_ticker.split(':')[1]
    if 'CVE:' in google_ticker:
        return google_ticker.split(':')[1] + '.V'
    if 'EPA:' in google_ticker:
        return google_ticker.split(':')[1] + '.PA'
    if 'NASDAQ:' in google_ticker:
        return google_ticker.split(':')[1]
    if 'OTCMKTS:' in google_ticker:
        return google_ticker.split(':')[1]
    if 'LON:' in google_ticker:
        return google_ticker.split(':')[1] + '.L'
    if 'ETR:' in google_ticker:
        return google_ticker.split(':')[1] + '.DE'
    if 'JSE:' in google_ticker:
        return google_ticker.split(':')[1] + '.JO'
    if 'SWX:' in google_ticker:
        return google_ticker.split(':')[1] + '.VX'
    if 'TSE:' in google_ticker:
        return google_ticker.split(':')[1] + '.TO'
    if 'NYSEARCA:' in google_ticker:
        return google_ticker.split(':')[1]
    if 'NYSEAMERICAN:' in google_ticker:
        return google_ticker.split(':')[1]
    if 'BIT:' in google_ticker:
        return google_ticker.split(':')[1] + '.MI'
    else:
        return google_ticker


if __name__ == '__main__':

    # Parse arguments
    parser = argparse.ArgumentParser(description="Generates new score based on\
                                     current prices")
    parser.add_argument("-i", "--input", required=True, type=str, help="CSV\
                        input file")
    parser.add_argument("-o", "--output", required=True, type=str, help="CSV\
                        output file")
    parser.add_argument("-k", "--key", required=True, type=str, help="Alpha\
                        Vantage API KEY")
    parser.add_argument("-d", "--divs", required=True, type=str, help="JSON\
                        dividends file")
    parser.add_argument("-b", "--bench", required=True, type=str, help="CSV\
                        benchmark file")
    parser.add_argument("-s", "--start", required=True, type=str, help="JSON\
                        start prices file")
    args = parser.parse_args()

    
    # Input data    
        
    raw_data = pd.read_csv(getattr(args, 'input'), 
                       names=["name",
                              "stock_1_name",
                              "stock_1_ticker",
                              "stock_1_start_price",
                              "stock_2_name",
                              "stock_2_ticker",
                              "stock_2_start_price",
                              "stock_3_name",
                              "stock_3_ticker",
                              "stock_3_start_price"]
                      )
 
    data = raw_data.dropna().reset_index(drop=True)

    tickers = []
    stocknames = []

    for i in range(1,4):
        data["stock_"+str(i)+"_ticker"] = data["stock_"+str(i)+"_ticker"].str.upper()
        tickers += data["stock_"+str(i)+"_ticker"].tolist()
        stocknames += data["stock_"+str(i)+"_name"].tolist()
    
    # Current Pricing Data
    
    price_dict = {}
    
    for i in set(tickers):
        if i != '' and i != '#REF!':
            print(i)
            price = get_previous_close(convert_to_alphavan_ticker(i),
                                       getattr(args, 'key'))
            print('      ' + str(price))
            price_dict[i] = price
            time.sleep(1.5)

    # Get Dividents

    json_data = open(getattr(args, 'divs')).read()

    divs_dict = json.loads(json_data)

    # Get Start Prices

    json_data = open(getattr(args, 'start')).read()

    start_price_dict = json.loads(json_data)



    # Calculate Score

    for i in range(1, 4):
        data["stock_"+str(i)+"_current_price"] = data["stock_"+str(i)+"_ticker"].apply(lambda x: price_dict[x])
        data["stock_"+str(i)+"_divs"] = data["stock_"+str(i)+"_ticker"].apply(lambda x: divs_dict[x])

    for i in range(1, 4):
            data["stock_"+str(i)+"_return"] = (((data["stock_"+str(i)+"_current_price"] + data["stock_"+str(i)+"_divs"])/data["stock_"+str(i)+"_start_price"] - 1)*10000).astype(int)/100

    data['total_return'] = (((data.stock_1_return + data.stock_2_return + data.stock_3_return)/3)*100).astype(int)/100

    data.sort_values(by='total_return', ascending=False, inplace=True)

    data.reset_index(inplace=True, drop=True)

    data.index += 1

    score = data[['name', 'total_return', 'stock_1_name', 'stock_1_return', 'stock_2_name', 'stock_2_return', 'stock_3_name', 'stock_3_return']].copy()

    score.rename(columns={'name': 'Facebook Naam',
                          'total_return': 'Totaal Rendement',
                          'stock_1_name': 'Aandeel 1', 
                          'stock_2_name': 'Aandeel 2', 
                          'stock_3_name': 'Aandeel 3',
                          'stock_1_return': 'Rendement 1', 
                          'stock_2_return': 'Rendement 2',
                          'stock_3_return': 'Rendement 3',
                         }, inplace=True
                )

    score['Totaal Rendement'] = score['Totaal Rendement'].astype(str) + '%'
    score['Rendement 1'] = score['Rendement 1'].astype(str) + '%'
    score['Rendement 2'] = score['Rendement 2'].astype(str) + '%'
    score['Rendement 3'] = score['Rendement 3'].astype(str) + '%'

    score.index.name = 'Klassement'

    score.to_csv(getattr(args, 'output'))

    BH10 = pd.DataFrame.from_dict(Counter(tickers), orient='index', columns=['gekozen']).sort_values(by='gekozen', ascending=False).head(10)
    BH10['Price'] = BH10.index.map(lambda x: price_dict[x])
    BH10['Divs'] = BH10.index.map(lambda x: divs_dict[x])
    BH10['Start'] = BH10.index.map(lambda x: start_price_dict[x])
    BH10['PnL'] =  (BH10.Price + BH10.Divs)/BH10.Start - 1

    Bench = {}
    Bench['BH-10'] = str(int((BH10.PnL * BH10.gekozen).sum()/BH10.gekozen.sum() * 10000)/100) + '%'
    Bench['S&P-500'] = get_pnl_string('^GSPC', getattr(args, 'key'))
    time.sleep(1.5)
    Bench['ESX-50'] = get_pnl_string('ETR:EUN2', getattr(args,'key'))
    time.sleep(1.5)
    Bench['BEL-20'] = get_pnl_string('^BFX', getattr(args, 'key'))

    bench = pd.DataFrame.from_dict(Bench, orient='index', columns=['Index Rendement']).sort_values(by='Index Rendement', ascending=False)

    bench.to_csv(getattr(args, 'bench'))
