# Email Configuration Guide

## Problem Identified
The verification and login emails were not being sent because:
1. **Email credentials were not configured** - `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` were empty strings
2. **SMTP Backend was hardcoded** without credentials fallback

## Solution Implemented

### For Development (Currently Active)
✅ Using **Console Email Backend** - emails are printed to terminal/console instead of being sent
- This is perfect for testing
- You'll see all email content in your Django development server logs

### For Production
Use **SMTP Email Backend** with real credentials (Gmail, SendGrid, etc.)

---

## How to Use

### Current Setup (Development with Console Backend)

1. **Start Django development server:**
   ```bash
   python manage.py runserver
   ```

2. **Try the two-step login:**
   - Go to `/accounts/login/`
   - Enter username and password
   - Check your Django console/terminal for the verification email output
   - You'll see the 6-digit code printed

3. **Example Console Output:**
   ```
   Content-Type: text/plain; charset="utf-8"
   Subject: Your verification code
   From: your-email@gmail.com
   To: user@example.com
   
   Your verification code is: 123456
   ```

---

## Switch to Gmail SMTP (For Production/Real Emails)

### Step 1: Set up Gmail
1. Go to https://myaccount.google.com/apppasswords
2. Create an **App Password** (not your regular Gmail password)
3. Google will give you a 16-character password

### Step 2: Update `.env` file
Edit `/Users/atharvshinde/social_book/.env`:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### Step 3: Test the connection
```bash
python test_email.py
```

---

## Environment Variables Reference

| Variable | Default | Purpose |
|----------|---------|---------|
| `EMAIL_BACKEND` | `django.core.mail.backends.console.EmailBackend` | Email service backend |
| `EMAIL_HOST` | `smtp.gmail.com` | SMTP server address |
| `EMAIL_PORT` | `587` | SMTP port (587=TLS, 465=SSL) |
| `EMAIL_USE_TLS` | `True` | Enable TLS encryption |
| `EMAIL_USE_SSL` | `False` | Enable SSL encryption |
| `EMAIL_HOST_USER` | Empty | Email account username |
| `EMAIL_HOST_PASSWORD` | Empty | Email account password/app-password |
| `DEFAULT_FROM_EMAIL` | `noreply@socialbook.local` | Sender email address |
| `LOGIN_NOTIFICATION_RECIPIENT` | None | Optional: email address to notify on user login |

---

## Email Flow in Your Application

### Registration
- User creates account → No email sent (yet)

### Two-Step Login
1. User enters username/password
2. System generates 6-digit verification code
3. **Email is sent** with the verification code
4. User enters code to complete login
5. If `LOGIN_NOTIFICATION_RECIPIENT` is set, a notification email is sent

---

## Troubleshooting

### Emails not appearing in console?
- Ensure `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` in `.env`
- Restart Django development server
- Check Django logs/console output

### SMTP Connection Error (when using real credentials)?
- Verify `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are correct
- Check firewall allows port 587 (TLS) or 465 (SSL)
- For Gmail: ensure you're using an **App Password**, not your regular password
- Enable "Less secure app access" if not using App Passwords

### Email still not working?
- Run: `python test_email.py` to test configuration
- Check `.env` file is in the project root
- Ensure environment variables are properly loaded

---

## Files Modified

1. **`social_book/settings.py`**
   - Added python-dotenv import and loading
   - Updated EMAIL_BACKEND to use console backend by default
   - Fixed EMAIL_USE_SSL default (was "False" string, now properly compared)

2. **`.env`** (Created)
   - Configuration file for environment variables
   - Add to `.gitignore` (already included)

3. **`.env.example`** (Created)
   - Template for reference
   - Safe to commit to version control

4. **`test_email.py`** (Created)
   - Utility script to test email configuration

---

## Next Steps

1. **For testing now**: Code is ready! Emails will print to console
2. **For production**: Set up real email credentials in `.env` (Gmail, SendGrid, etc.)
3. **Optional**: Customize email templates in `accounts/views.py`
