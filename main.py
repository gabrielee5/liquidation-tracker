from pybit.unified_trading import WebSocket
from time import sleep

ws = WebSocket(
    testnet=False,
    channel_type="linear",
)

def handle_message(message):
    print(message)

ws.liquidation_stream(
    symbol="ETHUSDT",
    callback=handle_message
)

ws.liquidation_stream(
    symbol="BTCUSDT",
    callback=handle_message
)

ws.liquidation_stream(
    symbol="SOLUSDT",
    callback=handle_message
)

ws.trade_stream(
    symbol="BTCUSDT",
    callback=handle_message
)

while True:
    sleep(1)