
'''

ISE Senior Design Project - Kailey's Queens
For our year-long capstone project, our senior design project team partnered with Kailey's Queens – an online, 
international, safe space for girls to make new friends and learn new skills. 
Kailey's Queens is up-and-coming, so prior to the integration of our new system design, nearly all business processes were conducted manually. 
The Kailey's Queens team had to manually send confirmation/post-purchase emails to event participants, 
assign participants into their Zoom breakout rooms (based on age & preference) during the time of an online event, 
and send Zoom links to participants before the time of an event.

Our project team was tasked with systematizing and automating our client’s business processes. 
In summary, our project involved the following components: updating the Kailey's Queens website for improved participant data collection, 
writing multiple risk-averse Python scripts to effectively manipulate and export participant data, 
creating & executing effective testing procedures to ensure maximal efficacy of our scripts, 
and providing an effective method to send event-specific mass emails to participants.

This project is extremely meaningful because it allowed me to couple my knowledge of industrial & systems engineering concepts 
along with my programming skills to streamline and execute our system design, which ultimately solved a real-life business problem. 
Our project deliverables were used to automate our client's business processes, which allows for future scalability of our client's business.

'''

import pandas as pd
import numpy as np
import math

############################################################################################################
# IMPORTING SHOPIFY CLIENT CSV & 
############################################################################################################
pd.set_option('display.width', None)
pd.set_option('display.max_rows', None)
loop1 = 0
file_path = input('Please enter the file path for the Shopify Export Data.\n'
                  'Sample file path: /Users/adreannalaporte/Desktop/ISE 495B/data export mult events & prefs.csv\n'
                  'File path: ')
while loop1 == 0:
    if isinstance(file_path, str) and '/' in file_path and '.csv' in file_path:
        loop1 = 1
    else:
        print('Please enter a valid file path. Make sure your formatting is correct (follow sample file path given '
              'above):')
        file_path = input('File path: ')
        loop1 = 0
data = pd.read_csv(file_path)

# removing blank spaces in order number column
ords = data.iloc[:, 0].tolist()
order_numbers = []
for order in ords:
    if isinstance(order, str):
        order_numbers.append(order)

# going to parse through values list and split up emails and ages
# grabbing column w emails, ages, prefs from shopify csv
info = data.iloc[:, 1].tolist()
# creating empty lists
emails = []
ages = []
prefs = []
# starting at index 2, pulling every 3 values for email, age, pref (based on formatting from shopify csv)
# will pull in pref value even if empty
# if last girl does not have pref, then it will manually add a nan value to make list lengths equal
for x in range(2, (len(info) + 1), 5):
    emails.append(info[x])
    ages.append(int(info[x + 1]))
    if (x + 2) < len(info):
        prefs.append(info[x + 2])
    else:
        prefs.append(np.nan)

# removing blank spaces in product name column (reads product ids and floats in case no product name available)
prod = data.iloc[:, 2].tolist()
products = []
for i in prod:
    if isinstance(i, (float, int)):
        if i > 0:
            products.append(i)
        elif not math.isnan(i):
            products.append(i)
    else:
        products.append(i)

# check the length of each list to make sure they are all the same
# if each list length is not equivalent, then the program will quit & tell kailey to re-try with new export file
x = 0
while x == 0:
    if not len(order_numbers) == len(emails) == len(ages) == len(prefs) == len(products):
        print('\n\nPlease ensure all columns are the same length in Shopify Export File.\n'
              'Exiting Program Now...\n'
              'PLEASE ADJUST SHOPIFY EXPORT FILE BEFORE RESTARTING THE PROGRAM!')
        quit()
    else:
        x = 1

# put together the dataframe
data_dictionary = {'Order Number': order_numbers,
                   'E-Mail': emails,
                   'Age': ages,
                   'Products': products,
                   'Preference': prefs}
new_df = pd.DataFrame(data_dictionary)

