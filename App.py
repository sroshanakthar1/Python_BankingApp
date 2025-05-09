import datetime

acc_file = "accounts.txt"
trans_file = "transactions.txt"
users_file = "users.txt"
admins_file = "admins.txt"

# Time
def get_time():
    return datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

def setup_admin_account():
    print("=============== Admin Setup ================")
    username = input("Set admin username: ")
    password = input("Set admin password: ")
    with open(admins_file, "a") as f:
        f.write(f"{username},{password}\n")
    print("Admin account created successfully.")


# Authenticating - it is user or admin
def authenticate(role):
    username = input("Username: ")
    password = input("Password: ")
    file = admins_file if role == "admin" else users_file
    try:
        with open(file, "r") as f:
            for line in f:
                data = line.strip().split(",")
                if role == "admin" and len(data) == 2:
                    if data[0] == username and data[1] == password:
                        return True, username
                elif role == "user" and len(data) == 3:
                    if data[1] == username and data[2] == password:
                        return True, data[0]  # return correct account number
    except FileNotFoundError:
        print(f"{role.capitalize()} file not found.")
    print("Invalid credentials.")
    return False, None

# Generate a unique account number
def get_new_account_number():
    try:
        with open(acc_file, "r") as file:
            lines = file.readlines()
            if not lines:
                return 1001
            last_line = lines[-1]
            last_acc_no = int(last_line.split(",")[0])
            return last_acc_no + 1
    except FileNotFoundError:
        return 1001

# Admin-only: Create account
def create_account():
    name = input("Enter customer name: ")
    username = input("Set username for user: ")
    password = input("Set password for user: ")
    try:
        initial_balance = float(input("Enter initial balance (>= 0): "))
        if initial_balance < 0:
            print("Initial balance cannot be negative.")
            return
    except ValueError:
        return print("Enter only amount value")

    acc_no = get_new_account_number()

    with open(acc_file, "a") as file:
        file.write(f"{acc_no},{name},{initial_balance}\n")

    with open(users_file, "a") as file:
        file.write(f"{acc_no},{username},{password}\n")

    with open(trans_file, "a") as file:
        file.write(f"{acc_no},Deposit   ,{initial_balance},{get_time()}\n")

    print(f"Account created successfully! Account Number: {acc_no}")

# Deposit
def deposit_money(user_acc):
    amount = float(input("Enter amount to deposit: "))
    if amount <= 0:
        print("Amount must be positive.")
        return

    deposit_process = False
    new_data = []
    with open(acc_file, "r") as file:
        for line in file:
            acc, name, bal = line.strip().split(",")
            if acc == user_acc:
                bal = float(bal) + amount
                new_data.append(f"{acc},{name},{bal}\n")
                deposit_process = True
            else:
                new_data.append(line)

    if deposit_process:
        with open(acc_file, "w") as file:
            file.writelines(new_data)
        with open(trans_file, "a") as t_file:
            t_file.write(f"{user_acc},Deposit   ,{amount},{get_time()}\n")
        print("Deposit successful.")
    else:
        print("Account not found.")

# Withdraw
def withdraw_money(user_acc):
    amount = float(input("Enter amount to withdraw: "))
    if amount <= 0:
        print("Amount must be positive.")
        return

    withdraw_process = False
    new_data = []    #for adding updated data
    with open(acc_file, "r") as file:
        for line in file:
            acc, name, bal = line.strip().split(",")
            if acc == user_acc:
                bal = float(bal)
                if amount > bal:
                    print("Insufficient balance.")
                    return
                else:
                    bal -= amount
                    new_data.append(f"{acc},{name},{bal}\n")
                    withdraw_process = True
            else:
                new_data.append(line)
    
    if withdraw_process:
        with open(acc_file, "w") as file:
            file.writelines(new_data)
        with open(trans_file, "a") as t_file:
            t_file.write(f"{user_acc},Withdrawal ,{amount},{get_time()}\n")
        print("Withdrawal successful.")
    else:
        print("Account not found.")

# Check Balance
def check_balance(user_acc):
    with open(acc_file, "r") as file:
        for line in file:
            acc, name, bal = line.strip().split(",")
            if acc == user_acc:
                print(f"Account Holder: {name}\nBalance: Rs.{bal}")
                return
    print("Account not found.")

