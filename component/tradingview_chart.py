# components/tradingview_chart.py

import streamlit as st

def display_tradingview_chart(symbol: str, interval="5"):
    tv_symbol = f"NSE:{symbol.upper()}"

    st.markdown(f"""
        <iframe 
            src="https://s.tradingview.com/widgetembed/?symbol={tv_symbol}&interval={interval}&theme=dark&style=1&toolbarbg=rgba(0,0,0,1)&hideideas=1"
            width="100%" 
            height="500" 
            frameborder="0" 
            allowtransparency="true" 
            scrolling="no">
        </iframe>
    """, unsafe_allow_html=True)
