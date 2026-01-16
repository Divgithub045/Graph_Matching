import os
import logging
import csv
import re
from typing import List, Dict, Optional
from datetime import datetime
from mailersend import emails
import pandas as pd

logger = logging.getLogger(__name__)

class EmailAutomationHandler:
    def __init__(self):
        self.api_key = os.getenv("MAILERSEND_API_KEY")
        self.from_email = os.getenv("MAIL_FROM", "noreply@trial-3z0vklo7vvx4jy5k.mlsender.net")
        self.from_name = os.getenv("MAIL_FROM_NAME", "ReLoop Team")
        
        if not self.api_key:
            logger.error("MAILERSEND_API_KEY not found in environment variables")
            raise ValueError("MAILERSEND_API_KEY is required")
        
        self.mailer = emails.NewEmail(self.api_key)
        self.deals_csv = "output/email_deals.csv"
        self.email_log_csv = "output/email_log.csv"
        self._ensure_csv_files()
        logger.info(f"MailerSend email handler initialized with from_email: {self.from_email}")
    
    def _ensure_csv_files(self):
        """Create CSV files with headers if they don't exist"""
        os.makedirs(os.path.dirname(self.deals_csv), exist_ok=True)
        
        if not os.path.exists(self.deals_csv):
            with open(self.deals_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'deal_id', 'buyer_id', 'buyer_email', 'buyer_company', 'buyer_contact_name',
                    'status', 'match_score', 'facility_location', 'facility_industry',
                    'waste_types', 'total_waste_volume_tons', 'clarification_count',
                    'created_at', 'last_updated'
                ])
        
        if not os.path.exists(self.email_log_csv):
            with open(self.email_log_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'log_id', 'deal_id', 'buyer_email', 'email_type',
                    'subject', 'sent_at', 'status'
                ])
    
    def _generate_deal_id(self) -> str:
        """Generate unique deal ID"""
        try:
            df = pd.read_csv(self.deals_csv)
            if len(df) > 0:
                last_id = df['deal_id'].iloc[-1]
                id_number = int(last_id.replace('DEAL', '')) + 1
                return f"DEAL{id_number:03d}"
            return "DEAL001"
        except:
            return "DEAL001"
    
    def _generate_log_id(self) -> str:
        """Generate unique log ID"""
        try:
            df = pd.read_csv(self.email_log_csv)
            if len(df) > 0:
                last_id = df['log_id'].iloc[-1]
                id_number = int(last_id.replace('LOG', '')) + 1
                return f"LOG{id_number:04d}"
            return "LOG0001"
        except:
            return "LOG0001"
    
    def _get_deal_by_email(self, buyer_email: str) -> Optional[Dict]:
        """Get deal record by buyer email"""
        try:
            df = pd.read_csv(self.deals_csv)
            deal = df[df['buyer_email'].str.lower() == buyer_email.lower()]
            if not deal.empty:
                return deal.iloc[0].to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting deal: {e}")
            return None
    
    def _update_deal_status(self, buyer_email: str, status: str, increment_clarification: bool = False):
        """Update deal status in CSV"""
        try:
            df = pd.read_csv(self.deals_csv)
            mask = df['buyer_email'].str.lower() == buyer_email.lower()
            
            if mask.any():
                df.loc[mask, 'status'] = status
                df.loc[mask, 'last_updated'] = datetime.now().isoformat()
                
                if increment_clarification:
                    df.loc[mask, 'clarification_count'] = df.loc[mask, 'clarification_count'] + 1
                
                df.to_csv(self.deals_csv, index=False)
                logger.info(f"Updated deal status for {buyer_email} to {status}")
        except Exception as e:
            logger.error(f"Error updating deal: {e}")
    
    def _log_email(self, deal_id: str, buyer_email: str, email_type: str, subject: str, status: str = "sent"):
        """Log email activity to CSV"""
        try:
            log_id = self._generate_log_id()
            
            with open(self.email_log_csv, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    log_id, deal_id, buyer_email, email_type,
                    subject, datetime.now().isoformat(), status
                ])
            logger.info(f"Logged email: {log_id}")
        except Exception as e:
            logger.error(f"Error logging email: {e}")
    
    async def send_initial_opportunity_email(
        self,
        buyer_email: str,
        buyer_name: str,
        buyer_company: str,
        buyer_id: str,
        waste_profile: dict,
        match_score: float,
        facility_location: str,
        facility_industry: str
    ) -> dict:
        """Send initial opportunity email to buyer"""
        try:
            waste_streams = waste_profile.get('waste_streams', [])
            waste_details = "<br>".join([
                f"• {ws.get('type', 'Unknown')}: {ws.get('quantity_min_tons', 0)}-{ws.get('quantity_max_tons', 0)} tons/month "
                f"({ws.get('quality_grade', 'N/A')}, {ws.get('hazard_class', 'N/A')})"
                for ws in waste_streams[:3]
            ])
            
            total_volume = sum([ws.get('quantity_max_tons', 0) for ws in waste_streams])
            waste_types = ", ".join([ws.get('type', 'Unknown') for ws in waste_streams])
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #0d9488 0%, #06b6d4 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .highlight {{ background: #e0f2f1; padding: 15px; border-left: 4px solid #0d9488; margin: 20px 0; }}
                    .score {{ font-size: 36px; color: #0d9488; font-weight: bold; }}
                    .keywords {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                    .keyword {{ display: inline-block; background: #0d9488; color: white; padding: 5px 15px; margin: 5px; border-radius: 20px; }}
                    .footer {{ text-align: center; color: #6c757d; padding: 20px; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔄 New Circular Economy Opportunity</h1>
                    </div>
                    <div class="content">
                        <p>Dear {buyer_name},</p>
                        <p>Our AI-powered matching platform has identified a <strong>high-compatibility opportunity</strong> between your material requirements and a waste stream from a {facility_industry} facility in {facility_location}.</p>
                        <div class="highlight">
                            <h3>Match Score: <span class="score">{match_score}/100</span></h3>
                        </div>
                        <h3>📊 Opportunity Details:</h3>
                        <div class="highlight">{waste_details}</div>
                        <p><strong>Location:</strong> {facility_location}</p>
                        <p><strong>Industry:</strong> {facility_industry}</p>
                        <p><strong>AI Confidence:</strong> {waste_profile.get('overall_confidence', 0) * 100:.0f}%</p>
                        <div class="keywords">
                            <h3>⚡ Quick Response Required</h3>
                            <p>Please reply to this email with ONE of these keywords to proceed:</p>
                            <div>
                                <span class="keyword">Ready to deal</span>
                                <span class="keyword">Need Clarification</span>
                                <span class="keyword">Not interested</span>
                            </div>
                            <p style="margin-top: 10px;"><em>Simply type the keyword in your reply email body. Our system will automatically process your response.</em></p>
                        </div>
                        <p><strong>Next Steps:</strong></p>
                        <ul>
                            <li><strong>Ready to deal:</strong> We'll connect you directly with the facility</li>
                            <li><strong>Need Clarification:</strong> We'll provide additional details</li>
                            <li><strong>Not interested:</strong> We'll note your preference and search for better matches</li>
                        </ul>
                        <p>This opportunity is time-sensitive. Please respond within 48 hours to secure this match.</p>
                        <p>Best regards,<br><strong>{self.from_name}</strong><br>Circular Economy Platform</p>
                    </div>
                    <div class="footer">
                        <p>© 2026 ReLoop - Powering Sustainable Industry</p>
                        <p>Buyer ID: {buyer_id} | Match Reference: {datetime.now().strftime('%Y%m%d-%H%M%S')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            subject = f"🔄 High-Priority Match: {match_score}/100 Score - {facility_industry} Waste Stream"
            
            # Setup MailerSend email
            mail_body = {}
            
            self.mailer.set_mail_from({"name": self.from_name, "email": self.from_email}, mail_body)
            self.mailer.set_mail_to([{"name": buyer_name, "email": buyer_email}], mail_body)
            self.mailer.set_subject(subject, mail_body)
            self.mailer.set_html_content(html_content, mail_body)
            
            # Send email
            response = self.mailer.send(mail_body)
            
            # Generate deal ID
            deal_id = self._generate_deal_id()
            
            # Save deal record to CSV
            with open(self.deals_csv, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    deal_id, buyer_id, buyer_email, buyer_company, buyer_name,
                    'pending', match_score, facility_location, facility_industry,
                    waste_types, total_volume, 0,
                    datetime.now().isoformat(), datetime.now().isoformat()
                ])
            
            # Log email
            self._log_email(deal_id, buyer_email, "initial_opportunity", subject)
            
            logger.info(f"Initial opportunity email sent to {buyer_email}, Deal ID: {deal_id}")
            return {"success": True, "message": "Email sent successfully", "deal_id": deal_id}
        
        except Exception as e:
            logger.error(f"Error sending email to {buyer_email}: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_deal_closed_email(self, buyer_email: str, buyer_name: str, buyer_company: str):
        """Send thank you email when deal is closed"""
        try:
            deal = self._get_deal_by_email(buyer_email)
            if not deal:
                return {"success": False, "error": "Deal not found"}
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .success {{ background: #d4edda; border: 1px solid #c3e6cb; padding: 20px; border-radius: 10px; text-align: center; }}
                    .checkmark {{ font-size: 64px; color: #28a745; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="success">
                        <div class="checkmark">✓</div>
                        <h2>Deal Confirmed! 🎉</h2>
                    </div>
                    <p>Dear {buyer_name},</p>
                    <p>Thank you for confirming your interest! We're excited to facilitate this circular economy partnership.</p>
                    <p><strong>Next Steps:</strong></p>
                    <ul>
                        <li>Our team will contact you within 24 hours with facility contact details</li>
                        <li>You'll receive a detailed logistics and compliance document</li>
                        <li>We'll schedule a coordination call if needed</li>
                    </ul>
                    <p>We appreciate your commitment to sustainable waste management!</p>
                    <p>Best regards,<br><strong>{self.from_name}</strong></p>
                </div>
            </body>
            </html>
            """
            
            subject = "✅ Deal Confirmed - Next Steps for Your Circular Economy Partnership"
            
            mail_body = {}
            self.mailer.set_mail_from({"name": self.from_name, "email": self.from_email}, mail_body)
            self.mailer.set_mail_to([{"name": buyer_name, "email": buyer_email}], mail_body)
            self.mailer.set_subject(subject, mail_body)
            self.mailer.set_html_content(html_body, mail_body)
            
            self.mailer.send(mail_body)
            
            # Update deal status
            self._update_deal_status(buyer_email, "closed")
            
            # Log email
            self._log_email(deal['deal_id'], buyer_email, "deal_closed", subject)
            
            logger.info(f"Deal closed email sent to {buyer_email}")
            return {"success": True, "message": "Deal closed email sent"}
        
        except Exception as e:
            logger.error(f"Error sending deal closed email: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_clarification_email(self, buyer_email: str, buyer_name: str, waste_profile: dict):
        """Send clarification email"""
        try:
            deal = self._get_deal_by_email(buyer_email)
            if not deal:
                return {"success": False, "error": "Deal not found"}
            
            waste_streams = waste_profile.get('waste_streams', [])
            detailed_waste = "".join([
                f"<li><strong>{ws.get('type', 'Unknown')}</strong><br>"
                f"Quantity: {ws.get('quantity_min_tons', 0)}-{ws.get('quantity_max_tons', 0)} tons/month<br>"
                f"Quality: {ws.get('quality_grade', 'N/A')}<br>"
                f"Contamination: {ws.get('contamination_pct', 0)}%<br>"
                f"Classification: {ws.get('hazard_class', 'N/A')}</li>"
                for ws in waste_streams
            ])
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .detail {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>📋 Additional Details for Your Review</h2>
                    <p>Dear {buyer_name},</p>
                    <p>Here are the comprehensive details about the waste streams:</p>
                    <div class="detail">
                        <h3>Waste Stream Details:</h3>
                        <ul>{detailed_waste}</ul>
                    </div>
                    <p><strong>Please reply with:</strong></p>
                    <ul>
                        <li><strong>Ready to deal</strong> - If you're satisfied with the details</li>
                        <li><strong>Not interested</strong> - If this doesn't meet your requirements</li>
                    </ul>
                    <p>If you need further clarification, please reply with specific questions.</p>
                    <p>Best regards,<br><strong>{self.from_name}</strong></p>
                </div>
            </body>
            </html>
            """
            
            subject = "📋 Clarification: Detailed Waste Stream Information"
            
            mail_body = {}
            self.mailer.set_mail_from({"name": self.from_name, "email": self.from_email}, mail_body)
            self.mailer.set_mail_to([{"name": buyer_name, "email": buyer_email}], mail_body)
            self.mailer.set_subject(subject, mail_body)
            self.mailer.set_html_content(html_body, mail_body)
            
            self.mailer.send(mail_body)
            
            # Update deal status and increment clarification count
            self._update_deal_status(buyer_email, "need_clarification", increment_clarification=True)
            
            # Log email
            self._log_email(deal['deal_id'], buyer_email, "clarification", subject)
            
            logger.info(f"Clarification email sent to {buyer_email}")
            return {"success": True, "message": "Clarification email sent"}
        
        except Exception as e:
            logger.error(f"Error sending clarification email: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_rejection_email(self, buyer_email: str, buyer_name: str):
        """Send polite rejection email"""
        try:
            deal = self._get_deal_by_email(buyer_email)
            if not deal:
                return {"success": False, "error": "Deal not found"}
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Thank You for Your Response</h2>
                    <p>Dear {buyer_name},</p>
                    <p>We appreciate you taking the time to review this opportunity. We understand it wasn't the right fit at this time.</p>
                    <p>We'll continue to search for matches that better align with your requirements and will reach out when we find more suitable opportunities.</p>
                    <p>Thank you for being part of the circular economy movement!</p>
                    <p>Best regards,<br><strong>{self.from_name}</strong></p>
                </div>
            </body>
            </html>
            """
            
            subject = "Thank You - We'll Keep Looking for Better Matches"
            
            mail_body = {}
            self.mailer.set_mail_from({"name": self.from_name, "email": self.from_email}, mail_body)
            self.mailer.set_mail_to([{"name": buyer_name, "email": buyer_email}], mail_body)
            self.mailer.set_subject(subject, mail_body)
            self.mailer.set_html_content(html_body, mail_body)
            
            self.mailer.send(mail_body)
            
            # Update deal status
            self._update_deal_status(buyer_email, "not_interested")
            
            # Log email
            self._log_email(deal['deal_id'], buyer_email, "rejection", subject)
            
            logger.info(f"Rejection email sent to {buyer_email}")
            return {"success": True, "message": "Rejection email sent"}
        
        except Exception as e:
            logger.error(f"Error sending rejection email: {e}")
            return {"success": False, "error": str(e)}
    
    def process_email_response(self, buyer_email: str, email_body: str) -> dict:
        """Process incoming email response and extract keyword"""
        email_body_lower = email_body.lower()
        
        if re.search(r'\bready\s+to\s+deal\b', email_body_lower):
            return {"action": "deal_closed", "keyword": "Ready to deal"}
        elif re.search(r'\bneed\s+clarification\b', email_body_lower):
            return {"action": "clarification", "keyword": "Need Clarification"}
        elif re.search(r'\bnot\s+interested\b', email_body_lower):
            return {"action": "rejection", "keyword": "Not interested"}
        else:
            return {"action": "unknown", "keyword": None}
    
    async def handle_email_response(self, buyer_email: str, email_body: str) -> dict:
        """Main handler for processing email responses"""
        try:
            deal = self._get_deal_by_email(buyer_email)
            
            if not deal:
                return {"success": False, "error": "Deal not found"}
            
            result = self.process_email_response(buyer_email, email_body)
            
            if result["action"] == "unknown":
                return {"success": False, "error": "No valid keyword found in email"}
            
            buyer_name = deal['buyer_contact_name']
            
            # Reconstruct waste_profile from deal record
            waste_profile = {
                'waste_streams': [],
                'overall_confidence': 0.85
            }
            
            if result["action"] == "deal_closed":
                await self.send_deal_closed_email(buyer_email, buyer_name, deal['buyer_company'])
                return {"success": True, "action": "deal_closed", "message": "Thank you email sent"}
            
            elif result["action"] == "clarification":
                await self.send_clarification_email(buyer_email, buyer_name, waste_profile)
                return {"success": True, "action": "clarification", "message": "Clarification email sent"}
            
            elif result["action"] == "rejection":
                await self.send_rejection_email(buyer_email, buyer_name)
                return {"success": True, "action": "rejection", "message": "Rejection email sent"}
        
        except Exception as e:
            logger.error(f"Error handling email response: {e}")
            return {"success": False, "error": str(e)}
    
    def get_all_deals(self) -> List[Dict]:
        """Get all deals from CSV"""
        try:
            df = pd.read_csv(self.deals_csv)
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error loading deals: {e}")
            return []
    
    def get_email_logs(self, deal_id: str = None) -> List[Dict]:
        """Get email logs, optionally filtered by deal_id"""
        try:
            df = pd.read_csv(self.email_log_csv)
            if deal_id:
                df = df[df['deal_id'] == deal_id]
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error loading email logs: {e}")
            return []
