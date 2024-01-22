import gspread
import os
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
user_month = None
user_gsheet = None
user_budget = None
user_budget_remainder = None
user_currency = None
user_expenses = []

def print_intro():
    """
    Prints large heading. 
    """
    text = text2art('Tag - Tracker')
    print(Fore.LIGHTGREEN_EX + text + Fore.RESET)

# _________ Beginning of shared functionalities, called throughout the application.
    
def quick_escape():
    """
    Allow users to exit the log or continue in the application
    """
    print('\n⚠️  Checking in!⚠️\n If you\'ve made any errors - now is the time to exit and restart. Don\'t worry - nothing has been logged yet :) ')
    while True:
        user_escape = input('➤  Please press "Enter" to continue or type "q" to quit...')
        if user_escape == 'q':
            print_intro()
            exit_tag()
            break
        elif user_escape == '':
            break
        else:
            print(f'❌  Invalid input. You entered {user_escape}. Please try again.')
    return user_escape

def exit_tag():
    print(f'\n👋  Thanks for using Tag-Track! Exiting...')

def clear_terminal():
    """
    Clears the terminal screen.
    """
    os.system('cls')

def validate_string(string):
    """
    Validates any string input for alphabet-only characters. 
    Returns true if no digits or symbols are present. 
    """
    if not string:
        print('❌  Please enter a value to begin.\n')
    elif not all(letter.isalpha() for letter in string.split()):
        print('❌  Why you using digits, bro?\n')
    else:
        return True

def validate_num_selection(num):
    """
    Validates any number input. 
    Returns true if no digits or symbols are present. 
    """
    if not num:
        print('❌  Please enter a value to begin.\n')
        return False
        # Allow decimal point values.
    try:
        if not all(float(digit) for digit in num.split()):
            print('❌  Why you not using digits only, bro?\n')
            return False
        else:
            return float(num)
    except ValueError:
        print(f'❌  Invalid input. \n👉  Please use digits only.')
        return False

def validate_selection(selection, num_range, min_num_range = 0):
    """
    Validates the selected input in conjunction with the validate_num_selection() function using a set number range.
    """
    if validate_num_selection(selection):
        if float(selection) > min_num_range and float(selection) <= num_range:
            return True
        else:
            print(f'❌  Invalid input. Please choose one of the {num_range} options provided.')
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
            clear_terminal()
            print(f'\n✅  Hey, {capitalised}!')
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
        global user_month
        print('\n(💡  Type the \'No.\' that corresponds to the Month you want :) )')
        month = input('➤  Please choose the month you want to log for: ')
        user_month = month
        if validate_selection(month, 12):
            clear_terminal()
            month_name = MONTHS[int(month)]
            print(f'\n✅  You have chosen {month_name}.')
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
    print(f'✅  Got it!\n⌛  Hold on while we fetch the next table...\n')
    return user_gsheet

def ask_curr():
    """
    Asks user to select one of the options in the currency table for logging expenses. 
    If valid input, asks user if they wish to continue. 
    """
    create_table(CURRENCY, 'Currency')
    while True:
        print('\n(💡 Type the \'No.\' that corresponds to the Currency you want ;))')
        curr = input('➤  Please choose the currency you wish to log in: ')
        if validate_selection(curr, 5):
            global user_currency
            user_currency = curr
            clear_terminal()
            print(f'✅  You have chosen to log in {CURRENCY[int(curr)]}')
            escape = quick_escape()
            if escape == '':
                ask_budget()
            break
    return curr

def format_expenses(curr, expense):
    """
    Formats the user's expenses with the chosen currency symbol. 
    """
    # Code taken from Currency example on (https://pypi.org/project/currencies/).
    currency = Currency(CURRENCY[int(curr)])
    formatted_expense = currency.get_money_format(expense)
    return formatted_expense

def ask_budget():
    """
    Asks user for budget and updates global budget variable.
    If valid input, asks user if they wish to continue. 
    """
    global user_budget
    current_value = user_gsheet.acell('B1').value
    use_existing_budget = retrieve_budget(current_value, user_budget)
    if use_existing_budget == 'u':
        print(f'Your budget remains at {current_value} for the month of {MONTHS[int(user_month)]}.')
        user_budget = current_value
        ask_category()
    elif use_existing_budget == 'c':
        while True:
            budget = input(f'\n➤  Please enter your budget for {MONTHS[int(user_month)]}: ')
            if budget == '':
                print('❌  Please enter your budget to continue.')
                continue
            elif validate_num_selection(budget):
                global user_currency
                # Format the budget output to the user in their chosen currency.
                formatted_budget = format_expenses(user_currency, budget)
                clear_terminal()
                print(f'✅  Budget for the month of {MONTHS[int(user_month)]}: {formatted_budget}')
                # Update the global variable with the format.
                user_budget = formatted_budget
                ask_category()
                return user_budget
        
