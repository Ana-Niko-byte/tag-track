import gspread
from google.oauth2.service_account import Credentials
from art import *
from colorama import Fore
from prettytable import PrettyTable
from termcolor import colored

# Scope of application credentials, code and links taken from love-sandwiches project.
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
# Months the user can select when logging an expense. 
MONTHS = {
        1 : 'January',
        2 : 'February', 
        3 : 'March', 
        4 : 'April', 
        5 : 'May', 
        6 : 'June', 
        7 : 'July', 
        8 : 'August', 
        9 : 'September', 
        10 : 'October', 
        11 : 'November',
        12 : 'December'
    }

# Currency the user can select for logging an expense. 
CURRENCY = {
    1 : 'EUR',
    2 : 'GBP',
    3 : 'USD',
    4 : 'AUD',
    5 : 'PLN'
}

CREDS = Credentials.from_service_account_file('creds.json')
CREDS_SCOPE = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(CREDS_SCOPE)
SHEET = GSPREAD_CLIENT.open('Tag-Track')

def print_intro():
    """
    Prints large heading. 
    """
    text = text2art('Tag - Tracker')
    print(Fore.GREEN + 'Welcome to')
    print(Fore.GREEN + text + Fore.RESET)

def quick_escape():
    """
    Allow users to exit the log or continue in the application
    """
    print('\nCheckpoint!')
    escape_msg = '\nPlease press "Enter" to continue or type "q" to quit...'
    return input(escape_msg)

def validate_string(string):
    """
    Validates any string input for alphabet-only characters. 
    Returns true if no digits or symbols are present. 
    """
    return string.isalpha()

def validate_num_selection(num):
    """
    Validates any number input. 
    Returns true if no digits or symbols are present. 
    """
    return num.isdigit()

def ask_name():
    """
    A user loop asking for name until valid input is provided. 
    Once valid, the user is asked to selected a month from the provided list. 
    """
    while True:
        name = input('Please tell me your name: ')
        if validate_string(name):
            ask_month()
            break
    return name

def ask_month():
    """
    Asks user to select one of the options in the months table for logging expenses. 
    If valid input, asks users to select the currency they wish to proceed with. 
    """
    while True:
        # Assign PrettyTable object to month_table
        month_table = PrettyTable()
        # Assign headings and iterate over each value in tuple MONTHS to append to the table. 
        month_table.field_names = [colored('No.', 'light_green'), colored('Month', 'light_green')]
        for num, month in MONTHS.items():
            month_table.add_row([colored(num, 'grey'), colored(month, 'grey')])
            month_table.align = 'l'
        print(f'\n{month_table}')
        month = input('\nPlease choose the month you want to log for: ')
        if validate_month_selection(month):
            ask_curr()
            break
    return month

def validate_month_selection(month_selection):
    """
    Validates the selected number input for the month in conjunction with the validate_num_selection() function.
    """
    if validate_num_selection(month_selection):
        if int(month_selection) > 0 and int(month_selection) <= 12:
            return True
        else:
            print('Please choose one of the options provided.')
            return False
    else:
        return False

def validate_curr_selection(curr_selection):
    """
    Validates the selected number input for the currency in conjunction with the validate_num_selection() function.
    """
    if validate_num_selection(curr_selection):
        if int(curr_selection) > 0 and int(curr_selection) <= 5:
            return True
        else:
            print('Please choose one of the options provided.')
            return False
    else:
        return False

def ask_curr():
    """
    Asks user to select one of the options in the currency table for logging expenses. 
    If valid input, asks user if they wish to continue. 
    """
    while True:
        # Assign PrettyTable object to curr_table
        curr_table = PrettyTable()
        # Assign headings and iterate over each value in tuple MONTHS to append to the table. 
        curr_table.field_names = [colored('No.', 'light_green'), colored('Currency', 'light_green')]
        for num, currency in CURRENCY.items():
            curr_table.add_row([colored(num, 'grey'), colored(currency, 'grey')])
            curr_table.align = 'l'
        print(f'\n{curr_table}')
        curr = input('\nPlease choose the currency you wish to log in: ')
        if validate_curr_selection(curr):
            quick_escape()
            break
    return curr

def main():
    print_intro()
    ask_name()
main()