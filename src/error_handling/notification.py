import smtplib
from email.mime.text import MIMEText

class NotificationManager:
    def __init__(self, smtp_server='smtp.example.com', port=587):
        self.smtp_server = smtp_server
        self.port = port

    def send_notification(self, recipient_email, subject, message):
        """重要な通知をユーザーへメールで送信する機能"""
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = 'system@example.com'
        msg['To'] = recipient_email

        try:
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls()
                server.login('user@example.com', 'password')
                server.sendmail('system@example.com', recipient_email, msg.as_string())
                print("Notification sent successfully.")
        except Exception as e:
            print(f"Failed to send notification: {e}")
