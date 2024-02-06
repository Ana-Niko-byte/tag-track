import gspread
import os
from google.oauth2.service_account import Credentials
from art import *
from forex_python.converter import CurrencyRates
from decimal import Decimal
from colorama import Fore
from prettytable import PrettyTable
from termcolor import colored
from currencies import Currency

# Code and links taken from love-sandwiches project.
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]
# Months the user can select when logging an expense.
MONTHS = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}

# Currency the user can select for logging an expense.
CURRENCY = {1: "EUR", 2: "GBP", 3: "USD", 4: "AUD", 5: "UAH"}
SYMBOLS = {"€": "EUR", "£": "GBP", "$": "USD", "$": "AUD", "₴": "UAH"}

# Categories the user can select for logging an expense.
EXPENSES = {
    1: "Rent",
    2: "Groceries",
    3: "Vehicle",
    4: "Cafe/Restaurant",
    5: "Online Shopping",
    6: "Other",
}

CREDS = Credentials.from_service_account_file("creds.json")
CREDS_SCOPE = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(CREDS_SCOPE)
SHEET = GSPREAD_CLIENT.open("Tag-Track")

# List of read-only headers from google sheets.
# These are used in user-feedback throughout the application.
COLUMNS = []

user_month = None
user_gsheet = None
user_budget = None
user_budget_remainder = None
user_currency = None
user_expenses = []


def print_intro():
    """
    Uses colorama styling library to print large green heading.
    """
    clear_terminal()
    text = text2art("Tag - Tracker")
    print(Fore.LIGHTGREEN_EX + text + Fore.RESET)


def exit_tag():
    clear_terminal()
    print_intro()
    print(f"\n 👋  Thanks for using Tag-Track! See you soon :) \n")


def clear_terminal():
    """
    Clears the terminal screen for improved UX based on os.
    """
    # For windows os.
    if os.name == "nt":
        os.system("cls")
    # For Unix/Linux os.
    else:
        os.system("clear")


def validate_string(string):
    """
    Args:
        string (str): The string input to be validated.

    Returns:
        bool: Valid string.
    """
    if not string:
        print(" ❌  Please enter a value to begin.\n")
    elif not all(letter.isalpha() for letter in string.split()):
        print(" ❌  Why you using digits, bro?\n")
    else:
        return True


def validate_num_selection(num):
    """
    Args:
        num (num): The number input to be validated.

    Returns:
        (bool): Valid number.
    """
    if not num:
        print(" ❌  Please enter a value to begin.\n")
        return False
        # Allow decimal point values.
    try:
        if not all(float(digit) for digit in num.split()):
            print(" ❌  Why you not using digits only, bro?\n")
            return False
        else:
            return float(num)
    except ValueError:
        print(f" ❌  Invalid input. \n 👉  Please use digits only.")
        return False


def validate_selection(selection, num_range, min_num_range=0):
    """
    Validates using validate_num_selection() for number validation.
    Args:
        selection (num): The user selection to be validated.
        num_range (num): The maximum number that can be selected.
        min_num_range (num): The default starting range point.

    Returns:
        bool: Valid selection (from selected choice of options).
    """
    if validate_num_selection(selection):
        if float(selection) > min_num_range and float(selection) <= num_range:
            return True
        else:
            print(
                f""" ❌  Invalid input.
                Please choose one of the {num_range} options provided."""
            )
            return False
    else:
        return False


def confirm_input(user_input):
    """
    If correct, proceeds to next step. If not, loops back to function.
    Args:
        user_input (str): The letter to be validated.

    Returns:
        (str): Valid user_input letter.
    """
    while True:
        user_conf = input(
            f"""\n 👉  You've chosen {user_input}.
            Type 'p' to proceed, 'c' to change, or 'q' to quit: """
        )
        if not user_conf:
            print(" ❌  Please enter a value to continue.\n")
        elif user_conf == "p" or user_conf == "c":
            break
        elif user_conf == "q":
            exit_tag()
            break
        else:
            print(
                f""" ❌  Invalid input.
                \n 👉  Please choose either 'p', or 'c' to proceed."""
            )
    return user_conf


