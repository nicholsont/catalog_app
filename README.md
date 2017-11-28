# Catalog App

The Catalog App is a simple script to catalog games that you own.  The items are categorized and saved into a database
file using sqlite. The database used contains the tables user, category, and item. The app implements Third Party OAuth
login from Google and Facebook to eliminate the need to for setting up a separate authentication and authorization
process and the need to store passwords.  The catalog can be viewed without logging in but all creating, updating, and
deleting functions are only available to users logged in to the app.  The app also sets up JSON endpoints where
serialized data can be accessed.


## Requirements

* Python 2.7
* Flask version >=0.9

## Installation
1. Clone the GitHub repository then cd to catalog.
  ```
  $ git clone https://github.com/nicholsont/catalog_app.git
  $ cd catalog
  ```

## Usage
How to run Request Log Analysis Tool

1. Use python to run database.py to import catalog database.
  ```
  $ python database.py
  ```
2. Use python to run the catalog app.
  ```
  $ python application.py
  ```

## License
Please refer to the [License](LICENSE.md).
