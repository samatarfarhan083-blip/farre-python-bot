import os
import ccxt
import pandas as pd
import requests

TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# Dhammaan 62-ka coin ee aad liiska u soo dirtay
COINS = [
    "RARE/USDT", "AMP/USDT", "QNT/USDT", "BTC/USDT", "ETH/USDT", "BNB/USDT", 
    "XRP/USDT", "SOL/USDT", "TRX/USDT", "ZEC/USDT", "DOGE/USDT", "LINK/USDT", 
    "XMR/USDT", "ADA/USDT", "XLM/USDT", "NEAR/USDT", "BCH/USDT", "LTC/USDT", 
    "SUI/USDT", "AVAX/USDT", "HBAR/USDT", "TAO/USDT", "CRO/USDT", "DOT/USDT", 
    "WLD/USDT", "ICP/USDT", "ETC/USDT", "KAS/USDT", "POL/USDT", "ARB/USDT", 
    "RENDER/USDT", "JUP/USDT", "ALGO/USDT", "KCS/USDT", "ORDI/USDT", "TIA/USDT", 
    "INJ/USDT", "STX/USDT", "FET/USDT", "AR/USDT", "SEI/USDT", "MANTA/USDT", 
    "PYTH/USDT", "EIGEN/USDT", "ZK/USDT", "GALA/USDT", "SAND/USDT", "MANA/USDT", 
    "CHZ/USDT", "ENJ/USDT", "OP/USDT", "GRT/USDT", "CFX/USDT", "AIOZ/USDT", 
    "APE/USDT", "GRASS/USDT"
]

def analyze_timeframe(exchange, symbol, timeframe):
    try:
        # Soo jiid 150 shamac ee u dambeeyay si EMA-da loo xisaabiyo
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=150)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Xisaabi EMA-yada (9, 21, 100)
        df['ema9'] = df['close'].ewm(span=9, adjust=False).mean()
        df['ema21'] = df['close'].ewm(span=21, adjust=False).mean()
        df['ema100'] = df['close'].ewm(span=100, adjust=False).mean()
        
        current_price = df['close'].iloc[-1]
        e9 = df['ema9'].iloc[-1]
        e21 = df['ema21'].iloc[-1]
        e100 = df['ema100'].iloc[-1]
        
        # Xisaabi boqolleyda masaafada u dhaxaysa EMA 9 iyo EMA 21 (0.15%)
        diff_percentage = abs(e9 - e21) / current_price * 100
        
        # Shuruudda: Masaafadu ha noqoto 0.15% ama ka yar (isku dhawaansho / crossover zone)
        if diff_percentage <= 0.15:
            return True, current_price, e9, e21, e100
            
    except Exception as e:
        print(f"Khalad ku yimid {symbol} ({timeframe}): {e}")
        
    return False, 0, 0, 0, 0

def check_market():
    exchange = ccxt.binance({
        'enableRateLimit': True,
    })
    
    signals_found = []
    
    for symbol in COINS:
        # Baadh labada Timeframe: '1h' iyo '4h'
        for tf in ['1h', '4h']:
            is_matched, price, e9, e21, e100 = analyze_timeframe(exchange, symbol, tf)
            
            if is_matched:
                clean_name = symbol.replace("/USDT", "")
                signal_text = (
                    f"🚨 **SIGNAL ALERT ({tf})** 🚨\n\n"
                    f"🔹 **Coin:** {clean_name}\n"
                    f"💵 **Qiimaha:** ${price:,.4f}\n"
                    f"📊 **EMA 9:** ${e9:,.4f}\n"
                    f"📊 **EMA 21:** ${e21:,.4f}\n"
                    f"📊 **EMA 100:** ${e100:,.4f}\n"
                    f"✨ *Masaafada EMA 9 & 21 waa ku dhowdahay (<= 0.15%)!*"
                )
                signals_found.append(signal_text)
                
    # Haddii signal la helo, Telegram u dir
    if signals_found:
        for msg in signals_found:
            send_telegram_message(msg)
    else:
        print("Baadhistii waa dhamaatay, majiro signal la helay wareegan.")

def send_telegram_message(text):
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(telegram_url, json=payload)

if __name__ == "__main__":
    check_market()
