import asyncio
import json
from datetime import datetime
from pybit.unified_trading import WebSocket
from termcolor import cprint
import os
from zoneinfo import ZoneInfo

# Configuration
SYMBOLS = ["BTCUSDT"]
THRESHOLD = 5000
trades_filename = "bybit_trades.csv"

# Create/check trades file
if not os.path.isfile(trades_filename):
    with open(trades_filename, "w") as f:
        f.write("Event Time, Symbol, Price, Quantity, Trade ID, Trade Time, Side\n")

def format_trade(message):
    try:
        for trade in message['data']:
            # Extract trade data
            event_time = int(trade['T'])
            symbol = trade['s']
            price = float(trade['p'])
            quantity = float(trade['v'])
            trade_time = int(trade['T'])
            side = trade['S']
            trade_id = trade['i']
            
            # Calculate trade value and format time
            usd_size = price * quantity
            
            # Skip trades under $1000
            if usd_size < THRESHOLD:
                continue
                
            readable_trade_time = datetime.fromtimestamp(
                trade_time / 1000, 
                ZoneInfo("America/New_York")
            ).strftime('%H:%M:%S')
            
            # Format display symbol
            display_symbol = symbol.replace('USDT', '')
            
            # Determine trade type and color
            trade_type = side
            color = 'red' if trade_type == "Sell" else 'green'
            
            # Initialize stars and attributes based on trade size
            stars = '   '
            attrs = ['bold'] if usd_size >= 50000 else []
            repeat_count = 1
            
            # Format based on trade size
            if usd_size >= 100000:
                stars = ' **'
                repeat_count = 1
                if usd_size >= 500000:
                    stars = '***'
                    repeat_count = 1
                    if trade_type == "Sell":
                        color = 'magenta'
                    else:
                        color = 'blue'
            elif usd_size >= 50000:
                stars = '  *'
                # stars = '⭐' * 1
                repeat_count = 1
                
            # Create output string
            output = f"{stars}{trade_type} {display_symbol} {readable_trade_time} ${usd_size:,.2f}"
            
            # Print with formatting
            for _ in range(repeat_count):
                cprint(output, color, attrs=attrs)
            
            # Write to CSV
            with open(trades_filename, "a") as f:
                f.write(f"{event_time},{symbol},{price},{quantity},"
                       f"{trade_id},{trade_time},{side}\n")
                
    except Exception as e:
        print(f"Error processing message: {e}")

def handle_message(message):
    if message['topic'].startswith('publicTrade'):
        format_trade(message)

async def keep_alive():
    while True:
        await asyncio.sleep(1)

async def main():
    # Initialize WebSocket
    ws = WebSocket(
        testnet=False,
        channel_type="linear"
    )
    
    # Subscribe to trade streams for each symbol
    for symbol in SYMBOLS:
        ws.trade_stream(
            symbol=symbol,
            callback=handle_message
        )
    
    print(f"Subscribed to trade info for {', '.join(SYMBOLS)}")
    print("Waiting for trades (showing only trades > $1000)...")
    
    # Keep the connection alive
    await keep_alive()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")