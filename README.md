# Tag Track
This application allows users to track their monthly expenses on a budget basis. The application presents a number of categories to the user, used to log expenses in an organised manner. These categories are classed as 'necessity' and 'luxury'. After logging their expenses, the user can view a summary of their budget on a Google sheets spread.  

The application is available for viewing [here]().
The Google Sheets for this application is available for use [here](https://docs.google.com/spreadsheets/d/1kGdwNqPvyRYIRL4LbEy-CgS1YDIHI6uKYHOG7gMbuB8/edit#gid=1925370965).

![reponsive UI]()

# Business/Social Goals
- Create a fully functioning and intuitive expense tracker to help users optimise their spending habits. 
- Provide a clear way of showing the (im)balance of certain spending habits, and the effect this has on monthly budgets. 
- Create a Google Sheet (database of sorts) with all tracked expenses so the user can refer back to them after logging. 
- Create an advice generator based on individual spending conditions. 

# UX Goals
As this project is backend-only, little can be done to make the UI attractive. However:
- Create a clear terminal face incorporating spacing for maximum legibility comfort.
- Where appropriate, include headings which stand out from ordinary text. 
- Where appropriate, include colours in elements to stand out from ordinary text. 

# Structure 
The structure of the 'Tag Track' application is as follows: 

## Terminal Face
- Title of tracker
    - Name input prompt
    - Month input prompt (number list)
    - Currency input prompt
        - EUR
        - GBP
        - USD
        - AUD
        - PLN
    - Total Monthly Budget input prompt
- _Press 'Enter' to Continue OR Type 'q' to quit..._

![first terminal stage]()

- List of Categorised Expenses
    - Rent
    - Groceries
    - Vehicle
    - Cafe/Restaurant
    - Online Shopping
    - Other
- Category Input prompt
- _Press 'Enter' to Continue OR Type 'q' to quit..._

![second terminal stage]()

- Expense input prompt
- Visual Appendage + Google Sheets Update
- _Press 'Enter' to Continue OR Type 'q' to quit..._
- _Type 'b' to view remaining Monthly Budget OR Type 'a' for advice..._
- _Press 'Enter' to return to Home Page..._

# Scope of Application
The application is intended for the purpose of collecting expense information from the user, and inputting the information into google sheets as rows. 
The scope of this application is as follows: 
1. Name input with validation (to personalise the experience). Used in the terminal throughout the application. 
2. Month selection with validation & input confirmation (as the application operates on a monthly basis for budget and final calculation). This selection is listed in the terminal for the user and the user may select a month using a number system, i.e. 1 - JAN, 2 - FEB, etc. The confirmation is implemented in case the user wanted to select December (no. 12), but accidentally pressed 'Enter' after typing '1'. The month is assigned as a heading in Google Sheets and in the terminal table. 
3. Currency selection with validation. 
4. Monthly Budget Input - transfers to Google Sheets as data for calculation. 
5. Several _'Enter' to continue_, or _'q' to quit_ prompts for user comfort. 
6. Expense category list so users can input their expenses in an organised manner. This is used to categorise expenses in Google Sheets for reference, and at the end of the application cycle to generate advice (if the user opts for this).
7. After expense input, existing and new expenses in each category are automatically added and a total for the month is displayed at the end of each row. This gives users an understanding of their spending habits, as well as allows them to see the potential disproportion. 
8. The terminal will allow users to see their remaining monthly budget after all deductions are made, without them needing to access Google Sheets (which is there for reference as this application is intended for use multiple times over the course of a month). 
9. Advice generator - Disclaimer: I am not a financial advisor, and frankly spend too much money on pastries, so these are general pieces of advice, generated based on certain conditions in the expense categories. 

# Strategy
It is the goal of the application to create an intuitive and communicative platform on which to track expenses on a budgetary means. This application operates on a monthly basis - i.e. users track their expenses based off of a monthly budget, and are able to view their remaining balance (positive or negative) whenever they please. By using Tag Tracker, users will acquire an understanding of their spending habits, see which months are more expensive for them, and be able to make adjustments to their habits accordingly. 

## Target Audience
- Anyone aged 16+ yrs.
- Anyone who would like to impove their spending habits.
- Anyone who would like a visual representation of their spending habits and the appropriate calculations. 

## Key Information Deliverables
- Visual Expense Tracking and logging
- Category Selection
- Expense Input
- Calculations & Advice

## Visual Simplicity
- As this is a backend project, little can be done to improve the UI of the terminal. However:
- Where possible, spacing will be added to the begining of sentences to separate them off the edge of the terminal. 
- Where possible, spacing will be added between sentences for better visual legibility. 
- Where appropriate, colours will be added to differentiate information for clearer legibility.

- On Google Sheets, each month will be set as a separate spread, so users have concise, separate areas in which to view their expenses. 

# Wireframes & FlowChart
Below is the flowchart for the application. Noted is the general flow of the application, the user story, and several validations with ValueError considerations and decision flows. 

![application flow](docs/images/flowchart.jpg)

# Aesthetics
# Features
# Technologies
# Testing & Debugging
#### Issues
### Debugging
# Accessibility & Performance
### Lighthouse
### Colour Accessibility Validator 
# Deployment
# Future Development
# Credits
# Acknowledgements