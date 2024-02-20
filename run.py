import gspread
import os
from google.oauth2.service_account import Credentials
from art import *
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


def create_user_month():
    """Getter & Setter functions for int month value.
    Returns:
        retrieve & update month functions."""
    user_month = None

    def retrieve_month():
        return user_month

    """Updates user_month with int argument."""

    def update_month(set_month: int):
        nonlocal user_month
        user_month = set_month

    return retrieve_month, update_month


def create_user_budget():
    """Getter & Setter functions for float budget value.
    Returns:
        retrieve & update budget functions."""
    user_budget = None

    def retrieve_budget():
        return user_budget

    """Updates user_budget with float argument."""

    def update_budget(set_budget: float):
        nonlocal user_budget
        user_budget = set_budget

    def retrieve_formatted_budg():
        nonlocal user_budget
        return format_expenses(user_budget)

    return retrieve_budget, update_budget, retrieve_formatted_budg


def create_user_budget_rem():
    """Getter & Setter functions for float remainder value.
    Returns:
        retrieve and update budget remainder functions."""
    user_budget_remainder = None

    def retrieve_rem():
        return user_budget_remainder

    """Updates user_budget_remainder with float argument."""

    def update_rem(set_remainder: float):
        nonlocal user_budget_remainder
        user_budget_remainder = set_remainder

    def retrieve_formatted_rem():
        nonlocal user_budget_remainder
        return format_expenses(user_budget_remainder)

    return retrieve_rem, update_rem, retrieve_formatted_rem


def create_user_gsheet():
    """Getter & Setter functions for user google sheet.
    Returns:
        retrieve & update user google sheet functions."""
    user_gsheet = None

    def retrieve_gsheet():
        return user_gsheet

    """Updates user_gsheet with str argument."""

    def update_gsheet(gsheet_name: str):
        nonlocal user_gsheet
        user_gsheet = gsheet_name

    return retrieve_gsheet, update_gsheet


def create_user_expenses():
    """Getter & Setter functions for list create_user_expenses value.
    Returns:
        retrieve, update (append), and replace expenses functions."""
    user_expenses = []

    def retrieve_expenses():
        return user_expenses

    """Updates the list with an argument"""

    def update_expenses(value: list):
        nonlocal user_expenses
        user_expenses.append(value)

    """Replaces list user_expenses"""

    def replace_expenses(value: any):
        nonlocal user_expenses
        user_expenses = value

    return retrieve_expenses, update_expenses, replace_expenses


def print_intro():
    """Prints intro heading with colorama styling library.
    Returns:
        None."""
    clear_terminal()
    text = text2art("$ Tag - Track")
    print(Fore.LIGHTGREEN_EX + text + Fore.RESET)


def exit_tag():
    clear_terminal()
    print_intro()
    print(f"\n 👋  Thanks for using Tag-Track! See you soon :) \n")


def clear_terminal():
    """Clears the terminal screen for improved UX based on os.
    Returns:
        None."""
    # For windows os.
    if os.name == "nt":
        os.system("cls")
    # For Unix/Linux os.
    else:
        os.system("clear")


def validate_string(string: any):
    """Args:
        string (any): The string input to be validated.
    Returns:
        bool: Valid string."""
    if not string:
        print("\n ❌  Please enter a value to begin.\n")
        return False
    elif not all(letter.isalpha() for letter in string.split()):
        print("\n ❌  Why you using digits, bro?\n")
        return False
    else:
        return True


def validate_num_selection(num: any):
    """Args:
        num (any): The number input to be validated.
    Returns:
        bool: Valid number."""
    if not num:
        clear_terminal()
        print("\n ❌  Please enter a value to begin.\n")
        return False
    try:
        if not all(float(digit) for digit in num.split()):
            clear_terminal()
            print("\n ❌  Why you not using digits only, bro?\n")
            return False
        else:
            return True
    except ValueError:
        clear_terminal()
        print(f"\n ❌  Invalid input.")
        print("👉  Why you not using digits only, bro?")
        return False


