# order_book.py

import sqlite3
from datetime import datetime
import yfinance as yf

def connect_db():
    """Connect to the SQLite database."""
    return sqlite3.connect('order_book.db')

def place_order(order_type, symbol, price, quantity):
    """Place a new buy or sell order."""
    conn = connect_db()
    cursor = conn.cursor()
    timestamp = datetime.utcnow().isoformat()

    cursor.execute("""
        INSERT INTO orders (timestamp, type, symbol, price, quantity, status, filled_qty)
        VALUES (?, ?, ?, ?, ?, 'open', 0)
    """, (timestamp, order_type, symbol, price, quantity))
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    print(f"Order {order_id} placed: {order_type.upper()} {quantity} {symbol} @ {price}")
    return order_id

def match_orders():
    """Match open buy and sell orders based on price-time priority."""
    conn = connect_db()
    cursor = conn.cursor()

    # Get list of unique symbols with open orders
    cursor.execute("""
        SELECT DISTINCT symbol FROM orders WHERE status='open'
    """)
    symbols = [row[0] for row in cursor.fetchall()]

    for symbol in symbols:
        # Fetch open buy orders for the symbol (highest price first)
        cursor.execute("""
            SELECT * FROM orders
            WHERE type='buy' AND status='open' AND symbol=?
            ORDER BY price DESC, timestamp ASC
        """, (symbol,))
        buy_orders = cursor.fetchall()

        # Fetch open sell orders for the symbol (lowest price first)
        cursor.execute("""
            SELECT * FROM orders
            WHERE type='sell' AND status='open' AND symbol=?
            ORDER BY price ASC, timestamp ASC
        """, (symbol,))
        sell_orders = cursor.fetchall()

        # Match orders
        buy_index = 0
        sell_index = 0
        while buy_index < len(buy_orders) and sell_index < len(sell_orders):
            buy_order = buy_orders[buy_index]
            sell_order = sell_orders[sell_index]

            if buy_order[4] >= sell_order[4]:  # buy_price >= sell_price
                execute_trade(buy_order, sell_order, cursor)

                # Update orders after execution
                cursor.execute("""
                    SELECT * FROM orders
                    WHERE order_id = ?
                """, (buy_order[0],))
                buy_order = cursor.fetchone()
                cursor.execute("""
                    SELECT * FROM orders
                    WHERE order_id = ?
                """, (sell_order[0],))
                sell_order = cursor.fetchone()

                # Update lists if orders are filled
                if buy_order[6] == 'filled':
                    buy_index += 1
                if sell_order[6] == 'filled':
                    sell_index += 1
            else:
                break  # Prices do not overlap, no further matches possible

    conn.commit()
    conn.close()

def execute_trade(buy_order, sell_order, cursor):
    """Execute a trade between a buy order and a sell order."""
    buy_order_id = buy_order[0]
    sell_order_id = sell_order[0]
    symbol = buy_order[3]
    timestamp = datetime.utcnow().isoformat()

    # Determine trade quantity
    remaining_buy_qty = buy_order[5] - buy_order[7]
    remaining_sell_qty = sell_order[5] - sell_order[7]
    trade_qty = min(remaining_buy_qty, remaining_sell_qty)

    # Trade price is the price of the sell order (price-time priority)
    trade_price = sell_order[4]

    # Insert trade record
    cursor.execute("""
        INSERT INTO trades (timestamp, buy_order_id, sell_order_id, symbol, price, quantity)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (timestamp, buy_order_id, sell_order_id, symbol, trade_price, trade_qty))

    # Update filled quantities
    cursor.execute("""
        UPDATE orders SET filled_qty = filled_qty + ? WHERE order_id = ?
    """, (trade_qty, buy_order_id))
    cursor.execute("""
        UPDATE orders SET filled_qty = filled_qty + ? WHERE order_id = ?
    """, (trade_qty, sell_order_id))

    # Update order statuses
    update_order_status(buy_order_id, cursor)
    update_order_status(sell_order_id, cursor)

    print(f"Executed trade: BUY order {buy_order_id} and SELL order {sell_order_id}, "
          f"Symbol: {symbol}, Quantity: {trade_qty}, Price: {trade_price}")

def update_order_status(order_id, cursor):
    """Update the status of an order based on its filled quantity."""
    cursor.execute("""
        SELECT quantity, filled_qty FROM orders WHERE order_id = ?
    """, (order_id,))
    quantity, filled_qty = cursor.fetchone()
    if filled_qty == 0:
        status = 'open'
    elif filled_qty < quantity:
        status = 'partial'
    elif filled_qty >= quantity:
        status = 'filled'
    else:
        status = 'error'

    cursor.execute("""
        UPDATE orders SET status = ? WHERE order_id = ?
    """, (status, order_id))

def cancel_order(order_id):
    """Cancel an open order."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE orders SET status='cancelled' WHERE order_id=? AND status='open'
    """, (order_id,))
    if cursor.rowcount == 0:
        print(f"Order {order_id} cannot be cancelled (may already be filled or cancelled).")
    else:
        print(f"Order {order_id} has been cancelled.")
    conn.commit()
    conn.close()

def get_open_orders():
    """Retrieve all open orders."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT order_id, timestamp, type, symbol, price, (quantity - filled_qty) AS remaining_qty, status
        FROM orders WHERE status='open'
        ORDER BY timestamp ASC
    """)
    orders = cursor.fetchall()
    conn.close()
    return orders

def get_stock_symbols():
    """Retrieve all stock symbols from the stocks table."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT symbol FROM stocks")
    symbols = [row[0] for row in cursor.fetchall()]
    conn.close()
    return symbols

def get_order_book(symbol):
    """Retrieve the order book for a specific symbol."""
    conn = connect_db()
    cursor = conn.cursor()

    # Sell Orders (Asks)
    cursor.execute("""
        SELECT price, SUM(quantity - filled_qty) AS qty
        FROM orders
        WHERE type='sell' AND status='open' AND symbol=?
        GROUP BY price
        ORDER BY price ASC
    """, (symbol,))
    asks = cursor.fetchall()

    # Buy Orders (Bids)
    cursor.execute("""
        SELECT price, SUM(quantity - filled_qty) AS qty
        FROM orders
        WHERE type='buy' AND status='open' AND symbol=?
        GROUP BY price
        ORDER BY price DESC
    """, (symbol,))
    bids = cursor.fetchall()

    conn.close()
    return bids, asks

def get_trades():
    """Retrieve the trade history."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT trade_id, timestamp, symbol, price, quantity
        FROM trades
        ORDER BY timestamp DESC
    """)
    trades = cursor.fetchall()
    conn.close()
    return trades

def update_stock_prices():
    """Update current prices of stocks in the database using yfinance."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT symbol FROM stocks")
    symbols = [row[0] for row in cursor.fetchall()]
    updated_stocks = []

    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            if data.empty:
                continue
            current_price = data['Close'][0]
            updated_stocks.append((current_price, symbol))
        except Exception as e:
            print(f"Error updating price for {symbol}: {e}")

    cursor.executemany("""
        UPDATE stocks SET current_price = ? WHERE symbol = ?
    """, updated_stocks)

    conn.commit()
    conn.close()
    print("Stock prices updated.")