def retrieve_budget(current, budget):
    """
    Retrieves current budget value and asks user if they wish to use it or change its value. 
    """
    if current:
        print(f'\n⚠️  Your budget for the month of {MONTHS[int(user_month)]} is currently set to {current}.⚠️')
        user_budget_input = input('\n➤  Would you like to use this or amend it?\n(Please type \'u\' to use existing, or \'c\' to change)')
        return user_budget_input
    else:
        append_budget(budget)
        
def append_budget(budget):
    """
    Updates B1 of the respective google sheets with the value of the user's budget.
    """
    sheet = user_gsheet
    # This will change any previously logged budget in the 'B1' cell. 
    sheet.update_acell('B1', budget)

def ask_category():
    """
    Asks user to select one of the options in the category table for logging expenses. 
    If valid input, asks user if they wish to continue. 
    """
    create_table(EXPENSES, 'Expense Category')
    while True:
        print('\n(💡  Type the \'No.\' that corresponds to the Category you want :) )')
        cat = input('➤  Please choose a category: ')
        if cat == '':
            print('❌  Please choose a category to log an expense.')
            continue
        elif validate_selection(cat, 6):
            if int(cat) == 1 or int(cat) == 2:
                print(f'✅  Ouch...spending on {EXPENSES[int(cat)]}...')
            elif int(cat) > 2 and int(cat) != 6:
                print(f'✅  Ooo...spending on {EXPENSES[int(cat)]}? Nice!')
            ask_expense(EXPENSES[int(cat)])
        return cat
    
def ask_expense(category):
    """
    Asks user for expense in the chosen category. 
    If valid input, asks user if they wish to continue. 
    """
    while True:
        expense_msg = f'\n➤ Please enter the amount you spent on {category}: '
        user_expense = input(expense_msg)
        global user_expenses
        global user_month
        global user_budget
        if user_expense == '':
            print(f'❌  Please enter your expenses for {category}')
            continue
        elif validate_num_selection(user_expense):
            print('✅  Thanks!\n⌛  Updating your expense log...')
            # Push the expense into the global user_expenses list.
            user_expenses.append([category, user_expense])
            if continue_expenses():
                clear_terminal()
                return ask_category()
            else:
                clear_terminal()
                create_expense(user_month, user_budget)
                break
    return user_expense

def continue_expenses():
    """
    Loop to ask the user if they want to log another expense, with validation. 
    """
    while True:
        user_answer = input('\n➤  Please press "a" to add another expense, or "c" to continue.')
        if user_answer == 'a':
            return True
        elif user_answer == 'c':
            print('\n⌛  Printing your expense log...')
            return False
        else:
            print(f'❌  Invalid input: {user_answer}. Please try again.')

def check_list():
    """
    Checks the user's logged expenses list for duplicate categories. 
    If found, merges and adds their expense values together.
    """
    # Gets the logged expenses - these may contain duplicates if user logs one category more than once.
    global user_expenses
    duplicates = {}
    for item in user_expenses:
        cat, value = item
        # Checks if the category (key) is already in the duplicates dictionary.
        if cat in duplicates:
            # If it is, it adds the values together.
            duplicates[cat] += round(float(value), 2)
        else:
            # Adds the key and value to the dictionary.
            duplicates[cat] = round(float(value), 2)
    # Re-assign the global variable the value of duplicates (used to update the Google Sheet logs).
    user_expenses = duplicates
    return duplicates

