from pybit.unified_trading import WebSocket
from time import sleep
from colorama import Fore, Style, init
from datetime import datetime

# Initialize colorama for colored output
init()

# Symbols we're interested in
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

def format_liquidation(data):
    symbol = data['symbol']
    side = data['side']
    price = float(data['price'])
    size = float(data['size'])
    timestamp = datetime.fromtimestamp(data['updatedTime'] / 1000).strftime('%H:%M:%S')
    
    color = Fore.RED if side == 'Sell' else Fore.GREEN
    return f"{color}{timestamp} {symbol.ljust(7)} {side.ljust(4)} {size:.6f} @{price:.2f}{Style.RESET_ALL}"

def handle_message(message):
    if message['topic'].startswith('liquidation'):
        print(format_liquidation(message['data']))

# Initialize WebSocket
ws = WebSocket(
    testnet=True,
    channel_type="linear",
)

# Subscribe to liquidation streams for each symbol
for symbol in SYMBOLS:
    ws.liquidation_stream(
        symbol=symbol,
        callback=handle_message
    )

print(f"Subscribed to liquidation info for {', '.join(SYMBOLS)}")
print("Waiting for liquidation events...")

# Keep the connection alive
while True:
    sleep(1)