def create_table(value, heading, colour="light_green"):
    """
    Prints a table using predefined tuple values.
    Args:
        value (tuple): The string to be iterated for row values.
        heading (str): String to be displayed in second column.
        colour (str): Has a default value of "light_green".

    Returns:
        None.
    """
    # Assign PrettyTable object to month_table.
    table = PrettyTable()
    # Assign headings and iterate over each value in defined tuple.
    # Append to the table.
    table.field_names = [colored("No.", colour), colored(heading, colour)]
    for num, parameter in value.items():
        table.add_row([colored(num, "white"), colored(parameter, "white")])
        table.align = "l"
    print(f"\n{table}")


# _________ End of shared functionalities.


def ask_name():
    """
    A loop asking for user name.
    If valid, calls for month selection from a provided list.

    Returns:
        (str): User's name.
    """
    while True:
        name = input("   ➤ Please tell me your name: ").strip()
        if validate_string(name):
            capitalised = name.capitalize()
            clear_terminal()
            print(f"\n ✅  Hey, {capitalised}!")
            ask_month()
            break
    return name


def ask_month():
    """
    Displays selection of month options in a table.
    If valid, calls for currency selection.

    Returns:
        (str): Month as a string.
    """
    create_table(MONTHS, "Month")
    while True:
        global user_month
        print("\n (💡  Type the 'No.' )")
        month = input(" ➤  Please choose the month you want to log for: ")
        user_month = month
        if validate_selection(month, 12):
            month_name = MONTHS[int(month)]
            user_choice = confirm_input(month_name)
            if user_choice == "p":
                get_month_sheet(month_name)
                validate_currbudget()
            elif user_choice == "c":
                clear_terminal()
                ask_month()
            break
    return month_name


def retrieve_currbudget():
    """
    Retrieves current budget value.
    Asks user whether to use or change value.

    Returns:
        (str): User input.
    """
    current = user_gsheet.acell("B1").value
    if current:
        clear_terminal()
        print(
            f"""\n ⚠️  Your budget for the month of
            {MONTHS[int(user_month)]} is currently set to {current}.⚠️"""
        )        
        print(f'If you choose a new currency, all previously logged expenses for the month of {MONTHS[int(user_month)]} will be changed according to the current conversion rate.')
        user_budget_input = input(
            """\n ➤  Would you like to use this (type 'u'),
            or change it? (type 'c'): """
        )
        return user_budget_input


def validate_currbudget():
    """
    Calls functions based on user procedure choice.

    Returns:
        None.
    """
    while True:
        budg = user_gsheet.acell("B1").value
        if budg is None:
            ask_curr()
        else:
            currency = SYMBOLS[budg[0]]
            num_curr = [number for number, curr in CURRENCY.items() if curr == currency][0]
            # budget = budg[1:]
            # print(f'used budget is {budget}')
            user_choice = retrieve_currbudget()
            if user_choice == "u":
                global user_currency
                global user_budget
                user_currency = num_curr
                user_budget = budg
                print(
                    f""" ✅  Budget for the month of {
                        MONTHS[int(user_month)]}: {budg}"""
                )
                ask_category()
                break
            elif user_choice == "c":
                ask_curr()
                break
            else:
                print(
                    f""" ❌  Invalid input.
                        \n 👉  Please choose either 'u', or 'c' to proceed."""
                )
                continue


def get_month_sheet(month_needed):
    """
    Fetches the specified month worksheet.

    Args:
        month_needed (str): Name of the specified month.

    Returns:
        Gsheet for specified month.
    """
    print(f"Fetching the '{month_needed}' worksheet...\n")
    global user_gsheet
    try:
        user_gsheet = SHEET.worksheet(month_needed)
        print(
            f""" ✅  Worksheet retrieved successfully!
            \n ⌛  Hold on while we fetch the next table...\n"""
        )
        clear_terminal()
    # Code from snyk.io
    except gspread.exceptions.WorksheetNotFound:
        print(
            """ ❌  We weren'nt able to retrieve your worksheet.
            \n 👉  Please check your internet connection and try again"""
        )
        exit_tag()
    return user_gsheet


