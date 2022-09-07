import streamlit as st
import pandas as pd
import numpy as np
from yahoo_fin.stock_info import get_data
from yahoo_fin.stock_info import get_quote_table
import yahoo_fin.stock_info as si
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from yahoo_fin.options import get_options_chain

st.set_page_config(layout='wide')


st.markdown(f"<h1 style='text-align: center; color: black;'>Stock Analysis</h1>", unsafe_allow_html=True)

data_load_state = st.text('Loading data...')
@st.cache
def get_quote_data(ticker):
    quote_data = {}
    quote_data[ticker] = get_quote_table(ticker, dict_result=False)
    return quote_data

@st.cache
def get_cash_data(ticker):
    cash_data = {}
    cash_data[ticker] = si.get_cash_flow(ticker, yearly = False)
    return cash_data


#Ticker input
ticker = st.text_input("Input ticker for analysis",value="")
ticker = ticker.upper()
if ticker:
    current_price = si.get_live_price(ticker)
    market_status = si.get_market_status()
    st.markdown(f"<h2 style='text-align: center; color: black;'>Market is currently {market_status}</h2>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; color: black;'>{ticker}s current price</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center; color: green;'>{current_price}</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap='large')
if ticker:
    data_load_state.text('Loading data...done!')
    #Load Ticker Data
    cash_data = get_cash_data(ticker)
    quote_data = get_quote_data(ticker)
    #Investement amount
    with col1:
        fig = px.bar(cash_data[ticker].T, x=cash_data[ticker].T.index, y='investments', 
                    title = f'{ticker}s Investment Amount', color="investments", labels = {'endDate':'Date', 'investments':'Investment ($)'})
        st.plotly_chart(fig)
    
    #netBorrowings	 amount
    with col2:
        fig2 = px.bar(cash_data[ticker].T, x=cash_data[ticker].T.index, y='netBorrowings', 
                title = f'{ticker}s Net Borrowing', color="netBorrowings", labels = {'endDate':'Date', 'netBorrowings':'Net Borrowing'})
        st.plotly_chart(fig2)
    
    #netIncome amount
    with col1:
        fig3 = px.bar(cash_data[ticker].T, x=cash_data[ticker].T.index, y='netIncome', 
                title = f'{ticker}s Net Income', color="netIncome", labels = {'endDate':'Date', 'netIncome':'Net Income'})
        st.plotly_chart(fig3)
    
    #changeInCash amount
    with col2:
        fig4 = px.bar(cash_data[ticker].T, x=cash_data[ticker].T.index, y='changeInCash', 
                title = f'{ticker}s Change In Cash', color="changeInCash", labels = {'endDate':'Date', 'changeInCash':'Net Income'})
        st.plotly_chart(fig4)
    
    #KPIS
    # Volume
    volume = quote_data[ticker].loc[3].value
    with col1:
        fig5 = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = volume,
            domain = {'x': [0.1, 1], 'y': [0.2, 0.9]},
            title = {'text': f"Average(3 Month) ${ticker} Volume"}))
        st.plotly_chart(fig5)
    
    #Market Cap remove letter
    measure = quote_data[ticker].loc[11].value[-1]
    value = float(quote_data[ticker].loc[11].value.rstrip(measure))
    
    # Market Cap
    with col2:
        fig6 = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = value,
            domain = {'x': [0.1, 1], 'y': [0.2, 0.9]},
            title = {'text': f"Market Cap ${ticker} {measure}illion"}))

        st.plotly_chart(fig6)
    
    
    #52 Week Range
    end = float(quote_data[ticker].loc[1].value.split()[-1])
    begin = float(quote_data[ticker].loc[1].value.split()[0])
    col1.metric("52 Week Range",quote_data[ticker].loc[1].value, delta = (end - begin)) 
    
    #Days Range
    end = float(quote_data[ticker].loc[6].value.split()[-1])
    begin = float(quote_data[ticker].loc[6].value.split()[0])
    col2.metric("Days Range",quote_data[ticker].loc[6].value, delta = (end - begin)) 

    #EPS Data
    def earnings_data(ticker):
        earnings = si.get_earnings_history(ticker)
        earnings_df = pd.DataFrame()
        for i in earnings:
            earnings_df = pd.concat([earnings_df, pd.DataFrame(pd.Series(i)).T])
        return earnings_df, earnings
    
    earnings_df, earnings_dict = earnings_data(ticker)
    title = earnings_dict[0]['companyshortname']
    
    with col1:
        fig7 = px.line(earnings_df, x='startdatetime', y = ['epsestimate', 'epsactual'], 
                title = f"EPS {title} Estimate vs Acutal", labels = {'startdatetime':'Date', 'value':'EPS in $'})
        st.plotly_chart(fig7)
    with col2:
        st.markdown(f"<h2 style='text-align: center; color: green;'>Need Visual Here</h2>", unsafe_allow_html=True)
    with col1:
        st.markdown(f"<h2 style='text-align: center; color: green;'>Calls Option Chain</h2>", unsafe_allow_html=True)
        st.dataframe(get_options_chain(ticker)['calls'])
        
    with col2:
        st.markdown(f"<h2 style='text-align: center; color: green;'>Put Options Chain</h2>", unsafe_allow_html=True)
        st.dataframe(get_options_chain(ticker)['calls'])