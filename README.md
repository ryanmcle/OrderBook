# **Order Book Management System**

A Python application that simulates an order book for trading financial instruments (stocks). The system allows users to place buy and sell orders, view the current order book, match and execute orders, and visualize trade history. The project uses a GUI built with Tkinter and stores data in an SQLite database.

## **Table of Contents**

- [Features](#features)
- [Screenshot](#screenshot)
- [Technologies Used](#technologies-used)
- [Future Improvements](#future-improvements)

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

![Order Book GUI Screenshot](images/order_book_gui.png)

*Include a screenshot of your application here. To add the image to your README, place it in your repository's `images` directory and reference its path.*

## **Technologies Used**

- **Python 3**
- **Tkinter** for GUI development
- **SQLite3** for database management
- **yfinance** for fetching stock market data
- **Git** and **GitHub** for version control

## **Future Improvements**

- **Web-Based Interface:** Develop a web version of the application using Flask or Django.
- **User Authentication:** Implement user accounts and permissions.
- **Real-Time Data Streaming:** Integrate live data feeds for real-time updates.
- **Advanced Order Types:** Support for market orders, stop-loss, and other advanced order types.
- **Data Visualization:** Graphical representation of order book depth and trade volumes.
- **Automated Testing:** Implement unit tests to enhance reliability.
