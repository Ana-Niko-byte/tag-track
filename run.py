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

# Categories the user can select for logging an expense. 
EXPENSES = {
    1 : 'Rent',
    2 : 'Groceries',
    3 : 'Vehicle',
    4 : 'Cafe/Restaurant',
    5 : 'Online Shopping',
    6 : 'Other'
}

# List of headers in google sheets.
COLUMNS = []

CREDS = Credentials.from_service_account_file('creds.json')
CREDS_SCOPE = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(CREDS_SCOPE)
SHEET = GSPREAD_CLIENT.open('Tag-Track')

def print_intro():
    """
    Prints large heading. 
    """
    text = text2art('Tag - Tracker')
    print(Fore.CYAN + 'Welcome to')
    print(Fore.CYAN + text + Fore.RESET)

def quick_escape():
    """
    Allow users to exit the log or continue in the application
    """
    print('\nCheckpoint!')
    while True:
        escape_msg = '\n➤ Please press "Enter" to continue or type "q" to quit...'
        user_escape = input(escape_msg)
        if user_escape == 'q':
            print('exit')
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
    return string.isalpha()

def validate_num_selection(num):
    """
    Validates any number input. 
    Returns true if no digits or symbols are present. 
    """
    return num.isdigit()

def validate_selection(selection, num_range, min_num_range = 0):
    """
    Validates the selected input in conjunction with the validate_num_selection() function using a set number range.
    """
    if validate_num_selection(selection):
        if int(selection) > min_num_range and int(selection) <= num_range:
            return True
        else:
            print('❌ Invalid input. Please choose one of the options provided.')
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

def ask_name():
    """
    A user loop asking for name until valid input is provided. 
    Once valid, the user is asked to selected a month from the provided list. 
    """
    while True:
        name = input('➤ Please tell me your name: ')
        if validate_string(name):
            print('✅')
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
            print('✅')
            get_month_sheet(MONTHS[int(month)])
            get_worksheet_column(MONTHS[int(month)])
            ask_curr()
            break
    return month

def get_month_sheet(month_needed):
    """
    Fetches the worksheet based on the month the user chose. 
    """
    print(f'Fetching the {month_needed} worksheet...\n')
    month_worksheet = SHEET.worksheet(month_needed)
    print(f'Got it! Hold on while we fetch the next table...\n')
    return month_worksheet

def ask_curr():
    """
    Asks user to select one of the options in the currency table for logging expenses. 
    If valid input, asks user if they wish to continue. 
    """
    create_table(CURRENCY, 'Currency')
    while True:
        curr = input('\n➤ Please choose the currency you wish to log in: ')
        if validate_selection(curr, 5):
            print('✅')
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
        cat = input('\n➤ Please choose a category: ')
        if validate_selection(cat, 6):
            print('✅')
            get_category_cell(cat)
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
            print('✅')
            print('valid number input')
            break
        else:
            print('❌ Invalid Input. Please enter the amount using digits only.')
    return user_expense

def get_worksheet_column(working_sheet):
    """
    Retrieves all columns from the spreadsheets based on the month the user chose.
    """
    sheet = SHEET.worksheet(working_sheet)
    # Avoid 'DATE' in spreadsheet + take into account indent of one cell in both axes. 
    for col in range(3,9):
        column = sheet.col_values(col)
        COLUMNS.append(column[1:])
    return column

def get_category_cell(cat):
    """
    Retrieves the cell from the worksheet columns based on the category the user chose.
    """
    # As COLUMNS is a list, we need to subtract one to get the index of the correct cell.
    cell = COLUMNS[int(cat) - 1]
    return cell

def main():
    print_intro()
    ask_name()
main()