def validate_selection(selection: float, num_range: int, min_num_range=0):
    """Validates using validate_num_selection() for number validation.
    Args:
        selection (float): The user selection to be validated.
        num_range (num): The maximum number that can be selected.
        min_num_range (num): The default starting range point.
    Returns:
        bool: Valid selection (from selected choice of options)."""
    if validate_num_selection(selection):
        if float(selection) > min_num_range and float(selection) <= num_range:
            return True
        else:
            clear_terminal()
            print("\n ❌  Invalid input.")
            print(f"Please choose one of the {num_range} options provided.")
            return False
    else:
        return False


def confirm_input(user_input: any, additional="."):
    """If correct, proceeds to next step. If not, loops back to function.
    Args:
        user_input (str): The letter to be validated.
    Returns:
        user_conf (str): Valid user_input letter."""
    while True:
        print(f"\n 👉  You've chosen {user_input}{additional}")
        user_conf = (
            input("Type 'p' to proceed, 'c' to change, or 'q' to quit: ")
            .strip()
            .lower()
        )
        if not user_conf:
            print("\n ❌  Please enter a value to continue.\n")
        elif user_conf == "p" or user_conf == "c":
            break
        elif user_conf == "q":
            exit_tag()
            break
        else:
            print("\n ❌  Invalid input.")
            print(" 👉  Please choose either 'p', or 'c' to proceed.")
    return user_conf


def create_table(value, heading: str, colour="light_green"):
    """Prints a table using predefined tuple values.
    Args:
        value (tuple): The string to be iterated for row values.
        heading (str): String to be displayed in second column.
        colour (str): Has a default value of "light_green".
    Returns:
        None."""
    table = PrettyTable()
    table.field_names = [colored("No.", colour), colored(heading, colour)]
    for num, parameter in value.items():
        table.add_row([colored(num, "white"), colored(parameter, "white")])
        table.align = "l"
    print(f"\n{table}")


def fetch_gsheet_exp():
    """Returns:
    (list): all values of previously logged expenses."""
    gsheet = retrieve_gsheet()
    return gsheet.get_all_values()[2:]


def append_budget():
    """Updates B1 cell with user's budget value.
    Args:
        budget (str): Value to be uploaded.
    Returns:
        None."""
    retrieved_budg = retrieve_budget()
    gsheet = retrieve_gsheet()
    user_budget_format = format_expenses(retrieved_budg)
    gsheet.update_acell("B1", user_budget_format)


def append_remainder():
    """Updates F1 cell with user's remaining budget value.
    Args:
        remainder (str): Value to be uploaded.
    Returns:
        None."""
    retrieved_rem = retrieve_rem()
    gsheet = retrieve_gsheet()
    user_rem_format = format_expenses(retrieved_rem)
    gsheet.update_acell("F1", user_rem_format)


def retrieve_overview():
    """Returns:
    None, or Overview sheet from Google Sheets."""
    return SHEET.worksheet("Overview")


def retrieve_remainder_value():
    """Returns:
    (str): None, or Current budget remainder from GS."""
    gsheet = retrieve_gsheet()
    return gsheet.acell("F1").value


def retrieve_gsheet_budget():
    """Retrieves current budget value. Performs some basic validation.
    Returns:
        None, or budget (str)."""
    gsheet = retrieve_gsheet()
    return gsheet.acell("B1").value


def remove_formatting(exp_value: str):
    """
    Removes currency symbol and converts to float.
    Returns:
        (float).
    """
    if exp_value is None:
        retrieved_budg = retrieve_budget()
        return float(str(retrieved_budg)[1:].replace(",", ""))
    elif exp_value:
        neg_pos = exp_value[0]
        if neg_pos == "-":
            symbol = exp_value[1]
            return float(exp_value.replace(",", "").replace(symbol, ""))
        else:
            return float(exp_value[1:].replace(",", ""))


def format_expenses(expense: float):
    """Formats the user's expenses with the chosen currency symbol.
    Args:
        expense (num): Value of expense.
    Returns:
        formatted_expense (str): Formatted Expense."""
    # Code taken from Currency example on pypi.org
    currency = Currency('EUR')
    formatted_expense = currency.get_money_format(expense)
    return formatted_expense


