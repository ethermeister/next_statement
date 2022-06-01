#!/usr/bin/env python
#
# Read PDF file from next.co.uk account section and extract details into a CSV
# Version 1.0
# Author: Marcelo Ramos
# License: MIT
#

import sys
import pdfplumber
import re
import csv
import pandas as pd
from dateutil.parser import parse
from datetime import datetime

# Define what to look for on a line to decide if it is a transaction
TRANSACTION = "^[0-9]{1,2}(st|nd|rd|th).*"
# Format date fields properly
DATE_FORMAT = "%d/%m/%Y"

document = sys.argv[1]
raw_transactions = []                       # List of all transactions as extracted from text
transaction = []                            # A transaction split into date, description, amount
transactions = []                           # List of transactions
csv_header = ["Date","Payee","Memo","Outflow","Inflow"]

with pdfplumber.open(document) as pdf:
    for page in pdf.pages:
        text = page.extract_text().splitlines()
        for line in text:
            if re.compile(TRANSACTION).match(line):
                raw_transactions.append(line)

for raw_transaction in raw_transactions:
    raw_transaction_values =  raw_transaction.split()[:-1]     # We pop the last field as we don't want running totals
    extracted_date = parse(' '.join(raw_transaction_values[:2]), fuzzy=True)
    transaction.append(extracted_date.strftime(DATE_FORMAT))
    transaction.append("NEXT Directory")                        # This never changes for this use case
    transaction.append(' '.join(raw_transaction_values[2:-1]))
    # Conditionally append to a certain part of the list depending on whether transaction
    # is a credit or a payment - on these statements a payment starts with "-"
    amount = raw_transaction_values.pop()
    if "-" in amount:
        transaction.append("")
        transaction.append(amount.replace("-", ""))
    else:
        transaction.append(amount)
        transaction.append("")
    transactions.append(transaction)
    transaction = []

# Save the list of transactions into a CSV
df = pd.DataFrame(transactions, columns=csv_header)
df.to_csv("output.csv", quoting=csv.QUOTE_ALL, index=False)
