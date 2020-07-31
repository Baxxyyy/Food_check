# Food_check

Food check is a simple script made to check for foods that are going to exipire

Currently it uses a very simple system, connecting a google sheets and reading the first two columns (A1:B1000), extracting the name of item from the first column, and then the date of the item (in the format [day,month]) e.g. Carrots | [2,11] woulld be interpreted as carrots which go out of date on the 2nd of Novemember, 2020.

This information is then sent to emails using mailgun, based on what will expire on on the day, the next day and then the next 2-3 days.

As a requirement of using this script, a number of python modules must be installed, some like decouple and gspread can be installed via pip, datetime, ast, json and requests come standard in python 3, however the main bulk of the modules comes from googles api install, which can be found here: https://github.com/googleapis/google-api-python-client
