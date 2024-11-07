import asyncio
import json
from datetime import datetime
from pybit.unified_trading import WebSocket
from termcolor import cprint
import os
from zoneinfo import ZoneInfo

# Configuration
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
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
            
            # Calculate trade value
            usd_size = price * quantity
            
            # Format time
            readable_trade_time = datetime.fromtimestamp(
                trade_time / 1000, 
                ZoneInfo("America/New_York")
            ).strftime('%H:%M:%S')
            
            # Create output string with new format
            output = f"{readable_trade_time} {symbol} {side.ljust(4)} {quantity:,.6f} @{price:.2f} (${usd_size:,.2f})"
            
            # Determine color based on side
            color = 'red' if side == "Sell" else 'green'
            
            # Print with formatting
            cprint(output, color)
            
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
    print("Waiting for trades...")

    # Keep the connection alive
    await keep_alive()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")