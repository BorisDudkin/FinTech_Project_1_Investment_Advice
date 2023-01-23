import holoviews as hv
import hvplot.pandas
import pandas as pd
from matplotlib import pyplot as plt


def plot_var_contribution(var_vector, var):
    plot_title = f"VaR Contribution by Asset - VaR of {-var}"
    contributors = var_vector.plot(kind='barh', title=plot_title, xlabel = 'USD', ylabel='VaR Date')
    contributors.get_figure().savefig("VaR_contributors.png", bbox_inches="tight")
    return contributors

def plot_var_pnl_density(pnl_vector, var, days):
    plot_title = f"Silumated 1 Day PnL Distribution based on {days} Days of Historical Data and VaR of {var}"
    plt = pnl_vector.plot(kind='density', title=plot_title)
    plt.axvline(var, color='r')
    plt.get_figure().savefig("VaR_PnL_Vector_Density.png", bbox_inches="tight")
    return plt

    
def plot_portfolio_composition(portfolio):

    composition = portfolio.hvplot.barh(
        xlabel='Assrts',
        ylabel='Position',
        label = 'Portfolio Composition',    
        color='blue'
    ).opts(xformatter='%.0f')


    # plot_title = "Portfolio Composition"
    # composition = portfolio.plot(kind='barh', title=plot_title, ylabel = 'Assets', xlabel = 'USD', color='blue')
    # composition.get_figure().savefig("Portfolio Composition.png", bbox_inches="tight")
    return composition