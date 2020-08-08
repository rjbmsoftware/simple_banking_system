import random
import sqlite3
import sys


def print_menu():
    print('1. Create an account',
          '2. Log into account',
          '0. Exit', sep='\n')


def generate_pin() -> str:
    return f'{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}'


def generate_account_number() -> str:
    new_account = ''
    for i in range(9):
        new_account += str(random.randint(0, 9))

    return new_account


def generate_luhn_validated_checksum(bank_id_and_account_number: str) -> int:
    digits = [int(digit) for digit in bank_id_and_account_number]
    for i in range(0, len(digits), 2):
        new_value = digits[i] * 2
        if new_value > 9:
            new_value -= 9
        digits[i] = new_value

    total = sum(digits)
    return 0 if total % 10 == 0 else 10 - total % 10


def generate_card_number() -> str:
    bank_id_number = '400000'
    nine_digit_account_number = generate_account_number()
    checksum = generate_luhn_validated_checksum(f'{bank_id_number}{nine_digit_account_number}')

    return f'{bank_id_number}{nine_digit_account_number}{checksum}'


def generate_unique_card() -> str:
    card_number = generate_account_number()
    while read_account(card_number) is None:
        card_number = generate_account_number()

    return card_number


def save_account(card_number: str, pin: str) -> None:
    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO card (number, pin) VALUES ({card_number}, {pin})')
    conn.commit()


def create_account():
    account_card_number = generate_card_number()
    account_pin = generate_pin()
    save_account(account_card_number, account_pin)

    print('Your card has been created',
          'Your card number:',
          account_card_number,
          'Your card PIN:',
          account_pin, sep='\n')


def read_account(card_number: str) -> {}:
    cursor = conn.cursor()
    cursor.execute(f'SELECT number, pin, balance FROM card WHERE number = {card_number}')
    cols = cursor.fetchone()
    if cols is None:
        return None

    return {'account_number': cols[0], 'pin': cols[1], 'balance': cols[2]}


def login_account():
    print('Enter your card number:')
    user_card_number = input()
    print('Enter your PIN:')
    user_pin = input()

    account_details = read_account(user_card_number)
    if account_details is not None and account_details['pin'] == user_pin:
        logged_in_path(account_details)
    else:
        print('Wrong card number or PIN!')


def print_logged_in_menu():
    print('1. Balance',
          '2. Add income',
          '3. Do transfer',
          '4. Close account',
          '5. Log out',
          '0. Exit', sep='\n')


def update_balance(card_number, change_in_balance):
    cursor = conn.cursor()
    cursor.execute(f'UPDATE card SET balance = balance + {change_in_balance} WHERE number = {card_number}')
    conn.commit()


def add_income(card_number: str) -> None:
    print('Enter income:')
    income = int(input())
    update_balance(card_number, income)
    print('Income was added!')


def luhn_validate(card_number) -> bool:
    digits = [int(digit) for digit in card_number[:-1]]
    for i in range(0, len(digits), 2):
        new_value = digits[i] * 2
        if new_value > 9:
            new_value -= 9
        digits[i] = new_value

    total = sum(digits)
    calculated_check_digit = 0 if total % 10 == 0 else 10 - total % 10
    check_digit = int(card_number[-1])
    return calculated_check_digit == check_digit


def do_transfer(card_number) -> None:
    print('Transfer', 'Enter card number:', sep='\n')
    to_account_number = input()
    if not luhn_validate(to_account_number):
        print("Probably you made mistake in the card number. Please try again!")
        return

    to_account = read_account(to_account_number)
    if to_account:
        if to_account['account_number'] == card_number:
            print("You can't transfer money to the same account!")
            return

        print('Enter how much money you want to transfer:')
        transfer_amount = int(input())
        from_account = read_account(card_number)
        if transfer_amount > from_account['balance']:
            print('Not enough money!')
            return

        update_balance(from_account['account_number'], -transfer_amount)
        update_balance(to_account['account_number'], transfer_amount)
        print('Success!')
    else:
        print('Such a card does not exist.')


def delete_account(card_number):
    cursor = conn.cursor()
    cursor.execute(f'DELETE FROM card WHERE number = {card_number}')
    conn.commit()


def close_account(card_number: str) -> None:
    delete_account(card_number)
    print('The account has been closed!')


def logged_in_path(account_details: []) -> None:
    print('You have successfully logged in!')
    print_logged_in_menu()
    logged_in_user_choice = int(input())
    card_number = account_details['account_number']

    while logged_in_user_choice != 5:
        if logged_in_user_choice == 1:
            print(f'Balance: {read_account(card_number)["balance"]}')
        elif logged_in_user_choice == 2:
            add_income(card_number)
        elif logged_in_user_choice == 3:
            do_transfer(card_number)
        elif logged_in_user_choice == 4:
            close_account(card_number)
            break
        elif logged_in_user_choice == 0:
            sys.exit()

        print_logged_in_menu()
        logged_in_user_choice = int(input())


sql_create_account_table = """
CREATE TABLE IF NOT EXISTS card (   
    id INTEGER,
    number TEXT,
    pin TEXT,
    balance INTEGER DEFAULT 0  
);"""


def initialise_db(connection: sqlite3.Connection) -> None:
    cursor = connection.cursor()
    cursor.execute(sql_create_account_table)
    connection.commit()


conn = sqlite3.connect('card.s3db')
initialise_db(conn)
print_menu()
user_choice = int(input())

while user_choice:
    if user_choice == 1:
        create_account()
    elif user_choice == 2:
        login_account()
    print_menu()
    user_choice = int(input())
