#!/usr/bin/env python
"""
Test script to verify email sending functionality.
Run with: python test_email.py
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "social_book.settings")
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print(f"Email Backend: {settings.EMAIL_BACKEND}")
print(f"Email Host: {settings.EMAIL_HOST}")
print(f"Email Port: {settings.EMAIL_PORT}")
print(f"Email Use TLS: {settings.EMAIL_USE_TLS}")
print(f"Email From: {settings.DEFAULT_FROM_EMAIL}")
print()

try:
    result = send_mail(
        subject="Test Email - Verification Code",
        message="Your verification code is: 123456",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=["test@example.com"],
        fail_silently=False,
    )
    print(f"✓ Test email sent successfully! (result: {result})")
except Exception as e:
    print(f"✗ Failed to send email: {e}")
