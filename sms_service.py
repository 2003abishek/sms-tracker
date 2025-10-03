from twilio.rest import Client
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

class SMSService:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.server_url = os.getenv('SERVER_URL', 'http://localhost:8501')
        
        # Check if Twilio credentials are configured
        self.twilio_configured = all([self.account_sid, self.auth_token, self.phone_number])
        
        if self.twilio_configured:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                # Test credentials by making a simple API call
                self.client.api.accounts(self.account_sid).fetch()
            except Exception as e:
                st.error(f"Twilio configuration error: {e}")
                self.twilio_configured = False
                self.client = None
        else:
            self.client = None
            st.warning("⚠️ Twilio not configured - SMS features disabled")
    
    def send_tracking_request(self, recipient_phone, tracking_id, custom_message=None):
        tracking_url = f"{self.server_url}/?tracking_id={tracking_id}"
        
        # Demo mode - show tracking URL instead of sending SMS
        if not self.twilio_configured:
            return {
                'success': True,  # Change to True to continue without SMS
                'sms_sent': False,
                'tracking_url': tracking_url,
                'message': 'DEMO MODE: Copy this URL to share manually',
                'debug_info': {
                    'formatted_phone': recipient_phone,
                    'demo_mode': True
                }
            }
        
        try:
            # Format phone number (remove spaces, ensure + format)
            recipient_phone = recipient_phone.strip().replace(' ', '')
            if not recipient_phone.startswith('+'):
                recipient_phone = '+' + recipient_phone
            
            message_body = f"{custom_message or 'Please share your location for safety reasons.'}\n\nShare your location here: {tracking_url}\n\nThis link will expire in 24 hours."
            
            message = self.client.messages.create(
                body=message_body,
                from_=self.phone_number,
                to=recipient_phone
            )
            
            return {
                'success': True,
                'message_sid': message.sid,
                'tracking_url': tracking_url,
                'message': 'SMS sent successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'tracking_url': tracking_url,
                'message': f'SMS failed: {str(e)}'
            }

sms_service = SMSService()

