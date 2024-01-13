import gspread
from google.oauth2.service_account import Credentials
from art import *
from colorama import Fore
from prettytable import PrettyTable
from termcolor import colored
from currencies import Currency

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

# Categories the user can select for logging an expense. 
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

# List of read-only headers from google sheets. These are used in user-feedback throughout the application. 
COLUMNS = []
# List of global variables - user_gsheet -> google sheet, user_budget -> user budget for the month. 
user_gsheet = None
user_budget = None

def print_intro():
    """
    Prints large heading. 
    """
    text = text2art('Tag - Tracker')
    print(Fore.LIGHTGREEN_EX + 'Welcome to')
    print(Fore.LIGHTGREEN_EX + text + Fore.RESET)

# _________ Beginning of shared functionalities, called throughout the application.
def quick_escape():
    """
    Allow users to exit the log or continue in the application
    """
    print('\nCheckpoint!')
    while True:
        escape_msg = '\n➤ Please press "Enter" to continue or type "q" to quit...'
        user_escape = input(escape_msg)
        if user_escape == 'q':
            print(f'👋 You pressed "q". Exiting...')
            break
        # 'Enter' gives an empty string so we check for this instead.
        elif user_escape == '':
            break
        else:
            print(f'❌ Invalid input. You entered {user_escape}. Please try again.')
            return False
    return user_escape

def validate_string(string):
    """
    Validates any string input for alphabet-only characters. 
    Returns true if no digits or symbols are present. 
    """
    if not string:
        print('❌ Please enter a value to begin.\n')
    elif not all(letter.isalpha() for letter in string.split()):
        print('❌ Why you using digits, bro?\n')
    else:
        return True

def validate_num_selection(num):
    """
    Validates any number input. 
    Returns true if no digits or symbols are present. 
    """
    if not num:
        print('❌ Please enter a value to begin.\n')
    elif not all(digit.isdigit() for digit in num.split()):
        print('❌ Why you not using digits only, bro?\n')
    return num.isdigit()

def validate_selection(selection, num_range, min_num_range = 0):
    """
    Validates the selected input in conjunction with the validate_num_selection() function using a set number range.
    """
    if validate_num_selection(selection):
        if int(selection) > min_num_range and int(selection) <= num_range:
            return True
        else:
            print(f'❌ Invalid input. Please choose one of the {num_range} options provided.')
            return False
    else:
        return False

def create_table(value, heading, colour = 'light_green'):
    """
    Creates tables using predefined tuple values.
    """
    # Assign PrettyTable object to month_table.
    table = PrettyTable()
    # Assign headings and iterate over each value in defined tuples to append to the table.
    table.field_names = [colored('No.', colour), colored(heading, colour)]
    for num, parameter in value.items():
        table.add_row([colored(num, 'white'), colored(parameter, 'white')])
        table.align = 'l'
    print(f'\n{table}')
# _________ End of shared functionalities.

def ask_name():
    """
    A user loop asking for name until valid input is provided. 
    Once valid, the user is asked to selected a month from the provided list. 
    """
    while True:
        name = input('➤ Please tell me your name: ').strip()
        if validate_string(name):
            capitalised = name.capitalize()
            print(f'\n✅ Hey, {capitalised}!')
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
        month = input('\n➤ Please choose the month you want to log for: ')
        if validate_selection(month, 12):
            month_name = MONTHS[int(month)]
            print(f'\n✅ You have chosen {month_name}.')
            get_month_sheet(month_name)
            ask_curr()
            break
    return month_name

def get_month_sheet(month_needed):
    """
    Fetches the worksheet based on the month the user chose. 
    """
    print(f'Fetching the {month_needed} worksheet...\n')
    global user_gsheet 
    user_gsheet = SHEET.worksheet(month_needed)
    print(f'Got it! Hold on while we fetch the next table...\n')
    return user_gsheet

def ask_curr():
    """
    Asks user to select one of the options in the currency table for logging expenses. 
    If valid input, asks user if they wish to continue. 
    """
    create_table(CURRENCY, 'Currency')
    while True:
        curr = input('\n➤ Please choose the currency you wish to log in: ')
        if validate_selection(curr, 5):
            print(f'✅ You have chosen to log in {CURRENCY[int(curr)]}')
            escape = quick_escape()
            if escape == '':
                ask_budget(curr)
            break
    return curr

def format_budget(curr, budget):
    """
    Formats the user's budget with the chosen currency symbol. 
    """
    # Code taken from Currency example on (https://pypi.org/project/currencies/).
    currency = Currency(CURRENCY[int(curr)])
    formatted_budget = currency.get_money_format(budget)
    print(f'✅ Budget: {formatted_budget}')
    return format_budget

def ask_budget(curr):
    """
    Asks user for budget and updates global budget variable.
    If valid input, asks user if they wish to continue. 
    """
    budget = input('\n➤ Please input your budget for this month: ')
    if validate_num_selection(budget):
        global user_budget
        user_budget = budget
        format_budget(curr, user_budget)
        create_table(EXPENSES, 'Expense Category', colour = 'magenta')
        ask_category()
    return user_budget

def ask_category():
    """
    Asks user to select one of the options in the category table for logging expenses. 
    If valid input, asks user if they wish to continue. 
    """
    while True:
        cat = input('\n➤ Please choose a category: ')
        if validate_selection(cat, 6):
            if int(cat) == 1 or int(cat) == 2:
                print(f'✅ Ouch...spending on {EXPENSES[int(cat)]}...')
            elif int(cat) > 2 and int(cat) != 6:
                print(f'✅ Ooo...spending on {EXPENSES[int(cat)]}? Nice!')
            escape = quick_escape()
            if escape == '':
                ask_expense(EXPENSES[int(cat)])
            break
    return cat
    
def ask_expense(category):
    """
    Asks user for expense in the chosen category. 
    If valid input, asks user if they wish to continue. 
    """
    while True:
        expense_msg = f'\n➤ Please enter the amount you spent on {category}: '
        user_expense = input(expense_msg)
        if validate_num_selection(user_expense):
            print('✅ Updating your expense log...')
            # update_expenses(user_gsheet, category, user_expense)
            break
        else:
            print('❌ Invalid Input. Please enter the amount using digits only.')
    return user_expense

def main():
    print_intro()
    ask_name()
    print(f'global : {user_gsheet}')
main()