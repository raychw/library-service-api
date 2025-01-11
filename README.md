# Library Service API

A simple Library Service API for your local library!

## Description

This project serves for you to comfortably manage your library. Starting from adding and updating books'
information (such as inventory, cover type, and daily fee), ending with practical borrowings and payments system
with the direct user's interaction - anybody can register and borrow a book.

## Features

* **In-depth book information management:**
    * Add new books to the library
    * Update existing books' information (title, author, inventory, cover, etc.)
    * Delete books from the library
    * Only staff members can manage books' information


* **Practical and secure registration and authorization system:**
    * Anybody can register at the library
    * Secure authorization via JWT token
    * Only registered users can borrow books
    * Users can manage their profile information


* **User-friendly borrowing and return system:**
    * Logical constraints for borrowing books to protect the service
    * Simple and intuitive borrowing process with the automatic fee calculation
    * Convenient return process with the automatic fine calculation if book is returned late
    * Users can see and filter their borrowings
    * Staff can see and filter all borrowings by user and activity


* **Flexible and secure payment system:**
    * Integrated Stripe payment system
    * The payment is automatically calculated and attached when the borrowing is made and when the book is returned late
    * Users can see their payment history attached to each borrowing
    * Staff can see all payments
    * Success and cancel urls are provided for the user to be redirected after the payment


* **Convenient Telegram bot notifications:**
    * A practical positive notification is sent when the service is ready to use.
    * The notification is sent automatically upon borrowing a new book with the precise information.
    * A scheduled daily check for overdue borrowings via Django-Q service.


## Getting Started

### Dependencies

* Python 3.13
* Django >4.0
* Telegram
* PostgreSQL 16.0
* Docker & Docker Compose

### Installing and Executing program

* Checkout the .env.sample file and make sure that you have everything filled in there:
    * Make sure to set up the Telegram bot token and chat id for the notifications
    * Also, the Stripe keys for the payment system
    * PostgreSQL database settings
    * And last, but not least, the Django secret key


* Then execute the following code:

``` shell
git clone https://github.com/raychw/library-service-api
cd library-service-api
docker-compose up
```
