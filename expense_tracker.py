import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import base64
from fpdf import FPDF
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from users import init_users, create_user, authenticate
from local_storage import save_local_data, load_local_data, init_local_storage
import plotly.graph_objects as go

# Helper functions
def get_transaction_types():
    return ["Expense", "Additional Income"]

def get_category_options():
    return {
        "Food": "🍔 Food",
        "Transportation": "🚗 Transportation",
        "Rent": "🏠 Rent",
        "Bills": "💡 Bills",
        "Entertainment": "🎮 Entertainment",
        "Shopping": "🛍️ Shopping",
        "Healthcare": "🏥 Healthcare",
        "Education": "📚 Education",
        "Salary": "💰 Salary",
        "Other": "📦 Other"
    }

# Page configuration
st.set_page_config(
    page_title="Income & Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# Custom CSS for better appearance
st.markdown("""
    <style>
    /* Main container and general styling */
    .main {
        padding: 1rem;
        max-width: 1200px;
        margin: 0 auto;
    }

    .stApp {
        background:rgb(17, 18, 18);
    }

    /* Container styling */
    .element-container, 
    .stTextInput, 
    .stNumberInput, 
    .stDateInput, 
    .stSelectbox,
    [data-testid="stForm"] {
        width: 100% !important;
        padding: 0 !important;
        margin: 0 0 1rem 0 !important;
    }

    /* Input fields styling */
    .stTextInput>div>div>input, 
    .stNumberInput>div>div>input,
    .stDateInput>div>div>input,
    .stSelectbox>div>div>div {
        width: 100% !important;
        background-color: #ffffff !important;
        color: #2c3e50 !important;
        border-radius: 10px !important;
        padding: 0.5rem 1rem !important;
        border: 2px solid #e0e0e0 !important;
        box-sizing: border-box !important;
    }

    /* Gradient header containers */
    div[data-testid="stHeader"],
    div.gradient-header {
        width: 100% !important;
        box-sizing: border-box !important;
        margin: 0 0 1.5rem 0 !important;
        padding: 1rem !important;
        background: linear-gradient(135deg, #1f77b4, #2c3e50) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    /* Card containers */
    .card-container {
        background: white !important;
        border-radius: 15px !important;
        padding: 1.5rem !important;
        margin-bottom: 1.5rem !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        width: 100% !important;
        box-sizing: border-box !important;
        overflow: hidden !important;
    }

    /* Sidebar styling */
    .css-1d391kg, .css-12oz5g7 {
        background: white !important;
        padding: 2rem 1rem !important;
        width: 100% !important;
    }

    /* Grid layout for metrics */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    .metric-label {
        color: #1f77b4;
        font-size: 1rem;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    .income-value { color: #2ecc71; }
    .expense-value { color: #e74c3c; }
    .balance-value { color: #3498db; }
    .savings-value { color: #9b59b6; }

    /* Responsive adjustments */
    @media screen and (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }
        
        .metrics-grid {
            grid-template-columns: repeat(2, 1fr) !important;
        }

        .stTextInput>div>div>input, 
        .stNumberInput>div>div>input,
        .stDateInput>div>div>input,
        .stSelectbox>div>div>div,
        .stRadio>div,
        .stButton>button,
        p, h1, h2, h3, h4, h5, h6,
        div[data-testid="stMarkdownContainer"] p,
         .metric-label,
        .metric-value,
        .stTab > div > div > div > div,
        .stTab [data-testid="stMarkdownContainer"],
        .stInfo > div,
        .stSuccess > div {
            color: #2c3e50 !important;
            font-weight: normal !important;
            background-color: transparent !important;
        }
        
        /* Override dark mode text color */
        .stApp {
            color: #2c3e50 !important;
        }
        
        /* Make metric cards stand out more */
        .metric-card {
            background: white !important;
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
        }
        
        /* Fix for radio buttons */
        .stRadio > div {
            background-color: white !important;
            border-radius: 5px !important;
            padding: 10px !important;
        }
        
        /* Fix for radio button labels */
        .stRadio label {
            color: #2c3e50 !important;
            font-weight: normal !important;
        }
        
        /* Make card backgrounds white for contrast */
        div.element-container {
            background-color: white !important;
            border-radius: 10px !important;
            padding: 10px !important;
            margin-bottom: 10px !important;
        }
        
        /* Fix inputs */
        input, textarea, select {
            color: #2c3e50 !important;
            background-color: white !important;
        }
    }

    /* Fix for overlapping elements */
    .stHorizontalBlock {
        width: 100% !important;
        box-sizing: border-box !important;
        padding: 0 !important;
    }

    .row-widget {
        width: 100% !important;
        box-sizing: border-box !important;
    }

    /* Select box styling */
    .stSelectbox > div > div:first-child {
        background-color: white;
        border: 1px solid #ccc;
        border-radius: 4px;
        padding: 4px;
    }

    /* SelectBox Selected Value */
    .stSelectbox > div > div:first-child > div {
        color: #2c3e50;
        font-weight: normal;
        font-size: 14px;
    }

    /* SelectBox Dropdown */
    .stSelectbox > div > div:last-child {
        background-color: white;
        border: 1px solid #ccc;
        border-radius: 4px;
    }

    /* SelectBox Options */
    .stSelectbox > div > div:last-child > div > div {
        color: #2c3e50;
        font-size: 14px;
    }

    /* SelectBox Hover State */
    .stSelectbox > div > div:first-child:hover {
        border-color: #1f77b4;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        color: #2c3e50 !important;
        background-color: white !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    /* Dark mode adjustments */
    @media (prefers-color-scheme: dark) {
        .stSelectbox > div > div > div,
        .stSelectbox [data-baseweb="select"] > div,
        .stSelectbox [role="listbox"],
        .stSelectbox [role="option"],
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stDateInput > div > div > input {
            background-color: white !important;
            color: #2c3e50 !important;
        }
    }

    /* Base styling for select boxes */
    .stSelectbox [data-baseweb="select"] {
        background-color: white !important;
    }
    
    /* Selected value styling */
    .stSelectbox [data-baseweb="select"] span {
        color: #2c3e50 !important;
        font-size: 1rem !important;
        opacity: 1 !important;
    }
    
    /* Dropdown container styling */
    .stSelectbox [data-baseweb="popover"] {
        background-color: white !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 5px !important;
    }
    
    /* Dropdown options styling */
    .stSelectbox [data-baseweb="menu"] {
        background-color: white !important;
    }
    
    .stSelectbox [role="option"] {
        color: #2c3e50 !important;
    }
    
    .stSelectbox [role="option"]:hover {
        background-color: #f8f9fa !important;
    }
    
    /* Fix for select box container */
    .stSelectbox > div {
        background-color: white !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 5px !important;
    }
    
    /* Fix for placeholder and selected value */
    .stSelectbox [data-baseweb="select"] div {
        color: #2c3e50 !important;
        opacity: 1 !important;
    }
    
    /* Arrow icon color fix */
    .stSelectbox [data-baseweb="icon"] svg {
        fill: #2c3e50 !important;
    }
    
    /* Dark mode overrides */
    @media (prefers-color-scheme: dark) {
        .stSelectbox [data-baseweb="select"],
        .stSelectbox [data-baseweb="popover"],
        .stSelectbox [data-baseweb="menu"],
        .stSelectbox > div {
            background-color: white !important;
        }
        
        .stSelectbox [data-baseweb="select"] span,
        .stSelectbox [role="option"],
        .stSelectbox [data-baseweb="select"] div {
            color: #2c3e50 !important;
        }
    }

    /* Base select box styling */
    .stSelectbox {
        margin-bottom: 1rem;
    }
    
    .stSelectbox > div {
        background-color: white !important;
    }
    
    .stSelectbox > div > div {
        background-color: white !important;
        color: #2c3e50 !important;
    }
    
    /* Selected value styling */
    .stSelectbox [data-baseweb="select"] {
        background-color: white !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 4px !important;
        padding: 4px !important;
    }
    
    .stSelectbox [data-baseweb="select"] span {
        color: #2c3e50 !important;
        opacity: 1 !important;
    }
    
    /* Dropdown styling */
    .stSelectbox [role="listbox"] {
        background-color: white !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 4px !important;
    }
    
    .stSelectbox [role="option"] {
        color: #2c3e50 !important;
        background-color: white !important;
    }
    
    .stSelectbox [role="option"]:hover {
        background-color: #f8f9fa !important;
    }
    
    /* Label styling */
    .stSelectbox label {
        color: #2c3e50 !important;
        font-weight: 500 !important;
    }
    
    /* Dark mode overrides */
    @media (prefers-color-scheme: dark) {
        .stSelectbox [data-baseweb="select"],
        .stSelectbox [role="listbox"],
        .stSelectbox [role="option"] {
            background-color: white !important;
        }
        
        .stSelectbox [data-baseweb="select"] span,
        .stSelectbox [role="option"],
        .stSelectbox label {
            color: #2c3e50 !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Helper Functions
def set_category_budget(category, amount):
    st.session_state.budgets[category] = amount
    save_current_state()

def add_reminder(date, note, amount):
    st.session_state.reminders.append({
        'date': date.strftime("%Y-%m-%d"),
        'note': note,
        'amount': amount,
        'completed': False
    })
    save_current_state()

def add_savings_goal(name, target_amount, target_date):
    st.session_state.savings_goals.append({
        'name': name,
        'target_amount': target_amount,
        'target_date': target_date.strftime("%Y-%m-%d"),
        'current_amount': 0.0
    })
    save_current_state()

def calculate_monthly_trends(df):
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date'])
        # Create a month-year string for better grouping
        df['Month'] = df['Date'].dt.strftime('%Y-%m')
        # Group by month and type, then pivot
        monthly = df.groupby(['Month', 'Type'])['Amount'].sum().reset_index()
        # Convert to wide format
        monthly_wide = monthly.pivot(index='Month', columns='Type', values='Amount').fillna(0)
        # Ensure both columns exist
        if 'Expense' not in monthly_wide.columns:
            monthly_wide['Expense'] = 0
        if 'Additional Income' not in monthly_wide.columns:
            monthly_wide['Additional Income'] = 0
        return monthly_wide
    return pd.DataFrame(columns=['Expense', 'Additional Income'])

def get_category_analysis(df):
    if not df.empty:
        return df[df['Type'] == 'Expense'].groupby('Category')['Amount'].sum()
    return pd.Series()

def update_savings_goal(goal_name, amount):
    for goal in st.session_state.savings_goals:
        if goal['name'] == goal_name:
            goal['current_amount'] += amount
            save_current_state()
            return True
    return False

def delete_reminder(index):
    if 0 <= index < len(st.session_state.reminders):
        st.session_state.reminders.pop(index)
        save_current_state()
        return True
    return False

def mark_reminder_complete(index):
    if 0 <= index < len(st.session_state.reminders):
        st.session_state.reminders[index]['completed'] = True
        save_current_state()
        return True
    return False

# Initialize session state
if 'expenses' not in st.session_state:
    st.session_state.expenses = []
if 'income' not in st.session_state:
    st.session_state.income = 0
if 'reminders' not in st.session_state:
    st.session_state.reminders = []
if 'savings_goals' not in st.session_state:
    st.session_state.savings_goals = []
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'counter' not in st.session_state:
    st.session_state.counter = 0

# Initialize users config
init_users()

# Initialize local storage
init_local_storage()

def save_current_state():
    if 'username' in st.session_state:
        user_data = {
            "expenses": st.session_state.expenses,
            "income": st.session_state.income,
            "reminders": st.session_state.reminders,
            "savings_goals": st.session_state.savings_goals
        }
        save_local_data(st.session_state['username'], user_data)

def add_expense(date, category, amount, description, transaction_type):
    st.session_state.expenses.append({
        'Date': date.strftime("%Y-%m-%d"),
        'Category': category,
        'Amount': amount,
        'Description': description,
        'Type': transaction_type
    })
    save_current_state()

def get_csv_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="expense_report.csv">Download CSV Report</a>'
    return href

def create_pdf_report(df, total_income, total_expenses, remaining_balance):
    pdf = FPDF()
    pdf.add_page()
    
    # Calculate total savings
    total_savings = sum(goal['current_amount'] for goal in st.session_state.savings_goals)
    
    # Set font
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Financial Report', 0, 1, 'C')
    pdf.ln(10)
    
    # Add Summary Section
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Financial Summary', 0, 1, 'L')
    pdf.ln(5)
    
    # Summary details
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f'Total Income: Rs. {total_income:.2f}', 0, 1)
    pdf.cell(0, 8, f'Total Expenses: Rs. {total_expenses:.2f}', 0, 1)
    pdf.cell(0, 8, f'Balance: Rs. {remaining_balance:.2f}', 0, 1)
    pdf.cell(0, 8, f'Total Savings: Rs. {total_savings:.2f}', 0, 1)
    pdf.ln(10)
    
    # Add Savings Goals Section
    if st.session_state.savings_goals:
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Savings Goals', 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 12)
        for goal in st.session_state.savings_goals:
            progress = (goal['current_amount'] / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
            pdf.cell(0, 8, f"Goal: {goal['name']}", 0, 1)
            pdf.cell(0, 8, f"Target: Rs. {goal['target_amount']:.2f}", 0, 1)
            pdf.cell(0, 8, f"Saved: Rs. {goal['current_amount']:.2f}", 0, 1)
            pdf.cell(0, 8, f"Progress: {progress:.1f}%", 0, 1)
            pdf.cell(0, 8, f"Due Date: {goal['target_date']}", 0, 1)
            pdf.ln(5)
        pdf.ln(10)
    
    # Add Transaction History
    if not df.empty:
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Transaction History', 0, 1, 'L')
        pdf.ln(5)
        
        # Table header
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(30, 10, 'Date', 1)
        pdf.cell(30, 10, 'Type', 1)
        pdf.cell(40, 10, 'Category', 1)
        pdf.cell(50, 10, 'Amount', 1)
        pdf.cell(40, 10, 'Description', 1)
        pdf.ln()
        
        # Table content
        pdf.set_font('Arial', '', 12)
        for _, row in df.iterrows():
            pdf.cell(30, 10, str(row['Date']), 1)
            pdf.cell(30, 10, str(row['Type']), 1)
            pdf.cell(40, 10, str(row['Category']), 1)
            pdf.cell(50, 10, f"Rs. {row['Amount']:.2f}", 1)
            pdf.cell(40, 10, str(row['Description']), 1)
            pdf.ln()
    
    # Save the PDF
    pdf_path = "financial_report.pdf"
    pdf.output(pdf_path)
    return pdf_path

def delete_expense(index):
    del st.session_state.expenses[index]
    save_current_state()

def edit_expense(index, date, category, amount, description, transaction_type):
    st.session_state.expenses[index] = {
        'Date': date.strftime("%Y-%m-%d"),
        'Category': category,
        'Amount': amount,
        'Description': description,
        'Type': transaction_type
    }
    save_current_state()

def login_page():
    st.title("💰 Smart Money Manager")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 SignUp"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            if authenticate(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                # Load user's local data
                user_data = load_local_data(username)
                st.session_state.expenses = user_data["expenses"]
                st.session_state.income = user_data["income"]
                st.session_state.reminders = user_data["reminders"]
                st.session_state.savings_goals = user_data["savings_goals"]
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    with tab2:
        st.subheader("SignUp")
        new_username = st.text_input("Username", key="register_username")
        new_password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("SignUp"):
            if new_password != confirm_password:
                st.error("Passwords do not match!")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters long!")
            else:
                if create_user(new_username, new_password):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Username already exists!")

# Main app
if not st.session_state['logged_in']:
    login_page()
else:
    # Add logout button in sidebar
    with st.sidebar:
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()
    
    # Rest of your existing app code goes here...
    # (Keep all the existing code, just indent it one level)

    st.title("💰 Smart Money Manager")

    # Add margin after title
    st.markdown("<br>", unsafe_allow_html=True)

    # Sidebar with gradient background
    with st.sidebar:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #1f77b4, #2c3e50); 
                        padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                <h2 style="color: white; margin: 0;">Transaction Manager</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # Income Section
        st.subheader("💵 Update Income")
        new_income = st.number_input("Monthly Income", min_value=0.0, step=1000.0)
        if st.button("Update Income"):
            st.session_state.income = new_income
            save_current_state()
            st.success("✅ Income updated successfully!")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Expense Section
        st.subheader("💰 Add Transaction")
        date = st.date_input("Date", datetime.now())
        
        # Transaction Type Selection - Simplified
        transaction_type = st.radio(
            "Transaction Type",
            ["Expense", "Additional Income"],
            key="transaction_type_radio"
        )
        
        # Category Selection - Simplified
        category_list = [
            "🍔 Food",
            "🚗 Transportation",
            "🏠 Rent",
            "💡 Bills",
            "🎮 Entertainment",
            "🛍️ Shopping",
            "🏥 Healthcare",
            "📚 Education",
            "💰 Salary",
            "📦 Other"
        ]
        
        category = st.radio(
            "Category",
            category_list,
            key="category_radio"
        )
        
        # Remove emoji for storage
        category = category.split(" ")[1] if " " in category else category
        
        amount = st.number_input("Amount", min_value=0.0, step=1.0)
        description = st.text_input("Description")
        
        if st.button("Add Transaction"):
            add_expense(date, category, amount, description, transaction_type)
            st.success("✅ Transaction added successfully!")

    # Main content
    if st.session_state.expenses:
        df = pd.DataFrame(st.session_state.expenses)
        
        # Calculate totals
        expenses_df = df[df['Type'] == 'Expense']
        income_df = df[df['Type'] == 'Additional Income']
        total_expenses = expenses_df['Amount'].sum() if not expenses_df.empty else 0
        additional_income = income_df['Amount'].sum() if not income_df.empty else 0
        total_income = st.session_state.income + additional_income
        remaining_balance = total_income - total_expenses

        # Calculate total savings from all goals
        total_savings = sum(goal['current_amount'] for goal in st.session_state.savings_goals)

        # Update Financial Summary section
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1f77b4, #2c3e50); 
                        padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                <h2 style="color: white; margin: 0; text-align: center;">Financial Summary</h2>
            </div>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Total Income</div>
                    <div class="metric-value income-value">₹{total_income:.2f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Total Expenses</div>
                    <div class="metric-value expense-value">₹{total_expenses:.2f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Balance</div>
                    <div class="metric-value balance-value">₹{remaining_balance:.2f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Total Savings</div>
                    <div class="metric-value savings-value">₹{total_savings:.2f}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Add a section for quick savings update
        if st.session_state.savings_goals:
            st.markdown("""
                <div style="background: white;
                            padding: 1.5rem;
                            border-radius: 10px;
                            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                            margin: 1rem 0;">
                    <h3 style="color: #1f77b4; margin-bottom: 1rem;">Quick Savings Update</h3>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_goal = st.radio(
                    "Select Goal",
                    options=[goal['name'] for goal in st.session_state.savings_goals],
                    key="quick_save_goal",
                    horizontal=True
                )
            
            with col2:
                save_amount = st.number_input(
                    "Amount to Save",
                    min_value=0.0,
                    step=100.0,
                    key="quick_save_amount"
                )
            
            if st.button("Add to Savings", key="quick_save_button"):
                if update_savings_goal(selected_goal, save_amount):
                    st.success(f"✅ Added ₹{save_amount:.2f} to {selected_goal}")
                else:
                    st.error("Failed to update savings")

            # Show progress for all goals
            for goal in st.session_state.savings_goals:
                progress = min(goal['current_amount'] / goal['target_amount'], 1.0) if goal['target_amount'] > 0 else 0.0
                st.markdown(f"""
                    <div style="margin: 1rem 0;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span>🎯 {goal['name']}</span>
                            <span>₹{goal['current_amount']:.2f} / ₹{goal['target_amount']:.2f}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                st.progress(progress)
        
        # After the metrics cards and before transaction table, add pie chart
        if not expenses_df.empty:
            st.markdown("""
                <div style="background: linear-gradient(135deg, #1f77b4, #2c3e50); 
                            padding: 1rem; border-radius: 10px; margin: 2rem 0;">
                    <h2 style="color: white; margin: 0;">Expense Distribution</h2>
                </div>
            """, unsafe_allow_html=True)
            
            fig = px.pie(expenses_df, 
                         values='Amount', 
                         names='Category',
                         hole=0.3,
                         color_discrete_sequence=px.colors.sequential.Blues_r)
            
            fig.update_layout(
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(t=0, l=0, r=0, b=0),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Display transaction table with improved styling and edit/delete options
        st.markdown("""
            <div style="background: linear-gradient(135deg, #1f77b4, #2c3e50); 
                        padding: 1rem; border-radius: 10px; margin: 2rem 0;">
                <h2 style="color: white; margin: 0;">Transaction History</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # Create tabs for viewing and editing transactions
        tab1, tab2 = st.tabs(["📊 View Transactions", "✏️ Edit Transactions"])

        with tab1:
            st.dataframe(
                df.style.format({'Amount': '{:.2f}'})
                      .set_properties(**{'background-color': '#f8f9fa', 
                                       'color': '#2c3e50',
                                       'border-color': '#dee2e6'})
            )

        with tab2:
            for idx, row in df.iterrows():
                col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 1, 1])
                
                with col1:
                    st.write(f"**Date:** {row['Date']}")
                with col2:
                    st.write(f"**Type:** {row['Type']}")
                with col3:
                    st.write(f"**Category:** {row['Category']}")
                with col4:
                    st.write(f"**Amount:** {row['Amount']:.2f}")
                    
                with col5:
                    if st.button("Edit", key=f"edit_{idx}"):
                        st.session_state[f'edit_mode_{idx}'] = True
                        
                with col6:
                    if st.button("Delete", key=f"delete_{idx}"):
                        delete_expense(idx)
                        st.success("Transaction deleted successfully!")
                        st.rerun()
                
                # Edit mode for this transaction
                if st.session_state.get(f'edit_mode_{idx}', False):
                    with st.expander("Edit Transaction", expanded=True):
                        edit_date = st.date_input(
                            "Date", 
                            datetime.strptime(row['Date'], "%Y-%m-%d") if isinstance(row['Date'], str) else row['Date'], 
                            key=f"date_{idx}"
                        )
                        
                        # Transaction Type Selection - Simplified
                        edit_type = st.radio(
                            "Transaction Type",
                            ["Expense", "Additional Income"],
                            index=0 if row['Type']=="Expense" else 1,
                            key=f"type_{idx}_edit"
                        )
                        
                        # Category Selection - Simplified
                        category_list = [
                            "🍔 Food",
                            "🚗 Transportation",
                            "🏠 Rent",
                            "💡 Bills",
                            "🎮 Entertainment",
                            "🛍️ Shopping",
                            "🏥 Healthcare",
                            "📚 Education",
                            "💰 Salary",
                            "📦 Other"
                        ]
                        
                        edit_category = st.radio(
                            "Category",
                            category_list,
                            index=category_list.index(f"🍔 {row['Category']}") if row['Category'] == "Food" else
                                  category_list.index(f"🚗 {row['Category']}") if row['Category'] == "Transportation" else
                                  category_list.index(f"🏠 {row['Category']}") if row['Category'] == "Rent" else
                                  category_list.index(f"💡 {row['Category']}") if row['Category'] == "Bills" else
                                  category_list.index(f"🎮 {row['Category']}") if row['Category'] == "Entertainment" else
                                  category_list.index(f"🛍️ {row['Category']}") if row['Category'] == "Shopping" else
                                  category_list.index(f"🏥 {row['Category']}") if row['Category'] == "Healthcare" else
                                  category_list.index(f"📚 {row['Category']}") if row['Category'] == "Education" else
                                  category_list.index(f"💰 {row['Category']}") if row['Category'] == "Salary" else
                                  category_list.index(f"📦 {row['Category']}"),
                            key=f"category_{idx}_edit"
                        )
                        
                        # Remove emoji for storage
                        edit_category = edit_category.split(" ")[1] if " " in edit_category else edit_category
                        
                        edit_amount = st.number_input("Amount", 
                            value=float(row['Amount']),
                            min_value=0.0,
                            step=1.0,
                            key=f"amount_{idx}")
                        
                        edit_description = st.text_input("Description",
                            value=row['Description'],
                            key=f"desc_{idx}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Save Changes", key=f"save_{idx}"):
                                edit_expense(idx, edit_date, edit_category,
                                           edit_amount, edit_description, edit_type)
                                st.session_state[f'edit_mode_{idx}'] = False
                                st.success("Transaction updated successfully!")
                                st.session_state.counter += 1
                        with col2:
                            if st.button("Cancel", key=f"cancel_{idx}"):
                                st.session_state[f'edit_mode_{idx}'] = False
                                st.rerun()
                
                st.markdown("<hr>", unsafe_allow_html=True)
        
        # Download options
        st.markdown("""
            <div style="background: linear-gradient(135deg, #1f77b4, #2c3e50); 
                        padding: 1rem; border-radius: 10px; margin: 2rem 0;">
                <h2 style="color: white; margin: 0;">Download Reports</h2>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            st.download_button(
                label="Download CSV Report",
                data=csv,
                file_name="expense_report.csv",
                mime="text/csv"
            )
        
        with col2:
            if st.button("Generate PDF Report"):
                pdf_path = create_pdf_report(df, total_income, total_expenses, remaining_balance)
                if pdf_path and os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as pdf_file:
                        PDFbyte = pdf_file.read()
                        st.download_button(
                            label="Download PDF Report",
                            data=PDFbyte,
                            file_name="financial_report.pdf",
                            mime='application/octet-stream'
                        )

        # Update the Reminders Section
        st.markdown("""
            <div style="background: linear-gradient(135deg, #1f77b4, #2c3e50); 
                        padding: 1rem; border-radius: 10px; margin: 2rem 0;">
                <h2 style="color: white; margin: 0;">Bill Reminders</h2>
            </div>
        """, unsafe_allow_html=True)

        reminder_col1, reminder_col2 = st.columns(2)

        with reminder_col1:
            st.subheader("⏰ Add Reminder")
            rem_date = st.date_input("Reminder Date", key="new_reminder_date")
            rem_note = st.text_input("Note", key="new_reminder_note")
            rem_amount = st.number_input("Amount", min_value=0.0, key="new_reminder_amount")
            if st.button("Add Reminder"):
                add_reminder(rem_date, rem_note, rem_amount)
                st.success("Reminder added!")

        with reminder_col2:
            st.subheader("📝 Upcoming Bills")
            if not st.session_state.reminders:
                st.info("No reminders set yet!")
            else:
                # Sort reminders by date
                sorted_reminders = sorted(
                    [r for r in st.session_state.reminders if not r.get('completed', False)],
                    key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d")
                )
                
                for idx, reminder in enumerate(sorted_reminders):
                    with st.container():
                        col1, col2, col3 = st.columns([4, 1, 1])
                        
                        with col1:
                            st.info(f"""
                                📅 Date: {reminder['date']}
                                💭 Note: {reminder['note']}
                                💰 Amount: ₹{reminder['amount']:.2f}
                            """)
                        
                        with col2:
                            if st.button("✅ Done", key=f"complete_reminder_{idx}"):
                                if mark_reminder_complete(idx):
                                    st.success("Marked as complete!")
                                    st.rerun()
                        
                        with col3:
                            if st.button("🗑️ Delete", key=f"delete_reminder_{idx}"):
                                if delete_reminder(idx):
                                    st.success("Reminder deleted!")
                                    st.rerun()

        # Update the Savings Goals Section
        st.markdown("""
            <div style="background: linear-gradient(135deg, #1f77b4, #2c3e50); 
                        padding: 1rem; border-radius: 10px; margin: 2rem 0;">
                <h2 style="color: white; margin: 0;">Savings Goals</h2>
            </div>
        """, unsafe_allow_html=True)

        goal_col1, goal_col2 = st.columns(2)

        with goal_col1:
            # Add tabs for new goal and regular savings
            goal_tab1, goal_tab2 = st.tabs(["🎯 Set New Goal", "💰 Regular Savings"])
            
            with goal_tab1:
                st.subheader("Set New Goal")
                goal_name = st.text_input("Goal Name", key="new_goal_name")
                goal_amount = st.number_input("Target Amount", min_value=0.0, key="new_goal_amount")
                goal_date = st.date_input("Target Date", key="new_goal_date")
                
                # Calculate recommended monthly savings
                if goal_amount > 0 and goal_date > datetime.now().date():
                    months = (goal_date - datetime.now().date()).days / 30
                    if months > 0:
                        monthly_savings = goal_amount / months
                        st.info(f"💡 Recommended monthly savings: ₹{monthly_savings:.2f}")
                
                if st.button("Add Goal"):
                    add_savings_goal(goal_name, goal_amount, goal_date)
                    st.success("Goal added!")
            
            with goal_tab2:
                st.subheader("Add Regular Savings")
                if st.session_state.savings_goals:
                    # Change selectbox to radio for goals
                    selected_goal = st.radio(
                        "Select Goal",
                        options=[goal['name'] for goal in st.session_state.savings_goals],
                        key="regular_savings_goal",
                        horizontal=True  # Make radio buttons horizontal
                    )
                    
                    savings_amount = st.number_input(
                        "Amount to Save",
                        min_value=0.0,
                        step=100.0,
                        key="regular_savings_amount"
                    )
                    
                    # Change selectbox to radio for frequency
                    savings_frequency = st.radio(
                        "Saving Frequency",
                        options=["Daily", "Weekly", "Monthly"],
                        key="savings_frequency",
                        horizontal=True  # Make radio buttons horizontal
                    )
                    
                    if st.button("Add to Savings"):
                        if update_savings_goal(selected_goal, savings_amount):
                            # Calculate next auto-save date based on frequency
                            next_date = datetime.now()
                            if savings_frequency == "Daily":
                                next_date = next_date + timedelta(days=1)
                            elif savings_frequency == "Weekly":
                                next_date = next_date + timedelta(days=7)
                            else:  # Monthly
                                next_date = next_date + timedelta(days=30)
                            
                            # Add a reminder for next savings
                            add_reminder(
                                next_date,
                                f"Regular savings for {selected_goal}",
                                savings_amount
                            )
                            
                            st.success(f"""
                                ✅ Added ₹{savings_amount:.2f} to {selected_goal}
                                📅 Next saving reminder set for {next_date.strftime('%Y-%m-%d')}
                            """)
                        else:
                            st.error("Failed to update savings")
                else:
                    st.info("Create a savings goal first!")

        with goal_col2:
            st.subheader("🏆 Your Goals")
            if st.session_state.savings_goals:
                for goal in st.session_state.savings_goals:
                    progress = min(goal['current_amount'] / goal['target_amount'], 1.0) if goal['target_amount'] > 0 else 0.0
                    remaining = goal['target_amount'] - goal['current_amount']
                    
                    # Create an expander for each goal
                    with st.expander(f"🎯 {goal['name']}", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"Target: ₹{goal['target_amount']:.2f}")
                            st.write(f"Saved: ₹{goal['current_amount']:.2f}")
                        with col2:
                            st.write(f"Remaining: ₹{remaining:.2f}")
                            st.write(f"Due Date: {goal['target_date']}")
                        
                        st.write(f"Progress: {(progress * 100):.1f}%")
                        st.progress(progress)
                        
                        # Calculate daily/monthly needed to reach goal
                        if remaining > 0:
                            target_date = datetime.strptime(goal['target_date'], "%Y-%m-%d").date()
                            days_left = (target_date - datetime.now().date()).days
                            if days_left > 0:
                                daily_needed = remaining / days_left
                                monthly_needed = daily_needed * 30
                                st.info(f"""
                                    💡 To reach your goal:
                                    • Save ₹{daily_needed:.2f} daily
                                    • Or ₹{monthly_needed:.2f} monthly
                                    • {days_left} days remaining
                                """)
            else:
                st.info("No savings goals set yet!")

        # Add Analytics Section
        st.markdown("""
            <div style="background: linear-gradient(135deg, #1f77b4, #2c3e50); 
                        padding: 1rem; border-radius: 10px; margin: 2rem 0;">
                <h2 style="color: white; margin: 0;">Advanced Analytics</h2>
            </div>
        """, unsafe_allow_html=True)

        if not df.empty:
            # Monthly Trends
            st.subheader("📈 Monthly Trends")
            monthly_trends = calculate_monthly_trends(df)
            if not monthly_trends.empty:
                # Convert index to datetime for better sorting
                monthly_trends.index = pd.to_datetime(monthly_trends.index)
                monthly_trends = monthly_trends.sort_index()
                
                # Create the plot
                fig = go.Figure()
                
                # Add Expense line
                fig.add_trace(go.Scatter(
                    x=monthly_trends.index.strftime('%Y-%m'),
                    y=monthly_trends['Expense'],
                    name='Expense',
                    line=dict(color='#e74c3c'),
                    mode='lines+markers'
                ))
                
                # Add Income line
                fig.add_trace(go.Scatter(
                    x=monthly_trends.index.strftime('%Y-%m'),
                    y=monthly_trends['Additional Income'],
                    name='Additional Income',
                    line=dict(color='#2ecc71'),
                    mode='lines+markers'
                ))
                
                # Update layout
                fig.update_layout(
                    title='Monthly Income vs Expenses',
                    xaxis_title='Month',
                    yaxis_title='Amount (₹)',
                    hovermode='x unified',
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)

            # Category Analysis with Plotly
            st.subheader("📊 Category Analysis")
            category_analysis = get_category_analysis(df)
            if not category_analysis.empty:
                fig = px.bar(
                    category_analysis,
                    title='Expenses by Category',
                    labels={'value': 'Amount', 'index': 'Category'}
                )
                fig.update_layout(
                    xaxis_title="Category",
                    yaxis_title="Amount (₹)",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)

            # Spending Insights
            st.subheader("💡 Spending Insights")
            col1, col2 = st.columns(2)
            with col1:
                top_expenses = df[df['Type']=='Expense'].nlargest(3, 'Amount')
                st.write("Top Expenses:")
                for _, expense in top_expenses.iterrows():
                    st.write(f"₹{expense['Amount']:.2f} - {expense['Category']}")
            
            with col2:
                savings_rate = ((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0
                st.write("Savings Rate:")
                st.write(f"{savings_rate:.1f}%")
    else:
        st.info("👋 Welcome! Add your first transaction using the sidebar.")

# Add a counter to session state if not exists
if 'counter' not in st.session_state:
    st.session_state.counter = 0 