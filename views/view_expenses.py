import streamlit as st
import gspread
from google.oauth2 import service_account
import pandas as pd
from datetime import datetime

with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Define the scope and credentials for accessing Google Sheets
scopes = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["credentials"], scopes=scopes
)
client = gspread.authorize(credentials)

# Open the Google Sheet
spreadsheet = client.open("Expense Tracker Updated")
sheet = spreadsheet.sheet1


# Define a function to fetch data from Google Sheet
def fetch_expenses():
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df


st.markdown(
    """
    <style>
    .centered-title {
        text-align: center;
        margin-top: -100px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown('<h1 class="centered-title">View Expenses</h1>', unsafe_allow_html=True)

# Fetch and display expenses
df = fetch_expenses()

# Convert 'Date' column to datetime for filtering
df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%y")
df["Month_Year"] = df["Date"].dt.to_period("M")

# Create a list of months with names and year
months = df["Date"].apply(lambda x: x.strftime("%B %Y")).unique()
sorted_months = sorted(months, key=lambda x: datetime.strptime(x, "%B %Y"))

# Add an option to display all expenses
sorted_months.insert(0, "All")

# Dropdown for selecting month
selected_month = st.selectbox("Select Month", sorted_months)

# Filter data based on selected month
if selected_month == "All":
    filtered_df = df
else:
    selected_period = datetime.strptime(selected_month, "%B %Y").strftime("%Y-%m")
    filtered_df = df[df["Month_Year"] == pd.Period(selected_period, freq="M")]


# Drop the "Month_Year" column before displaying
filtered_df = filtered_df.drop(columns=["Month_Year"])

# Format the 'Date' column to remove the timestamp
filtered_df["Date"] = filtered_df["Date"].dt.strftime("%d-%m-%y")

# Calculate the total amount for the selected period
total_amount = filtered_df["Amount (INR)"].sum()

# Display filtered data without the index
st.dataframe(filtered_df, use_container_width=True, hide_index=True)


tanmai_share = filtered_df.loc[
    filtered_df["Paid By"] == "Shivangi", "Tanmai's Share (INR)"
].sum()
shivangi_share = filtered_df.loc[
    filtered_df["Paid By"] == "Tanmai", "Shivangi's Share (INR)"
].sum()

st.write('---')

col1, col2, col3 = st.columns(3)
with col1: 
    st.metric(label="Total Monthly Spend", value=f"₹{total_amount}")
with col2: 
    st.metric(label="Shivangi's Share", value=f"₹{shivangi_share}")
with col3: 
    st.metric(label="Tanmai's Share", value=f"₹{tanmai_share}")

st.write('---')
if shivangi_share > tanmai_share:     
    st.metric(label="Shivangi Owes Tanmai", value=f"₹{(shivangi_share - tanmai_share):.2f}")
else:     
    st.metric(label="Shivangi Owes Tanmai", value=f"₹{(tanmai_share - shivangi_share):.2f}")

st.write('---')