def num_lett(num: int):
    """Converts ASCII code to character using built-in chr function.
    Args:
        num (int): Value to be converted to string.
    Returns:
        (str): Letter."""
    if 1 <= num <= 7:
        return chr(num + 64)


# _________ End of shared functionalities.
retrieve_month, update_month = create_user_month()
retrieve_budget, update_budget, retrieve_formatted_budg = create_user_budget()
retrieve_rem, update_rem, retrieve_formatted_rem = create_user_budget_rem()
retrieve_gsheet, update_gsheet = create_user_gsheet()
retrieve_expenses, update_expenses, replace_expenses = create_user_expenses()


def ask_name():
    """A loop asking for user name.
    If valid, calls for month selection from a provided list.
    Returns:
        name (str): User's name."""
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
    """Displays selection of month options in a table.
    If valid, calls for currency selection.
    Returns:
        month_name (str): Month as a string."""
    while True:
        create_table(MONTHS, "Month")
        print("\n (💡  Type the 'No.' )")
        month = input(" ➤  Please choose a month to log for: ")
        if validate_selection(month, 12):
            update_month(month)
            month_name = MONTHS[int(month)]
            user_choice = confirm_input(month_name)
            if user_choice == "p":
                get_month_sheet(month_name)
                nextsteps_retr_budget()
                return month_name
            elif user_choice == "c":
                clear_terminal()


def get_month_sheet(month_needed: str):
    """Fetches the specified month worksheet.
    Args:
        month_needed (str): Name of the specified month.
    Returns:
        Gsheet for specified month."""
    print(f"Fetching the '{month_needed}' worksheet...\n")
    try:
        gsheet = update_gsheet(SHEET.worksheet(month_needed))
        print("\n ✅  Worksheet retrieved successfully!")
        print(" ⌛  Hold on while we fetch the next table...")
        clear_terminal()
        return gsheet
    # Code from snyk.io
    except gspread.exceptions.WorksheetNotFound:
        print("\n ❌  We weren'nt able to retrieve your worksheet.")
        print(" 👉  Please check your internet connection and try again")
        exit_tag()
        return False


# __________ budget handling logic ____________


def validate_retr_budget(budg):
    """Validates returned budget value.
    Returns:
        user_budget_input (str): User input."""
    if budg:
        clear_terminal()
        month = retrieve_month()
        budg_month = MONTHS[int(month)]
        print(f"\n ⚠️  Budget for {budg_month} is set to {budg}.⚠️")
        while True:
            user_budget_input = (
                input("\n ➤  Type 'u' to use existing or 'c' to change: ")
                .strip()
                .lower())
            if user_budget_input == "u":
                clear_terminal()
                print(f"✅  Budget for {budg_month}: {budg}")
                break
            elif user_budget_input == "c":
                clear_terminal()
                ask_budget()
                break
            else:
                print(" ❌  Invalid input.")
                print(" 👉  Please choose either 'u', or 'c' to proceed.")
        return user_budget_input
    else:
        ask_budget()


def nextsteps_retr_budget():
    """Calls functions based on user procedure choice.
    Returns:
        None."""
    budg = retrieve_gsheet_budget()
    validation = validate_retr_budget(budg)
    if validation == "u":
        budg = remove_formatting(budg)
        update_budget(budg)
        ask_category()


def ask_budget():
    """Asks for budget and updates global budget variable.
    If valid, calls for category selection.
    Returns:
        None."""
    clear_terminal()
    while True:
        month = retrieve_month()
        budg_month = MONTHS[int(month)]
        budget = input(f"\n   ➤  Please enter a budget for {budg_month}: ")
        if validate_num_selection(budget):
            update_budget(budget)
            nextsteps_budget(budg_month)
            break


def nextsteps_budget(month: str):
    """Executes nextsteps following buget validation.
    Args:
        budget_entry (float): value of budget.
        month (str): budget month.
    Returns:
        None."""
    formatted_budget = retrieve_formatted_budg()
    user_choice = confirm_input(formatted_budget)
    if user_choice == "p":
        clear_terminal()
        print(f"\n ✅  Budget for {month}: {formatted_budget}")
        ask_category()
    if user_choice == 'c':
        clear_terminal()
        ask_budget()


# __________ end of budget handling logic ____________


