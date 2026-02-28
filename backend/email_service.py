"""
Email Service for Jarvis AI Agent
Provides background email sending capabilities using SMTP.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_email_tool(recipient_email: str, subject: str, body: str, attachment_filepaths: Optional[List[str]] = None) -> Tuple[bool, str]:
    """
    Sends an email using Gmail SMTP and App Passwords.
    
    Args:
        recipient_email: The email address of the recipient.
        subject: The subject line of the email.
        body: The body content of the email.
        attachment_filepaths: Optional list of local file paths to attach.
        
    Returns:
        Tuple[bool, str]: (Success status, Result message)
    """
    sender_email = os.getenv("EMAIL_SENDER_ADDRESS")
    app_password = os.getenv("EMAIL_APP_PASSWORD")
    
    if not sender_email or not app_password:
        return False, "Email credentials not found in environment variables."
        
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    
    try:
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Handle attachments
        if attachment_filepaths:
            for filepath in attachment_filepaths:
                if not os.path.exists(filepath):
                    print(f"Warning: Attachment file not found: {filepath}")
                    continue
                    
                filename = os.path.basename(filepath)
                try:
                    with open(filepath, "rb") as f:
                        part = MIMEApplication(f.read(), Name=filename)
                    
                    part['Content-Disposition'] = f'attachment; filename="{filename}"'
                    msg.attach(part)
                except Exception as e:
                    print(f"Error attaching file {filepath}: {e}")
                    
        # Connect to SMTP server and send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls() # Secure the connection
            server.login(sender_email, app_password)
            server.send_message(msg)
            
        return True, f"Email sent successfully to {recipient_email}"
        
    except smtplib.SMTPAuthenticationError:
        return False, "Authentication failed. Please check your App Password and email address."
    except smtplib.SMTPConnectError:
        return False, "Failed to connect to the SMTP server. Check your network connection."
    except Exception as e:
        return False, f"An unexpected error occurred: {str(e)}"

if __name__ == "__main__":
    # Quick manual test (requires valid ENV variables)
    # success, response = send_email_tool("test@example.com", "Test Subject", "Test Body")
    # print(response)
    pass
