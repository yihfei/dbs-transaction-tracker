import imaplib
import email
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import re
import pandas as pd
from collections import defaultdict, Counter
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

    # load credentials from .env
load_dotenv()
EMAIL = os.getenv("YOUR_EMAIL")
PASSWORD = os.getenv("YOUR_PASSWORD")

# bank filter
SENDER_FILTER = "ibanking.alert@dbs.com"  # Replace this with your bank's sender email
# define cutoff date
CUTOFF_DATE = datetime(2025, 1, 1, tzinfo=timezone.utc)

 # adapted from chatGPT
    # SPECIFIC TO DBS iBanking transaction emails (accurate as of June 2025)
def parse_dbs_transaction(email_text):
    result = {}

    amount_match = re.search(r"Amount:\s*\nSGD([\d,]+\.\d{2})", email_text)
    if amount_match:
        result["amount"] = float(amount_match.group(1).replace(",", ""))

    date_match = re.search(r"Date & Time:\s*\n(.+?) \(SGT\)", email_text)
    if date_match:
        result["date_time"] = date_match.group(1)

    to_match = re.search(r"To:\s*\n(.+?)\s*\(UEN", email_text)
    if to_match:
        result["recipient"] = to_match.group(1).strip()

    from_match = re.search(r"From:\s*\n.+?ending (\d+)", email_text)
    if from_match:
        result["from_acct"] = from_match.group(1)

    return result

def fetch_transactions(cutoff_date=CUTOFF_DATE):
    # connect to Gmail using IMAP
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(EMAIL, PASSWORD)
    imap.select("inbox")

    # serach DBS iBanking emails
    status, messages = imap.search(None, f'FROM "{SENDER_FILTER}"')
    email_ids = messages[0].split() # get list of email IDs

    # log out if no emails found
    if not email_ids:
        print(f"No emails found from {SENDER_FILTER}.")
        imap.logout()
        exit()

    
    transactions = []

    # loop through the emails
    for id in reversed(email_ids):
        res, msg_data = imap.fetch(id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        email_sent_dt = parsedate_to_datetime(msg["Date"])
        if email_sent_dt < cutoff_date:
            print("Reached cutoff date. Stopping.")
            break

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()

                content_disposition = str(part.get("Content-Disposition"))
                # usual format for ibanking alerts
                if "html" in content_type and "attachment" not in content_disposition:
                    charset = part.get_content_charset() or "utf-8"

                    # Decode the HTML payload from bytes to string
                    html = part.get_payload(decode=True).decode(charset)

                    # Use BeautifulSoup to parse HTML and extract clean text with line breaks
                    soup = BeautifulSoup(html, "html.parser")
                    body = soup.get_text(separator="\n", strip=True)
                    parsed = parse_dbs_transaction(body)
                    required_keys = ["amount", "date_time", "recipient"]
                    if all(parsed.get(k) for k in required_keys):
                        parsed["datetime"] = email_sent_dt 
                        transactions.append(parsed)




    # Analysis of transactions
    # Total spent
    total_spent = sum(t["amount"] for t in transactions)

    # Number of transactions
    num_txns = len(transactions)

    # Average transaction
    avg_txn = total_spent / num_txns if num_txns > 0 else 0

    # Count by recipient
    recipient_counter = Counter(t["recipient"] for t in transactions)

    # Spending by date

    daily_spending = defaultdict(float)
    for t in transactions:
        sent_dt = t["datetime"]
        date_key = sent_dt.strftime("%Y-%m-%d")
        daily_spending[date_key] += t["amount"]



    imap.logout()


    df = pd.DataFrame(transactions)
    df['datetime'] = pd.to_datetime(df['datetime'])  # Ensure proper dtype


    return df
        

if __name__ == "__main__":
    df = fetch_transactions()
 