def ask_curr():
    """
    Displays selection of currency options in a table.
    If valid, checks in.

    Returns:
        (num): Number corresponding currency in table.
    """
    clear_terminal()
    print(f"\n ✅  You have chosen {MONTHS[int(user_month)]}.")
    create_table(CURRENCY, "Currency")
    while True:
        print("\n (💡 Type the 'No.' ")
        curr = input(" ➤  Please choose the currency you wish to log in: ")
        if validate_selection(curr, 5):
            global user_currency
            user_currency = curr
            str_curr = CURRENCY[int(curr)]
            user_choice = confirm_input(str_curr)
            if user_choice == "p":
                clear_terminal()
                print(f" ✅  You have chosen to log in '{str_curr}'")
                ask_budget()
                break
            elif user_choice == "c":
                ask_curr()
            break
    return curr


def fetch_gsheet_exp():
    """
    Returns:
        (list): all values of previously logged expenses. 
    """
    all_v = user_gsheet.get_all_values()[2:]
    return all_v


def convert_gsheet_exp(old_curr, chosen_curr, exp):
    # Code from forex-python documentation.
    c = CurrencyRates()
    new_amount = c.convert(CURRENCY[int(old_curr)], CURRENCY[int(chosen_curr)], exp)
    return new_amount


def append_gsheet_exp(v):
    """
    Args:
        old_curr (int): The number of the currency that was previously logged in. Retrieved from Google Sheets from each expense. 

    Returns:
        (list): converted values of previously logged expenses.  
    """
    all_rows = []
    for expense in v:
        updates = []
        for value in expense:
            if value:
                symbol = SYMBOLS[value[0]]
                num_curr = [number for number, curr in CURRENCY.items() if curr == symbol][0]
                # In the case of 'GBP' where the value is '3,000'.
                value = round(Decimal(value[1:].replace(",", "")), 2)
                new_amount = convert_gsheet_exp(num_curr, user_currency, value)
                # Get rid of 'Decimal' class through float conversion.
                dec_amount = float(round((new_amount), 2))
                form_amount = format_expenses(user_currency, dec_amount)
                updates.append(form_amount)
            else:
                updates.append(value)
                continue
        all_rows.append(updates)
    return all_rows


def retrieve_rows():
    values = fetch_gsheet_exp()
    return append_gsheet_exp(values)


def update_currency_exps(new_rows):
    """
    Updates the converted previously logged expenses. 

    Returns: 
        None. 
    """
    v = fetch_gsheet_exp()
    print(v)
    new_rows = append_gsheet_exp(v)
    row_amount = len(v)
    for i in range(3, row_amount + 3):
        clear_range = [f"A{i}:F{i}"]
        user_gsheet.batch_clear(clear_range)
    for row in new_rows:
        user_gsheet.append_row(row)


def format_expenses(curr, expense):
    """
    Formats the user's expenses with the chosen currency symbol.

    Args:
        curr (num): Number corresponding currency in table.
        expense (num): Value of expense.

    Returns:
        (str): Formatted Expense.
    """
    # Code taken from Currency example on pypi.org
    currency = Currency(CURRENCY[int(curr)])
    formatted_expense = currency.get_money_format(expense)
    return formatted_expense


def append_budget(budget):
    """
    Updates B1 cell with user's budget value.

    Args:
        budget (str): Value to be uploaded.

    Returns:
        None.
    """
    sheet = user_gsheet
    # This will change any previously logged budget in the 'B1' cell.
    sheet.update_acell("B1", budget)


def append_remainder(remainder):
    """
    Updates F1 cell with user's remaining budget value.

    Args:
        remainder (str): Value to be uploaded.

    Returns:
        None.
    """
    user_gsheet.update_acell("F1", remainder)

def ask_budget():
    """
    Asks for budget and updates global budget variable.
    If valid, calls for category selection.

    Returns:
        (str): Currency Symbol + Value of budget.
    """
    while True:
        global user_budget
        clear_terminal()
        budget = input(
            f"\n   ➤  Please enter your budget for {MONTHS[int(user_month)]}: "
        )
        if budget == "":
            print(" ❌  Please enter your budget to continue.")
            continue
        elif validate_num_selection(budget):
            global user_currency
            # Format the budget output to the user in their chosen currency.
            formatted_budget = format_expenses(user_currency, budget)
            user_choice = confirm_input(formatted_budget)
            if user_choice == "p":
                clear_terminal()
                print(
                    f""" ✅  Budget for the month of {
                        MONTHS[int(user_month)]}: {formatted_budget}"""
                )
                # Update the global variable with the format.
                user_budget = formatted_budget
                ask_category()
                return user_budget
            elif user_choice == "c":
                ask_budget()