# checking shopify data to make sure it looks good before it gets manipulated
print('\n\nPlease verify that the following data from Shopify looks correct before it gets manipulated:\n\n', new_df)
checker = input('\n\nEnter 1 if YES or enter 0 if NO:')
a = 1
while a == 1:
    if checker == '1':
        print('\nYou verified that the Shopify Export Data looked correct! Moving on...\n\n')
        a = 0
    elif checker == '0':
        print('Please adjust Shopify Export File as needed.\n'
              'Exiting Program Now...\n'
              'PLEASE ADJUST SHOPIFY EXPORT FILE AND SAVE IT UNDER THE SAME FILE NAME BEFORE RESTARTING THE PROGRAM!')
        a = 0
        quit()
    else:
        a = 1
        print('Please enter valid input. Try again.')
        checker = input('Enter 1 if yes & 0 if no:')

# ask for kailey to input product menu selection (from unique values of products in shopify export file)
# and checking if input work
prod_names = new_df['Products'].unique()
prod_dict = {}
for x in range(len(prod_names)):
    prod_dict[str(x + 1)] = prod_names[x]
print("Here are the products/events that are available based on the data you uploaded:")
for k in prod_dict.keys():
    print(f'{k}. {prod_dict[k]}')
product_num = input('Please Enter a Number from the Menu Above: ')

