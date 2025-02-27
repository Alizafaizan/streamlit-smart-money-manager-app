import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import base64
from fpdf import FPDF
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from users import init_users, create_user, authenticate

# Page configuration
st.set_page_config(
    page_title="Income & Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# Custom CSS for better appearance
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2c3e50;
    }
    .stTextInput>div>div>input {
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 16px;
        color: #7f8c8d;
    }
    div[data-testid="stHeader"] {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .st-emotion-cache-1y4p8pa {
        padding: 2rem;
        border-radius: 10px;
        background-color: #ffffff;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        padding: 1rem;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #1f77b4, #2c3e50);
        color: white;
        border-radius: 10px;
    }
    h2 {
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'expenses' not in st.session_state:
    st.session_state.expenses = []
if 'income' not in st.session_state:
    st.session_state.income = 0

# Initialize session state for authentication
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Initialize users config
init_users()

def add_expense(date, category, amount, description, transaction_type):
    st.session_state.expenses.append({
        'Date': date,
        'Category': category,
        'Amount': amount,
        'Description': description,
        'Type': transaction_type
    })

def get_csv_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="expense_report.csv">Download CSV Report</a>'
    return href

def create_pdf_report(df, total_income, total_expenses, remaining_balance):
    try:
        pdf_path = "financial_report.pdf"
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        normal_style = styles['Normal']
        
        # Title
        elements.append(Paragraph("Financial Report", title_style))
        elements.append(Spacer(1, 20))
        
        # Summary
        summary_data = [
            ["Total Income:", f"{total_income:.2f}"],
            ["Total Expenses:", f"{total_expenses:.2f}"],
            ["Remaining Balance:", f"{remaining_balance:.2f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        # Transactions Table
        elements.append(Paragraph("Transaction Details", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        # Prepare table data
        table_data = [['Date', 'Type', 'Category', 'Amount', 'Description']]
        for _, row in df.iterrows():
            table_data.append([
                str(row['Date'])[:10],
                str(row['Type']),
                str(row['Category']),
                f"₹{row['Amount']:.2f}",
                str(row['Description'])[:30]
            ])
        
        # Create table
        table = Table(table_data, colWidths=[1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
        ]))
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
        return pdf_path
    except Exception as e:
        st.error(f"Error creating PDF: {str(e)}")
        return None

def delete_expense(index):
    del st.session_state.expenses[index]

def edit_expense(index, date, category, amount, description, transaction_type):
    st.session_state.expenses[index] = {
        'Date': date,
        'Category': category,
        'Amount': amount,
        'Description': description,
        'Type': transaction_type
    }

def login_page():
    st.title("💰 Smart Money Manager")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            if authenticate(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    with tab2:
        st.subheader("Register")
        new_username = st.text_input("Username", key="register_username")
        new_password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("Register"):
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
            st.success("✅ Income updated successfully!")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Expense Section
        st.subheader("�� Add Transaction")
        date = st.date_input("Date", datetime.now())
        transaction_type = st.selectbox("Transaction Type", ["Expense", "Additional Income"])
        category = st.selectbox("Category", [
            "🍔 Food", "🚗 Transportation", "🏠 Rent", 
            "💡 Bills", "🎮 Entertainment", "🛍️ Shopping",
            "🏥 Healthcare", "📚 Education", "💰 Salary", "�� Other"
        ])
        amount = st.number_input("Amount (₹)", min_value=0.0, step=1.0)
        description = st.text_input("Description")
        
        if st.button("Add Transaction"):
            add_expense(date, category.split(" ")[1], amount, description, transaction_type)
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
        
        # Summary metrics with custom styling and increased margin
        st.markdown("""
            <div style="margin-top: 3rem; margin-bottom: 3rem;">
                <div style="background: linear-gradient(135deg, #1f77b4, #2c3e50); 
                            padding: 1rem; border-radius: 10px;">
                    <h2 style="color: white; margin: 0;">Financial Summary</h2>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
                <div class="metric-card">
                    <h3 style="color: #1f77b4;">Total Income</h3>
                    <h2 style="color: #2c3e50;">{:.2f}</h2>
                </div>
            """.format(total_income), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="metric-card">
                    <h3 style="color: #1f77b4;">Total Expenses</h3>
                    <h2 style="color: #e74c3c;">{:.2f}</h2>
                </div>
            """.format(total_expenses), unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
                <div class="metric-card">
                    <h3 style="color: #1f77b4;">Remaining Balance</h3>
                    <h2 style="color: #27ae60;">{:.2f}</h2>
                </div>
            """.format(remaining_balance), unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
                <div class="metric-card">
                    <h3 style="color: #1f77b4;">Transactions</h3>
                    <h2 style="color: #2c3e50;">{}</h2>
                </div>
            """.format(len(df)), unsafe_allow_html=True)
        
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
                        edit_date = st.date_input("Date", row['Date'], key=f"date_{idx}")
                        edit_type = st.selectbox("Transaction Type", 
                                               ["Expense", "Additional Income"],
                                               index=0 if row['Type']=="Expense" else 1,
                                               key=f"type_{idx}")
                        edit_category = st.selectbox("Category", [
                            "🍔 Food", "🚗 Transportation", "🏠 Rent", 
                            "💡 Bills", "🎮 Entertainment", "🛍️ Shopping",
                            "🏥 Healthcare", "📚 Education", "�� Salary", "📦 Other"
                        ], index=["Food", "Transportation", "Rent", "Bills", "Entertainment", 
                                 "Shopping", "Healthcare", "Education", "Salary", "Other"].index(row['Category']),
                        key=f"category_{idx}")
                        edit_amount = st.number_input("Amount", 
                                                    value=float(row['Amount']),
                                                    key=f"amount_{idx}")
                        edit_description = st.text_input("Description",
                                                       value=row['Description'],
                                                       key=f"desc_{idx}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Save Changes", key=f"save_{idx}"):
                                edit_expense(idx, edit_date, edit_category.split(" ")[1],
                                           edit_amount, edit_description, edit_type)
                                st.session_state[f'edit_mode_{idx}'] = False
                                st.success("Transaction updated successfully!")
                                st.rerun()
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
    else:
        st.info("👋 Welcome! Add your first transaction using the sidebar.") 