def ask_category():
    """
    Displays categories in a table.
    If valid, calls for expense value.

    Returns:
        (num): Number corresponding to category.
    """
    create_table(EXPENSES, "Expense Category")
    while True:
        print("\n (💡  Type the 'No.' )")
        cat = input(" ➤  Please choose a category: ")
        if cat == "":
            print(" ❌  Please choose a category to log an expense.")
            continue
        elif validate_selection(cat, 6) is False:
            continue
        elif validate_selection(cat, 6):
            exp = EXPENSES[int(cat)]
            user_choice = confirm_input(exp)
            if user_choice == "p":
                ask_expense(exp)
            elif user_choice == "c":
                ask_category()
        return cat


def ask_expense(category):
    """
    Asks for expense in category.
    If valid, calls expense loop.

    Args:
        category (str): Category to log expense in.

    Returns:
        (num): Expense value in category.
    """
    while True:
        expense_msg = f"   ➤ Please enter the amount you spent on {category}: "
        user_expense = input(expense_msg)
        global user_expenses
        if user_expense == "":
            print(f" ❌  Please enter your expenses for {category}")
            continue
        elif validate_num_selection(user_expense):
            form_expense = format_expenses(user_currency, user_expense)
            user_choice = confirm_input(form_expense)
            if user_choice == "p":
                print(" ✅  Thanks!\n ⌛  Updating your expense log...")
                # Push the expense into the global user_expenses list.
                user_expenses.append([category, user_expense])
                if continue_expenses():
                    clear_terminal()
                    return ask_category()
                else:
                    clear_terminal()
                    create_expense(user_month, user_budget)
                    break
            elif user_choice == "c":
                ask_expense(category)
            elif user_choice == "q":
                exit_tag()
    return user_expense


def continue_expenses():
    """
    Expense logging loop with validation.

    Returns:
        (bool): Another expense or continue.
    """
    while True:
        user_answer = input(
            "\n➤  Please type 'a' to add another expense, or 'c' to continue."
        )
        if user_answer == "a":
            return True
        elif user_answer == "c":
            clear_terminal()
            print("\n ⌛  Printing your expense log...")
            return False
        else:
            print(f" ❌  Invalid input: {user_answer}. Please try again.")


def check_list():
    """
    Checks the user's logged expenses list for duplicate categories.
    If found, merges categories and adds values.

    Returns:
        (dict): Non-duplicated expenses.
    """
    # Gets the logged expenses - may contain duplicates.
    global user_expenses
    non_duplicates = {}
    for item in user_expenses:
        cat, value = item
        value = round(float(value), 2)
        # Checks if the category (key) is already in the duplicates dictionary.
        if cat in non_duplicates:
            # If it is, it adds the values together.
            non_duplicates[cat] += value
        else:
            # Adds the key and value to the dictionary.
            non_duplicates[cat] = value
    # Re-assign the global variable the value of duplicates.
    user_expenses = non_duplicates
    return non_duplicates


def create_expense(month, budget, colour="light_green"):
    """
    Prints conclusive user table with budget + expenses.

    Args:
        month (num): Num corresponding to Month selection.
        budget (str): Formatted budget.
        colour (str): Has default value of "light_green".

    Returns:
        None.
    """
    # Assign PrettyTable object to month_table.
    table = PrettyTable()
    # Assign headings and colours to the table.
    table.field_names = [
        colored(f"Expenses for {MONTHS[int(month)]}", colour),
        colored(f"{MONTHS[int(month)]}'s budget: {budget}", colour),
    ]
    # So the table doesn't display duplicate categories.
    validated_cat_expenses = check_list()
    for list_category, list_expense in validated_cat_expenses.items():
        formatted_exp = format_expenses(user_currency, round(list_expense, 2))
        table.add_row(
            [colored(list_category, "white"), colored(formatted_exp, "white")]
        )
        table.align = "l"

    remainder = calculate_budget_remainder()
    print(remainder)
    # Add separating rows to the table to differentiate final data.
    table.add_row(["-----------------------", "-----------------------"])
    # Check if budget is '-' or '+' to determine colour of final table row.
    if float(remainder[1:]) < 0:
        print(remainder)
        table.add_row(
            [
                colored("Your remaining budget:", "red"),
                colored(user_budget_remainder, "red"),
            ]
        )
    else:
        table.add_row(
            [
                colored("Your remaining budget:", "green"),
                colored(user_budget_remainder, "green"),
            ]
        )
    clear_terminal()
    print(f"\n{table}")
    ask_update()


