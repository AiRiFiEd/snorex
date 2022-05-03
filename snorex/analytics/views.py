# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 15:01:36 2021

@author: yuanq
"""
import logging
logger = logging.getLogger(__name__)
#import sys
#sys.path.append(r'E:/Program Files/Dropbox/Yuan Qing/Work/Projects/Libraries/3. Python/dd8/')
#import dd8.finance.crypto as crypto
#import dd8.finance.technical_analysis as ta
import enum
import requests
import datetime
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

@enum.unique
class ENUM_SMOOTHING_TYPE(enum.Enum):
    NONE = 1
    SIMPLE_AVERAGING = 2
    EXPONENTIAL_AVERAGING = 3
    SMOOTHED_AVERAGING = 4
    LINEAR_WEIGHTED_AVERAGING = 5

@enum.unique
class ENUM_RESOLUTION(enum.Enum):
    #window length in seconds. options: 15, 60, 300, 900, 3600, 14400, 86400, 
    #or any multiple of 86400 up to 30*86400
    SECOND_15 = 15
    MINUTE_1 = 60
    MINUTE_5 = 300
    MINUTE_15 = 900
    HOUR_1 = 3600
    HOUR_4 = 14400
    DAY_1 = 86400
    DAY_2 = (2*86400)
    DAY_3 = (3*86400)
    DAY_4 = (4*86400)
    DAY_5 = (5*86400)
    DAY_6 = (6*86400)
    DAY_7 = (7*86400)
    DAY_8 = (8*86400)
    DAY_9 = (9*86400)
    DAY_10 = (10*86400)
    DAY_11 = (11*86400)
    DAY_12 = (12*86400)
    DAY_13 = (13*86400)
    DAY_14 = (14*86400)
    DAY_15 = (15*86400)
    DAY_16 = (16*86400)
    DAY_17 = (17*86400)
    DAY_18 = (18*86400)
    DAY_19 = (19*86400)
    DAY_20 = (20*86400)
    DAY_21 = (21*86400)
    DAY_22 = (22*86400)
    DAY_23 = (23*86400)
    DAY_24 = (24*86400)
    DAY_25 = (25*86400)
    DAY_26 = (26*86400)
    DAY_27 = (27*86400)
    DAY_28 = (28*86400)
    DAY_29 = (29*86400)
    DAY_30 = (30*86400)

@enum.unique
class ENUM_RETURNS_TYPE(enum.Enum):
    SIMPLE = 1
    NATURAL_LOG = 2

def generate_timestamp(int_year,
                       int_month,
                       int_day,
                       int_hour=0,
                       int_minute=0,
                       int_second=0,
                       int_microsecond=0):
    return datetime.datetime(year=int_year,
                             month=int_month,
                             day=int_day,
                             hour=int_hour,
                             minute=int_minute,
                             second=int_second,
                             microsecond=int_microsecond).timestamp()

def rolling_window(npa_1d, int_window_size):
    shape = npa_1d.shape[:-1] + (npa_1d.shape[-1] - int_window_size + 1, int_window_size)
    strides = npa_1d.strides + (npa_1d.strides[-1],)
    return np.lib.stride_tricks.as_strided(npa_1d, shape=shape, strides=strides)

class TechnicalIndicator(object):
    def __init__(self):
        pass
    
    def fit(self):
        pass
    
    def target_level(self):
        pass
    
    def _to_numpy_array(self, X):
        if not isinstance(X, np.ndarray):
            if isinstance(X, pd.Series):
                return X.values
            else:
                raise ValueError('`X` must be np.ndarray or pd.Series.')
        else:
            return X

class RateOfChange(TechnicalIndicator):
    def __init__(self, int_period, 
                 enum_returns_type=ENUM_RETURNS_TYPE.NATURAL_LOG):
        self.period = int_period
        self.returns_type = enum_returns_type
        
    @property
    def period(self):
        return self.__int_period
    
    @period.setter
    def period(self, int_period):
        if int_period > 0:
            self.__int_period = int_period
        else:
            raise ValueError('`int_period` must be positive.')
            
    @property
    def returns_type(self):
        return self.__enum_returns_type
    
    @returns_type.setter
    def returns_type(self, enum_returns_type):
        if isinstance(enum_returns_type, ENUM_RETURNS_TYPE):
            self.__enum_returns_type = enum_returns_type
        else:
            raise ValueError('`enum_returns_type` must be of `dd8.finance.enums.ENUM_RETURNS_TYPE`.')
            
    def fit(self, X):
        _ = self._to_numpy_array(X)
        if self.returns_type == ENUM_RETURNS_TYPE.SIMPLE:
            rate_of_change = _[self.period:] / _[:-self.period] - 1.0
        elif self.returns_type == ENUM_RETURNS_TYPE.NATURAL_LOG:
            rate_of_change = np.log(_[self.period:] / _[:-self.period])
        
        _ = np.empty(self.period)
        _[:] = np.nan
        rate_of_change = np.concatenate([_, rate_of_change],
                                        axis=0)
        return rate_of_change
    
    def target_value(self, dbl_target):
        pass

class RelativeStrengthIndex(TechnicalIndicator):
    def __init__(self, int_averaging_period):
        self.averaging_period = int_averaging_period
        
    @property
    def averaging_period(self):
        return self.__int_averaging_period
    
    @averaging_period.setter
    def averaging_period(self, int_averaging_period):
        if int_averaging_period > 0:
            self.__int_averaging_period = int_averaging_period
        else:
            raise ValueError('`int_averaging_period` must be positive.')
    
    def fit(self, X):
        _ = self._to_numpy_array(X)
        diff = np.diff(_)
        gains = np.abs(diff * (diff>0))
        losses = np.abs(diff * (diff<0)) 
        gains = (np.convolve(gains, np.ones(self.averaging_period), 'valid') / 
                     self.averaging_period)
        losses = (np.convolve(losses, np.ones(self.averaging_period), 'valid') / 
                      self.averaging_period)
        rsi = 100.0 - (100.0 / (1.0 + gains/losses))
        rsi = np.concatenate([np.zeros(self.averaging_period), 
                              rsi], axis=0)
        return rsi
    
    def target_value(self, dbl_target):
        pass
    
class StandardDeviation(TechnicalIndicator):
    def __init__(self, int_averaging_period,
                         bln_demean = True,
                         int_degrees_of_freedom = 0,
                         enum_smoothing_type=ENUM_SMOOTHING_TYPE.NONE):
        self.averaging_period = int_averaging_period
        self.demean = bln_demean
        self.degrees_of_freedom = int_degrees_of_freedom
        self.smoothing_type = enum_smoothing_type
    
    def fit(self, X):
        _ = self._to_numpy_array(X)[::-1]
        window = rolling_window(_, self.averaging_period)        
        n = self.averaging_period - self.degrees_of_freedom
        if self.smoothing_type == ENUM_SMOOTHING_TYPE.NONE:
            _ = np.empty(self.averaging_period - 1)
            _[:] = np.nan            
            if self.demean:
                mean = np.mean(window,1).reshape(-1,1)
            else:
                mean = 0
            _ = np.concatenate( ((np.sum( (window-mean)**2,axis=1)/(n))**0.5,
                                _))          
        return _[::-1]
    
    def target_value(self, dbl_target):
        pass
    
    @property
    def averaging_period(self):
        return self.__int_averaging_period
    
    @averaging_period.setter
    def averaging_period(self, int_averaging_period):
        if int_averaging_period > 0:
            self.__int_averaging_period = int_averaging_period
        else:
            raise ValueError('`int_averaging_period` must be positive.')
            
    @property
    def demean(self):
        return self.__bln_demean
    
    @demean.setter
    def demean(self, bln_demean):
        if isinstance(bln_demean, bool):
            self.__bln_demean = bln_demean
        else:
            raise TypeError('`bln_demean` must be of boolean type.')
            
    @property
    def degrees_of_freedom(self):
        return self.__int_degrees_of_freedom
            
    @degrees_of_freedom.setter
    def degrees_of_freedom(self, int_degrees_of_freedom):
        self.__int_degrees_of_freedom = int_degrees_of_freedom
    
    @property
    def smoothing_type(self):
        return self.__enum_smoothing_type
    
    @smoothing_type.setter
    def smoothing_type(self, enum_smoothing_type):
        if isinstance(enum_smoothing_type, ENUM_SMOOTHING_TYPE):
            self.__enum_smoothing_type = enum_smoothing_type
        else:
            raise ValueError('`enum_smoothing_type` must be of `dd8.finance.enums.ENUM_SMOOTHING_TYPE`.')

class ParkinsonHistoricalVolatility(StandardDeviation):
    def __init__(self, int_averaging_period, 
                         bln_demean = False, 
                         int_degrees_of_freedom = 0,
                         enum_smoothing_type = ENUM_SMOOTHING_TYPE.NONE):
        super().__init__(int_averaging_period = int_averaging_period,
                              bln_demean = bln_demean,
                              int_degrees_of_freedom = int_degrees_of_freedom,
                              enum_smoothing_type = enum_smoothing_type)
    
    def fit(self, X):
        _ = self._to_numpy_array(X)[::-1]
        window = rolling_window(_, self.averaging_period)             
        n = self.averaging_period - self.degrees_of_freedom        
        if self.smoothing_type == ENUM_SMOOTHING_TYPE.NONE:
            _ = np.empty(self.averaging_period-1)
            _[:] = np.nan            
            if self.demean:
                mean = np.mean(window,1).reshape(-1,1)
            else:
                mean = 0
            _ = np.concatenate( (( ((1 / (4*np.log(2))) *  np.sum( (window-mean)**2,axis=1))/(n))**0.5,
                                _))          
        return _[::-1]
    
    def target_value(self, dbl_target):
        pass


class FtxMarketData(object):
    _ENDPOINT = 'https://ftx.com/api/'
    _HISTORICAL_DATA_LIMIT = 5000
    
    def __init__(self, bln_as_dataframe=True):
        self.__bln_as_dataframe = bln_as_dataframe
    
    @property
    def as_dataframe(self):
        return self.__bln_as_dataframe
    
    @property
    def end_point(self):
        return self._ENDPOINT
    
    @property
    def historical_data_limit(self):
        return self._HISTORICAL_DATA_LIMIT
    
    def get_markets(self):
        url = '{end_point}markets'.format(end_point = self._ENDPOINT)
        data = requests.get(url)
        if data.status_code == 200:
            data = data.json()
            if self.as_dataframe:
                data = pd.DataFrame(data['result'])
                data.set_index('name', inplace=True)               
            return data
        else:
            logger.error('''`FtxMarketData.get_markets` failed with status code: 
                         {status_code}'''.format(status_code=data.status_code))
            return None        

    def get_market(self, str_market_name):
        url = '{end_point}markets/{market_name}'.format(
                    end_point = self._ENDPOINT,
                    market_name = str_market_name)
        data = requests.get(url)
        if data.status_code==200:
            data = data.json()
            if self.as_dataframe:
                data = data['result']
                header = [data.pop('name', None)]
                data = pd.DataFrame.from_dict(data, orient='index')
                data.columns = header            
            return data
        else:
            logger.error('''`FtxMarketData.get_market` for {market_name} failed 
                         with status code: {status_code}'''.format(
                         status_code=data.status_code, 
                         market_name=str_market_name))
            return None
        
    def get_historical(self, str_market_name,
                       int_resolution,
                       int_start_time,
                       int_end_time,
                       int_limit = 5000):
        limit = min(5000, int_limit)
        time_steps = (int_end_time-int_start_time)/int_resolution
        if time_steps <= limit:
            url = '{end_point}markets/{market_name}/candles?resolution={resolution}&start_time={start_time}&end_time={end_time}&limit={limit}'.format(
                        end_point = self._ENDPOINT,        
                        market_name = str_market_name,
                        resolution = int_resolution,
                        start_time = int_start_time,
                        end_time = int_end_time,
                        limit = limit)
            data = requests.get(url)
            if data.status_code == 200:
                data = data.json()
                if self.as_dataframe:
                    data = pd.DataFrame(data['result'])
                    data.set_index('startTime', inplace=True)                
                return data        
            else:
                return None
        else:
            start_time = int_start_time
            end_time = start_time + (limit * int_resolution)
            output = []
            while end_time < int_end_time:
                url = '{end_point}markets/{market_name}/candles?resolution={resolution}&start_time={start_time}&end_time={end_time}&limit={limit}'.format(
                            end_point = self._ENDPOINT,        
                            market_name = str_market_name,
                            resolution = int_resolution,
                            start_time = start_time,
                            end_time = end_time,
                            limit = limit)
                data = requests.get(url)
                if data.status_code == 200:
                    output.append(data.json())
                start_time = end_time + int_resolution
                end_time = start_time + (limit * int_resolution)
            url = '{end_point}markets/{market_name}/candles?resolution={resolution}&start_time={start_time}&end_time={end_time}&limit={limit}'.format(
                        end_point = self._ENDPOINT,        
                        market_name = str_market_name,
                        resolution = int_resolution,
                        start_time = start_time,
                        end_time = end_time,
                        limit = limit)
            data = requests.get(url)
            if data.status_code == 200:
                output.append(data.json())
            # check length of `output` is expected
            if self.as_dataframe:
                output = [pd.DataFrame(data['result']) for data in output]
                output = pd.concat(output)
                output.set_index('startTime', inplace=True)
            return output







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

        start_time = generate_timestamp(start_date.year,
                                                start_date.month,
                                                start_date.day)
        end_time = generate_timestamp(end_date.year,
                                                end_date.month,
                                                end_date.day)

        market_data = FtxMarketData()

        markets = market_data.get_historical(underlying, resolution, start_time, end_time, 5000)

        rsi = RelativeStrengthIndex(14)
        markets['RSI_14'] = rsi.fit(markets['close'])

        roc = RateOfChange(1)
        markets['RETURNS (%)'] = roc.fit(markets['close']) * 100.0
        markets['HL_RETURNS (%)'] = np.log(markets['high']/markets['low']) * 100

        labels = []
        std = StandardDeviation(window_1)          
        label = 'VOL_{window}'.format(window=window_1)
        markets[label] = std.fit(markets['RETURNS (%)']) * (365**0.5)
        labels.append(label)
        pkstd = ParkinsonHistoricalVolatility(window_1)
        label = 'PKVOL_{window}'.format(window=window_1)
        markets[label] = pkstd.fit(markets['HL_RETURNS (%)']) * (365**0.5)        
        labels.append(label)
        std = StandardDeviation(window_2)
        label = 'VOL_{window}'.format(window=window_2)
        markets[label] = std.fit(markets['RETURNS (%)']) * (365**0.5)
        labels.append(label)
        pkstd = ParkinsonHistoricalVolatility(window_2)
        label = 'PKVOL_{window}'.format(window=window_2)
        markets[label] = pkstd.fit(markets['HL_RETURNS (%)']) * (365**0.5)        
        labels.append(label)
        std = StandardDeviation(window_3)
        label = 'VOL_{window}'.format(window=window_3)
        markets[label] = std.fit(markets['RETURNS (%)']) * (365**0.5)
        labels.append(label)
        pkstd = ParkinsonHistoricalVolatility(window_3)
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
    market_data = FtxMarketData()
    market_name = 'BTC/USD'
    resolution = ENUM_RESOLUTION.HOUR_1.value
    start_time = generate_timestamp(2021, 1, 1)
    end_time = generate_timestamp(2021, 12, 20)
    markets = market_data.get_historical(market_name, resolution, start_time, end_time, 5000)

    rsi = RelativeStrengthIndex(14)
    markets['RSI_14'] = rsi.fit(markets['close'])

    roc = RateOfChange(1)
    markets['RETURNS (%)'] = roc.fit(markets['close']) * 100.0

    return render_template('dashboard.html', table=markets.to_html(float_format=lambda x: '%10.2f' % x,
                                                                classes=['table table-bordered table-striped table-hover']))
