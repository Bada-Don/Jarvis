---
name: email
description: "Use this skill whenever the user wants to send an email, compose and dispatch a message to someone via email, or forward/attach files via email. Triggers include: 'send email', 'email to', 'mail this', 'forward', 'compose email', 'attach and send'. This skill sends emails in the background without any UI interaction. Do NOT use for opening email clients manually (use ui_os skill) or for web-based email composition requiring browser interaction."
---

For send_email steps (BACKGROUND - no UI), include:
- "recipient_email": email address of the recipient
- "subject": subject line of the email
- "body": body text of the email (supports UTF-8)
- "attachment_filepaths": (optional) list of absolute paths to local files (e.g. ["C:\\Users\\user\\Desktop\\report.pdf"])
- Use this for: "Send an email to...", "Email the report to...", "Forward this file to..."

## Example - Send a background email with attachment:
{
  "sequence":[
    {
      "order": 1, 
      "type": "send_email", 
      "recipient_email": "example@gmail.com", 
      "subject": "Monthly Report", 
      "body": "Hi, please find the attached report.",
      "attachment_filepaths": ["{DESKTOP_PATH}\\report.pdf"],
      "desc": "Send report via background email"
    }
  ],
  "expected_final_state": "Email sent in background to example@gmail.com with report.pdf attachment"
}
