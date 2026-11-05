import os
import time
import ccxt
import pandas as pd
import requests

# Isticmaalka GitHub Secrets si loo ilaaliyo xogta sirta ah
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


def send_telegram_message(message):
  if not TELEGRAM_TOKEN or not CHAT_ID:
    print("Fariinta lama diri karin: Telegram Token ama Chat ID lama helin.")
    return

  url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload)
  except Exception as e:
    print("Khalad xagga Telegram ah:", e)


# Ku xirnaanshaha Binance Spot
exchange = ccxt.binance({
    "enableRateLimit": True,
    "options": {"defaultType": "spot"},
})


def analyze_timeframe(symbol, timeframe):
  try:
    # Soo akhrinta xogta suuqa
    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=100)
    df = pd.DataFrame(
        bars, columns=["timestamp", "open", "high", "low", "close", "volume"]
    )

    # Xisaabinta EMA 9 iyo EMA 21
    df["EMA9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["EMA21"] = df["close"].ewm(span=21, adjust=False).mean()

    # Xisaabinta RSI (6)
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=6).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=6).mean()
    rs = gain / loss
    df["RSI6"] = 100 - (100 / (1 + rs))

    last_row = df.iloc[-1]

    # Farqiga u dhexeeya labada EMA oo la waafajiyay 0.15% (0.0015)
    diff_ema = abs(last_row["EMA9"] - last_row["EMA21"])
    threshold = last_row["close"] * 0.0015

    # Shuruudda: EMA9 oo ka hooseysa EMA21 balse ku dhow in ay is-jarto
    if last_row["EMA9"] < last_row["EMA21"] and diff_ema <= threshold:
      message = (
          f"🚨 *{symbol} Spot Pre-Crossover Signal!* 🚨\n\n"
          f"⏱️ **Timeframe:** `{timeframe}`\n"
          f"💰 Qiimaha Hadda: `{last_row['close']}`\n"
          f"📈 EMA9: `{last_row['EMA9']:.3f}`\n"
          f"📉 EMA21: `{last_row['EMA21']:.3f}`\n"
          f"⚡ RSI(6): `{last_row['RSI6']:.2f}`\n\n"
          f"🔔 *Waa ku dhowdahay in ay is-jarto, diyaar garow!*"
      )
      send_telegram_message(message)
      print(f"Signal la diray: {symbol} ({timeframe})")

  except Exception as e:
    print(f"Khalad ka dhacay {symbol} ({timeframe}): {e}")


def run_bot():
  print("Bot-kii wuu bilaabay inuu soo jiito suuqa Binance Spot...")

  # Si otomaatig ah ayuu u soo akhrinayaa dhammaan suuqyada
  exchange.load_markets()

  # Wuxuu soo saarayaa oo keliya kuwa ku lammaan USDT oo firfircoon (Active)
  symbols = [
      symbol
      for symbol in exchange.symbols
      if symbol.endswith("/USDT") and exchange.markets[symbol]["active"]
  ]

  print(
      f"Wadarta guud ee lacagaha USDT la baarayo waa: {len(symbols)} coins."
  )

  # Loo beddelay labada Timeframe ee 1h iyo 4h
  timeframes = ["1h", "4h"]

  for symbol in symbols:
    for tf in timeframes:
      analyze_timeframe(symbol, tf)
      time.sleep(0.5)  # Nasasho yar si uusan Binance API-gu kuu xannibin


if __name__ == "__main__":
  run_bot()
