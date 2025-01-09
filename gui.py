# gui.py

import tkinter as tk
from tkinter import ttk, messagebox
from order_book import place_order, match_orders, cancel_order, get_stock_symbols, get_order_book, get_trades, update_stock_prices
import sqlite3

class OrderBookGUI:
    def __init__(self, master):
        self.master = master
        master.title("Order Book Management System")
        master.geometry("800x600")

        # Fetch stock symbols
        self.symbols = get_stock_symbols()

        # Create variables
        self.order_type = tk.StringVar(value="buy")
        self.symbol = tk.StringVar(value=self.symbols[0] if self.symbols else "")
        self.price = tk.DoubleVar()
        self.quantity = tk.DoubleVar()
        self.selected_symbol = tk.StringVar(value=self.symbols[0] if self.symbols else "")

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        # Order Placement Frame
        order_frame = ttk.LabelFrame(self.master, text="Place Order")
        order_frame.pack(fill='x', padx=10, pady=5)

        # Order Type
        ttk.Label(order_frame, text="Order Type:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        ttk.Radiobutton(order_frame, text="Buy", variable=self.order_type, value="buy").grid(row=0, column=1, sticky='w')
        ttk.Radiobutton(order_frame, text="Sell", variable=self.order_type, value="sell").grid(row=0, column=2, sticky='w')

        # Symbol
        ttk.Label(order_frame, text="Symbol:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.symbol_combo = ttk.Combobox(order_frame, textvariable=self.symbol)
        self.symbol_combo['values'] = self.symbols
        self.symbol_combo.grid(row=1, column=1, columnspan=2, sticky='we')
        self.symbol_combo.current(0)

        # Price
        ttk.Label(order_frame, text="Price:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.price_entry = ttk.Entry(order_frame, textvariable=self.price)
        self.price_entry.grid(row=2, column=1, columnspan=2, sticky='we')

        # Quantity
        ttk.Label(order_frame, text="Quantity:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.quantity_entry = ttk.Entry(order_frame, textvariable=self.quantity)
        self.quantity_entry.grid(row=3, column=1, columnspan=2, sticky='we')

       # Place Order Button
        self.place_order_button = ttk.Button(order_frame, text="Place Order", command=self.place_order)
        self.place_order_button.grid(row=4, column=1, pady=10, sticky='e')

        # Select Symbol for Order Book
        ttk.Label(order_frame, text="Order Book Symbol:").grid(row=5, column=0, sticky='e', padx=5, pady=5)
        self.order_book_symbol_combo = ttk.Combobox(order_frame, textvariable=self.selected_symbol)
        self.order_book_symbol_combo['values'] = self.symbols
        self.order_book_symbol_combo.grid(row=5, column=1, columnspan=2, sticky='we')
        self.order_book_symbol_combo.current(0)
        self.order_book_symbol_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_order_book())

        # Order Book Frame
        book_frame = ttk.LabelFrame(self.master, text="Order Book")
        book_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.order_book_panes = ttk.PanedWindow(book_frame, orient=tk.HORIZONTAL)
        self.order_book_panes.pack(fill='both', expand=True)

        # Bids Treeview
        bids_frame = ttk.Frame(self.order_book_panes)
        self.bids_tree = ttk.Treeview(bids_frame, columns=('Price', 'Quantity'), show='headings')
        self.bids_tree.heading('Price', text='Bid Price')
        self.bids_tree.heading('Quantity', text='Bid Quantity')
        self.bids_tree.pack(fill='both', expand=True)
        self.order_book_panes.add(bids_frame, weight=1)

        # Asks Treeview
        asks_frame = ttk.Frame(self.order_book_panes)
        self.asks_tree = ttk.Treeview(asks_frame, columns=('Price', 'Quantity'), show='headings')
        self.asks_tree.heading('Price', text='Ask Price')
        self.asks_tree.heading('Quantity', text='Ask Quantity')
        self.asks_tree.pack(fill='both', expand=True)
        self.order_book_panes.add(asks_frame, weight=1)

        # Controls Frame (Define before using it)
        controls_frame = ttk.Frame(self.master)
        controls_frame.pack(fill='x', padx=10, pady=5)

        # Match Orders Button
        self.match_button = ttk.Button(controls_frame, text="Match Orders", command=self.match_orders)
        self.match_button.pack(side='left', padx=5)

        # Refresh Button
        self.refresh_button = ttk.Button(controls_frame, text="Refresh Order Book", command=self.refresh_order_book)
        self.refresh_button.pack(side='left', padx=5)

        # Update Prices Button
        self.update_prices_button = ttk.Button(controls_frame, text="Update Prices", command=self.update_prices)
        self.update_prices_button.pack(side='left', padx=5)

        # Trades Frame
        trades_frame = ttk.LabelFrame(self.master, text="Trade History")
        trades_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Trades Treeview
        self.trades_tree = ttk.Treeview(trades_frame, columns=('Trade ID', 'Timestamp', 'Symbol', 'Price', 'Quantity'), show='headings')
        self.trades_tree.heading('Trade ID', text='Trade ID')
        self.trades_tree.heading('Timestamp', text='Timestamp')
        self.trades_tree.heading('Symbol', text='Symbol')
        self.trades_tree.heading('Price', text='Price')
        self.trades_tree.heading('Quantity', text='Quantity')
        self.trades_tree.pack(fill='both', expand=True)

        # Refresh Trades Button
        self.refresh_trades_button = ttk.Button(trades_frame, text="Refresh Trades", command=self.refresh_trades)
        self.refresh_trades_button.pack(pady=5)

        # Initial refresh
        self.refresh_order_book()
        self.refresh_trades()


    def place_order(self):
        """Event handler for placing an order."""
        order_type = self.order_type.get()
        symbol = self.symbol.get().upper()
        try:
            price = float(self.price.get())
            quantity = float(self.quantity.get())
            if price <= 0 or quantity <= 0:
                raise ValueError
            place_order(order_type, symbol, price, quantity)
            messagebox.showinfo("Success", "Order placed successfully.")
            self.refresh_order_book()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid price and quantity.")

    def refresh_order_book(self):
        """Refresh the order book display for the selected symbol."""
        symbol = self.selected_symbol.get().upper()

        # Clear current contents
        for row in self.bids_tree.get_children():
            self.bids_tree.delete(row)
        for row in self.asks_tree.get_children():
            self.asks_tree.delete(row)

        # Get order book data
        bids, asks = get_order_book(symbol)

        # Insert bids into the treeview
        for price, qty in bids:
            self.bids_tree.insert('', 'end', values=(price, qty))

        # Insert asks into the treeview
        for price, qty in asks:
            self.asks_tree.insert('', 'end', values=(price, qty))

    def match_orders(self):
        """Event handler for matching orders."""
        match_orders()
        messagebox.showinfo("Info", "Order matching completed.")
        self.refresh_order_book()
        self.refresh_trades()

    def refresh_trades(self):
        """Refresh the trade history display."""
        # Clear current contents
        for row in self.trades_tree.get_children():
            self.trades_tree.delete(row)

        # Get trade history
        trades = get_trades()

        # Insert trades into the treeview
        for trade in trades:
            self.trades_tree.insert('', 'end', values=trade)
    
    def update_prices(self):
        """Update stock prices from yfinance and refresh order book."""
        update_stock_prices()
        messagebox.showinfo("Info", "Stock prices updated.")
        self.refresh_order_book()

if __name__ == '__main__':
    root = tk.Tk()
    app = OrderBookGUI(root)
    root.mainloop()
