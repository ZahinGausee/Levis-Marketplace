from django.conf import settings
from django.core.mail import send_mail

def send_account_activation_email(email, email_token):
    subject = 'Your account needs to be verified'
    from_email = settings.EMAIL_HOST_USER
    message = f'Hi, click on the link to activate your account: http://127.0.0.1:8000/accounts/activate/{email_token}'
    
    print(f"📧 Sending email to: {email}")  # Debugging print

    send_mail(
        subject,
        message,
        from_email,  # Replace with EMAIL_HOST_USER
        [email],  # Fix: remove extra quotes around `email`
        fail_silently=False,
    )