def retrieve_remainder_value():
    return user_gsheet.acell("F1").value


def calculate_budget_remainder():
    """
    Returns:
        (str): Remainder of budget after expense(s) deduction.
    """
    # Get the unformatted version of remainder budget.
    pre_rem = retrieve_remainder_value()
    if pre_rem is None:
        num_remainder = float(user_budget[1:].replace(",", ""))
    elif pre_rem:
        num_remainder = float(pre_rem[1:].replace(",", ""))
    # Get the total of the user's expenses.
    prev_exps = retrieve_rows()
    print(prev_exps)
    total = sum(user_expenses.values()) 
    print(total)
    total = str(total)
    remainder = round(num_remainder - float(total), 2)
    # Update the global variable for the remainder.
    global user_budget_remainder
    user_budget_remainder = format_expenses(user_currency, remainder)
    return user_budget_remainder


def ask_update():
    """
    Asks to update google sheets or quit application.

    Returns:
        None.
    """
    while True:
        print("\nWould you like to upload your expenses to Google Sheets?\n")
        print(
            """ ⚠️  Note: You will need to manually remove your expenses
            from your Month sheet and deduct from your
            Overview sheet if you reconsider. ⚠️"""
        )
        user_update = input(
            """\n   ➤ Please type 'u' to upload your
            expenses to Google sheets, or 'q' to exit tag-track: """
        )
        if user_update == "u":
            update_worksheet()
            break
        elif user_update == "q":
            exit_tag()
            break
        else:
            print(
                f""" ❌  Invalid input. You entered '{user_update}'.
            Please try again."""
            )
            continue


def format_data():
    """
    Returns:
        (array): sorted user expenses.
    """
    format = {
        "Rent": "",
        "Groceries": "",
        "Vehicle": "",
        "Cafe/Restaurant": "",
        "Online Shopping": "",
        "Other": "",
    }
    expenses = user_expenses
    for key, value in expenses.items():
        if key in format:
            format[key] = format_expenses(user_currency, value)
    return format


def expensive_battleships():
    """
    Adds two parameters to create a cell format, e.g. 'C3'.

    Returns:
        (array): cells to be updated.
    """
    sheet = SHEET.worksheet("Overview")
    global user_month
    # List user_expenses changed to dict in check_list().
    global user_expenses

    # Num input for month.
    # + 1 is added to get the next cell after headers.
    battleship_two = int(user_month) + 1
    used_keys = list(user_expenses.keys())
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
    Converts ASCII code to character using built-in chr function.

    Args:
        num (num): Value to be converted to string.

    Returns:
        (str): Letter.
    """
    if 1 <= num <= 7:
        # chr(65) = A
        return chr(num + 64)


def update_cell_values():
    """
    Updates "Overview" sheet with values.

    Returns:
        None.
    """
    cells_to_update = expensive_battleships()
    user_logs = list(user_expenses.values())
    OVERVIEW = SHEET.worksheet("Overview")
    for i, cell in enumerate(cells_to_update):
        if i < len(user_logs):
            initial_log = user_logs[i]
            cell_value = OVERVIEW.acell(cell).value
            if cell_value is None:
                cell_value = 0
                addition = initial_log
            else:
                addition = float(cell_value) + float(initial_log)
            OVERVIEW.update_acell(cell, addition)
    append_remainder(user_budget_remainder)
    print(
        f"""\n ✅  We've successfully updated your
    Month sheet and annual Overview sheet!"""
    )
    print(
        """Tip: Make sure to check this sheet regularly
    to stay on top of your spending habits :)\n"""
    )


def update_worksheet():
    """
    Updates relevant Google Sheet with user's expenses.

    Returns:
        None.
    """
    print("   ⌛  Updating your worksheet...")
    values = fetch_gsheet_exp()
    append_gsheet_exp(values)
    expenses = format_data()
    values_to_append = list(expenses.values())
    append_budget(user_budget)
    user_gsheet.append_row(values_to_append)
    update_cell_values()


def main():
    """
    Starts application.

    Returns:
        None.
    """
    print_intro()
    ask_name()


main()