def create_expense(month, budget, colour = 'light_green'):
    """
    Creates final table to display all user input.
    """
    # Assign PrettyTable object to month_table.
    table = PrettyTable()
    # Assign headings and colours to the table.
    table.field_names = [
        colored(f'Expenses for {MONTHS[int(month)]}', colour),
        colored(f'{MONTHS[int(month)]}\'s budget: {budget}', colour)
        ]
    # Gets the returned dictionary value so the table doesn't display duplicate categories.
    validated_cat_expenses = check_list()
    for list_category, list_expense in validated_cat_expenses.items():
        formatted_expense = format_expenses(user_currency, list_expense)
        table.add_row([colored(list_category, 'white'), colored(formatted_expense, 'white')])
        table.align = 'l'
    
    remainder = calculate_budget_remainder()
    remainder_value = float(remainder[1:])
    # Add separating rows to the table to differentiate final data.
    table.add_row(['-----------------------', '-----------------------'])
    # Check if budget is negative or positive to determine colour of final table row.
    if remainder_value < 0:
        table.add_row([colored('Your remaining budget:', 'red'), colored(user_budget_remainder, 'red')])
    else:
        table.add_row([colored('Your remaining budget:', 'green'), colored(user_budget_remainder, 'green')])
    print(f'\n{table}')
    ask_update()

def calculate_budget_remainder():
    # Get the unformatted version of budget.
    global user_budget
    unformatted_budget = user_budget[1:]
    # Get the total of the user's expenses.
    total = sum(user_expenses.values())
    total = str(total)
    remainder = round(float(unformatted_budget) - float(total), 2)
    # Update the global variable for the remainder.
    global user_budget_remainder
    user_budget_remainder = format_expenses(user_currency, remainder)
    return user_budget_remainder

def ask_update():
    """
    Asks user whether to update google sheets with their values or provide some advice for future spending.
    """
    while True:
        print('\nWould you like to upload your expenses to Google Sheets?')
        print('⚠️  Note: You will need to manually remove your expenses from your Month sheet if you reconsider.⚠️')
        user_update = input('\n➤ Type \'u\' to update Google sheets with your expenses, or \'q\' to exit tag-track...')
        if user_update == 'u':
            update_worksheet()
            break
        elif user_update == 'q':
            print_intro()
            exit_tag()
            break
        else:
            print(f'❌  Invalid input. You entered {user_update}. Please try again.')
            continue

def format_data():
    """
    Formats data for the google sheet. 
    """
    format = {'Rent': '','Groceries': '', 'Vehicle': '','Cafe/Restaurant': '','Online Shopping': '', 'Other': ''}
    expenses = user_expenses
    for key, value in expenses.items():
        if key in format:
            format[key] = format_expenses(user_currency, value)
    return format

def expensive_battleships():
    """
    Adds two parameters to create a cell format as in Excel/ Google Sheets, e.g. 'C3'.
    """
    sheet = SHEET.worksheet('Overview')
    global user_month
    # The list user_expenses was changed to a dictionary in check_list().
    global user_expenses

    # The user inputs a number when selecting a month. This row holds all the values that need to be updated after the initial log. 
    # + 1 is added to get the next cell (accounting for headers being in the first row).
    battleship_two = int(user_month) + 1
    used_keys = list(user_expenses.keys())
    # Stores the column indexes of the logged expenses.
    column_indexes = []

    for key in used_keys:
        cell = sheet.find(key)
        # Index of column in spreadsheet.
        cell_column = cell.col
        lettered_column = num_lett(cell_column)
        column_indexes.append(lettered_column)

    cells = []
    for letter in column_indexes:
        battleship_one = letter
        cell = battleship_one + str(battleship_two)
        cells.append(cell)
    return cells

def num_lett(num):
    """
    Converts ASCII code to character using Python's built-in chr function.
    """
    if 1 <= num <= 7:
        # chr(65) = A
        return chr(num + 64)

def update_cell_values():
    cells_to_update = expensive_battleships()
    user_logs = list(user_expenses.values())
    OVERVIEW = SHEET.worksheet('Overview')
    for i, cell in enumerate(cells_to_update):
        if i < len(user_logs):
            initial_log = user_logs[i]
            cell_value = OVERVIEW.acell(cell).value
            if cell_value == None:
                cell_value = 0
                addition = initial_log
            else:
                addition = float(cell_value) + float(initial_log)
            OVERVIEW.update_acell(cell, addition)
    print(f'\n✅  We\'ve successfully updated your annual Overview sheet!')
    print('Tip: Make sure to check this sheet regularly to stay on top of your spending habits :)')

def update_worksheet():
    """
    Updates relevant Google Sheets with user's expenses. 
    """
    print('⌛  Updating your worksheet...')
    expenses = format_data()
    values_to_append = list(expenses.values())
    append_budget(user_budget)
    user_gsheet.append_row(values_to_append)
    update_cell_values()

def main():
    print_intro()
    ask_name()
main()