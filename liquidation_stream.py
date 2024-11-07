import asyncio
import json
from datetime import datetime
from pybit.unified_trading import WebSocket
from termcolor import cprint
import os
from zoneinfo import ZoneInfo
from alert import play_alert

# Configuration
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "FETUSDT"]
liquidation_filename = "bybit_liquidations.csv"

# Create/check liquidations file
if not os.path.isfile(liquidation_filename):
    with open(liquidation_filename, "w") as f:
        f.write("Timestamp,Symbol,Side,Size,Price,USD_Value\n")

def format_liquidation(message):
    try:
        liq_data = message['data']
        
        # Extract liquidation data
        timestamp = int(message['ts'])
        symbol = liq_data['symbol']
        side = liq_data['side']
        size = float(liq_data['size'])
        price = float(liq_data['price'])
        
        # Calculate USD value
        usd_value = price * size # wrong, the price is the bankruptcy price. modify with actual price
        
        # Format readable time
        readable_time = datetime.fromtimestamp(
            timestamp / 1000,
            ZoneInfo("America/New_York")
        ).strftime('%H:%M:%S')
        
        # Format display symbol
        display_symbol = symbol.replace('USDT', '')
        
        # Determine formatting based on size and side
        color = 'red' if side == "Sell" else 'blue'

        # convert to long/short for better clarity
        direction = 'Long' if side == "Buy" else 'Short'
        
        # Initialize stars and attributes based on liquidation size
        stars = '   '
        attrs = ['bold']
        
        # Format based on liquidation size
        if usd_value >= 1000000:  # $1M+
            stars = '***'
            if side == "Sell":
                color = 'magenta'
            else:
                color = 'cyan'
        elif usd_value >= 500000:  # $500k+
            stars = ' **'
        elif usd_value >= 100000:  # $100k+
            stars = '  *'
            
        # Create output string
        output = (
            f"{stars}{readable_time} {display_symbol} "
            f"LIQUIDATED {direction.upper()} "
            f"{size:.3f} contracts "
            # f"@ ${price:,.2f} " # this is the bankruptcy price 
            f"(${usd_value:,.2f})"
        )
        
        # Print with formatting
        cprint(output, color, attrs=attrs)
        if usd_value > 100000: play_alert('Sosumi')
        
        # Write to CSV
        with open(liquidation_filename, "a") as f:
            f.write(f"{timestamp},{symbol},{side},{size},{price},{usd_value}\n")
                
    except Exception as e:
        print(f"Error processing liquidation: {e}")

def handle_message(message):
    if message['topic'].startswith('liquidation'):
        format_liquidation(message)

async def keep_alive():
    while True:
        await asyncio.sleep(1)

async def main():
    # Initialize WebSocket
    ws = WebSocket(
        testnet=False,
        channel_type="linear"
    )
    
    # Subscribe to liquidation streams for each symbol
    for symbol in SYMBOLS:
        ws.liquidation_stream(
            symbol=symbol,
            callback=handle_message
        )
    
    print(f"Subscribed to liquidation info for {', '.join(SYMBOLS)}")
    print("Monitoring liquidations...")
    print("Stars indicate size: *** $1M+, ** $500k+, * $100k+")
    print("Format: Time Symbol SIDE Size @ Price (USD Value)")
    
    # Keep the connection alive
    await keep_alive()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")