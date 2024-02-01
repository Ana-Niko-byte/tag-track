import gspread
import os
from google.oauth2.service_account import Credentials
from art import *
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
CURRENCY = {1: "EUR", 2: "GBP", 3: "USD", 4: "AUD", 5: "PLN"}

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
# List of global variables:
# - user_gsheet -> google sheet,
# user_budget -> user budget for the month.
user_month = None
user_gsheet = None
user_budget = None
user_budget_remainder = None
user_currency = None
user_expenses = []


def print_intro():
    """
    Prints large heading using colorama styling library.
    """
    text = text2art("Tag - Tracker")
    print(Fore.LIGHTGREEN_EX + text + Fore.RESET)


def exit_tag():
    print_intro()
    print(f"\n 👋  Thanks for using Tag-Track! See you soon :) \n")


def clear_terminal():
    """
    Clears the terminal screen for improved UX.
    """
    # For windows os.
    if os.name == "nt":
        os.system("cls")
    # For Unix/Linux os.
    else:
        os.system("clear")


def validate_string(string):
    """
    Validates any string input for alphabet-only characters.
    Returns true if no digits or symbols are present.
    """
    if not string:
        print(" ❌  Please enter a value to begin.\n")
    elif not all(letter.isalpha() for letter in string.split()):
        print(" ❌  Why you using digits, bro?\n")
    else:
        return True


def validate_num_selection(num):
    """
    Validates any number input.
    Returns true if no digits or symbols are present.
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
    Validates using validate_num_selection() using a set number range.
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
    """
    while True:
        user_conf = input(
            f"""\n 👉  You've chosen {user_input}.
            \n Type 'p' to proceed, 'c' to change, or 'q' to quit: """
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
    Creates tables using predefined tuple values.
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
    A user loop asking for name until valid input is provided.
    Once valid, the user is asked to selected a month from the provided list.
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
    Displays selection of month options in a table for logging expenses.
    If valid input, asks users to select a currency to proceed with.
    """
    create_table(MONTHS, "Month")
    while True:
        global user_month
        print(
            """\n (💡  Type the 'No.' that corresponds
        to the Month you want :) )"""
        )
        month = input(" ➤  Please choose the month you want to log for: ")
        user_month = month
        if validate_selection(month, 12):
            month_name = MONTHS[int(month)]
            user_choice = confirm_input(month_name)
            if user_choice == "p":
                get_month_sheet(month_name)
                ask_curr()  # retrieve_currency()
            elif user_choice == "c":
                clear_terminal()
                ask_month()
            break
    return month_name


def get_month_sheet(month_needed):
    """
    Fetches the worksheet based on the month the user chose.
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
    Displays selection of currency options in a table for logging expenses.
    If valid input, asks user if they wish to continue.
    """
    clear_terminal()
    print(f"\n ✅  You have chosen {MONTHS[int(user_month)]}.")
    create_table(CURRENCY, "Currency")
    while True:
        print(
            """\n (💡 Type the 'No.' that
        corresponds to the Currency you want ;))"""
        )
        curr = input(" ➤  Please choose the currency you wish to log in: ")
        if validate_selection(curr, 5):
            global user_currency
            user_currency = curr
            user_choice = confirm_input(CURRENCY[int(curr)])
            if user_choice == "p":
                clear_terminal()
                print(f" ✅  You have chosen to log in '{CURRENCY[int(curr)]}'")
                current = user_gsheet.acell("B1").value
                validate_budget_retrieval(current)
                break
            elif user_choice == "c":
                ask_curr()
            break
    return curr


def format_expenses(curr, expense):
    """
    Formats the user's expenses with the chosen currency symbol.
    """
    # Code taken from Currency example on pypi.org
    currency = Currency(CURRENCY[int(curr)])
    formatted_expense = currency.get_money_format(expense)
    return formatted_expense


def append_budget(budget):
    """
    Updates B1 cell in google sheets with the value of the user's budget.
    """
    sheet = user_gsheet
    # This will change any previously logged budget in the 'B1' cell.
    sheet.update_acell("B1", budget)


def retrieve_budget():
    """
    Retrieves current budget value.
    Asks user if they wish to use it or change its value.
    """
    current = user_gsheet.acell("B1").value
    if current is None:
        ask_budget()
    elif current:
        clear_terminal()
        print(
            f"""\n ⚠️  Your budget for the month of
            {MONTHS[int(user_month)]} is currently set to {current}.⚠️"""
        )
        user_budget_input = input(
            """\n ➤  Would you like to use this (type 'u'),
            or amend it? (type 'c') """
        )
        return user_budget_input


def validate_budget_retrieval(current_budget):
    retrieved_choice = retrieve_budget()
    if retrieved_choice == "u":
        global user_budget
        user_budget = current_budget
        print(
            f"""Your budget remains at {current_budget}
            for the month of {MONTHS[int(user_month)]}."""
        )
        ask_category()
    elif retrieved_choice == "c":
        ask_budget()


def ask_budget():
    """
    Asks user for budget and updates global budget variable.
    If valid input, asks user if they wish to continue.
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
                current = user_gsheet.acell("B1").value
                validate_budget_retrieval(current)


