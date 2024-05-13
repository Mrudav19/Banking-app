import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import matplotlib.pyplot as plt

class BankAccount:
    dataset = {
        "Alice": {"balance": 1000, "password": "alice@123"},
        "Bob": {"balance": 200, "password": "bob@123"}
    }

    def __init__(self, name, password, currency="USD"):
        self.name = name
        self.password = password
        self.balance = self.dataset[name]["balance"]
        self.currency = currency
        self.interest_rate = 5  
        self.transaction_history = []

    def deposit(self, amount):
        if amount <= 0:
            messagebox.showerror("Error", "Deposit amount must be positive")
            return
        self.balance += amount
        self.transaction_history.append((datetime.datetime.now(), 'Deposit', amount, self.currency, None))
        messagebox.showinfo("Success", f"Deposit successful. Balance: {self.balance}")
        self.apply_interest()

    def withdraw(self, amount, category=None):
        if amount <= 0:
            messagebox.showerror("Error", "Withdrawal amount must be positive")
            return
        if self.balance - amount < 0:
            messagebox.showerror("Error", "Insufficient funds")
            return
        self.balance -= amount
        self.transaction_history.append((datetime.datetime.now(), 'Withdrawal', amount * -1, self.currency, category))
        messagebox.showinfo("Success", f"Withdrawal successful. Balance: {self.balance}")

    def transfer(self, amount, to_account, category=None):
        if amount <= 0:
            messagebox.showerror("Error", "Transfer amount must be positive")
            return
        if self.balance - amount < 0:
            messagebox.showerror("Error", "Insufficient funds")
            return
        self.withdraw(amount, category)
        to_account.deposit(amount, category)
        self.transaction_history.append((datetime.datetime.now(), 'Transfer to ' + to_account.name, amount * -1, self.currency, category))

    def apply_interest(self):
        if self.balance > 20:
            interest = self.balance * (self.interest_rate / 100)
            self.balance += interest
            self.transaction_history.append((datetime.datetime.now(), 'Interest Received', interest, self.currency, 'Interest'))
            messagebox.showinfo("Interest Received", f"Interest received: {interest} {self.currency}")
        elif self.balance < 20:
            messagebox.showwarning("Low Balance", "Your balance is below $20. You are not eligible for interest.")

    def view_transaction_history(self):
        return self.transaction_history

    def get_spending_habits(self):
        categories = {}
        for transaction in self.transaction_history:
            _, action, amount, _, category = transaction
            if action in ('Deposit', 'Interest Received'):
                continue
            if category not in categories:
                categories[category] = 0
            categories[category] += amount
        return categories

    def save_data(self):
        transaction_history_serializable = [
            (transaction[0].isoformat(), transaction[1], transaction[2], transaction[3], transaction[4])
            for transaction in self.transaction_history
        ]
        with open(f"{self.name}.json", "w") as file:
            json.dump({"balance": self.balance, "transaction_history": transaction_history_serializable}, file)

class BankApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Banking App")
        self.geometry("600x400")

        self.create_login_widgets()

    def create_login_widgets(self):
        self.info_label = tk.Label(self, text="Welcome to the Banking App!\nPlease log in to continue.", font=("Helvetica", 16))
        self.info_label.pack(pady=10)

        self.username_label = tk.Label(self, text="Username:")
        self.username_label.pack(pady=5)

        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)

        self.password_label = tk.Label(self, text="Password:")
        self.password_label.pack(pady=5)

        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        self.login_button = tk.Button(self, text="Login", command=self.login)
        self.login_button.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username in BankAccount.dataset and password == BankAccount.dataset[username]["password"]:
            self.create_bank_app(username)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def create_bank_app(self, username):
        self.info_label.destroy()
        self.username_label.destroy()
        self.username_entry.destroy()
        self.password_label.destroy()
        self.password_entry.destroy()
        self.login_button.destroy()

        self.current_user = username
        self.account = BankAccount(self.current_user, BankAccount.dataset[username]["password"])

        self.info_label = tk.Label(self, text=f"Welcome, {self.current_user}!")
        self.info_label.pack()

        self.create_bank_app_widgets()

    def create_bank_app_widgets(self):
        self.info_label = tk.Label(self, text=f"Welcome, {self.current_user}!", font=("Helvetica", 16))
        self.info_label.pack(pady=10)

        self.withdraw_button = tk.Button(self, text="Withdraw", command=self.withdraw_page)
        self.withdraw_button.pack(pady=5)

        self.deposit_button = tk.Button(self, text="Deposit", command=self.deposit_page)
        self.deposit_button.pack(pady=5)

        self.history_button = tk.Button(self, text="Transaction History", command=self.view_history_page)
        self.history_button.pack(pady=5)

        self.balance_button = tk.Button(self, text="View Balance", command=self.view_balance)
        self.balance_button.pack(pady=5)

        self.spending_habits_button = tk.Button(self, text="Spending Habits", command=self.view_spending_habits)
        self.spending_habits_button.pack(pady=5)

        self.history_graph_button = tk.Button(self, text="View Transaction History Graph", command=self.view_transaction_history_graph)
        self.history_graph_button.pack(pady=5)

        self.logout_button = tk.Button(self, text="Logout", command=self.logout)
        self.logout_button.pack(pady=10)

    def withdraw_page(self):
        amount = simpledialog.askfloat("Withdraw", "Enter amount to withdraw:")
        if amount is not None:
            category = simpledialog.askstring("Transaction Category", "Enter transaction category (optional):")
            try:
                self.account.withdraw(amount, category)
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def deposit_page(self):
        amount = simpledialog.askfloat("Deposit", "Enter amount to deposit:")
        if amount is not None:
            try:
                self.account.deposit(amount)
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def view_history_page(self):
        history = self.account.view_transaction_history()
        if not history:
            messagebox.showinfo("Transaction History", "No transactions found.")
        else:
            formatted_history = '\n'.join([f'{transaction[0]}: {transaction[1]} {transaction[2]:.2f} {transaction[3]} ({transaction[4]})' for transaction in history])
            messagebox.showinfo("Transaction History", formatted_history)

    def view_balance(self):
        messagebox.showinfo("Balance", f"Current balance: {self.account.balance} {self.account.currency}")

    def view_spending_habits(self):
        spending_habits = self.account.get_spending_habits()
        if not spending_habits:
            messagebox.showinfo("Spending Habits", "No spending habits found.")
        else:
            formatted_habits = '\n'.join([f'{category}: {amount:.2f} {self.account.currency}' for category, amount in spending_habits.items()])
            messagebox.showinfo("Spending Habits", formatted_habits)

    def view_transaction_history_graph(self):
        history = self.account.view_transaction_history()
        categories = [transaction[4] if transaction[4] else 'Uncategorized' for transaction in history]
        amounts = [abs(transaction[2]) for transaction in history]

        plt.figure(figsize=(8, 8))
        plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
        plt.title('Transaction History by Category')
        plt.axis('equal')
        plt.show()

    def logout(self):
        self.account.save_data()
        self.destroy()
        app = BankApp()
        app.mainloop()


if __name__ == "__main__":
    app = BankApp()
    app.mainloop()

