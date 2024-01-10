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

def validate_string(string):
    """
    Validates any string input for alphabet-only characters. 
    Returns true if no digits or symbols are present. 
    """
    return string.isalpha()

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
    if valid input, asks users to select the currency they wish to proceed with. 
    """
    # Assign PrettyTable object to month_table
    month_table = PrettyTable()
    # Assign headings and iterate over each value in tuple MONTHS to append to the table. 
    month_table.field_names = [colored('No.', 'light_green'), colored('Month', 'light_green')]
    for num, month in MONTHS.items():
        month_table.add_row([colored(num, 'grey'), colored(month, 'grey')])
        month_table.align = 'l'
    print(f'\n{month_table}')
    month = input('\nPlease choose the month you want to log for: ')
    validate_num_selection(month)

    return month

def validate_num_selection(num):
    if num.isdigit():
        print('I\'m a number')
    else:
        print('input number')


def main():
    print_intro()
    ask_name()
main()