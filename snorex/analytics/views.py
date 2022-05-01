# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 15:01:36 2021

@author: yuanq
"""
import sys
sys.path.append(r'E:/Program Files/Dropbox/Yuan Qing/Work/Projects/Libraries/3. Python/dd8/')
import dd8.finance.crypto as crypto
import dd8.finance.technical_analysis as ta
import numpy as np
import pandas as pd
import plotly
import plotly.graph_objects as go
import json

from snorex.analytics.forms import DataRequestForm

from flask import Blueprint, render_template
from flask_login import login_required
analytics_blueprints = Blueprint('analytics', __name__,
                                    template_folder='templates/analytics')

@analytics_blueprints.route('/historical_price', methods=['GET', 'POST'])
@login_required
def historical_price():
    form = DataRequestForm()
    table = None
    graph_json = None
    if form.validate_on_submit():
        underlying = form.underlying.data.upper()
        resolution = int(form.resolution.data)
        window_1 = int(form.rolling_window_1.data)
        window_2 = int(form.rolling_window_2.data)
        window_3 = int(form.rolling_window_3.data)
        start_date = form.start_date.data
        end_date = form.end_date.data

        start_time = crypto.generate_timestamp(start_date.year,
                                                start_date.month,
                                                start_date.day)
        end_time = crypto.generate_timestamp(end_date.year,
                                                end_date.month,
                                                end_date.day)

        market_data = crypto.FtxMarketData()

        markets = market_data.get_historical(underlying, resolution, start_time, end_time, 5000)

        rsi = ta.RelativeStrengthIndex(14)
        markets['RSI_14'] = rsi.fit(markets['close'])

        roc = ta.RateOfChange(1)
        markets['RETURNS (%)'] = roc.fit(markets['close']) * 100.0
        markets['HL_RETURNS (%)'] = np.log(markets['high']/markets['low']) * 100

        labels = []
        std = ta.StandardDeviation(window_1)          
        label = 'VOL_{window}'.format(window=window_1)
        markets[label] = std.fit(markets['RETURNS (%)']) * (365**0.5)
        labels.append(label)
        pkstd = ta.ParkinsonHistoricalVolatility(window_1)
        label = 'PKVOL_{window}'.format(window=window_1)
        markets[label] = pkstd.fit(markets['HL_RETURNS (%)']) * (365**0.5)        
        labels.append(label)
        std = ta.StandardDeviation(window_2)
        label = 'VOL_{window}'.format(window=window_2)
        markets[label] = std.fit(markets['RETURNS (%)']) * (365**0.5)
        labels.append(label)
        pkstd = ta.ParkinsonHistoricalVolatility(window_2)
        label = 'PKVOL_{window}'.format(window=window_2)
        markets[label] = pkstd.fit(markets['HL_RETURNS (%)']) * (365**0.5)        
        labels.append(label)
        std = ta.StandardDeviation(window_3)
        label = 'VOL_{window}'.format(window=window_3)
        markets[label] = std.fit(markets['RETURNS (%)']) * (365**0.5)
        labels.append(label)
        pkstd = ta.ParkinsonHistoricalVolatility(window_3)
        label = 'PKVOL_{window}'.format(window=window_3)
        markets[label] = pkstd.fit(markets['HL_RETURNS (%)']) * (365**0.5)        
        labels.append(label)
        
        #std = ta.StandardDeviation(365)
        #markets['VOL_365'] = std.fit(markets['RETURNS (%)']) * (365**0.5)

        #hist_vol = []
        #for hv in ['VOL_30','VOL_90','VOL_180','VOL_365']:
        #    hist_vol.append(markets.loc[markets.loc[:, hv]!=0.0, hv].quantile(
        #        np.array(range(0,105,5))/100
        #        ))
        #hist_vol = pd.concat(hist_vol, axis=1)
        hist_vol = markets.loc[:, labels]
        hist_vol = hist_vol.quantile(np.array(range(0,105,5))/100, axis=0)
        
        fig = go.Figure(data=[
                    go.Candlestick(x=markets.index,
                    open=markets['open'],
                    high=markets['high'],
                    low=markets['low'],
                    close=markets['close'])
        ])
        fig.update_layout(
            title=underlying + ' - ' + start_date.strftime('%d %b %Y') + ' to ' + end_date.strftime('%d %b %Y'),
            xaxis_title='Date',
            yaxis_title='Price',
            )
        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        #return render_template('data_request.html', form=form, table=markets.to_html(float_format=lambda x: '%10.2f' % x,
        #                                                            classes=['table table-bordered table-striped table-hover']))
        return render_template('data_request.html', form=form,
                                graph_json=graph_json,
                                table=hist_vol.to_html(float_format=lambda x: '%10.2f' % x,
                                    classes=['table table-bordered table-striped table-hover']))
    return render_template('data_request.html', form=form)

@analytics_blueprints.route('/dashboard')
@login_required
def dashboard():
    market_data = crypto.FtxMarketData()
    market_name = 'BTC/USD'
    resolution = crypto.ENUM_RESOLUTION.HOUR_1.value
    start_time = crypto.generate_timestamp(2021, 1, 1)
    end_time = crypto.generate_timestamp(2021, 12, 20)
    markets = market_data.get_historical(market_name, resolution, start_time, end_time, 5000)

    rsi = ta.RelativeStrengthIndex(14)
    markets['RSI_14'] = rsi.fit(markets['close'])

    roc = ta.RateOfChange(1)
    markets['RETURNS (%)'] = roc.fit(markets['close']) * 100.0

    return render_template('dashboard.html', table=markets.to_html(float_format=lambda x: '%10.2f' % x,
                                                                classes=['table table-bordered table-striped table-hover']))
