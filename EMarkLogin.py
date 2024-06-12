# main.py

import streamlit as st
import sqlite3
import subprocess
                                                                                                                                                                        
# Create a SQLite database connection
with sqlite3.connect('mydatabase.db') as conn:
    cursor = conn.cursor()

# Define the table name
table_name = "logindetails"

try:
    # Create a table to store user details
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    ''')
    conn.commit()
except sqlite3.Error as e:
    # Handle the 'Table already exists' error
    if "already exists" in str(e):
        st.warning(f"Table '{table_name}' already exists.")
    else:
        st.error(f"SQLite Error: {e}")

def signup(username, password):
    cursor.execute(f"INSERT INTO {table_name} (username, password) VALUES (?, ?)", (username, password))
    conn.commit()

def login(username, password):
    cursor.execute(f"SELECT username, password FROM {table_name} WHERE username=?", (username,))
    user_data = cursor.fetchone()

    if user_data and user_data[0] == username and user_data[1] == password:
        return True
    else:
        return False

def run_exam_evaluator():
    subprocess.run(["streamlit", "run", "EMark.py"])

def main():
    st.title("Login/Signup Page")

    # Display login/signup page
    page = st.sidebar.radio("Select Page", ["Login", "Signup"])

    if page == "Signup":
        st.header("Signup")
        new_username = st.text_input("Username:")
        new_password = st.text_input("Password:", type="password")

        if st.button("Signup"):
            signup(new_username, new_password)
            st.success("Signup successful. Please go to the login page to login.")
    
    elif page == "Login":
        st.header("Login")
        username = st.text_input("Username:")
        password = st.text_input("Password:", type="password")

        if st.button("Login"):
            if login(username, password):
                st.success(f"Welcome, {username}!")

                # Continue with the rest of your app after successful login
                st.write("Redirecting to another page...")
                
                # Add the redirection logic here
                st.experimental_set_query_params(page="AnotherPage")
                run_exam_evaluator()  # Redirect to Another Page
            else:
                st.error("Failed to login. Please check your username and password.")

if __name__ == "__main__":
    main()
