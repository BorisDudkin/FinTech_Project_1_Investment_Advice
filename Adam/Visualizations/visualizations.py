import holoviews as hv
import hvplot.pandas
import pandas as pd
import streamlit as st
import hvplot
import matplotlib_inline
from bokeh.models import HoverTool

# A Function Used to Visualize the Weighted Dataframes of each portfolio

def weighted_charts(port_weights):
    hover = HoverTool(tooltips=[('Weight', '@weights{0.2f}')]) #Using the 'HoverTool' to adjust what is seen when the user hovers chart
    global bar #Making 'bar' a global variable so it can be called outside of the function as well (specifically for streamlit compatability)
    bar = port_weights.hvplot.barh( #Using HvPlots to visualize the data from the dataframe
        title='Asset Weights',
        y='weights',
        ylabel='Weight',
        xlabel='Assets',
        color='tan',
        hover_color='brown',
        height=300,
        fontscale=1).opts(xformatter='%0.2f', tools=[hover])
    return bar

st.bokeh_chart(hv.render(bar, backend='bokeh')) #Code used to visualize the data into streamlit