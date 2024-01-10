import gspread
from google.oauth2.service_account import Credentials
from art import *
from colorama import Fore
import re

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

CREDS = Credentials.from_service_account_file('creds.json')
CREDS_SCOPE = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(CREDS_SCOPE)
SHEET = GSPREAD_CLIENT.open('Tag-Track')

def print_intro():
    text = text2art('Tag - Tracker')
    print(Fore.GREEN + 'Welcome to')
    print(Fore.GREEN + text + Fore.RESET)

def validate_string(string):
    return string.isalpha()

def ask_name():
    while True:
        name = input('Please tell me your name: ')
        if validate_string(name):
            ask_month()
            break

    return name

def ask_month():
    print('month')
    pass

def main():
    print_intro()
    ask_name()
main()