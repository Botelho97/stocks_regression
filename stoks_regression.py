import pandas as pd
import requests
import matplotlib.pyplot as plt
from scipy.stats import linregress
from os import environ

def make_prediction(stock_name: str, starting_year: int, predicted_days=0):
    stock = stock_name.upper() + '.SA'
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock}&apikey={environ["ALPHAVANTAGE_APIKEY"]}&outputsize=full'
    response = requests.get(url)
    data = response.json()
    if data.get('Error Message'):
        print("Couldn't find the stock")
        return
    df = pd.DataFrame.from_dict(data['Time Series (Daily)'], dtype='float64')
    df = df.transpose()

    df['Average'] = (df['2. high'] + df['3. low']) / 2
    stock_values = df['Average']
    stock_values = stock_values.reset_index()
    stock_values['date'] = pd.to_datetime(stock_values['index'])
    stock_values.drop(columns='index')
    stock_values['year'] = pd.DatetimeIndex(stock_values['date']).year
    stock_values = stock_values.loc[stock_values['year'] >= starting_year]

    reg = linregress(x=stock_values.index[::-1], y=stock_values['Average'])
    slope, intercept = reg[:2]
    x_estimator = [x for x in range(0, stock_values.shape[0]+1)]
    y_estimator = [slope * x + intercept for x in x_estimator]

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.set(
        title=f'Stock Prices for {stock[:-3]} in R$, starting year: ({starting_year})',
        ylabel='Value',
        xlabel='Date')
    ax.plot(stock_values.index[::-1], stock_values['Average'], color='blue')
    ax.plot(x_estimator, y_estimator, color='red')

    plt.savefig(f'images/{stock_name.upper()}-prediction-since-{starting_year}.png')
    return f'Targeted value: R${round(slope * (stock_values.shape[0] + predicted_days) + intercept, 2)}'