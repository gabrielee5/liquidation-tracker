import asyncio
import json
from datetime import datetime
from pybit.unified_trading import WebSocket
from termcolor import cprint
import os
from zoneinfo import ZoneInfo

# Configuration
SYMBOLS = ["BTCUSDT"]
ticker_filename = "bybit_tickers.csv"

# Create/check tickers file
if not os.path.isfile(ticker_filename):
    with open(ticker_filename, "w") as f:
        f.write("Timestamp,Symbol,LastPrice,24hChange%,24hHigh,24hLow,Volume24h,Turnover24h,"
                "OpenInterest,FundingRate,Bid1,Ask1\n")

def format_ticker(message):
    try:
        ticker_data = message['data']
        
        # Extract ticker data
        timestamp = int(message['ts'])
        symbol = ticker_data['symbol']
        last_price = float(ticker_data['lastPrice'])
        price_change = float(ticker_data['price24hPcnt']) * 100  # Convert to percentage
        high_24h = float(ticker_data['highPrice24h'])
        low_24h = float(ticker_data['lowPrice24h'])
        volume_24h = float(ticker_data['volume24h'])
        turnover_24h = float(ticker_data['turnover24h'])
        open_interest = float(ticker_data['openInterest'])
        funding_rate = float(ticker_data['fundingRate']) * 100  # Convert to percentage
        bid1 = float(ticker_data['bid1Price'])
        ask1 = float(ticker_data['ask1Price'])
        
        # Format readable time
        readable_time = datetime.fromtimestamp(
            timestamp / 1000,
            ZoneInfo("America/New_York")
        ).strftime('%H:%M:%S')
        
        # Format display symbol
        display_symbol = symbol.replace('USDT', '')
        
        # Determine color based on price change
        color = 'green' if price_change >= 0 else 'red'
        
        # Create output string
        output = (
            f"{readable_time} {display_symbol} "
            f"${last_price:,.2f} -- "
            f"OI: {open_interest:,.1f} "
            f"FR: {funding_rate:+.4f}%"
        )
        
        # Print with formatting
        cprint(output, color, attrs=['bold'] if abs(price_change) >= 2 else [])
        
        # Write to CSV
        with open(ticker_filename, "a") as f:
            f.write(f"{timestamp},{symbol},{last_price},{price_change},"
                   f"{high_24h},{low_24h},{volume_24h},{turnover_24h},"
                   f"{open_interest},{funding_rate},{bid1},{ask1}\n")
                
    except Exception as e:
        print(f"Error processing ticker: {e}")

def handle_message(message):
    if message['topic'].startswith('tickers'):
        format_ticker(message)

async def keep_alive():
    while True:
        await asyncio.sleep(1)

async def main():
    # Initialize WebSocket
    ws = WebSocket(
        testnet=False,
        channel_type="linear"
    )
    
    # Subscribe to ticker streams for each symbol
    for symbol in SYMBOLS:
        ws.ticker_stream(
            symbol=symbol,
            callback=handle_message
        )
    
    print(f"Subscribed to ticker info for {', '.join(SYMBOLS)}")
    print("Monitoring tickers...")
    print("Format: Time Symbol Price (24h±%) Volume OpenInterest FundingRate Spread")
    
    # Keep the connection alive
    await keep_alive()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")