def ask_category():
    """Displays categories in a table. If valid, calls for expense value.
    Returns:
        cat (num): Number corresponding to category."""
    while True:
        create_table(EXPENSES, "Expense Category")
        print("\n (💡  Type the 'No.' )")
        cat = input(" ➤  Please choose a category: ")
        if validate_selection(cat, 6):
            ask_expense(EXPENSES[int(cat)])
            return cat


def ask_expense(category: str):
    """Asks for expense in category.If valid, calls expense loop.
    Args:
        category (str): Expense category.
    Returns:
        None."""
    while True:
        expense_msg = f" ➤ Enter the amount you spent on {category}: "
        user_exp = input(expense_msg)
        if validate_num_selection(user_exp):
            form_expense = format_expenses(user_exp)
            user_choice = confirm_input(form_expense, f' for "{category}".')
            if user_choice == "p":
                clear_terminal()
                print("\n ✅  Saved!\n ⌛  Updating your expense log...")
                update_expenses([category, user_exp])
                continue_expenses()
                break
            elif user_choice == "c":
                clear_terminal()
                ask_category()
                break


def continue_expenses():
    """Expense logging loop with validation.
    Returns:
        (bool): Another expense or continue."""
    while True:
        user_answer = (
            input("\n➤  Type 'a' to add an expense, or 'c' to continue.")
            .strip()
            .lower())
        if user_answer == "a":
            clear_terminal()
            ask_category()
            break
        elif user_answer == "c":
            clear_terminal()
            print("\n ⌛  Calculating your expenses...")
            month = retrieve_month()
            retrieved_budg = retrieve_budget()
            create_expense(month, retrieved_budg)
            break
        else:
            print(f" ❌  Invalid input: '{user_answer}'.\nPlease try again.")


def check_list():
    """Checks expenses list for duplicate categories.
    If found, merges categories and adds values.
    Returns:
        non_duplicates (dict): Non-duplicated expenses."""
    # May contain duplicates.
    expenses = retrieve_expenses()
    non_duplicates = {}
    for item in expenses:
        cat, value = item
        value = round(float(Decimal(value)), 2)
        if cat in non_duplicates:
            non_duplicates[cat] += value
        else:
            non_duplicates[cat] = value
    replace_expenses(non_duplicates)
    return non_duplicates


def sum_prev_exps():
    gsheet = retrieve_gsheet()
    all_values = []
    for col in range(1, 7):
        column_list = gsheet.col_values(col)[2:]
        nums_only = []
        for col_value in column_list:
            if col_value != '':
                col_value = remove_formatting(col_value)
                nums_only.append(col_value)
            else:
                continue
        all_values.append(format_expenses(round((sum(nums_only)), 2)))
    return all_values


def create_expense(month: int, budget: str, colour="light_green"):
    """Creates conclusive user table with budget + expenses.
    Args:
        month (int): Num corresponding to Month selection.
        budget (str): Formatted budget.
        colour (str): Has default value of "light_green".
    Returns:
        None."""
    table = PrettyTable()
    budget = retrieve_formatted_budg()
    month = retrieve_month()
    budg_month = MONTHS[int(month)]
    table.field_names = [
        colored(f"Expenses for {budg_month}", colour),
        colored(f"{budg_month}'s budget: {budget}", colour),
    ]
    make_table_body(table)
    table.add_row(["-----------------------", "-----------------------"])
    make_table_body_past(table)
    table.add_row(["-----------------------", "-----------------------"])
    make_table_footer(table)
    table.align = "l"
    nextsteps_expense_table(table)


def make_table_body(table):
    """Makes up current expenses in table. Returns: None."""
    # Current Expenses.
    valid_cat_exp = check_list()
    for list_cat, list_exp in valid_cat_exp.items():
        f_exp = format_expenses(round(list_exp, 2))
        table.add_row([colored(list_cat, "white"), colored(f_exp, "white")])


def make_table_body_past(table):
    """Makes up retrieved expenses in table. Returns: None."""
    # Past Expenses.
    prev_exp = sum_prev_exps()
    cats = ["Rent",
            "Groceries",
            "Vehicle",
            "Cafe/Restaurant",
            "Online Shopping",
            "Other"]
    for value, cat in zip(prev_exp, cats):
        table.add_row(
            [colored(f"Past '{cat}' Tags:", "light_yellow"),
                colored(value, "light_yellow")])
        

