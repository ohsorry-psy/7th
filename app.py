import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objs as go

st.set_page_config(page_title="RSI 다이버전스 정신과 트레이딩", page_icon="💭")
st.title("💭 RSI 다이버전스 정신과 트레이딩")

# 🧠 왼쪽 사이드바에 종목과 날짜 선택 UI 생성
with st.sidebar:
    st.header("🔍 종목 및 기간 설정")
    symbol = st.text_input("종목 코드 입력 (예: AAPL, 005930.KS, 012450.KQ)", value="AAPL")
    start_date = st.date_input("시작 날짜", value=pd.to_datetime("2023-01-01"))
    end_date = st.date_input("종료 날짜", value=pd.to_datetime("2024-04-01"))

# 📊 데이터 다운로드
data = yf.download(symbol, start=start_date, end=end_date)

if data.empty:
    st.error("❌ 선택한 종목의 데이터를 가져오지 못했습니다.")
    st.stop()

if 'Close' not in data.columns:
    st.error("❌ 종가(Close) 데이터가 없습니다.")
    st.stop()

close = data['Close'].squeeze()
if close.empty:
    st.error("❌ 종가 데이터가 비어있습니다.")
    st.stop()

# ✅ RSI 계산
try:
    data['RSI'] = ta.momentum.RSIIndicator(close=close.squeeze(), window=14).rsi()
    if data['RSI'].isnull().all():
        st.error("❌ RSI 계산 결과가 모두 결측치입니다.")
        st.stop()
except Exception as e:
    st.error(f"RSI 계산 중 오류 발생: {e}")
    st.stop()

# 🧠 다이버전스 탐지 함수
def find_bullish_divergence(df):
    points = []
    for i in range(30, len(df)):
        price_now = float(df['Close'].iloc[i])
        price_prev = float(df['Close'].iloc[i-10:i].min())
        rsi_now = float(df['RSI'].iloc[i])
        rsi_prev = float(df['RSI'].iloc[i-10:i].min())
        if price_now < price_prev and rsi_now > rsi_prev:
            points.append(i)
    return points

def find_bearish_divergence(df):
    points = []
    for i in range(30, len(df)):
        price_now = float(df['Close'].iloc[i])
        price_prev = float(df['Close'].iloc[i-10:i].max())
        rsi_now = float(df['RSI'].iloc[i])
        rsi_prev = float(df['RSI'].iloc[i-10:i].max())
        if price_now > price_prev and rsi_now < rsi_prev:
            points.append(i)
    return points

bullish = find_bullish_divergence(data)
bearish = find_bearish_divergence(data)

# 📈 가격 차트
fig_price = go.Figure()
fig_price.add_trace(go.Scatter(
    x=data.index,
    y=data['Close'],
    name="종가",
    line=dict(color="blue")
))
fig_price.add_trace(go.Scatter(
    x=data.index[bullish],
    y=data['Close'].iloc[bullish],
    mode='markers',
    name='🟢 매수',
    marker=dict(color='green', size=10)
))
fig_price.add_trace(go.Scatter(
    x=data.index[bearish],
    y=data['Close'].iloc[bearish],
    mode='markers',
    name='🔴 매도',
    marker=dict(color='red', size=10)
))
fig_price.update_layout(
    title=f"{symbol} 가격 및 RSI 다이버전스",
    xaxis_title="날짜",
    yaxis_title="가격"
)
st.plotly_chart(fig_price, use_container_width=True)

# 📉 RSI 차트
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(
    x=data.index,
    y=data['RSI'],
    name='RSI',
    line=dict(color='purple')
))
fig_rsi.add_shape(type='line', x0=data.index[0], x1=data.index[-1], y0=70, y1=70,
                  line=dict(color='gray', dash='dot'))
fig_rsi.add_shape(type='line', x0=data.index[0], x1=data.index[-1], y0=30, y1=30,
                  line=dict(color='gray', dash='dot'))
fig_rsi.update_layout(
    title="RSI 지표",
    xaxis_title="날짜",
    yaxis_title="RSI"
)
st.plotly_chart(fig_rsi, use_container_width=True)

