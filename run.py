import gspread
from google.oauth2.service_account import Credentials
from art import *
from colorama import Fore

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

CREDS = Credentials.from_service_account_file('creds.json')
CREDS_SCOPE = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(CREDS_SCOPE)
SHEET = GSPREAD_CLIENT.open('Tag-Track')

text = text2art('Tag - Tracker')
print(Fore.GREEN + 'Welcome to Your')
print(Fore.GREEN + text + Fore.RESET)