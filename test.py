import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from customtkinter import *
from PIL import Image
from datetime import datetime
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class Application(CTk):
    def __init__(self):
        super().__init__()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        self.title("Sari-Sari Store POS")
        self.geometry("856x645")
        self.resizable(True, True)
        set_appearance_mode("light")  # Assuming set_appearance_mode is defined somewhere

        self.setup_sidebar()
        self.setup_main_view()

        self.current_page = None  # Track the currently shown page
        
        self.show_purchase()  # Show inventory page by default
        
        # Bind keys
        self.bind_keys()
        
        
    def bind_keys(self):
        self.bind("<Escape>", lambda event: self.clear_cart_init())
        self.bind("<space>", lambda event: self.search_product_init())
        self.bind('<Tab>', lambda event: self.focus_available_products())
        self.bind("<F1>", lambda event: self.enter_cash_init())
        self.bind('<F2>', lambda event: self.submit_init())

    def clear_cart_init(self):
        if self.current_page == self.purchase_page:
            self.purchase_page.isClear = True
            self.purchase_page.clear_cart()
            
    def search_product_init(self):
        if self.current_page == self.purchase_page:
            self.purchase_page.search_entry.focus_set()
            
    def focus_available_products(self):
        if self.current_page == self.purchase_page:
            first_item = self.purchase_page.table_available_product.get_children()[0]
            self.purchase_page.table_available_product.selection_set(first_item)
            self.purchase_page.table_available_product.focus(first_item)
            self.purchase_page.table_available_product.focus_set()
            
    def enter_cash_init(self):
        if self.current_page == self.purchase_page:
            self.purchase_page.enter_cash()
            
    def submit_init(self):
        if self.current_page == self.purchase_page:
            self.purchase_page.submit()

    def setup_sidebar(self):
        self.sidebar_frame = CTkFrame(master=self, fg_color="#2A8C55", width=176, height=650, corner_radius=0)
        self.sidebar_frame.pack_propagate(0)
        self.sidebar_frame.pack(fill="y", anchor="w", side="left")

        logo_img_data = Image.open("images/logo.png")
        logo_img = CTkImage(dark_image=logo_img_data, light_image=logo_img_data, size=(77.68, 85.42))
        CTkLabel(master=self.sidebar_frame, text="", image=logo_img).pack(pady=(38, 0), anchor="center")
        
        package_img_data = Image.open("images/shipping_icon.png")
        package_img = CTkImage(dark_image=package_img_data, light_image=package_img_data)
        self.purchase_button = CTkButton(master=self.sidebar_frame, image=package_img, text="Purchase", fg_color="#fff", font=("Arial Bold", 14), text_color="#2A8C55", hover_color="#eee", anchor="w", command=self.show_purchase)
        self.purchase_button.pack(anchor="center", ipady=5, pady=(60, 0))

        inventory_img_data = Image.open("images/inventory_icon.png")  # Assuming you have an icon for inventory
        inventory_img = CTkImage(dark_image=inventory_img_data, light_image=inventory_img_data)
        self.inventory_button = CTkButton(master=self.sidebar_frame, image=inventory_img, text="Inventory", fg_color="transparent", font=("Arial Bold", 14), hover_color="#207244", anchor="w", command=self.show_inventory)
        self.inventory_button.pack(anchor="center", ipady=5, pady=(16, 0))
        
        analytics_img_data = Image.open("images/analytics_icon.png")
        analytics_img = CTkImage(dark_image=analytics_img_data, light_image=analytics_img_data)
        self.dashboard_button = CTkButton(master=self.sidebar_frame, image=analytics_img, text="Database", fg_color="transparent", font=("Arial Bold", 14), hover_color="#207244", anchor="w", command=self.show_dashboard)
        self.dashboard_button.pack(anchor="center", ipady=5, pady=(16, 0))
        
    def setup_main_view(self):
        self.main_view = CTkFrame(master=self, fg_color="#fff", width=680, height=650, corner_radius=0)
        self.main_view.pack_propagate(0)
        self.main_view.pack(side="left", expand=True, fill="both")

    def show_dashboard(self):
        self.dashboard_page = UpdatePage(master=self.main_view)
        self.dashboard_page.pack_propagate(0)
        
        if self.current_page:
            self.current_page.pack_forget()

        self.dashboard_page.pack(side="left", expand=True, fill="both")
        self.current_page = self.dashboard_page
        
        # update the table every clicked on tab
        self.dashboard_page
        self.highlight_nav_button(self.dashboard_button)

    def show_purchase(self):
        self.purchase_page = PurchasePage(master=self.main_view)
        self.purchase_page.pack_propagate(0)
        
        
        if self.current_page:
            self.current_page.pack_forget()

        self.purchase_page.pack(side="left", expand=True, fill="both")
        self.current_page = self.purchase_page
        self.highlight_nav_button(self.purchase_button)

    def show_inventory(self):
        self.inventory_page = InventoryPage(master=self.main_view)
        self.inventory_page.pack_propagate(0)
        
        if self.current_page:
            self.current_page.pack_forget()

        self.inventory_page.pack(side="left", expand=True, fill="both")
        self.current_page = self.inventory_page
        self.highlight_nav_button(self.inventory_button)
        
    def highlight_nav_button(self, button):
        # Reset all buttons to their default color
        self.purchase_button.configure(fg_color="transparent", text_color="#d3d3d3")
        self.inventory_button.configure(fg_color="transparent", text_color="#d3d3d3")
        self.dashboard_button.configure(fg_color="transparent", text_color="#d3d3d3")
        
        # Highlight the selected button
        button.configure(fg_color="#fff", text_color="#2A8C55")

