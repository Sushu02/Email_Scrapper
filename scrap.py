import imaplib

# Manually check if login works
IMAP_SERVER = "imap.gmail.com"
EMAIL_USER = "sushmitha@kgrp.in"
EMAIL_PASS = "Sushu@02"

try:
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    print("Login Successful!")
    mail.logout()
except imaplib.IMAP4.error as e:
    print("Login Failed:", e)
