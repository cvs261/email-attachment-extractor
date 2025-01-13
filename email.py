import imaplib
import email
from email.header import decode_header
import os

# Your email credentials
EMAIL = "your_email@example.com"
PASSWORD = "your_password"
IMAP_SERVER = "imap.example.com"
SAVE_DIR = "./attachments"

def clean(text):
    """Clean text for creating safe filenames."""
    return "".join(c if c.isalnum() else "_" for c in text)

def save_attachments(msg, folder=SAVE_DIR):
    """Save attachments from an email message."""
    if not os.path.isdir(folder):
        os.makedirs(folder)

    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        if part.get("Content-Disposition") is None:
            continue

        filename = part.get_filename()
        if filename:
            filepath = os.path.join(folder, clean(filename))
            with open(filepath, "wb") as f:
                f.write(part.get_payload(decode=True))
            print(f"Saved attachment: {filepath}")

def connect_and_fetch():
    """Connect to the email server and fetch messages."""
    try:
        # Connect to the server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)

        # Select the mailbox you want to use
        mail.select("inbox")

        # Search for all emails
        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()

        print(f"Found {len(email_ids)} emails.")

        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = decode_header(msg["Subject"])[0][0]
                    if isinstance(subject, bytes):
                        subject = subject.decode()

                    print(f"Processing email: {subject}")
                    save_attachments(msg)

        mail.logout()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    connect_and_fetch()