def ask_category():
    """
    Displays selection of category options in a table for logging expenses.
    If valid input, asks user if they wish to continue.
    """
    create_table(EXPENSES, "Expense Category")
    while True:
        print(
            """\n (💡  Type the 'No.' that
        corresponds to the Category you want :) )"""
        )
        cat = input(" ➤  Please choose a category: ")
        if cat == "":
            print(" ❌  Please choose a category to log an expense.")
            continue
        elif validate_selection(cat, 6) is False:
            continue
        elif validate_selection(cat, 6):
            user_choice = confirm_input(EXPENSES[int(cat)])
            if user_choice == "p":
                if int(cat) == 1 or int(cat) == 2:
                    print(f"\n ✅  Ouch...spending on {EXPENSES[int(cat)]}...")
                elif int(cat) > 2 and int(cat) != 6:
                    print(
                        f"""\n ✅  Ooo...spending
                    on {EXPENSES[int(cat)]}? Nice!"""
                    )
                ask_expense(EXPENSES[int(cat)])
            elif user_choice == "c":
                ask_category()
        return cat


def ask_expense(category):
    """
    Asks user for expense in the chosen category.
    If valid input, asks user if they wish to continue.
    """
    while True:
        expense_msg = f"   ➤ Please enter the amount you spent on {category}: "
        user_expense = input(expense_msg)
        global user_expenses
        global user_month
        global user_budget
        if user_expense == "":
            print(f" ❌  Please enter your expenses for {category}")
            continue
        elif validate_num_selection(user_expense):
            user_choice = confirm_input(user_expense)
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
    return user_expense


def continue_expenses():
    """
    Loop asking the user if they want to log another expense, with validation.
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
    If found, merges and adds their expense values together.
    """
    # Gets the logged expenses - may contain duplicates.
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
    # Re-assign the global variable the value of duplicates.
    user_expenses = duplicates
    return duplicates


def create_expense(month, budget, colour="light_green"):
    """
    Creates final table to display all user input.
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
        formatted_exp = format_expenses(user_currency, list_expense)
        table.add_row(
            [colored(list_category, "white"), colored(formatted_exp, "white")]
        )
        table.align = "l"

    remainder = calculate_budget_remainder()
    remainder_value = float(remainder[1:])
    # Add separating rows to the table to differentiate final data.
    table.add_row(["-----------------------", "-----------------------"])
    # Check if budget is '-' or '+' to determine colour of final table row.
    if remainder_value < 0:
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


def calculate_budget_remainder():
    # Get the unformatted version of budget.
    global user_budget
    unformatted_budget = user_budget[1:]
    # Get the total of the user's expenses.
    total = sum(user_expenses.values())
    total = str(total)
    numeric_budget = float(unformatted_budget.replace(",", ""))
    remainder = round(numeric_budget - float(total), 2)
    # Update the global variable for the remainder.
    global user_budget_remainder
    user_budget_remainder = format_expenses(user_currency, remainder)
    return user_budget_remainder


def ask_update():
    """
    Asks user whether to update google sheets with their values
    or provide some advice for future spending.
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
    Formats data for the google sheet.
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
    """
    sheet = SHEET.worksheet("Overview")
    global user_month
    # The list user_expenses was changed to a dictionary in check_list().
    global user_expenses

    # The user inputs a number when selecting a month.
    # This row holds all the values for updating after the initial log.
    # + 1 is added to get the next cell (headers being in the first row).
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
    Updates relevant Google Sheets with user's expenses.
    """
    print("   ⌛  Updating your worksheet...")
    expenses = format_data()
    values_to_append = list(expenses.values())
    append_budget(user_budget)
    user_gsheet.append_row(values_to_append)
    update_cell_values()


def main():
    print_intro()
    ask_name()


main()
