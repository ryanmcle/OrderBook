# db_setup.py

import sqlite3
from datetime import datetime
import yfinance as yf

def create_connection(db_file):
    """Create a database connection to a SQLite database."""
    conn = sqlite3.connect(db_file)
    return conn

def create_tables(conn):
    """Create tables in the SQLite database."""
    orders_table = """CREATE TABLE IF NOT EXISTS orders (
                        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        type TEXT NOT NULL CHECK (type IN ('buy', 'sell')),
                        symbol TEXT NOT NULL,
                        price REAL NOT NULL,
                        quantity REAL NOT NULL,
                        status TEXT NOT NULL CHECK (status IN ('open', 'partial', 'filled', 'cancelled')),
                        filled_qty REAL NOT NULL DEFAULT 0
                      );"""

    trades_table = """CREATE TABLE IF NOT EXISTS trades (
                        trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        buy_order_id INTEGER NOT NULL,
                        sell_order_id INTEGER NOT NULL,
                        symbol TEXT NOT NULL,
                        price REAL NOT NULL,
                        quantity REAL NOT NULL,
                        FOREIGN KEY (buy_order_id) REFERENCES orders (order_id),
                        FOREIGN KEY (sell_order_id) REFERENCES orders (order_id)
                      );"""

    stocks_table = """CREATE TABLE IF NOT EXISTS stocks (
                        symbol TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        current_price REAL NOT NULL
                      );"""

    cursor = conn.cursor()
    cursor.execute(orders_table)
    cursor.execute(trades_table)
    cursor.execute(stocks_table)
    conn.commit()

def preload_stocks_and_orders(conn):
    """Fetch stock data from yfinance and preload stocks and multiple orders."""
    stock_symbols = ['AAPL', 'GOOGL', 'AMZN', 'MSFT', 'TSLA']
    stocks = []
    orders = []
    timestamp = datetime.utcnow().isoformat()

    for symbol in stock_symbols:
        try:
            ticker = yf.Ticker(symbol)
            # Get live price data
            data = ticker.history(period='1d')
            if data.empty:
                print(f"No data found for {symbol}. Skipping.")
                continue
            current_price = data['Close'][0]
            name = ticker.info.get('shortName', symbol)
            stocks.append((symbol, name, current_price))

            # Generate 5 bid and ask orders around the current price
            for i in range(1, 6):
                # Simulate market makers with different prices and quantities
                bid_price = round(current_price * (1 - 0.005 * i), 2)  # Decrease by 0.5% each step
                ask_price = round(current_price * (1 + 0.005 * i), 2)  # Increase by 0.5% each step
                bid_quantity = 100 + i * 10  # Increase quantity by 10 each step
                ask_quantity = 100 + i * 15  # Increase quantity by 15 each step

                # Create bid orders (Buy)
                orders.append((timestamp, 'buy', symbol, bid_price, bid_quantity, 'open', 0))

                # Create ask orders (Sell)
                orders.append((timestamp, 'sell', symbol, ask_price, ask_quantity, 'open', 0))
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

    cursor = conn.cursor()
    # Insert stocks into the stocks table
    cursor.executemany("""
        INSERT OR REPLACE INTO stocks (symbol, name, current_price)
        VALUES (?, ?, ?)
    """, stocks)

    # Insert orders into the orders table
    cursor.executemany("""
        INSERT INTO orders (timestamp, type, symbol, price, quantity, status, filled_qty)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, orders)

    conn.commit()
    print("Stocks and initial orders pre-loaded into the database.")

if __name__ == '__main__':
    conn = create_connection('order_book.db')
    create_tables(conn)
    preload_stocks_and_orders(conn)
    conn.close()
    print("Database and tables created successfully.")

    # Perform initial order matching
    from order_book import match_orders
    match_orders()
    print("Initial order matching completed.")
