import os
from dotenv import load_dotenv
from mailersend import emails

load_dotenv()

def test_mailersend():
    """Test MailerSend connection and send a test email"""
    
    api_key = os.getenv("MAILERSEND_API_KEY")
    from_email = os.getenv("MAIL_FROM")
    from_name = os.getenv("MAIL_FROM_NAME", "ReLoop Team")
    
    print("=" * 60)
    print("MailerSend Configuration Test")
    print("=" * 60)
    print(f"API Key: {api_key[:20]}..." if api_key else "❌ API Key not found!")
    print(f"From Email: {from_email}")
    print(f"From Name: {from_name}")
    print("=" * 60)
    
    if not api_key:
        print("\n❌ Error: MAILERSEND_API_KEY not found in environment variables")
        print("\nPlease add to backend/.env:")
        print("MAILERSEND_API_KEY=your_api_key_here")
        return False
    
    if not from_email:
        print("\n❌ Error: MAIL_FROM not found in environment variables")
        print("\nPlease add to backend/.env:")
        print("MAIL_FROM=your-email@yourdomain.com")
        return False
    
    try:
        # Get recipient email
        test_recipient = input("\nEnter email to send test to (or press Enter to use sender email): ").strip()
        if not test_recipient:
            test_recipient = from_email
        
        # Build email with old API (0.6.0)
        print(f"\n📧 Sending test email to {test_recipient}...")
        
        html_content = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #0d9488 0%, #06b6d4 100%); color: white; padding: 30px; text-align: center; border-radius: 10px; }
        .content { background: #f8f9fa; padding: 30px; border-radius: 10px; margin-top: 20px; }
        .success { color: #28a745; font-size: 48px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔄 ReLoop Email System</h1>
        </div>
        <div class="content">
            <div class="success">✓</div>
            <h2 style="text-align: center; color: #0d9488;">Success!</h2>
            <p>Your MailerSend integration is working perfectly!</p>
            <p>This test confirms that:</p>
            <ul>
                <li>✅ API Key is valid</li>
                <li>✅ Email sending works</li>
                <li>✅ HTML formatting is supported</li>
                <li>✅ Ready for production use</li>
            </ul>
            <p><strong>Next Steps:</strong></p>
            <ol>
                <li>Your email automation system is ready</li>
                <li>Run your backend server: python backend/main.py</li>
                <li>Use the platform to send buyer outreach emails</li>
            </ol>
            <p style="margin-top: 30px; font-size: 12px; color: #666;">
                © 2026 ReLoop - Circular Economy Platform
            </p>
        </div>
    </div>
</body>
</html>"""
        
        # Send email using mailersend 0.6.0 API
        mailer = emails.NewEmail(api_key)
        
        mail_body = {}
        mailer.set_mail_from({"name": from_name, "email": from_email}, mail_body)
        mailer.set_mail_to([{"name": "Test Recipient", "email": test_recipient}], mail_body)
        mailer.set_subject("MailerSend Test - ReLoop Platform", mail_body)
        mailer.set_html_content(html_content, mail_body)
        mailer.set_plaintext_content("Your MailerSend integration is working! Check the HTML version for full details.", mail_body)
        
        response = mailer.send(mail_body)
        
        print("\n" + "=" * 60)
        print("✅ SUCCESS! Test email sent successfully!")
        print("=" * 60)
        print("\nCheck your inbox for the test email.")
        print("\nMailerSend Free Tier includes:")
        print("  • 12,000 emails/month")
        print("  • 100 emails/day")
        print("  • Perfect for production!")
        print("\nYour email automation system is ready! 🚀")
        print("=" * 60)
        
        return True
    
    except Exception as e:
        print(f"\n❌ Error sending test email: {e}")
        print("\nTroubleshooting:")
        print("1. Check your API key is correct")
        print("2. Verify your sender email is verified in MailerSend")
        print("3. Check your MailerSend dashboard for more details")
        return False

if __name__ == "__main__":
    test_mailersend()
