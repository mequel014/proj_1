# app/utils/email.py
import os
import smtplib
from email.mime.text import MIMEText

SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", 1025))

def send_signup_link(email: str, link: str):
    subject = "Подтверждение регистрации"
    body = f"Перейдите по ссылке для завершения регистрации: {link}"

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = "no-reply@example.com"
    msg["To"] = email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.sendmail(msg["From"], [msg["To"]], msg.as_string())

    print(f"[SIGNUP LINK] Sent to {email}: {link}")

# def send_signup_link(email: str, link: str):
#     # В реальном проекте отправляйте письмо через SMTP / сервисы
#     print(f"[SIGNUP LINK] Send to {email}: {link}")