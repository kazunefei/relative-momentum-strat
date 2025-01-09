from portfolio import Portfolio
import matplotlib.pyplot as plt

def main():
    symbol1 = input("Enter first ticker: ")
    symbol2 = input("Enter second ticker: ")
    win1 = input("Enter short window: ")
    win2 = input("Enter long window: ")
    starting = input("Enter starting amount: ")
    
    portfolio = Portfolio()
    portfolio.load_data(symbol1, symbol2)
    portfolio.calculate_momentum_table(win1, win2)
    portfolio.trade()
    portfolio.calculate_value_and_positions(int(starting))    
    
    portfolio_stats = portfolio.get_statistics()
    print("Portfolio Statistics:\n", portfolio.get_statistics())
    
    with open(f'{portfolio.ticker1}_{portfolio.ticker2}_{portfolio.short}d_vs_{portfolio.long}d_stats.txt', "w") as file:
        file.write(f"Portfolio Statistics: {portfolio.ticker1} vs {portfolio.ticker2}, {portfolio.short}d vs {portfolio.long}d\n")
        file.write(portfolio_stats)
    
    plt.figure(figsize=(10, 6))
    portfolio.holdings['value'].plot(title=f"Portfolio Value Over Time({portfolio.ticker1} & {portfolio.ticker2}, {portfolio.short}d vs {portfolio.long}d)", xlabel="Date (M)", ylabel="Portfolio Value ($)")
    plt.grid(True)
    plt.savefig(f'{portfolio.ticker1}_{portfolio.ticker2}_{portfolio.short}d_vs_{portfolio.long}d_value.png')
    plt.close()
    
    position1 = portfolio.holdings[f'{portfolio.ticker1}_weight'] * portfolio.holdings['value']
    position2 = portfolio.holdings[f'{portfolio.ticker2}_weight'] * portfolio.holdings['value']
    plt.figure(figsize=(12, 6))
    plt.plot(portfolio.holdings.index, position1, label=f'{portfolio.ticker1} Position Value')
    plt.plot(portfolio.holdings.index, position2, label=f'{portfolio.ticker2} Position Value')
    plt.title(f"Portfolio Positions Over Time ({portfolio.ticker1} & {portfolio.ticker2}, {portfolio.short}d vs {portfolio.long}d)")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value ($)")
    plt.legend()
    plt.grid(True)
    plt.savefig(f'{portfolio.ticker1}_{portfolio.ticker2}_{portfolio.short}d_vs_{portfolio.long}d_holdings.png')
    plt.close()
    
if __name__ == "__main__":
    main()