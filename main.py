import pandas as pd
import pdfplumber as pp
import re
import collections

def main():
    df = get_dataframe("test-statement.pdf")
    
def get_dataframe(filename):
    with pp.open(filename) as pdf:
        bank_line = collections.namedtuple("bank_line", "Date TransactionType TransactionDetails WD Balance")
        bank_line_items = []
        
        opening_balance_pattern = re.compile(r'^\d{2} \w{3} Openingbalance (\d+(?:\.\d+)?)$') #opening balance pattern may be greater than current balance and it could have a comma to sepearte if amount is in thousands or higher
        pattern = re.compile(r'^(\d{2} \w{3}) ((?:\w{2} ))((?:\S+\s)*\S+)\s([\d,.]+)\s([\d,.]+\s*\w*)$') #pattern to get statement lines
        year_pattern = re.compile(r'Statementperiod (\d{2} \w{3} \d{4}) - (\d{2} \w{3} \d{4})') #pattern to get the statement period year
        
        opening_balance = []
        current_year = 0
        current_month = ''
        
        for page in pdf.pages: #for loop to iterate through all of the pages in the document
            text = page.extract_text() #extract the text from each page 
            text_list = text.split('\n') #split the contents of the page by a new line and create a list of all of the items from the page
            for line in text_list: #interate through the split content 
                
                bal = opening_balance_pattern.search(line) #obtain the opening blance of that page 
                if bal:
                    opening_balance.append(bal.group(1))
                
                year = year_pattern.search(line) #obtains the lines from the bank statement where there is statement period format for that line should be "Statement period 10 Mar 2023 - 09 Jun 2023"
                if year:
                    print(year)
                    start_date = year.group(1) #this should obtain the first part of the line eg just the 10 Dec 2022 as opposed to the 09 Mar 2023
                    print(start_date)
                    current_year = int(start_date.split()[-1])
                    print(current_year)
                    
                    
    return

main() 