class PurchasePage(CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.setup_search_bar()
        self.load_available_product()
        self.setup_table_available_product()
        self.setup_table_cart()
        self.setup_subtotal()
        self.setup_submit_button()
        self.enter_cash_button()
        self.setup_clear_button()
        self.setup_change_cash_label()
        
        
        # Bind keys
        self.bind_keys()
        
        self.cart_data = []
        self.isClear = False
        self.isSubmitted = None
        
        self.change = 0
        self.cash_received = 0
        self.amount_due = 0
        
        
    def bind_keys(self):
        # Bind the ESC key to the clear_cart method
        self.bind("<Escape>", self.clear_cart)
        
    def setup_search_bar(self):
        self.main_view = CTkFrame(master=self, fg_color="#fff", width=680, height=650, corner_radius=0)
        self.main_view.pack_propagate(0)
        self.main_view.pack(side="left", expand=True, fill="both")
        
        search_container = CTkFrame(master=self.main_view, height=50, fg_color="#F0F0F0")
        search_container.pack(fill="x", pady=(25, 0), padx=27)
        search_label = CTkLabel(master=search_container, text="Search: ").pack(side="left", padx=(13, 0), pady=10)
        self.search_entry = CTkEntry(master=search_container, width=305, placeholder_text="Enter Barcode or Product Name", border_color="#2A8C55", border_width=2)
        self.search_entry.pack(side="left", padx=(13, 0), pady=15)
        self.search_entry.bind("<KeyRelease>", self.search_product)
    
    def load_available_product(self):
        self.available_product = "inventory.csv"
        try:
            self.df_available_product = pd.read_csv(self.available_product)
            # convert Barcode to str type
            self.df_available_product['Barcode'] = self.df_available_product['Barcode'].astype(str).str.replace('\.0$', '', regex=True)
            self.header_available_product_list = list(self.df_available_product.columns)
            self.header_display_columns = [col for col in self.header_available_product_list if col != 'Purchased Price']
            self.list_available_product = self.df_available_product[self.header_display_columns].values.tolist()
        except FileNotFoundError:
            self.df_available_product = pd.DataFrame()
            self.list_available_product = []
            self.header_available_product_list = []
            self.header_display_columns = []

    def setup_table_available_product(self):
        available_product_label = CTkLabel(master=self.main_view, text="Available Products:")
        available_product_label.pack(side="top", anchor='nw', pady=(10,0), padx=27)

        available_product_container = CTkFrame(master=self.main_view, height=50, fg_color="black")
        available_product_container.pack(fill="x", pady=(0, 0), padx=27)

        treestyle = ttk.Style()
        treestyle.theme_use('clam')
        treestyle.configure("Treeview", background="white", foreground='black', fieldbackground='white', borderwidth=0, font=("Arial", 12), width=150)
        treestyle.configure("Treeview.Heading", anchor="center", font=("Arial", 14))

        self.table_available_product = ttk.Treeview(available_product_container, columns=self.header_display_columns, show='headings')
        for col in self.header_display_columns:
            self.table_available_product.heading(col, text=col, anchor='center')
        self.table_available_product.pack(fill='both', expand=True)

        for row in self.list_available_product:
            self.table_available_product.insert('', 'end', values=row)

        for col in self.table_available_product["columns"]:
            self.table_available_product.column(col, anchor='center')

        self.table_available_product.bind('<Return>', self.item_select)

    def item_select(self, event):
        self.clear_cart()
        selected_items = self.table_available_product.selection()
        for i in selected_items:
            item_values = self.table_available_product.item(i)['values']
            barcode = str(item_values[0])

            # get the Available quantity
            available_qty_index = self.header_display_columns.index('Qty Available')
            available_qty = float(item_values[available_qty_index])

            # get the Price
            price_index = self.header_display_columns.index('Price')
            price_qty = float(item_values[price_index])

            # get the Purchased Price (internal use only)
            # purchased_price_index = self.header_display_columns.index('Purchased Price')
            purchased_price = self.df_available_product.loc[self.df_available_product['Barcode'] == barcode, 'Purchased Price'].values[0]

            if not self.is_barcode_in_cart(barcode):
                quantity = self.prompt_quantity()
                if quantity is not None and quantity <= available_qty:
                    if quantity > 0:
                        subtotal = '{:.2f}'.format(quantity * price_qty)
                        item_values_with_quantity = list(item_values)
                        item_values_with_quantity.extend([quantity, subtotal, purchased_price])
                        self.table_cart.insert('', 'end', values=item_values_with_quantity)
                        self.cart_data.append(item_values_with_quantity)
                        self.update_subtotal()
                elif quantity is not None and quantity > available_qty:
                    self.show_message_box("Not enough items available.")
                elif quantity is None:
                    self.show_message_box("Invalid quantity input.")
                    
        self.pay_button.configure(state="enable")
        self.search_entry.delete(0, tk.END)
        self.search_entry.focus_set()

    def prompt_quantity(self):
        input_dialog = CTkInputDialog(title="Enter Quantity", text="Please enter the quantity:")
        quantity = input_dialog.get_input()
        try:
            quantity = float(quantity)
            if quantity > 0:
                return quantity
        except (ValueError, TypeError):
            pass
        return None

    def show_message_box(self, message):
        messagebox.showinfo("Message", message)
        
    def show_message_box_yesno(self, message):
        msg_box = messagebox.askquestion(
                    "Warning",
                    message,
                    icon="warning",
                    )
        return(msg_box)

    def delete_items(self, event):
        selected_items = self.table_cart.selection()
        for i in selected_items:
            item_values = self.table_cart.item(i)['values']
            barcode = item_values[0]
            self.cart_data = [item for item in self.cart_data if item[0] != barcode]
            self.table_cart.delete(i)
        self.update_subtotal()

    def is_barcode_in_cart(self, barcode):
        for item in self.cart_data:
            if item[0] == barcode:
                return True
        return False

    def setup_table_cart(self):
        self.cart_data = []
        self.cart_data_header = self.header_display_columns + ["Order Qty", "Sub Total"]
        cart_data_header_tuple = tuple(self.cart_data_header)

        cart_label = CTkLabel(master=self.main_view, text="Cart:")
        cart_label.pack(side="top", anchor='nw', pady=(10,0), padx=27)

        cart_container = CTkFrame(master=self.main_view, height=50, fg_color="#F0F0F0")
        cart_container.pack(fill="x", pady=(0, 0), padx=27)

        self.table_cart = ttk.Treeview(cart_container, columns=cart_data_header_tuple, show='headings')
        for col in cart_data_header_tuple:
            if col != "Purchased Price":
                self.table_cart.heading(col, text=col, anchor='center')
                self.table_cart.column(col, anchor='center')
        self.table_cart.pack(fill='both', expand=True)

        self.table_cart.bind('<Delete>', self.delete_items)

        total_units_label = CTkLabel(master=self.main_view, text="Total Units: ")
        total_units_label.pack(side="top", anchor='ne', pady=(2,10), padx=27)
        self.total_units_label = total_units_label

    def search_product(self, event=None):
        query = self.search_entry.get().strip().lower()
        result_count = 0

        # Clear the current rows in the table
        for row in self.table_available_product.get_children():
            self.table_available_product.delete(row)

        if query:
            for row in self.list_available_product:
                if any(query in str(cell).lower() for cell in row):
                    self.table_available_product.insert('', 'end', values=row)
                    result_count += 1
        else:
            for row in self.list_available_product:
                self.table_available_product.insert('', 'end', values=row)
                result_count += 1

        if result_count == 1:
            first_item = self.table_available_product.get_children()[0]
            self.table_available_product.selection_set(first_item)
            self.table_available_product.focus(first_item)
            self.table_available_product.focus_set()
            self.item_select(event=None)

    def setup_subtotal(self):
        due_container = CTkFrame(master=self.main_view, height=50, fg_color="#d3d3d3")
        due_container.pack(fill="x", pady=(2, 0), padx=27)

        self.due_label = CTkLabel(master=due_container, text="Amount Due: 0.00", font=(None, 32))
        self.due_label.pack(side="right", pady=15, padx=20)
        
    def update_subtotal(self):
        total = 0.00
        total_units = 0

        for child in self.table_cart.get_children():
            item = self.table_cart.item(child)['values']
            total += float(item[-2])  # Use -2 instead of -1 because 'Purchased Price' is hidden
            total_units += float(item[-3])

        self.due_label.configure(text="Amount Due: {:.2f}".format(total))
        self.total_units_label.configure(text="Total Units: {:.0f}".format(total_units))
        
        if self.cash_received > 0:
            self.amount_due = total
            change = self.update_change()
            
            if change < 0:
                self.submit_button.configure(state="disabled")
            
    def update_change(self):
        self.change = self.cash_received - self.amount_due
        self.change_label.configure(text="Change: {:.2f}".format(self.change))
        
        return self.change

    def clear_cart(self):
        self.search_entry.delete(0, tk.END)
        if self.isSubmitted == True:
              self.isClear = True
        elif self.isSubmitted == False and self.isClear:
            response = self.show_message_box_yesno("Are you sure you want to clear the data? You haven't submitted the payment yet.")
            if response == "yes":
                self.isClear = True
            else:
                self.isClear = False
        
        if self.isClear:
                self.cart_data.clear()
                for item in self.table_cart.get_children():
                    self.table_cart.delete(item)
                self.update_subtotal()
                
                self.change_label.configure(text="")
                self.cash_received_label.configure(text="")
                self.pay_button.configure(state="disabled")
                self.submit_button.configure(state="disabled")
                self.isClear = False
                self.isSubmitted = None
                
                self.change = 0
                self.cash_received = 0
                self.amount_due = 0

    def setup_change_cash_label(self):
        self.cash_received_label = CTkLabel(master=self.main_view, text="", font=(None, 24))
        self.cash_received_label.pack(side="left", anchor='ne', pady=(16,0), padx=27)
        
        self.change_label = CTkLabel(master=self.main_view, text="", font=(None, 24))
        self.change_label.pack(side="left", anchor='ne', pady=(16,0), padx=27)
        
    def setup_clear_button(self):
        self.clear_button = CTkButton(master=self.main_view, text="Clear (ESC)", fg_color="#FF0000", font=(None, 14), hover_color="#D70000", anchor="w", text_color='black', command=self.setup_clear_cart)
        self.clear_button.pack(side="right", anchor="ne", ipady=5, pady=(16, 0), padx=(0, 15))  
        self.clear_button.bind("<Escape>", self.clear_cart)

    def enter_cash_button(self):
        self.pay_button = CTkButton(master=self.main_view, state="disabled", text="Enter Cash (F1)", fg_color="#1e8beb", font=(None, 14), hover_color="#0467bf", anchor="w", text_color='black', command=self.enter_cash)
        self.pay_button.pack(side="right", anchor="ne", ipady=5, pady=(16, 0), padx=(0, 15))

    def setup_submit_button(self):
        self.submit_button = CTkButton(master=self.main_view, state="disabled", text="Submit (F2)", fg_color="#00FF00", font=(None, 14), hover_color="#00D700", text_color='black', command=self.submit)
        self.submit_button.pack(side="right", anchor="ne", ipady=5, pady=(16, 0), padx=(0, 25))
        
    def setup_clear_cart(self):
        self.isClear = True
        self.clear_cart()

    def update_inventory(self):
        sold_items = []
        for item in self.cart_data:
            order_qty_index = self.cart_data_header.index('Order Qty')
            barcode = str(item[0])
            order_qty = item[order_qty_index]
            self.df_available_product.loc[self.df_available_product['Barcode'] == barcode, 'Qty Available'] -= order_qty
            
            # Add date and Transaction ID
            item.extend([self.amount_due, self.change, self.cash_received, datetime.now(), str(int(time.time()))])
            print(item)
            sold_items.append(item)

        print(self.df_available_product)

        self.df_available_product.to_csv(self.available_product, index=False)

        print(sold_items)

        sold_items_file = "sold_items.csv"
        sold_items_header = self.cart_data_header + ["Purchased Price","Amount Due", "Change", "Cash Received", "Date", "Transaction Id"]
        print(sold_items_header)
        
        df_sold_items = pd.DataFrame(sold_items, columns=sold_items_header)

        with open(sold_items_file, 'a', newline='') as f:
            df_sold_items.to_csv(f, header=False, index=False, mode='a')
            
        self.refresh_table_available_product()  # Refresh available products table

    def refresh_table_available_product(self):
        for item in self.table_available_product.get_children():
            self.table_available_product.delete(item)

        self.load_available_product()
        for row in self.list_available_product:
            self.table_available_product.insert('', 'end', values=row)

    def submit(self):
        if self.submit_button.cget('state') == 'enable':
            try:
                self.update_inventory()
                self.isClear = True
                self.pay_button.configure(state="disabled")
                self.submit_button.configure(state="disabled")
                self.show_message_box(f"Payment Successful! Database has been updated")
            except (ValueError, TypeError) as e:
                print(f"An error occurred: {e}")
                self.show_message_box("Invalid payment.")
                
            self.isSubmitted = True
            self.change = 0
            self.cash_received = 0
            self.amount_due = 0
            
            self.search_entry.focus_set()
    
    def enter_cash(self):
        if self.pay_button.cget('state') == 'enable':
            pay_dialog = CTkInputDialog(title="Enter Payment Amount", text="Enter payment amount:")
            self.cash_received = pay_dialog.get_input()
            try:
                self.cash_received = float(self.cash_received)
                self.amount_due = float(self.due_label.cget("text").replace("Amount Due: ", ""))
                if self.cash_received >= self.amount_due:
                    self.update_change()
                    self.cash_received_label.configure(text="Cash Received: {:.2f}".format(self.cash_received))
                    self.submit_button.configure(state="enable")
                    self.isSubmitted = False
                else:
                    self.show_message_box("Insufficient payment amount.")
            except (ValueError, TypeError) as e:
                print(f"An error occurred: {e}")
                self.show_message_box("Invalid payment amount.")
                self.cash_received = 0
        
class InventoryPage(CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.setup_inventory_view()
        self.load_inventory_data()
        self.setup_search_bar()
        self.setup_inventory_table()
        self.setup_edit_controls()
        self.refresh_inventory_table()
    
    def setup_inventory_view(self):
        self.main_view = CTkFrame(master=self, fg_color="#fff", width=680, height=650, corner_radius=0)
        self.main_view.pack_propagate(0)
        self.main_view.pack(side="left", expand=True, fill="both")
        
    def load_inventory_data(self):
        self.inventory_file = "inventory.csv" 
        try:
            self.df_inventory = pd.read_csv(self.inventory_file)
            self.df_inventory['Barcode'] = self.df_inventory['Barcode'].astype(str).str.replace('\.0$', '', regex=True)
            self.header_inventory_columns = list(self.df_inventory.columns)
            self.list_inventory = self.df_inventory.values.tolist()
        except FileNotFoundError:
            self.df_inventory = pd.DataFrame()
            self.list_inventory = []
            self.header_inventory_columns = []

    def setup_search_bar(self):
        
        search_container = CTkFrame(master=self.main_view, height=50, fg_color="#F0F0F0")
        search_container.pack(fill="x", pady=(25, 0), padx=27)
        
        search_label = CTkLabel(master=search_container, text="Search: ").pack(side="left", padx=(13, 0), pady=10)
        self.search_entry = CTkEntry(master=search_container, width=305, placeholder_text="Enter Barcode or Product Name", border_color="#2A8C55", border_width=2)
        self.search_entry.pack(side="left", padx=(13, 0), pady=15)
        self.search_entry.bind("<KeyRelease>", self.search_product)

    def search_product(self, event=None):
        query = self.search_entry.get().strip().lower()
        result_count = 0

        # Clear the current rows in the table
        for row in self.table_inventory.get_children():
            self.table_inventory.delete(row)

        if query:
            for row in self.list_inventory:
                if any(query in str(cell).lower() for cell in row):
                    self.table_inventory.insert('', 'end', values=row)
                    result_count += 1
        else:
            for row in self.list_inventory:
                self.table_inventory.insert('', 'end', values=row)
                result_count += 1

    def setup_inventory_table(self):
        inventory_label = CTkLabel(master=self.main_view, text="Inventory:")
        inventory_label.pack(side="top", anchor='nw', pady=(10,0), padx=27)

        inventory_container = CTkFrame(master=self.main_view, height=50, fg_color="black")
        inventory_container.pack(fill="x", pady=(0, 0), padx=27)

        treestyle = ttk.Style()
        treestyle.theme_use('clam')
        treestyle.configure("Treeview", background="white", foreground='black', fieldbackground='white', borderwidth=0, font=("Arial", 12), width=150)
        treestyle.configure("Treeview.Heading", anchor="center", font=("Arial", 14))

        self.table_inventory = ttk.Treeview(inventory_container, columns=self.header_inventory_columns, show='headings')
        for col in self.header_inventory_columns:
            self.table_inventory.heading(col, text=col, anchor='center')
        self.table_inventory.pack(fill='both', expand=True)

        for row in self.list_inventory:
            self.table_inventory.insert('', 'end', values=row)

        for col in self.table_inventory["columns"]:
            self.table_inventory.column(col, anchor='center')

        self.table_inventory.bind('<<TreeviewSelect>>', self.select_item)

    def setup_edit_controls(self):
        edit_container = CTkFrame(master=self.main_view, fg_color="#F0F0F0")
        edit_container.pack(fill="x", pady=(10, 0), padx=27)

        self.entry_vars = {}
        for col in self.header_inventory_columns:
            label = CTkLabel(master=edit_container, text=col)
            label.pack(side="top", anchor="w", padx=5)
            var = tk.StringVar()
            self.entry_vars[col] = var
            entry = CTkEntry(master=edit_container, textvariable=var, width=400, border_color="#2A8C55", border_width=2)
            entry.pack(side="top", anchor="w", padx=5, pady=(0,15))
            
        self.save_button = CTkButton(master=edit_container, text="Save", fg_color="#00FF00", font=(None, 14), hover_color="#00D700", text_color='black', command=self.save_item)
        self.save_button.pack(side="top", padx=10, pady=10)
        
    def select_item(self, event):
        selected_item = self.table_inventory.selection()
        if selected_item:
            item_values = self.table_inventory.item(selected_item[0])['values']
            for col, value in zip(self.header_inventory_columns, item_values):
                self.entry_vars[col].set(value)
            self.selected_item = selected_item[0]
            
        
    def save_item(self):
        new_values = [self.entry_vars[col].get() for col in self.header_inventory_columns]
        new_barcode = new_values[0]

        if hasattr(self, 'selected_item') and not(self.selected_item == None):
            # This part handles updating existing items
            old_barcode = str(self.table_inventory.item(self.selected_item)['values'][0])

            # Check if the new barcode is unique, considering it might be the same as the old one
            if new_barcode != old_barcode and new_barcode in self.df_inventory['Barcode'].values:
                messagebox.showerror("Error", "The new barcode already exists. Please ensure the barcode is unique.")
                return  # Exit the function without saving

            # Identify the changes
            try:
                old_values = self.df_inventory.loc[self.df_inventory['Barcode'] == old_barcode].values[0]
                print(old_values)
            except IndexError:
                messagebox.showerror("Error", "The original barcode was not found in the inventory.")
                return

            changes = []
            for old_value, new_value, col in zip(old_values, new_values, self.header_inventory_columns):
                if str(old_value) != str(new_value):
                    changes.append(f"{col}: {old_value} -> {new_value}")

            if changes:
                changes_message = "\n".join(changes)
                confirmation_message = f"Are you sure you want to make the following changes?\n\n{changes_message}"
                if messagebox.askyesno("Confirm Changes", confirmation_message):
                    # Update the DataFrame
                    self.df_inventory.loc[self.df_inventory['Barcode'] == old_barcode] = new_values

                    # If the barcode was changed, ensure the DataFrame reflects this
                    if new_barcode != old_barcode:
                        self.df_inventory['Barcode'] = self.df_inventory['Barcode'].replace(old_barcode, new_barcode)

                    # Save the changes
                    self.df_inventory.to_csv(self.inventory_file, index=False)
                    self.refresh_inventory_table()
                    messagebox.showinfo("Success", "Inventory has been updated successfully.")
        else:
            # This part handles adding new items
            if new_barcode in self.df_inventory['Barcode'].values:
                messagebox.showerror("Error", "The barcode already exists. Please ensure the barcode is unique.")
                return  # Exit the function without saving

            new_row = pd.DataFrame([new_values], columns=self.header_inventory_columns)
            self.df_inventory = pd.concat([self.df_inventory, new_row], ignore_index=True)

            # Save the new item
            self.df_inventory.to_csv(self.inventory_file, index=False)
            self.refresh_inventory_table()
            messagebox.showinfo("Success", "New item has been added successfully.")

        # Clear entry inputs after saving
        for col in self.header_inventory_columns:
            self.entry_vars[col].set("")
        
        # Clear selection after saving
        self.table_inventory.selection_remove(self.table_inventory.selection())
        self.selected_item = None
        print(self.selected_item)

    def refresh_inventory_table(self):
        for item in self.table_inventory.get_children():
            self.table_inventory.delete(item)

        self.load_inventory_data()
        for row in self.list_inventory:
            self.table_inventory.insert('', 'end', values=row)

class UpdatePage(CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        self.SPREADSHEET_ID = "1t11jiTUTbk4Iid9FY-4TotmjuB2rnZ-E6y2mA6m9Qjc"
        self.TOKEN_PATH = "credentials/token.json"
        self.CREDENTIALS_PATH = "credentials/credentials.json"
        self.LAST_UPDATE_PATH = "last_update.txt"
        self.SOLD_ITEMS_PATH = "sold_items.csv"
        self.setup_update_view()

    def setup_update_view(self):
        self.main_view = CTkFrame(master=self, fg_color="#fff", width=680, height=650, corner_radius=0)
        self.main_view.pack_propagate(0)
        self.main_view.pack(side="left", expand=True, fill="both")

        update_button = CTkButton(master=self.main_view, text="Update Google Sheets", fg_color="#2A8C55", font=(None, 14), hover_color="#1A6B42", text_color="#fff", command=self.update_google_sheets)
        update_button.pack(side="top", padx=20, pady=20)

        last_update_time = self.read_last_update_time()
        self.last_update_label = CTkLabel(master=self.main_view, text=f"Last Update: {last_update_time}", font=(None, 12))
        self.last_update_label.pack(side="top", padx=20, pady=10)

    def read_last_update_time(self):
        if os.path.exists(self.LAST_UPDATE_PATH):
            with open(self.LAST_UPDATE_PATH, 'r') as file:
                return file.read().strip()
        return "Never"

    def write_last_update_time(self, last_update_time):
        with open(self.LAST_UPDATE_PATH, 'w') as file:
            file.write(last_update_time)

    def clear_sold_items(self):
        if os.path.exists(self.SOLD_ITEMS_PATH):
            with open(self.SOLD_ITEMS_PATH, 'r') as file:
                headers = file.readline()
            with open(self.SOLD_ITEMS_PATH, 'w') as file:
                file.write(headers)

    def update_google_sheets(self):
        try:
            # Authenticate and get the Sheets API service
            service = self.authenticate(self.SCOPES, self.TOKEN_PATH, self.CREDENTIALS_PATH)

            # Update inventory data (replace)
            inventory_data = pd.read_csv("inventory.csv")
            inventory_data = self.clean_data(inventory_data)
            self.write_to_google_sheets(service, inventory_data, self.SPREADSHEET_ID, "Inventory", replace=True)

            # Update sold items data (append)
            sold_items_data = pd.read_csv(self.SOLD_ITEMS_PATH)
            sold_items_data = self.clean_data(sold_items_data)
            self.write_to_google_sheets(service, sold_items_data, self.SPREADSHEET_ID, "Sold Items", replace=False)

            # Clear sold items file after update
            self.clear_sold_items()

            # Update the last update time
            last_update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.last_update_label.configure(text=f"Last Update: {last_update_time}")
            self.write_last_update_time(last_update_time)

            messagebox.showinfo("Success", "Google Sheets have been updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update Google Sheets: {e}")

    def clean_data(self, df):
        # Drop any rows with missing data
        df = df.dropna()

        # Convert all data to strings to avoid type issues
        df = df.astype(str)

        # Reset index to ensure a clean DataFrame
        df.reset_index(drop=True, inplace=True)

        return df

    def write_to_google_sheets(self, service, df, spreadsheet_id, sheet_name, replace):
        try:
            # Convert DataFrame to list of lists
            data_list = df.values.tolist()

            if replace:
                # Prepare the data for replacing without headers
                body = {
                    'values': data_list
                }
                range_name = f"{sheet_name}!A2"  # Assumes headers are already in the first row
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption="RAW",
                    body=body
                ).execute()
            else:
                # Get the current data in the sheet to determine the next available row
                result = service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range=sheet_name
                ).execute()
                existing_data = result.get('values', [])
                next_row = len(existing_data) + 1

                # Prepare the data for appending without headers
                body = {
                    'values': data_list
                }
                range_name = f"{sheet_name}!A{next_row}"
                service.spreadsheets().values().append(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption="RAW",
                    body=body
                ).execute()
        except HttpError as error:
            raise Exception(f"An error occurred while updating the sheet: {error}")

    def authenticate(self, scopes, token_path, credentials_path):
        credentials = self.load_credentials(token_path, scopes)
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
                credentials = flow.run_local_server(port=0)
            self.save_credentials(credentials, token_path)
        return build('sheets', 'v4', credentials=credentials)

    def load_credentials(self, token_path, scopes):
        credentials = None
        if os.path.exists(token_path):
            credentials = Credentials.from_authorized_user_file(token_path, scopes)
        return credentials

    def save_credentials(self, credentials, token_path):
        with open(token_path, "w") as token:
            token.write(credentials.to_json())

if __name__ == "__main__":
    app = Application()
    app.mainloop()
