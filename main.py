import pandas as pd
import pdfplumber as pp
import re
import collections

opening_balance_pattern = re.compile(r'^\d{2} \w{3} Openingbalance (\d+(?:\.\d+)?)$') #opening balance pattern may be greater than current balance and it could have a comma to sepearte if amount is in thousands or higher
pattern = re.compile(r'^(\d{2} \w{3}) ((?:\w{2} ))((?:\S+\s)*\S+)\s([\d,.]+)\s([\d,.]+\s*\w*)$') #pattern to get statement lines
year_pattern = re.compile(r'Statementperiod (\d{2} \w{3} \d{4}) - (\d{2} \w{3} \d{4})') #pattern to get the statement period year

def main():
    df = get_dataframe("test-statement.pdf")
    #print(df.head(10))
    df.to_csv('statement.csv')
    
def get_dataframe(filename):
    with pp.open(filename) as pdf:
        bank_line = collections.namedtuple("bank_line", "Date TransactionType TransactionDetails WD Balance")
        bank_line_items = []

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
                    start_date = year.group(1) #this should obtain the first part of the line eg just the 10 Dec 2022 as opposed to the 09 Mar 2023
                    current_year = int(start_date.split()[-1]) #apply the current year to the current_year variable so that it can be picked up if the datemonth is going to be decemeber and the next month is jan then can iterate current year and store actual year 
                    
                match = pattern.search(line)
                if match:
                    
                    date_month = match.group(1).split()[1] #splitting it so that I get only the month eg Sep, Mat etc 
                    if current_month == "Dec" and date_month == "Jan": #if the current month is Dec and the date month is Jan then it means that the current month year is 2022 however the datemonth if its Jan then the year for that month is 2023
                        current_year += 1 #current year will go up by 1 if the current month is Dec and the date month is jan
                    current_month = date_month #current month becomes date month 
                    
                    date = match.group(1) + " " + str(current_year) #when adding to the named tuple ensuring that the format is month year eg Mar 2022
                    transactiontype = match.group(2) 
                    transactiondetails = match.group(3)
                    Withdrawl_deposit = match.group(4).replace(",","") #although not on my statement it is a possibility that a there is a withdrawl or deposit of > 999 in which case a comma would be used to seperate it eg 1,000
                    balance = re.sub("[A-Za-z]","",match.group(5).replace(",","")) #replace all commas and any alpha variables. Although not in my statement I have seen statements where when overdraft there is a alphabet in there
                    
                    bank_line_items.append(bank_line(date,transactiontype,transactiondetails,Withdrawl_deposit,balance))
        
        df = pd.DataFrame(bank_line_items)
        openingBalance = float(opening_balance[0]) 

        for index,row in df.iterrows():
            if openingBalance > float(row['Balance']):
                df.at[index, "Withdrawals"] = row['WD']
            else:
                df.at[index, "Deposits"] = row['WD']
            openingBalance = float(row['Balance'])
                
        df = df.drop("WD", axis=1) #remove the WD column as withdrawals and deposits are now seperate 
        df = df[["Date","TransactionType","TransactionDetails","Withdrawals","Deposits","Balance"]] #re arranging the columns so that balance is at the end
        
        df = df.fillna(0) #is there are any null values then replace it with 0
        
        df['Date'] = pd.to_datetime(df["Date"], format ='%d %b %Y') #change the format of the data type in the columns so its easier to work with in excel
        df['Balance'] = pd.to_numeric(df["Balance"])
        df[['TransactionType', 'TransactionDetails']] = df[['TransactionType', 'TransactionDetails']].astype(str)
        
    return df 


main() 