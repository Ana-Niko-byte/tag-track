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

EXPENSES = {
    1 : 'Rent',
    2 : 'Groceries',
    3 : 'Vehicle',
    4 : 'Cafe/Restaurant',
    5 : 'Online Shopping',
    6 : 'Other'
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
    while True:
        escape_msg = '\nPlease press "Enter" to continue or type "q" to quit...'
        user_escape = input(escape_msg)
        if user_escape == 'q':
            print('exit')
            break
        # 'Enter' gives an empty string so we check for this instead.
        elif user_escape == '':
            break
        else:
            print(f'You have entered {user_escape}. Please try again.')
            return False
    return user_escape

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

def create_table(value, heading, colour = 'light_green'):
    """
    Creates tables using predefined tuple values.
    """
    # Assign PrettyTable object to month_table.
    table = PrettyTable()
    # Assign headings and iterate over each value in defined tuples to append to the table.
    table.field_names = [colored('No.', colour), colored(heading, colour)]
    for num, parameter in value.items():
        table.add_row([colored(num, 'grey'), colored(parameter, 'grey')])
        table.align = 'l'
    print(f'\n{table}')

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
    create_table(MONTHS, 'Month')
    while True:
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
    
def validate_category_selection(category_selection):
    """
    Validates the selected number input for the category in conjunction with the validate_num_selection() function.
    """
    if validate_num_selection(category_selection):
        if int(category_selection) > 0 and int(category_selection) <= 6:
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
    create_table(CURRENCY, 'Currency')
    while True:
        curr = input('\nPlease choose the currency you wish to log in: ')
        if validate_curr_selection(curr):
            escape = quick_escape()
            if escape == '':
                ask_category()
            break
    return curr

def ask_category():
    """
    Asks user to select one of the options in the category table for logging expenses. 
    If valid input, asks user if they wish to continue. 
    """
    create_table(EXPENSES, 'Expense Category', colour = 'magenta')
    while True:
        cat = input('\nPlease choose the category you wish to log in: ')
        if validate_category_selection(cat):
            escape = quick_escape()
            if escape == '':
                print('continuing...')
            break
    return cat
    
def main():
    print_intro()
    ask_name()
main()