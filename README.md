# dbs-transaction-tracker

## Overview
This is a DBS iBanking transaction tracker that fetches transaction data from your email inbox and displays it in dashboard using Streamlit.

## How it works
1. App connects to email inbox using IMAP (using env variables).
2. Extracted transaction data is converted into Pandas DataFrame format for analysis.
3. Streamlit dashboard displays the data.

## Features
- Allows for different cut off dates for transaction fetching
- Visualizes daily spending and top recipients.
- Allows downloading transaction data as a CSV file.

## Deployment 
### Prerequisites
1. Install Python 3.11 or higher.
2. Install `pip` for managing Python packages.
3. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

### Installation
1. Install the required dependencies using the [requirements.txt](requirements.txt) file:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file in the project root and add your email credentials. **Note:** For Gmail, you need to generate and use an "App Password".
   ```
   YOUR_EMAIL="your_email@gmail.com"
   YOUR_PASSWORD="your_app_password"
   ```

### Running the Application
1. Run the Streamlit application ([app.py](app.py)) from your terminal in the directory containign app.py:
   ```bash
   streamlit run app.py
   ```
2. Open the URL provided in the terminal in your web browser to view the dashboard.

**Note:** You can lower the minimum transaction amount required to trigger email notifications in the DBS/POSB mobile app

### Thoughts
Was a fun little project that I made to automate my tracking of expenses. I decided not to include an input for Email and Password as this was made purely for my personal usage, but it could be a potential extension. Parsing logic is also not super dynamic, as it doesn't work for older email alert formats and could become outdated in the future.