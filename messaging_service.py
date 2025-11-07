"""
Deep Blue Pool Chemistry - Messaging Service
Copyright (c) 2024 Michael Hayes. All rights reserved.

This module handles email and SMS notifications for the Deep Blue Pool Chemistry application.
Supports SMTP email and Twilio SMS messaging.
"""

import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Try to import Twilio (optional dependency)
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger.info("Twilio not installed. SMS functionality will be disabled.")

class MessagingService:
    """
    Handles email and SMS notifications for pool chemistry alerts.
    """
    
    def __init__(self, config_file: str = "messaging_config.json"):
        """
        Initialize the messaging service.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.twilio_client = None
        
        # Initialize Twilio if configured
        if TWILIO_AVAILABLE and self.config.get('sms_enabled', False):
            self._init_twilio()
    
    def _load_config(self) -> Dict:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return self._default_config()
        else:
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Return default configuration."""
        return {
            # Email settings
            'email_enabled': False,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_username': '',
            'smtp_password': '',
            'from_email': '',
            'to_emails': [],
            
            # SMS settings
            'sms_enabled': False,
            'twilio_account_sid': '',
            'twilio_auth_token': '',
            'twilio_phone_number': '',
            'to_phone_numbers': [],
            
            # Notification preferences
            'notify_critical_alerts': True,
            'notify_warning_alerts': True,
            'notify_readings_saved': False,
            'notify_chemical_adjustments': True,
            'notify_daily_summary': False,
            'daily_summary_time': '08:00',
            
            # Message templates
            'include_pool_name': True,
            'pool_name': 'My Pool'
        }
    
    def save_config(self, config: Dict) -> bool:
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            self.config = config
            
            # Reinitialize Twilio if SMS enabled
            if TWILIO_AVAILABLE and config.get('sms_enabled', False):
                self._init_twilio()
            
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def _init_twilio(self):
        """Initialize Twilio client."""
        try:
            account_sid = self.config.get('twilio_account_sid', '')
            auth_token = self.config.get('twilio_auth_token', '')
            
            if account_sid and auth_token:
                self.twilio_client = TwilioClient(account_sid, auth_token)
                logger.info("Twilio client initialized successfully")
            else:
                logger.warning("Twilio credentials not configured")
        except Exception as e:
            logger.error(f"Error initializing Twilio: {e}")
            self.twilio_client = None
    
    def send_email(self, subject: str, body: str, html_body: Optional[str] = None) -> Tuple[bool, str]:
        """
        Send an email notification.
        
        Args:
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            
        Returns:
            Tuple of (success, message)
        """
        if not self.config.get('email_enabled', False):
            return False, "Email notifications are disabled"
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            
            # Add pool name to subject if enabled
            if self.config.get('include_pool_name', True):
                pool_name = self.config.get('pool_name', 'My Pool')
                subject = f"[{pool_name}] {subject}"
            
            msg['Subject'] = subject
            msg['From'] = self.config.get('from_email', '')
            msg['To'] = ', '.join(self.config.get('to_emails', []))
            
            # Attach plain text
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach HTML if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(
                self.config.get('smtp_server', 'smtp.gmail.com'),
                self.config.get('smtp_port', 587)
            )
            server.starttls()
            
            # Login
            server.login(
                self.config.get('smtp_username', ''),
                self.config.get('smtp_password', '')
            )
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully: {subject}")
            return True, "Email sent successfully"
            
        except Exception as e:
            error_msg = f"Error sending email: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    

    def send_email_with_attachment(self, data: dict) -> dict:
        """
        Send an email with PDF attachment.
        
        Args:
            data: Dictionary containing:
                - subject: Email subject
                - body: HTML body
                - recipients: List of recipient emails
                - attachment: Path to PDF file
                - attachment_name: Name for the attachment
                
        Returns:
            Dictionary with success status and message
        """
        if not self.config.get('email', {}).get('enabled', False):
            return {'success': False, 'message': 'Email notifications are disabled'}
        
        try:
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.application import MIMEApplication
            from pathlib import Path
            import smtplib
            
            # Create message
            msg = MIMEMultipart()
            
            # Add pool name to subject if enabled
            subject = data.get('subject', 'Pool Chemistry Report')
            if self.config.get('email', {}).get('include_pool_name', True):
                pool_name = self.config.get('email', {}).get('pool_name', 'My Pool')
                subject = f"[{pool_name}] {subject}"
            
            msg['Subject'] = subject
            msg['From'] = self.config.get('email', {}).get('username', '')
            
            # Handle recipients
            recipients = data.get('recipients', [])
            if isinstance(recipients, str):
                recipients = [recipients]
            msg['To'] = ', '.join(recipients)
            
            # Attach HTML body
            body = data.get('body', '')
            msg.attach(MIMEText(body, 'html'))
            
            # Attach PDF if provided
            attachment_path = data.get('attachment')
            if attachment_path and Path(attachment_path).exists():
                with open(attachment_path, 'rb') as f:
                    pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                    attachment_name = data.get('attachment_name', Path(attachment_path).name)
                    pdf_attachment.add_header('Content-Disposition', 'attachment', filename=attachment_name)
                    msg.attach(pdf_attachment)
            
            # Connect to SMTP server
            smtp_config = self.config.get('email', {})
            server = smtplib.SMTP(
                smtp_config.get('smtp_server', 'smtp.gmail.com'),
                smtp_config.get('smtp_port', 587)
            )
            server.starttls()
            
            # Login
            server.login(
                smtp_config.get('username', ''),
                smtp_config.get('password', '')
            )
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email with attachment sent successfully: {subject}")
            return {'success': True, 'message': 'Email sent successfully'}
            
        except Exception as e:
            error_msg = f"Error sending email with attachment: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'message': error_msg}

    def _create_professional_email_html(self, notification_type, data):
        """Create professional HTML email with icons and detailed information"""
        
        # Color scheme
        colors = {
            'critical': '#e74c3c',  # Red
            'warning': '#f39c12',   # Orange
            'info': '#3498db',      # Blue
            'success': '#27ae60'    # Green
        }
        
        # Icons (using Unicode symbols that work in email)
        icons = {
            'critical': '',
            'warning': '',
            'info': '',
            'success': '',
            'pool': '',
            'chemistry': '',
            'alert': '',
            'health': ''
        }
        
        # Get notification color
        if notification_type == 'critical_alert':
            color = colors['critical']
            icon = icons['critical']
            title = 'CRITICAL SAFETY ALERT'
        elif notification_type == 'warning_alert':
            color = colors['warning']
            icon = icons['warning']
            title = 'Water Chemistry Warning'
        elif notification_type in ['reading_saved', 'readings_saved']:
            color = colors['success']
            icon = icons['success']
            title = 'Pool Reading Saved'
        elif notification_type == 'adjustments':
            color = colors['info']
            icon = icons['chemistry']
            title = 'Chemical Adjustments Recommended'
        else:
            color = colors['info']
            icon = icons['info']
            title = 'Pool Chemistry Notification'
        
        # Build HTML email
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, {color} 0%, {self._darken_color(color)} 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .icon {{
            font-size: 48px;
            margin-bottom: 10px;
        }}
        .content {{
            padding: 30px;
        }}
        .pool-name {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
        }}
        .alert-box {{
            background-color: #fff3cd;
            border-left: 4px solid {color};
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .critical-box {{
            background-color: #f8d7da;
            border-left: 4px solid #e74c3c;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .success-box {{
            background-color: #d4edda;
            border-left: 4px solid #27ae60;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .info-box {{
            background-color: #d1ecf1;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }}
        .metric:last-child {{
            border-bottom: none;
        }}
        .metric-name {{
            font-weight: 600;
            color: #2c3e50;
        }}
        .metric-value {{
            color: #7f8c8d;
        }}
        .status-badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .status-critical {{
            background-color: #e74c3c;
            color: white;
        }}
        .status-warning {{
            background-color: #f39c12;
            color: white;
        }}
        .status-good {{
            background-color: #27ae60;
            color: white;
        }}
        .health-score {{
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .health-score-value {{
            font-size: 48px;
            font-weight: 700;
            margin: 10px 0;
        }}
        .adjustment {{
            background-color: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid {color};
        }}
        .adjustment-chemical {{
            font-weight: 600;
            color: #2c3e50;
            font-size: 16px;
            margin-bottom: 5px;
        }}
        .adjustment-amount {{
            color: {color};
            font-size: 18px;
            font-weight: 700;
            margin: 5px 0;
        }}
        .adjustment-reason {{
            color: #7f8c8d;
            font-size: 14px;
            margin-top: 5px;
        }}
        .footer {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 12px;
        }}
        .footer a {{
            color: #3498db;
            text-decoration: none;
        }}
        .timestamp {{
            color: #95a5a6;
            font-size: 12px;
            text-align: center;
            margin-top: 10px;
        }}
        .action-button {{
            display: inline-block;
            padding: 12px 30px;
            background-color: {color};
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: 600;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="icon">{icon}</div>
            <h1>{title}</h1>
        </div>
        
        <div class="content">
            <div class="pool-name">
                {icons['pool']} {self.config.get('pool_name', 'My Pool')}
            </div>
"""
        
        # Add content based on notification type
        if notification_type == 'critical_alert':
            html += self._build_critical_alert_content(data, icons)
        elif notification_type == 'warning_alert':
            html += self._build_warning_alert_content(data, icons)
        elif notification_type in ['reading_saved', 'readings_saved']:
            html += self._build_reading_saved_content(data, icons)
        elif notification_type == 'adjustments':
            html += self._build_adjustments_content(data, icons, color)
        
        # Add timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        html += f"""
            <div class="timestamp">
                {icons['info']} Sent on {timestamp}
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Deep Blue Pool Chemistry Management System</strong></p>
            <p>Copyright  2024 Michael Hayes. All rights reserved.</p>
            <p style="margin-top: 10px;">
                This is an automated notification from your pool monitoring system.
            </p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def _build_critical_alert_content(self, data, icons):
        """Build content for critical alerts"""
        html = f"""
            <div class="critical-box">
                <h2 style="margin-top: 0; color: #e74c3c;">{icons['alert']} DO NOT SWIM!</h2>
                <p style="font-size: 16px; font-weight: 600;">
                    Critical water chemistry conditions detected. Swimming is unsafe until corrected.
                </p>
            </div>
"""
        
        if 'parameters' in data:
            html += '<div style="margin: 20px 0;">'
            for param, value in data['parameters'].items():
                html += f"""
                <div class="metric">
                    <span class="metric-name">{param}</span>
                    <span class="metric-value">{value} <span class="status-badge status-critical">CRITICAL</span></span>
                </div>
"""
            html += '</div>'
        
        if 'danger' in data:
            html += f"""
            <div class="alert-box">
                <h3 style="margin-top: 0;">{icons['warning']} Danger</h3>
                <p>{data['danger']}</p>
            </div>
"""
        
        if 'action' in data:
            html += f"""
            <div class="info-box">
                <h3 style="margin-top: 0;">{icons['chemistry']} Required Actions</h3>
                <p style="font-weight: 600;">{data['action']}</p>
            </div>
"""
        
        return html
    
    def _build_warning_alert_content(self, data, icons):
        """Build content for warning alerts"""
        html = f"""
            <div class="alert-box">
                <h2 style="margin-top: 0; color: #f39c12;">{icons['warning']} Attention Needed</h2>
                <p style="font-size: 16px;">
                    Your pool water chemistry needs adjustment.
                </p>
            </div>
"""
        
        if 'parameters' in data:
            html += '<div style="margin: 20px 0;">'
            for param, value in data['parameters'].items():
                html += f"""
                <div class="metric">
                    <span class="metric-name">{param}</span>
                    <span class="metric-value">{value} <span class="status-badge status-warning">WARNING</span></span>
                </div>
"""
            html += '</div>'
        
        if 'action' in data:
            html += f"""
            <div class="info-box">
                <h3 style="margin-top: 0;">{icons['chemistry']} Recommended Actions</h3>
                <p>{data['action']}</p>
            </div>
"""
        
        return html
    
    def _build_reading_saved_content(self, data, icons):
        """Build content for reading saved notifications"""
        html = f"""
            <div class="success-box">
                <h2 style="margin-top: 0; color: #27ae60;">{icons['success']} Reading Saved Successfully</h2>
                <p>Your pool chemistry reading has been recorded.</p>
            </div>
"""
        
        # Add health score if available
        if 'health_score' in data:
            score = data['health_score']
            if score >= 90:
                status = 'Excellent'
                status_class = 'status-good'
            elif score >= 70:
                status = 'Good'
                status_class = 'status-good'
            elif score >= 50:
                status = 'Fair'
                status_class = 'status-warning'
            else:
                status = 'Poor'
                status_class = 'status-critical'
            
            html += f"""
            <div class="health-score">
                <div>{icons['health']} Pool Health Score</div>
                <div class="health-score-value">{score}</div>
                <div>out of 100</div>
                <div style="margin-top: 10px;">
                    <span class="status-badge {status_class}">{status}</span>
                </div>
            </div>
"""
        
        # Add readings if available
        if 'readings' in data:
            html += '<h3>Current Readings</h3><div style="margin: 20px 0;">'
            for param, value in data['readings'].items():
                html += f"""
                <div class="metric">
                    <span class="metric-name">{param}</span>
                    <span class="metric-value">{value}</span>
                </div>
"""
            html += '</div>'
        
        return html
    
    def _build_adjustments_content(self, data, icons, color):
        """Build content for chemical adjustments"""
        html = f"""
            <div class="info-box">
                <h2 style="margin-top: 0; color: #3498db;">{icons['chemistry']} Chemical Adjustments Recommended</h2>
                <p>The following adjustments will optimize your pool chemistry:</p>
            </div>
"""
        
        if 'adjustments' in data:
            html += '<div style="margin: 20px 0;">'
            for adj in data['adjustments']:
                html += f"""
                <div class="adjustment">
                    <div class="adjustment-chemical">{adj.get('chemical', 'Chemical')}</div>
                    <div class="adjustment-amount">Add: {adj.get('amount', 'N/A')}</div>
                    <div class="adjustment-reason">{adj.get('reason', '')}</div>
                </div>
"""
            html += '</div>'
        
        return html
    
    def _darken_color(self, hex_color):
        """Darken a hex color by 20%"""
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Darken by 20%
        r = int(r * 0.8)
        g = int(g * 0.8)
        b = int(b * 0.8)
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'

    def send_sms(self, message: str) -> Tuple[bool, str]:
        """
        Send an SMS notification.
        
        Args:
            message: SMS message text
            
        Returns:
            Tuple of (success, message)
        """
        if not self.config.get('sms_enabled', False):
            return False, "SMS notifications are disabled"
        
        if not TWILIO_AVAILABLE:
            return False, "Twilio library not installed. Run: pip install twilio"
        
        if not self.twilio_client:
            return False, "Twilio not configured properly"
        
        try:
            from_number = self.config.get('twilio_phone_number', '')
            to_numbers = self.config.get('to_phone_numbers', [])
            
            if not from_number:
                return False, "Twilio phone number not configured"
            
            if not to_numbers:
                return False, "No recipient phone numbers configured"
            
            # Add pool name to message if enabled
            if self.config.get('include_pool_name', True):
                pool_name = self.config.get('pool_name', 'My Pool')
                message = f"[{pool_name}] {message}"
            
            # Send to all configured numbers
            sent_count = 0
            errors = []
            
            for to_number in to_numbers:
                try:
                    self.twilio_client.messages.create(
                        body=message,
                        from_=from_number,
                        to=to_number
                    )
                    sent_count += 1
                except Exception as e:
                    errors.append(f"{to_number}: {str(e)}")
            
            if sent_count > 0:
                logger.info(f"SMS sent to {sent_count} recipient(s)")
                if errors:
                    return True, f"Sent to {sent_count} recipient(s), {len(errors)} failed"
                return True, f"SMS sent to {sent_count} recipient(s)"
            else:
                error_msg = f"Failed to send SMS: {', '.join(errors)}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error sending SMS: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    
    def _create_reading_saved_email_template(self, data):
        """
        Create email template for reading_saved notifications
        Matches the green success design from screenshot
        """
        
        # Get pool name
        pool_name = self.config.get('pool_name', 'My Pool')
        
        # Get health score
        health_score = data.get('health_score', 0)
        
        # Determine status
        if health_score >= 90:
            status = 'EXCELLENT'
            status_class = 'status-good'
        elif health_score >= 70:
            status = 'GOOD'
            status_class = 'status-good'
        elif health_score >= 50:
            status = 'FAIR'
            status_class = 'status-warning'
        else:
            status = 'POOR'
            status_class = 'status-critical'
        
        # Build HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .icon {{
            font-size: 48px;
            margin-bottom: 10px;
        }}
        .content {{
            padding: 30px;
        }}
        .pool-name {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
        }}
        .success-box {{
            background-color: #d4edda;
            border-left: 4px solid #27ae60;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .health-score {{
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .health-score-value {{
            font-size: 48px;
            font-weight: 700;
            margin: 10px 0;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }}
        .metric:last-child {{
            border-bottom: none;
        }}
        .metric-name {{
            font-weight: 600;
            color: #2c3e50;
        }}
        .metric-value {{
            color: #7f8c8d;
        }}
        .status-badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .status-good {{
            background-color: #27ae60;
            color: white;
        }}
        .status-warning {{
            background-color: #f39c12;
            color: white;
        }}
        .status-critical {{
            background-color: #e74c3c;
            color: white;
        }}
        .footer {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 12px;
        }}
        .timestamp {{
            color: #95a5a6;
            font-size: 12px;
            text-align: center;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="icon">[CHECK]</div>
            <h1>Pool Reading Saved</h1>
        </div>
        
        <div class="content">
            <div class="pool-name">
                [SWIM] {pool_name}
            </div>
            
            <div class="success-box">
                <h2 style="margin-top: 0; color: #27ae60;">[CHECK] Reading Saved Successfully</h2>
                <p>Your pool chemistry reading has been recorded.</p>
            </div>
            
            <div class="health-score">
                <div>[HEART] Pool Health Score</div>
                <div class="health-score-value">{health_score}</div>
                <div>out of 100</div>
                <div style="margin-top: 10px;">
                    <span class="status-badge {status_class}">{status}</span>
                </div>
            </div>
            
            <h3>Current Readings</h3>
            <div style="margin: 20px 0;">
"""
        
        # Add readings
        if 'readings' in data:
            readings = data['readings']
            
            # Define order and formatting
            reading_order = [
                ('pH', 'pH', ''),
                ('free_chlorine', 'Free Chlorine', ' ppm'),
                ('total_chlorine', 'Total Chlorine', ' ppm'),
                ('alkalinity', 'Alkalinity', ' ppm'),
                ('calcium_hardness', 'Calcium Hardness', ' ppm'),
                ('cyanuric_acid', 'Cyanuric Acid', ' ppm'),
                ('temperature', 'Temperature', 'F'),
                ('orp', 'ORP', ' mV'),
                ('bromine', 'Bromine', ' ppm'),
                ('salt', 'Salt/TDS', ' ppm')
            ]
            
            for key, display_name, unit in reading_order:
                if key in readings and readings[key]:
                    value = readings[key]
                    # Format temperature with degree symbol
                    if key == 'temperature':
                        formatted_value = f"{value}[DEGREE]{unit}"
                    else:
                        formatted_value = f"{value}{unit}"
                    
                    html += f"""
                <div class="metric">
                    <span class="metric-name">{display_name}</span>
                    <span class="metric-value">{formatted_value}</span>
                </div>
"""
        
        # Add timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        html += f"""
            </div>
            
            <div class="timestamp">
                [INFO] Sent on {timestamp}
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Deep Blue Pool Chemistry Management System</strong></p>
            <p>Copyright 2024 Michael Hayes. All rights reserved.</p>
            <p style="margin-top: 10px;">
                This is an automated notification from your pool monitoring system.
            </p>
        </div>
    </div>
</body>
</html>
"""
        
        return html


    def _create_email_template_from_screenshot(self, notification_type, data):
        """
        Create email template that matches the screenshot EXACTLY
        This is for reading_saved notifications
        """
        
        # Get pool name
        pool_name = self.config.get('pool_name', 'My Pool')
        
        # Color scheme from screenshot
        header_blue = '#3498db'
        dark_footer = '#2c3e50'
        light_blue_box = '#d1ecf1'
        light_gray = '#ecf0f1'
        
        # Build HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 500px;
            margin: 0 auto;
            padding: 0;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            overflow: hidden;
        }}
        .header {{
            background-color: {header_blue};
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 20px;
            font-weight: 600;
        }}
        .pool-name {{
            background-color: {light_gray};
            padding: 15px;
            text-align: center;
            font-size: 16px;
            font-weight: 600;
            color: #2c3e50;
        }}
        .info-box {{
            background-color: {light_blue_box};
            padding: 15px;
            margin: 20px;
            border-left: 4px solid {header_blue};
        }}
        .info-title {{
            color: {header_blue};
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 10px;
        }}
        .chemical-card {{
            background-color: white;
            padding: 15px;
            margin: 15px 20px;
            border-left: 4px solid {header_blue};
        }}
        .chemical-name {{
            font-weight: 600;
            color: #2c3e50;
            font-size: 14px;
            margin-bottom: 5px;
        }}
        .chemical-amount {{
            color: {header_blue};
            font-size: 18px;
            font-weight: 700;
            margin: 8px 0;
        }}
        .chemical-details {{
            color: #7f8c8d;
            font-size: 13px;
            margin-top: 5px;
        }}
        .instructions-box {{
            background-color: {light_blue_box};
            padding: 15px;
            margin: 20px;
        }}
        .instructions-title {{
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .instructions-box ol {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .instructions-box li {{
            margin: 5px 0;
            color: #2c3e50;
        }}
        .timestamp {{
            text-align: center;
            color: #95a5a6;
            font-size: 12px;
            padding: 10px;
        }}
        .footer {{
            background-color: {dark_footer};
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 12px;
        }}
        .footer p {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            Chemical Adjustments Recommended
        </div>
        
        <div class="pool-name">
            🏊 {pool_name}
        </div>
        
        <div class="info-box">
            <div class="info-title">🧪 Chemical Adjustments Recommended</div>
            <div>The following adjustments will optimize your pool chemistry:</div>
        </div>
"""
        
        # Add chemical adjustments if provided
        if 'adjustments' in data and data['adjustments']:
            for adj in data['adjustments']:
                chemical = adj.get('chemical', 'Chemical')
                amount = adj.get('amount', 'N/A')
                current = adj.get('current', 'N/A')
                target = adj.get('target', 'N/A')
                ideal_range = adj.get('ideal_range', 'N/A')
                
                html += f"""
        <div class="chemical-card">
            <div class="chemical-name">{chemical}</div>
            <div class="chemical-amount">Add: {amount}</div>
            <div class="chemical-details">Current: {current} → Target: {target} (ideal range: {ideal_range})</div>
        </div>
"""
        
        # Add application instructions
        html += """
        <div class="instructions-box">
            <div class="instructions-title">📋 Application Instructions</div>
            <ol>
                <li>Add chemicals one at a time</li>
                <li>Wait 4 hours between additions</li>
                <li>Run pump for 8 hours after adding chemicals</li>
                <li>Retest water chemistry after 24 hours</li>
                <li>Always follow product label instructions</li>
            </ol>
        </div>
"""
        
        # Add timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        html += f"""
        <div class="timestamp">
            📅 Sent on {timestamp}
        </div>
        
        <div class="footer">
            <p><strong>Deep Blue Pool Chemistry Management System</strong></p>
            <p>Copyright © 2024 Michael Hayes. All rights reserved.</p>
            <p style="margin-top: 10px;">
                This is an automated notification from your pool monitoring system.
            </p>
        </div>
    </div>
</body>
</html>
"""
        
        return html

    def send_notification(self, notification_type: str, data: Dict) -> Dict[str, Tuple[bool, str]]:
        """
        Send a notification via configured channels.
        
        Args:
            notification_type: Type of notification (critical_alert, warning_alert, etc.)
            data: Notification data
            
        Returns:
            Dictionary with results for each channel
        """
        results = {}
        
        # Check if this notification type is enabled
        pref_key = f"notify_{notification_type}"
        if not self.config.get(pref_key, False):
            return {'skipped': (False, f"Notifications for {notification_type} are disabled")}
        
        # Generate message content
        subject, body, html_body = self._generate_message(notification_type, data)
        
        # Send email if enabled
        if self.config.get('email_enabled', False):
            results['email'] = self.send_email(subject, body, html_body)
        
        # Send SMS if enabled
        if self.config.get('sms_enabled', False):
            # SMS gets a shorter version
            sms_message = self._generate_sms_message(notification_type, data)
            results['sms'] = self.send_sms(sms_message)
        
        return results
    
    def _generate_message(self, notification_type: str, data: Dict) -> Tuple[str, str, str]:
        """
        Generate email subject, body, and HTML body using professional templates.
        
        Args:
            notification_type: Type of notification
            data: Notification data
            
        Returns:
            Tuple of (subject, plain_body, html_body)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        
        # Each notification type will generate its own HTML
        html_body = None
        
        if notification_type == 'critical_alert':
            subject = "CRITICAL POOL ALERT - Immediate Action Required"
            html_body = self._create_professional_email_html(notification_type, data)
            body = f"""CRITICAL POOL CHEMISTRY ALERT
Time: {timestamp}

{data.get('message', 'Critical condition detected')}

DANGER: {data.get('danger', 'Pool may be unsafe for swimming')}

IMMEDIATE ACTION REQUIRED:
{data.get('action', 'Check pool chemistry immediately')}

Affected Parameters:
{self._format_parameters(data.get('parameters', {}))}

This is an automated alert from Deep Blue Pool Chemistry Management System.
"""
            
            html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background-color: #dc3545; color: white; padding: 20px; text-align: center;">
        <h1 style="margin: 0;">CRITICAL POOL ALERT</h1>
        <p style="margin: 5px 0;">Immediate Action Required</p>
    </div>
    <div style="padding: 20px; background-color: #f8f9fa;">
        <p><strong>Time:</strong> {timestamp}</p>
        <div style="background-color: white; padding: 15px; border-left: 4px solid #dc3545; margin: 15px 0;">
            <p style="margin: 0;"><strong>{data.get('message', 'Critical condition detected')}</strong></p>
        </div>
        <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 15px 0;">
            <p style="margin: 0;"><strong>DANGER:</strong> {data.get('danger', 'Pool may be unsafe for swimming')}</p>
        </div>
        <div style="background-color: white; padding: 15px; margin: 15px 0;">
            <h3 style="color: #dc3545;">Immediate Action Required:</h3>
            <p>{data.get('action', 'Check pool chemistry immediately')}</p>
        </div>
        <div style="background-color: white; padding: 15px; margin: 15px 0;">
            <h3>Affected Parameters:</h3>
            {self._format_parameters_html(data.get('parameters', {}))}
        </div>
    </div>
    <div style="background-color: #343a40; color: white; padding: 10px; text-align: center; font-size: 12px;">
        <p style="margin: 0;">Deep Blue Pool Chemistry Management System</p>
        <p style="margin: 5px 0;">Copyright (c) 2024 Michael Hayes. All rights reserved.</p>
    </div>
</body>
</html>
"""
        
        elif notification_type == 'warning_alert':
            subject = "Pool Chemistry Warning - Attention Needed"
            html_body = self._create_professional_email_html(notification_type, data)
            body = f"""POOL CHEMISTRY WARNING
Time: {timestamp}

{data.get('message', 'Warning condition detected')}

CAUTION: {data.get('caution', 'Pool chemistry needs attention')}

RECOMMENDED ACTION:
{data.get('action', 'Adjust pool chemistry soon')}

Affected Parameters:
{self._format_parameters(data.get('parameters', {}))}

This is an automated alert from Deep Blue Pool Chemistry Management System.
"""
            
            html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background-color: #ffc107; color: #212529; padding: 20px; text-align: center;">
        <h1 style="margin: 0;">Pool Chemistry Warning</h1>
        <p style="margin: 5px 0;">Attention Needed</p>
    </div>
    <div style="padding: 20px; background-color: #f8f9fa;">
        <p><strong>Time:</strong> {timestamp}</p>
        <div style="background-color: white; padding: 15px; border-left: 4px solid #ffc107; margin: 15px 0;">
            <p style="margin: 0;"><strong>{data.get('message', 'Warning condition detected')}</strong></p>
        </div>
        <div style="background-color: #fff3cd; padding: 15px; margin: 15px 0;">
            <p style="margin: 0;"><strong>CAUTION:</strong> {data.get('caution', 'Pool chemistry needs attention')}</p>
        </div>
        <div style="background-color: white; padding: 15px; margin: 15px 0;">
            <h3 style="color: #ffc107;">Recommended Action:</h3>
            <p>{data.get('action', 'Adjust pool chemistry soon')}</p>
        </div>
        <div style="background-color: white; padding: 15px; margin: 15px 0;">
            <h3>Affected Parameters:</h3>
            {self._format_parameters_html(data.get('parameters', {}))}
        </div>
    </div>
    <div style="background-color: #343a40; color: white; padding: 10px; text-align: center; font-size: 12px;">
        <p style="margin: 0;">Deep Blue Pool Chemistry Management System</p>
        <p style="margin: 5px 0;">Copyright (c) 2024 Michael Hayes. All rights reserved.</p>
    </div>
</body>
</html>
"""
        
        elif notification_type in ['reading_saved', 'readings_saved']:
            subject = "Pool Reading Saved Successfully"
            body = f"""Pool Reading Saved
Time: {timestamp}

A new pool chemistry reading has been recorded.

Current Readings:
{self._format_parameters(data.get('readings', {}))}

Pool Health Score: {data.get('health_score', 'N/A')}/100

This is an automated notification from Deep Blue Pool Chemistry Management System.
"""
            
            # Use new professional template
            html_body = self._create_reading_saved_email_template(data)
        
        elif notification_type == 'chemical_adjustments':
            subject = "Chemical Adjustments Recommended"
            body = f"""Chemical Adjustments Recommended
Time: {timestamp}

The following chemical adjustments are recommended for your pool:

{self._format_adjustments(data.get('adjustments', []))}

This is an automated notification from Deep Blue Pool Chemistry Management System.
"""
            
            html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background-color: #17a2b8; color: white; padding: 20px; text-align: center;">
        <h1 style="margin: 0;">Chemical Adjustments Recommended</h1>
    </div>
    <div style="padding: 20px; background-color: #f8f9fa;">
        <p><strong>Time:</strong> {timestamp}</p>
        <div style="background-color: white; padding: 15px; margin: 15px 0;">
            <h3>Recommended Adjustments:</h3>
            {self._format_adjustments_html(data.get('adjustments', []))}
        </div>
    </div>
    <div style="background-color: #343a40; color: white; padding: 10px; text-align: center; font-size: 12px;">
        <p style="margin: 0;">Deep Blue Pool Chemistry Management System</p>
        <p style="margin: 5px 0;">Copyright (c) 2024 Michael Hayes. All rights reserved.</p>
    </div>
</body>
</html>
"""
        
        else:
            subject = "Pool Chemistry Notification"
            body = f"""Pool Chemistry Notification
Time: {timestamp}

{data.get('message', 'Notification from Deep Blue Pool Chemistry')}

This is an automated notification from Deep Blue Pool Chemistry Management System.
"""
            html_body = None
        
        return subject, body, html_body
    
    def _generate_sms_message(self, notification_type: str, data: Dict) -> str:
        """Generate short SMS message."""
        if notification_type == 'critical_alert':
            return f"CRITICAL ALERT: {data.get('message', 'Pool unsafe')}. Check immediately!"
        elif notification_type == 'warning_alert':
            return f"WARNING: {data.get('message', 'Pool needs attention')}. Adjust chemistry soon."
        elif notification_type in ['reading_saved', 'readings_saved']:
            score = data.get('health_score', 'N/A')
            return f"Pool reading saved. Health score: {score}/100"
        elif notification_type == 'chemical_adjustments':
            return f"Chemical adjustments recommended. Check Deep Blue app for details."
        else:
            return data.get('message', 'Pool notification')
    
    def _format_parameters(self, parameters: Dict) -> str:
        """Format parameters for plain text."""
        if not parameters:
            return "No parameters provided"
        
        lines = []
        for key, value in parameters.items():
            lines.append(f"  - {key}: {value}")
        return "\n".join(lines)
    
    def _format_parameters_html(self, parameters: Dict) -> str:
        """Format parameters for HTML."""
        if not parameters:
            return "<p>No parameters provided</p>"
        
        html = "<table style='width: 100%; border-collapse: collapse;'>"
        for key, value in parameters.items():
            html += f"""
            <tr style='border-bottom: 1px solid #dee2e6;'>
                <td style='padding: 8px; font-weight: bold;'>{key}</td>
                <td style='padding: 8px;'>{value}</td>
            </tr>
            """
        html += "</table>"
        return html
    
    def _format_adjustments(self, adjustments: List[Dict]) -> str:
        """Format adjustments for plain text."""
        if not adjustments:
            return "No adjustments needed"
        
        lines = []
        for adj in adjustments:
            chemical = adj.get('chemical', 'Unknown')
            action = adj.get('action', 'Unknown')
            amount = adj.get('amount', 'Unknown')
            lines.append(f"  - {chemical}: {action} {amount}")
        return "\n".join(lines)
    
    def _format_adjustments_html(self, adjustments: List[Dict]) -> str:
        """Format adjustments for HTML."""
        if not adjustments:
            return "<p>No adjustments needed</p>"
        
        html = "<table style='width: 100%; border-collapse: collapse;'>"
        for adj in adjustments:
            chemical = adj.get('chemical', 'Unknown')
            action = adj.get('action', 'Unknown')
            amount = adj.get('amount', 'Unknown')
            html += f"""
            <tr style='border-bottom: 1px solid #dee2e6;'>
                <td style='padding: 8px; font-weight: bold;'>{chemical}</td>
                <td style='padding: 8px;'>{action} {amount}</td>
            </tr>
            """
        html += "</table>"
        return html
    
    def test_email(self) -> Tuple[bool, str]:
        """Send a test email."""
        return self.send_email(
            "Test Email from Deep Blue",
            "This is a test email from Deep Blue Pool Chemistry Management System.\n\nIf you received this, your email configuration is working correctly!",
            "<html><body><h2>Test Email</h2><p>This is a test email from Deep Blue Pool Chemistry Management System.</p><p>If you received this, your email configuration is working correctly!</p></body></html>"
        )
    
    def test_sms(self) -> Tuple[bool, str]:
        """Send a test SMS."""
        return self.send_sms("Test SMS from Deep Blue Pool Chemistry. Your SMS configuration is working!")


if __name__ == "__main__":
    # Test the messaging service
    service = MessagingService()
    print("Messaging Service initialized")
    print(f"Email enabled: {service.config.get('email_enabled', False)}")
    print(f"SMS enabled: {service.config.get('sms_enabled', False)}")
    print(f"Twilio available: {TWILIO_AVAILABLE}")