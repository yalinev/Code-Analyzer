import tkinter as tk # import Tkinter for gui 
from tkinter import messagebox, simpledialog # msgbox and popups 
import json
from storage import save_password, get_password, delete_password, get_all_services

# Store PIN in a file
PIN_FILE = "pin.json"

# Retrieves stored pin, or ask to create new one 
def get_stored_pin():
    try: # handle error 
        with open(PIN_FILE, "r") as file: # open w/ read 
            # return pin, or none if empty 
            return json.load(file).get("pin", None)
    except (FileNotFoundError, json.JSONDecodeError):
        return None # if file DNE

# To set up a new 4 digit pin 
def set_new_pin():
    # popup simpleddialog.askstring(title,prompt, show="*") --> Shows password as *** etc 
    new_pin = simpledialog.askstring("Set PIN", "Enter a new 4-digit PIN:", show="*")

    # if valid pin (4 digits and nums)
    if new_pin and len(new_pin) == 4 and new_pin.isdigit():
        with open(PIN_FILE, "w") as file: 
            json.dump({"pin": new_pin}, file) # save pin in json file 
        messagebox.showinfo("Success", "Your PIN is set!")
        return new_pin
    else: # if invalid pin 
        messagebox.showwarning("Error", "PIN must be 4 digit numbers!")
        return None

# Ask for pin on start up or else close 
def verify_pin():
    # get the stored pin from func above 
    stored_pin = get_stored_pin()
    
    if stored_pin is None:
        # force user to enter pin :) 
        stored_pin = set_new_pin() 
        if stored_pin is None:
            return False  # Exit if PIN wasn't set

    attempts = 3  # Allow 3 attempts
    while attempts > 0:
        pin = simpledialog.askstring(" Enter PIN", "Enter your 4-digit PIN:", show="*")
        if pin == stored_pin:
            return True
        else:
            attempts -= 1 # minus num of attempts 
            messagebox.showerror("Error", "Incorrect PIN! " + str(attempts) + " attempts left.")

    # if attempts exceed 3, force quit it 
    messagebox.showerror("Access Denied", "Too many wrong attempts! >:(")
    root.destroy()  # Close the app
    return False

# create main window (initially hidden)
root = tk.Tk()
root.configure(bg="azure2")
root.withdraw()  # Hide until PIN is verified
root.title(" Welcome to Your Password Manager")
root.geometry("600x600")
root.resizable(False, False)

# Add grid configuration for centering
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Verify PIN before showing anything
if not verify_pin(): # call function to check 
    exit()

# to unhide the window if pin is correct 
root.deiconify()  

# Labels, align left of cell w/ stick="w"
tk.Label(root, text="Website/Service:", bg="azure2").grid(row=0, column=0, padx=15, pady=8, sticky="w") 
tk.Label(root, text="Username/Gmail:", bg="azure2").grid(row=1, column=0, padx=15, pady=8, sticky="w")  
tk.Label(root, text="Password:", bg="azure2").grid(row=2, column=0, padx=15, pady=8, sticky="w")  

# Enter fields 
service_entry = tk.Entry(root, width=40)
service_entry.grid(row=0, column=1, padx=15, pady=8)

username_entry = tk.Entry(root, width=40)
username_entry.grid(row=1, column=1, padx=15, pady=8)

password_entry = tk.Entry(root, width=40, show="*")  # Hide password input
password_entry.grid(row=2, column=1, padx=15, pady=8)

# Label for saved services list
tk.Label(root, text="Saved Passwords:", bg="azure2").grid(row=3, column=0, columnspan=2, pady=5, sticky="n")

# Listbox for stored passwords 
service_listbox = tk.Listbox(root, height=8, width=55)
service_listbox.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

# Label for retrieved password
password_label = tk.Label(root, text="Retrieved Password:", bg="azure2", fg="blue")
password_label.grid(row=5, column=0, columnspan=2, pady=5)
password_label.grid_remove()  # Hide initially

# Text area for retrieved passwords
result_text = tk.Text(root, height=4, width=50)
result_text.grid(row=6, column=0, columnspan=2, padx=10, pady=5)
result_text.grid_remove()  # Hide initially

# To update the list of passwords 
def update_service_list():
    service_listbox.delete(0, tk.END)
    services = get_all_services()
    for service in services:
        service_listbox.insert(tk.END, service)

# to save password into json file 
def save():
    # get user input from input fields 
    service = service_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    # check if any field is empty 
    if not service or not username or not password:
        messagebox.showwarning("Warning", "All fields must be filled!")
        return
    
    # save password using storage module function
    save_password(service, username, password)
    messagebox.showinfo("Success", f"Password for {service} saved!")
    
    # Reset the filed after saving, from first char to end 
    service_entry.delete(0, tk.END)
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)

    # add it to the list 
    update_service_list()

# retrieve the stored password 
def retrieve():
    # get current selected from list 
    selected_service = service_listbox.get(tk.ACTIVE)

    # if nothing selected, give warning 
    if not selected_service:
        messagebox.showwarning("Warning", "Select a service from the list!")
        return

    # else get the password and username for the selected 
    result = get_password(selected_service)
    if result:
        username = result["username"]
        password = result["password"]

        # clear previous text in result display 
        result_text.delete("1.0", tk.END)

        # put username n password into textbox
        result_text.insert("1.0", f"Username: {username}\nPassword: {password}")
        
        # Show password section
        password_label.grid()
        result_text.grid()
    else: # if no service found just clear and display erorr 
        result_text.delete("1.0", tk.END) # first char of first line
        result_text.insert("1.0", "Service not found.")

# function to delete the password 
def delete():
    # get the selected one to delete 
    selected_service = service_listbox.get(tk.ACTIVE)

    if not selected_service:
        messagebox.showwarning("Warning", "Select a service from the list!")
        return
    
    # use library function to delete 
    delete_password(selected_service)
    messagebox.showinfo("Success", f"Deleted password for {selected_service}!")

    # call la function to update 
    update_service_list()

    # remove displayed username/password from result area 
    result_text.delete("1.0", tk.END)
    password_label.grid_remove() # hides the grid 
    result_text.grid_remove() # hides the textbox 

# to change the stored pin 
def change_pin():
    new_pin = set_new_pin()
    if new_pin:
        messagebox.showinfo("Success", "PIN updated successfully!")

# Buttons
tk.Button(root, text="Save Password", command=save, bg="azure3").grid(row=7, column=0, columnspan=2, pady=8, sticky="ew", padx=150)
tk.Button(root, text="Retrieve Password", command=retrieve, bg="azure3").grid(row=8, column=0, columnspan=2, pady=8, sticky="ew", padx=150)
tk.Button(root, text="Delete Password", command=delete, bg="azure3").grid(row=9, column=0, columnspan=2, pady=8, sticky="ew", padx=150)
tk.Button(root, text="Change PIN", command=change_pin, bg="azure3").grid(row=10, column=0, columnspan=2, pady=8, sticky="ew", padx=150)

# Load services on startup
update_service_list()

# Run the app
root.mainloop()