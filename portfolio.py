from DataLoader import DataLoader
import math
import pandas as pd
import numpy as np

class Portfolio:
    def __init__(self):
        self.data = None
        self.ticker1 = None
        self.ticker2 = None
        self.momentum_table = None
        self.holdings = None
        self.short = None
        self.long = None
        self.data_loader = DataLoader()
    
    def load_data(self, ticker1: str, ticker2: str):
        self.ticker1 = ticker1.upper()
        self.ticker2 = ticker2.upper()
        self.data = self.data_loader.get_securities_data(self.ticker1, self.ticker2)
        
    def calculate_momentum_table(self, short_window, long_window):
        self.short = int(short_window)
        self.long = int(long_window)
        
        momentum_df = pd.DataFrame({
            f'{self.ticker1}_Momentum_Signal': (self.data[self.ticker1].shift(self.short) / self.data[self.ticker1].shift(self.long)) - 1,
            f'{self.ticker2}_Momentum_Signal': (self.data[self.ticker2].shift(self.short) / self.data[self.ticker2].shift(self.long)) - 1
            })
        
        momentum_df['momentum_difference'] = momentum_df[f'{self.ticker1}_Momentum_Signal'] - momentum_df[f'{self.ticker2}_Momentum_Signal']
        rolling_mean = momentum_df['momentum_difference'].rolling(window = 252).mean()
        rolling_std = momentum_df['momentum_difference'].rolling(window = 252).std()
        
        momentum_df['Z_score'] = (momentum_df['momentum_difference'] - rolling_mean) / rolling_std
        zscore = [-np.inf, -2, -1.5, -1, -0.5, -0.1, 0.1, 0.5, 1, 1.5, 2, np.inf]
        weights = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        
        momentum_df[f'{self.ticker1}_weight'] = pd.cut(momentum_df['Z_score'], bins=zscore, labels=weights, right=False).astype(float)
        momentum_df[f'{self.ticker2}_weight'] = 1 - momentum_df[f'{self.ticker1}_weight']
        
        momentum_df = momentum_df.shift()
        
        self.momentum_table = momentum_df
        
    def get_momentum_table(self):
        return self.momentum_table
    
    def trade(self):
        returns = self.data.pct_change()
        
        returns = returns.loc[self.data_loader.DATE_ONEYEARAGO:self.data_loader.DATE_TD]
        
        portfolio = self.momentum_table[[f'{self.ticker1}_weight', f'{self.ticker2}_weight']].copy()
        
        weighted_t1 = portfolio[f'{self.ticker1}_weight'] * returns[self.ticker1]
        weighted_t2 = portfolio[f'{self.ticker2}_weight'] * returns[self.ticker2]
        
        portfolio['weighted_avg'] = weighted_t1 + weighted_t2
        
        portfolio['cumulative_returns'] = (portfolio['weighted_avg']+1).cumprod() - 1
        portfolio = portfolio[(portfolio.index.date >= self.data_loader.DATE_ONEYEARAGO.date()) & (portfolio.index.date <= self.data_loader.DATE_TD.date())]
        portfolio.loc[portfolio.index[0], ['weighted_avg', 'cumulative_returns']] = [0, 0] 
        
        self.holdings = portfolio
        
    def get_statistics(self):
        annualized_return = (self.holdings['weighted_avg'] + 1).prod() ** (252 / len(self.holdings)) - 1
        annualized_std = self.holdings['weighted_avg'].std() * math.sqrt(252)
        sharpe_ratio = (annualized_return - self.data_loader.get_tbill())/annualized_std
        cumulative_return = self.holdings['cumulative_returns'].iloc[-1]
        maximum_dd = ((self.holdings['cumulative_returns'] + 1)/(self.holdings['cumulative_returns'] + 1).cummax() - 1).min()
        
        stats_str = (
            f"Annualized Return:       {annualized_return:.4%}\n"
            f"Annualized Std Dev:      {annualized_std:.4%}\n"
            f"Sharpe Ratio:            {sharpe_ratio:.4f}\n"
            f"Cumulative Return:       {cumulative_return:.4%}\n"
            f"Maximum Drawdown:        {maximum_dd:.4%}\n"
        )

        return stats_str
    
    def calculate_value_and_positions(self, starting_value: int):
        self.holdings['value'] = starting_value * (self.holdings['cumulative_returns'] + 1)
        self.holdings[f'{self.ticker1}_position'] = self.holdings[f'{self.ticker1}_weight'] * self.holdings['value']
        self.holdings[f'{self.ticker2}_position'] = self.holdings[f'{self.ticker2}_weight'] * self.holdings['value']
        