def transfer_money(user_acc):
    to_acc = input("Enter receiver's account number: ")
    finding_reciever = True
    with open(acc_file, "r") as file:
        for line in file:
            details = line.strip().split(",")
            if details[0] == to_acc:
                amount = float(input("Enter amount to transfer: "))
                if user_acc == to_acc:
                    print("Sender and receiver account cannot be the same.")
                    return
                if amount <= 0:
                    print("Amount must be positive.")
                    return

                transfer_process = False
                new_data = []
                try:
                    with open(acc_file, "r") as file:
                        for line in file:
                            acc, name, bal = line.strip().split(",")
                            if acc == user_acc:
                                bal = float(bal)
                                if amount > bal:
                                    print("Insufficient balance.")
                                    return
                                bal -= amount
                                transfer_process = True
                                new_data.append(f"{acc},{name},{bal}\n")
                            elif acc == to_acc:
                                bal = float(bal) + amount
                                new_data.append(f"{acc},{name},{bal}\n")
                            else:
                                new_data.append(line)
                except FileNotFoundError:
                    print("Account file not found.")
                    return

                if transfer_process:
                    with open(acc_file, "w") as file:
                        file.writelines(new_data)
                    time = get_time()
                    with open(trans_file, "a") as t_file:
                        t_file.write(f"{user_acc},TransferOut,{amount},{time}\n")
                        t_file.write(f"{to_acc},TransferIn ,{amount},{time}\n")
                    print("Transfer successful.")
                    finding_reciever = False
                return
    if finding_reciever:    
        print("Account not found.")

# View Transactions
def view_transactions(user_acc):
    print("===================================================")
    print("     Date & Time      |      Type       |    Amount")
    print("===================================================")
    found = False
    with open(trans_file, "r") as file:
        for line in file:
            acc, t_type, amount, time = line.strip().split(",")
            if acc == user_acc:
                print(f"{time}   |   {t_type}   | Rs.{amount}")
                found = True
    if not found:
        print("No transactions found.")


# ---------------- MENUS ----------------

def admin_menu():
    while True:
        print("\n=== Admin Menu ===")
        print("1. Create Account")
        print("2. Deposit Money")
        print("3. Check Balance")
        print("4. View Transactions")
        print("5. Create new admin")
        print("6. Logout")
        choice = input("Enter choice: ")
        if choice == '1':
            create_account()
        elif  choice == '2':
            num1 = input("Enter the account number that you deposit: ")
            deposit_money(num1)
        elif choice == '3':
            num1 = input("Enter the account number that you check balance: ")
            check_balance(num1)
        elif choice == '4':
            num1 = input("Enter the account number that you view transactions: ")
            view_transactions(num1)    
        elif choice == '5':
            setup_admin_account()
        elif choice == '6':
            break
        else:
            print("Invalid choice.")

def user_menu(account_number):
    while True:
        print("\n=== User Menu ===")
        print("1. Deposit Money")
        print("2. Withdraw Money")
        print("3. Check Balance")
        print("4. View Transactions")
        print("5. Transfer money")
        print("6. Logout")
        choice = input("Enter choice: ")
        if choice == '1':
            deposit_money(account_number)
        elif choice == '2':
            withdraw_money(account_number)
        elif choice == '3':
            check_balance(account_number)
        elif choice == '4':
            view_transactions(account_number)
        elif choice == '5':
            transfer_money(account_number)
        elif choice == '6':
            break
        else:
            print("Invalid choice.")

# ---------------- MAIN ----------------

def main():
    print("Welcome to the Banking System")

    # Admin setup if admins.txt is missing or empty
    try:
        with open(admins_file, "r") as f:
            lines = f.readlines()
            if not lines:
                setup_admin_account()
    except FileNotFoundError:
        setup_admin_account()

    # Main loop
    while True:
        print("\nLogin as:")
        print("1. Admin")
        print("2. User")
        print("3. Exit")
        role = input("Enter your choice: ")
        if role == '1':
            success, _ = authenticate("admin")
            if success:
                admin_menu()
        elif role == '2':
            success, acc_no = authenticate("user")
            if success:
                user_menu(acc_no)
        elif role == '3':
            print("Thank you for using the banking system.")
            break
        else:
            print("Invalid choice.")

main()
