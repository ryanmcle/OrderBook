# **Stock Order Book**

A Python application that simulates an order book for trading financial instruments (stocks). The system allows users to place buy and sell orders, view the current order book, match and execute orders, and visualize trade history. The project uses a GUI built with Tkinter and stores data in an SQLite database.

## **Video**

![Order Book Video](https://github.com/ryanmcle/OrderBook/blob/main/ScreenRecording2025-01-09190043-ezgif.com-video-to-gif-converter.gif)

## **Features**

- **GUI Application:** User-friendly interface built with Tkinter.
- **Order Placement:** Place buy or sell orders with specified price and quantity.
- **Multiple Market Makers:** Pre-loaded bid and ask orders from different market makers with varying prices and quantities.
- **Order Matching Engine:** Automatically matches orders based on price-time priority whenever bid and ask prices overlap.
- **Order Book Display:** View current bids and asks for selected stock symbols.
- **Trade History:** View a history of executed trades.
- **Stock Price Updates:** Fetch real-time stock data using `yfinance` and update prices within the application.
- **Data Persistence:** All orders and trades are stored using SQLite3.

## **Screenshot**

![Order Book GUI Screenshot](https://github.com/ryanmcle/OrderBook/blob/main/OrderBook.png)

## **Technologies Used**

- **Python 3**
- **Tkinter** for GUI development
- **SQLite3** for database management
- **yFinance** for fetching stock market data
- **Git** and **GitHub** for version control