# creating the while loop to check for appropriate input
loop = 0
while loop == 0:
    if product_num not in prod_dict.keys():
        print('Could not find that Product/Event Name. Please Enter a Valid Number.')
        product_num = input('Please Enter a Number from the Menu Above: ')

    else:
        print(f'\n\n~~~~~ Exporting CSV file for the following: {prod_dict[product_num]} ~~~~~\n\n')
        product_filt = new_df['Products'] == prod_dict[product_num]
        new_df = new_df[product_filt]

        ############################################################################################################
        # MANIPULATING THE ORGANIZED DATAFRAME BELOW :
        ############################################################################################################

        # reading in the restructured shopify csv file with participant data
        df_participants = new_df

        # sorting by age and then by preference
        df_participants = df_participants.sort_values('Age')
        df_participants = df_participants.sort_values('Preference', ascending=False)

        # removing unnecessary columns from the data frame
        del df_participants['Order Number']
        del df_participants['Products']

        # creating the breakout room column & initializing it to zero
        df_participants['Breakout Room'] = 0

        # reindexing the columns after sorting them
        df_participants = df_participants.reindex(columns=['Breakout Room', 'E-Mail', 'Age', 'Preference'])
        df_participants = df_participants.reset_index(drop=True)

        ############################################################################################################
        # PREFERENCES INCORPORATED BELOW:
        ############################################################################################################

        # creating lists of preferences and emails for manipulation
        pref_indexes = []
        email_indexes = []

        for pref in df_participants['Preference']:
            if isinstance(pref, str):
                pref_indexes.append(pref.lower())

        for email in df_participants['E-Mail']:
            if isinstance(email, str):
                email_indexes.append(email.lower())

        # moving preferences next to desired participant & inserting them into the email column
        counter1 = 1
        counter2 = 0
        pref_length = len(pref_indexes) - 1
        for pref in pref_indexes:
            if pref in email_indexes:
                temp_email_index = email_indexes.index(pref)
                if temp_email_index > counter2:
                    temp_email_value = email_indexes[temp_email_index]

                    if pref_length > temp_email_index:
                        temp_pref_index = temp_email_index
                        temp_pref_value = pref_indexes[temp_pref_index]
                        del pref_indexes[temp_pref_index]
                        pref_indexes.insert(counter1, temp_pref_value)
                    elif pref_length < temp_email_index:
                        pref_indexes.insert(counter1, ' ')

                    del email_indexes[temp_email_index]

                    email_indexes.insert(counter1, temp_email_value)
            counter1 += 1
            counter2 += 1

        # replacing the original email list with the new email list that accounts for preferences
        email_series = pd.Series(email_indexes)
        # print(email_series)
        df_participants['E-Mail'] = email_series
        # print statement below shows data frame with email, age, and preference

        ############################################################################################################
        # BREAKOUT ROOMS CREATED BELOW:
        ############################################################################################################

        # establishing breakout room size / number of breakout rooms based on requirements (ideal # is 16)
        breakout_room_size = 16
        num_of_breakout_rooms = int((len(df_participants['E-Mail']) / breakout_room_size))
        modulus = len(df_participants['E-Mail']) % breakout_room_size
        num_of_participants = len(df_participants['Breakout Room'])

        # assigning breakout rooms when # participants divides up evenly
        counter = 0
        if modulus == 0:
            for num in range(num_of_breakout_rooms):
                for x in range(breakout_room_size):
                    df_participants.iloc[counter, 0] = num + 1
                    counter += 1

        # assigning breakout rooms when # participants DOES NOT divide up evenly
        # but CREATING NEW breakout room to account for remaining girls
        elif modulus >= 10:
            for num in range(num_of_breakout_rooms):
                for x in range(breakout_room_size):
                    df_participants.iloc[counter, 0] = num + 1
                    counter += 1

            remainder_breakout_room_num = num_of_breakout_rooms + 1

            final_breakout_room_index = num_of_participants - (num_of_breakout_rooms * 20)

            total_num_participants = final_breakout_room_index + modulus

            total_num_participants_index = total_num_participants - 1

            for x in range(len(df_participants['E-Mail'])):
                if df_participants.iloc[x, 0] == 0:
                    df_participants.iloc[x, 0] = remainder_breakout_room_num

        # assigning breakout rooms when # participants DOES NOT divide up evenly
        # but NOT CREATING NEW breakout room to account for remaining girls
        else:

            if modulus <= num_of_breakout_rooms:
                breakout_room_size = breakout_room_size + 1
                for x in range(modulus):
                    for i in range(breakout_room_size):
                        df_participants.iloc[counter, 0] = x + 1
                        counter += 1
                breakout_room_size = breakout_room_size - 1
                for x in range(num_of_breakout_rooms - modulus):
                    for i in range(breakout_room_size):
                        df_participants.iloc[counter, 0] = x + modulus + 1
                        counter += 1

            else:
                breakout_room_size = round(num_of_participants / num_of_breakout_rooms)
                if breakout_room_size * num_of_breakout_rooms < num_of_participants:
                    breakout_room_size += 1
                if breakout_room_size <= 18:
                    modulus = num_of_participants % num_of_breakout_rooms

                    if modulus == 0:
                        for num in range(num_of_breakout_rooms):
                            for x in range(breakout_room_size):
                                df_participants.iloc[counter, 0] = num + 1
                                counter += 1
                    elif modulus <= num_of_breakout_rooms:

                        for x in range(modulus):
                            for i in range(breakout_room_size):
                                df_participants.iloc[counter, 0] = x + 1
                                counter += 1
                        breakout_room_size = breakout_room_size - 1
                        for x in range(num_of_breakout_rooms - modulus):
                            for i in range(breakout_room_size):
                                df_participants.iloc[counter, 0] = x + modulus + 1
                                counter += 1
                else:
                    num_of_breakout_rooms = num_of_breakout_rooms + 1
                    breakout_room_size = int(num_of_participants / num_of_breakout_rooms)
                    modulus = num_of_participants % num_of_breakout_rooms

                    if modulus <= num_of_breakout_rooms:
                        breakout_room_size = breakout_room_size + 1
                        for x in range(modulus):
                            for i in range(breakout_room_size):
                                df_participants.iloc[counter, 0] = x + 1
                                counter += 1
                        breakout_room_size = breakout_room_size - 1
                        for x in range(num_of_breakout_rooms - modulus):
                            for i in range(breakout_room_size):
                                df_participants.iloc[counter, 0] = x + modulus + 1
                                counter += 1

        # final product printed before exporting to csv
        print('\n\n~~~~~Here is what will be in your CSV export:~~~~~\n\n')
        print(df_participants)

        # asking Kailey to enter file path destination
        loop2 = 0
        export_file_path = input('Please enter the file path of where you want the output CSV to be stored.\n'
                                 'File path: ')
        while loop2 == 0:
            if isinstance(export_file_path, str) and '/' in export_file_path and '.csv' in export_file_path:
                loop2 = 1
            else:
                print('\n\nPlease enter a valid file path.')
                export_file_path = input('File path: ')
                loop2 = 0

        # exporting to csv!!
        df_participants.to_csv(export_file_path, index=False)
        loop = 1