def make_table_footer(table):
    """Retrieves budget remainder in table footer. Returns: None."""
    remainder = format_expenses(calculate_budget_remainder())
    if float(remainder[1:]) < 0:
        table.add_row(
            [
                colored("Your remaining budget:", "red"),
                colored(remainder, "red"),
            ]
        )
    else:
        table.add_row(
            [
                colored("Your remaining budget:", "green"),
                colored(remainder, "green"),
            ]
        )

def nextsteps_expense_table(conc_table: str):
    """Prints the conclusive expense table.
    Asks whether to upload to GS or exit.
    Args:
        conc_table (str): Expense table.
    Returns:
        None"""
    clear_terminal()
    print(f"\n{conc_table}")
    ask_update()


# ________ remainder value logic ___________


def calculate_budget_remainder():
    """Returns:
    user_budget_remainder (str): Budget remainder post deductions."""
    rem = retrieve_remainder_value()
    prev_exp = sum_prev_exps()
    budget = retrieve_budget()
    num_only = []
    for exp in prev_exp:
        num_only.append(remove_formatting(exp))
    summed = sum(num_only)
    if rem is None:
        set_remainder = float(budget)
    else:
        set_remainder = float(budget) - summed
    total_to_deduct = sum(retrieve_expenses().values())
    remainder = round(set_remainder - float(total_to_deduct), 2)
    update_rem(remainder)
    return remainder


def ask_update():
    """Asks to update google sheets or quit application.
    Returns:
        None."""
    while True:
        user_update = (
            input("\n ➤ Type 'u' to upload your expenses, or 'q' to exit: ")
            .strip()
            .lower()
        )
        if user_update == "u":
            update_worksheet()
            break
        elif user_update == "q":
            exit_tag()
            break
        else:
            print(" ❌  Invalid input.")
            print(f"You entered '{user_update}'. Please try again.")


def format_data():
    """Returns:
    format (list): sorted user expenses with currency symbol."""
    format = {
        "Rent": "",
        "Groceries": "",
        "Vehicle": "",
        "Cafe/Restaurant": "",
        "Online Shopping": "",
        "Other": "",
    }
    expenses = retrieve_expenses()
    for key, value in expenses.items():
        if key in format:
            format[key] = format_expenses(value)
    return format


def expensive_battleships():
    """Adds two parameters to create a cell format, e.g. 'C3'.
    Returns:
        cells (list): cells to be updated."""
    battleship = int(retrieve_month()) + 1
    return f"B{battleship}:G{battleship}"


def update_cell_actual_value():
    OV = retrieve_overview()
    cells_to_update = expensive_battleships()
    prev_exps = sum_prev_exps()
    all_values = [prev_exps]
    # Method Signature Arguments Deprecation warning [in version 6.0.0].
    OV.update(range_name=cells_to_update, values=all_values)
    print("\n ✅  We've successfully updated your Month sheet!")
    print("Check your Overview sheet to view your entire expense history.")
    ask_to_exit()


def ask_to_exit():
    while True:
        ex_user = (input(
            "\nPlease type 'q' to exit, or 's' to re-start the application: ")
            .strip()
            .lower())
        if ex_user == 'q':
            exit_tag()
            break
        elif ex_user == 's':
            # Reset expenses from a dict to empty list.
            replace_expenses([])
            clear_terminal()
            ask_month()
            break
        else:
            print(f"\n ❌  Invalid input '{ex_user}'.")
            print(" 👉  Please choose either 'q', or 's' to proceed.")


def update_worksheet():
    """Updates relevant Google Sheet with user's expenses.
    Returns:
        None."""
    print("⌛  Updating your worksheet...")
    append_remainder()
    append_budget()
    expenses = format_data()
    values_to_append = list(expenses.values())
    gsheet = retrieve_gsheet()
    gsheet.append_row(values_to_append)
    update_cell_actual_value()


def main():
    """Starts application.
    Returns:
        None."""
    print_intro()
    ask_name()


main()
