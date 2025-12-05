import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@neuronix.ai')
FROM_NAME = os.getenv('FROM_NAME', 'Neuronix AI JobFlow')

def send_password_reset_email(to_email, reset_token, user_name=None):
    """
    Send password reset email with token link.
    
    Args:
        to_email: Recipient email address
        reset_token: Password reset token
        user_name: Optional user name for personalization
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    
    # Create reset link (in production, use your actual domain)
    reset_link = f"http://localhost:5000/src/reset-password.html?token={reset_token}"
    
    # Create email content
    subject = "Password Reset Request - Neuronix AI JobFlow"
    
    greeting = f"Hello {user_name}," if user_name else "Hello,"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(to right, #6366f1, #8b5cf6);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 8px 8px 0 0;
            }}
            .content {{
                background: #f9fafb;
                padding: 30px;
                border-radius: 0 0 8px 8px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background: #6366f1;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                color: #6b7280;
                font-size: 14px;
            }}
            .warning {{
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 12px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Password Reset Request</h1>
            </div>
            <div class="content">
                <p>{greeting}</p>
                
                <p>We received a request to reset your password for your Neuronix AI JobFlow account.</p>
                
                <p>Click the button below to reset your password:</p>
                
                <center>
                    <a href="{reset_link}" class="button">Reset Password</a>
                </center>
                
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; background: white; padding: 10px; border-radius: 4px;">
                    {reset_link}
                </p>
                
                <div class="warning">
                    <strong>⚠️ Security Notice:</strong>
                    <ul>
                        <li>This link will expire in <strong>1 hour</strong></li>
                        <li>If you didn't request this reset, please ignore this email</li>
                        <li>Never share this link with anyone</li>
                    </ul>
                </div>
                
                <p>Need help? Contact us at <a href="mailto:neuronixaisolutions@gmail.com">neuronixaisolutions@gmail.com</a></p>
            </div>
            <div class="footer">
                <p>© 2025 Neuronix AI Solutions. All rights reserved.</p>
                <p>Empowering the Future with AI</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
    {greeting}
    
    We received a request to reset your password for your Neuronix AI JobFlow account.
    
    Click the link below to reset your password:
    {reset_link}
    
    This link will expire in 1 hour.
    
    If you didn't request this reset, please ignore this email.
    
    Need help? Contact us at neuronixaisolutions@gmail.com
    
    © 2025 Neuronix AI Solutions
    Empowering the Future with AI
    """
    
    try:
        # Create message
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
        message['To'] = to_email
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        message.attach(part1)
        message.attach(part2)
        
        # Send email
        if SMTP_USERNAME and SMTP_PASSWORD:
            # Use configured SMTP server
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(message)
            print(f"✓ Password reset email sent to {to_email}")
            return True
        else:
            # No SMTP configured - print to console for development
            print("\n" + "="*80)
            print("📧 EMAIL SIMULATION (No SMTP configured)")
            print("="*80)
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"\nReset Link: {reset_link}")
            print("="*80 + "\n")
            return True
            
    except Exception as e:
        print(f"✗ Failed to send email: {str(e)}")
        return False

def send_welcome_email(to_email, user_name):
    """
    Send welcome email to new users.
    
    Args:
        to_email: Recipient email address
        user_name: User's name
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    subject = "Welcome to Neuronix AI JobFlow! 🎉"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(to right, #6366f1, #8b5cf6);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 8px 8px 0 0;
            }}
            .content {{
                background: #f9fafb;
                padding: 30px;
                border-radius: 0 0 8px 8px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background: #6366f1;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                margin: 20px 0;
            }}
            .feature {{
                background: white;
                padding: 15px;
                margin: 10px 0;
                border-radius: 6px;
                border-left: 4px solid #6366f1;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Welcome to Neuronix AI JobFlow!</h1>
            </div>
            <div class="content">
                <p>Hello {user_name},</p>
                
                <p>Thank you for joining Neuronix AI JobFlow! We're excited to help you find your perfect job match using the power of AI.</p>
                
                <h3>🚀 Get Started:</h3>
                
                <div class="feature">
                    <strong>📝 Structured Search</strong><br>
                    Fill out a detailed form with your preferences
                </div>
                
                <div class="feature">
                    <strong>💬 Chat Mode</strong><br>
                    Describe yourself in your own words
                </div>
                
                <div class="feature">
                    <strong>📄 CV Upload</strong><br>
                    Upload your resume for instant matching
                </div>
                
                <center>
                    <a href="http://localhost:5000/src/structured.html" class="button">Start Job Search</a>
                </center>
                
                <p>Need help? Contact us at <a href="mailto:neuronixaisolutions@gmail.com">neuronixaisolutions@gmail.com</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
        message['To'] = to_email
        
        part = MIMEText(html_body, 'html')
        message.attach(part)
        
        if SMTP_USERNAME and SMTP_PASSWORD:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(message)
            print(f"✓ Welcome email sent to {to_email}")
            return True
        else:
            print(f"📧 Welcome email simulated for {to_email}")
            return True
            
    except Exception as e:
        print(f"✗ Failed to send welcome email: {str(e)}")
        return False
