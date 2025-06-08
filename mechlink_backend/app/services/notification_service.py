import smtplib
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import jinja2
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.notification import (
    Notification, NotificationTemplate, NotificationPreference,
    NotificationType, NotificationStatus, NotificationChannel
)
from app.models.user import User
from app.models.workshop import Appointment
from app.models.workshop import Workshop
from app.models.vehicle import Vehicle

logger = logging.getLogger(__name__)

class NotificationService:
    """Main service for managing notifications"""
    
    def __init__(self, db: Session):
        self.db = db
        self.jinja_env = jinja2.Environment(
            loader=jinja2.DictLoader({}),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
    
    def create_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        channel: NotificationChannel,
        title: str,
        message: str,
        data: Optional[Dict] = None,
        scheduled_for: Optional[datetime] = None,
        **kwargs
    ) -> Notification:
        """Create new notification"""
        
        # Get user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Check user preferences
        preferences = self.get_user_preferences(user_id)
        if not self._should_send_notification(notification_type, channel, preferences):
            logger.info(f"Notification {notification_type} omitted by user preferences {user_id}")
            return None
        
        # Create notification
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            channel=channel,
            title=title,
            message=message,
            data=data or {},
            scheduled_for=scheduled_for,
            recipient_email=user.email if channel.value == "email" else None,
            recipient_phone=user.phone if channel.value == "sms" else None,
            **kwargs
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        if not scheduled_for or scheduled_for <= datetime.now():
            self.send_notification(notification.id)
        
        return notification
    
    def send_notification(self, notification_id: str) -> bool:
        """Send specific notification"""
        
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        
        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return False
        
        if notification.status != NotificationStatus.PENDING:
            logger.warning(f"Notification {notification_id} already processed: {notification.status}")
            return False
        
        try:
            notification.attempts += 1
            
            # Send based on channel
            success = False
            if notification.channel.value == "email":
                success = self._send_email(notification)
            elif notification.channel.value == "sms":
                success = self._send_sms(notification)
            elif notification.channel.value == "push":
                success = self._send_push(notification)
            elif notification.channel.value == "in_app":
                success = self._send_in_app(notification)
            
            # Update status
            if success:
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.now()
                logger.info(f"Notification {notification_id} sent successfully")
            else:
                notification.status = NotificationStatus.FAILED
                logger.error(f"Error sending notification {notification_id}")
            
            self.db.commit()
            return success
            
        except Exception as e:
            notification.status = NotificationStatus.FAILED
            notification.last_error = str(e)
            self.db.commit()
            logger.error(f"Error sending notification {notification_id}: {str(e)}")
            return False
    
    def _send_email(self, notification: Notification) -> bool:
            """Enviar notificación por email"""
            try:
                # === CONFIGURACIÓN SMTP ===
                smtp_server = "smtp.gmail.com"
                smtp_port = 587
                smtp_user = "nauroy71106@gmail.com"  # Change to your real email
                smtp_password = "fqul mink zxep segl"  # Gmail app password, NOT your regular password
                
                # === VALIDATIONS ===
                if not all([smtp_user, smtp_password]):
                    logger.error("Incomplete SMTP configuration")
                    return False
                
                if not notification.recipient_email:
                    logger.error(f"Recipient email not found for notification {notification.id}")
                    return False
                
                # === CREATE MESSAGE ===
                msg = MIMEMultipart('alternative')
                
                # Email headers
                msg['From'] = f"MechLink <{smtp_user}>"
                msg['To'] = notification.recipient_email
                msg['Subject'] = notification.title
                
                # === CONTENT ===
                
                # Plain text (fallback)
                text_content = f"""
    {notification.title}

    {notification.message}

    ---
    Submitted by MechLink
    Your vehicle management platform in Puerto Rico
                """
                
                # Improved HTML
                html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                background-color: #f4f4f4;
                padding: 20px;
            }}
            .container {{
                background-color: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 3px solid #007bff;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .logo {{
                font-size: 28px;
                font-weight: bold;
                color: #007bff;
            }}
            .title {{
                color: #2c3e50;
                font-size: 24px;
                margin-bottom: 20px;
            }}
            .content {{
                font-size: 16px;
                margin-bottom: 30px;
                white-space: pre-line;
            }}
            .footer {{
                text-align: center;
                border-top: 1px solid #eee;
                padding-top: 20px;
                font-size: 14px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🚗 MechLink</div>
                <div style="color: #666;">Your vehicle management platform</div>
            </div>
            
            <h2 class="title">{notification.title}</h2>
            
            <div class="content">
                {notification.message}
            </div>
            
            <div class="footer">
                <p>Sent by <strong>MechLink</strong></p>
                <p>Puerto Rico's vehicle management platform</p>
            </div>
        </div>
    </body>
    </html>
                """
                
                # Add content to the message
                msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
                msg.attach(MIMEText(html_content, 'html', 'utf-8'))
                
                # === SEND EMAIL ===
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_password)
                    
                    text = msg.as_string()
                    server.sendmail(smtp_user, notification.recipient_email, text)
                
                logger.info(f"Email sent successfully to {notification.recipient_email}")
                return True
                
            except smtplib.SMTPAuthenticationError as e:
                logger.error(f"SMTP Authentication Error: {str(e)}")
                return False
            except smtplib.SMTPRecipientsRefused as e:
                logger.error(f"Recipient email rejected: {str(e)}")
                return False
            except Exception as e:
                logger.error(f"Error sending email: {str(e)}")
                return False

    
    def _send_sms(self, notification: Notification) -> bool:
        """Send SMS notification"""
        # Implement with a provider such as Twilio, AWS SNS, etc.
        try:
            # Example with Twilio (requires configuration)
            # from twilio.rest import Client
            # client = Client(account_sid, auth_token)
            # message = client.messages.create(
            #     body=notification.message,
            #     from_='+1234567890',
            #     to=notification.recipient_phone
            # )
            
            # For now, simulate success
            logger.info(f"Simulated SMS sent to {notification.recipient_phone}: {notification.message}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            return False
    
    def _send_push(self, notification: Notification) -> bool:
        """Send push notification"""
        # Implement with Firebase Cloud Messaging, OneSignal, etc.
        try:
            # Example with FCM (requires configuration)
            # import firebase_admin
            # from firebase_admin import messaging
            # message = messaging.Message(
            #     data=notification.data,
            #     token=notification.recipient_device_token,
            # )
            # response = messaging.send(message)

            # For now, simulate success
            logger.info(f"Simulated push notification sent: {notification.title}")
            return True

        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
            return False
    
    def _send_in_app(self, notification: Notification) -> bool:
        """Mark as in-app notification (already saved in DB)"""
        # In-app notifications are displayed when the user opens the app.
        return True
    
    def _get_html_content(self, notification: Notification) -> Optional[str]:
        """Generate HTML content for email"""
        try:
            template = self.db.query(NotificationTemplate).filter(
                and_(
                    NotificationTemplate.type == notification.type,
                    NotificationTemplate.channel == notification.channel,
                    NotificationTemplate.is_active == True
                )
            ).first()
            
            if not template or not template.html_template:
                return None
            
            template_obj = self.jinja_env.from_string(template.html_template)
            return template_obj.render(**notification.data)
            
        except Exception as e:
            logger.error(f"Error generating HTML content: {str(e)}")
            return None
    
    def get_user_preferences(self, user_id: str) -> NotificationPreference:
        """Get user notification preferences"""
        preferences = self.db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).first()
        
        if not preferences:
            preferences = NotificationPreference(user_id=user_id)
            self.db.add(preferences)
            self.db.commit()
            self.db.refresh(preferences)
        
        return preferences
    
    def _should_send_notification(
        self,
        notification_type: NotificationType,
        channel: NotificationChannel,
        preferences: NotificationPreference
    ) -> bool:
        """Check whether the notification should be sent according to preferences"""
        
        # Check enabled channel using .value to get the string
        if channel.value == "email" and not preferences.email_enabled:
            return False
        if channel.value == "sms" and not preferences.sms_enabled:
            return False
        if channel.value == "push" and not preferences.push_enabled:
            return False
        
        # Check enabled type using .value too
        type_preferences = {
            "appointment_reminder": preferences.appointment_reminders,
            "maintenance_reminder": preferences.maintenance_reminders,
            "appointment_confirmation": preferences.appointment_confirmations,
            "review_request": preferences.review_requests,
            "system_update": preferences.system_updates,
            "promotional": preferences.promotional,
        }
        
        return type_preferences.get(notification_type.value, True)

    
    def schedule_appointment_reminders(self, appointment_id: str) -> List[Notification]:
        """Set reminders for an appointment"""
        appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()
        
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        user_preferences = self.get_user_preferences(appointment.user_id)
        appointment_datetime = appointment.appointment_datetime
        
        reminders = []
        reminder_times = [user_preferences.reminder_hours_before, 1]  # 24h and 1h before by default
        
        for hours_before in reminder_times:
            reminder_time = appointment_datetime - timedelta(hours=hours_before)
            
            # Only schedule if it is in the future
            if reminder_time > datetime.now():
                workshop = self.db.query(Workshop).filter(
                    Workshop.id == appointment.workshop_id
                ).first()
                
                vehicle = self.db.query(Vehicle).filter(
                    Vehicle.id == appointment.vehicle_id
                ).first()
                
                title = f"Reminder: Appointment at {hours_before} hour{'s' if hours_before > 1 else ''}"
                message = f"Your appointment for {appointment.service_type} in {workshop.name} is in {hours_before} hour{'s' if hours_before > 1 else ''}. Vehicle: {vehicle.make} {vehicle.model} ({vehicle.license_plate})"
                
                reminder = self.create_notification(
                    user_id=appointment.user_id,
                    notification_type=NotificationType.APPOINTMENT_REMINDER,
                    channel=NotificationChannel("email"),
                    title=title,
                    message=message,
                    scheduled_for=reminder_time,
                    appointment_id=appointment_id,
                    workshop_id=appointment.workshop_id,
                    vehicle_id=appointment.vehicle_id,
                    data={
                        "appointment_datetime": appointment_datetime.isoformat(),
                        "workshop_name": workshop.name,
                        "service_type": appointment.service_type,
                        "vehicle_info": f"{vehicle.make} {vehicle.model}",
                        "hours_before": hours_before
                    }
                )
                
                if reminder:
                    reminders.append(reminder)
        
        return reminders
    
    def send_appointment_confirmation(self, appointment_id: str) -> Notification:
        """Send confirmation of created appointment"""
        appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()
        
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        workshop = self.db.query(Workshop).filter(
            Workshop.id == appointment.workshop_id
        ).first()
        
        vehicle = self.db.query(Vehicle).filter(
            Vehicle.id == appointment.vehicle_id
        ).first()
        
        title = "Appointment confirmed at MechLink"
        message = f"Your appointment has been confirmed:\n\n📅 Date: {appointment.appointment_datetime.strftime('%d/%m/%Y %H:%M')}\n🏪 Workshop: {workshop.name}\n🔧 Service: {appointment.service_type}\n🚗 Vehicle: {vehicle.make} {vehicle.model} ({vehicle.license_plate})\n📍 Address: {workshop.address}, {workshop.city}\n📞 Phone: {workshop.phone}"
        
        return self.create_notification(
            user_id=appointment.user_id,
            notification_type=NotificationType.APPOINTMENT_CONFIRMATION,
            channel=NotificationChannel("email"),
            title=title,
            message=message,
            appointment_id=appointment_id,
            workshop_id=appointment.workshop_id,
            vehicle_id=appointment.vehicle_id,
            data={
                "appointment_datetime": appointment.appointment_datetime.isoformat(),
                "workshop_name": workshop.name,
                "workshop_address": workshop.address,
                "workshop_city": workshop.city,
                "workshop_phone": workshop.phone,
                "service_type": appointment.service_type,
                "vehicle_info": f"{vehicle.make} {vehicle.model}",
                "license_plate": vehicle.license_plate,
                "estimated_cost": str(appointment.estimated_cost) if appointment.estimated_cost else "To be determined"
            }
        )
    
    def send_review_request(self, appointment_id: str) -> Notification:
        """Submit review request after service completed"""
        appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()
        
        if not appointment:
            raise ValueError(f"Cita {appointment_id} not found")
        
        workshop = self.db.query(Workshop).filter(
            Workshop.id == appointment.workshop_id
        ).first()
        
        title = "¿How was your experience?"
        message = f"Hello! Your service of {appointment.service_type} in {workshop.name} has been completed. We'd love to hear about your experience. Your feedback helps other users find the best workshops.\n\nCould you rate your experience?"
        
        return self.create_notification(
            user_id=appointment.user_id,
            notification_type=NotificationType.REVIEW_REQUEST,
            channel=NotificationChannel("email"),
            title=title,
            message=message,
            appointment_id=appointment_id,
            workshop_id=appointment.workshop_id,
            data={
                "workshop_name": workshop.name,
                "service_type": appointment.service_type,
                "appointment_date": appointment.appointment_datetime.strftime('%d/%m/%Y'),
                "review_url": f"https://mechlink.com/reviews/create?appointment={appointment_id}"
            }
        )
    
    def send_maintenance_reminder(self, vehicle_id: str, reminder_type: str, details: Dict) -> Notification:
        """Send maintenance reminder"""
        vehicle = self.db.query(Vehicle).filter(
            Vehicle.id == vehicle_id
        ).first()
        
        if not vehicle:
            raise ValueError(f"Vehicle {vehicle_id} not found")
        
        title = f"Maintenance reminder - {vehicle.make} {vehicle.model}"
        
        if reminder_type == "mileage":
            message = f"Your {vehicle.make} {vehicle.model} ({vehicle.license_plate}) needs maintenance:\n\n📊 Current mileage: {details.get('current_mileage', 'N/A')} km\n🔧 Recommended service: {details.get('service_type', 'General review')}\n📅 Last maintenance: {details.get('last_service_date', 'Unregistered')}\n\n¡Schedule your appointment to keep your vehicle in optimal condition!"
        elif reminder_type == "time":
            message = f"It's been a while since your last maintenance {vehicle.make} {vehicle.model} ({vehicle.license_plate}):\n\n📅 Last service: {details.get('last_service_date', 'Unregistered')}\n🔧 Recommended service: {details.get('service_type', 'General review')}\n⏰ Elapsed time: {details.get('days_since', 'N/A')} days\n\n¡It's time to give your vehicle some love!"
        else:
            message = f"Your {vehicle.make} {vehicle.model} ({vehicle.license_plate}) needs attention. ¡Schedule your next maintenance!"
        
        return self.create_notification(
            user_id=vehicle.user_id,
            notification_type=NotificationType.MAINTENANCE_REMINDER,
            channel=NotificationChannel("email"),
            title=title,
            message=message,
            vehicle_id=vehicle_id,
            data={
                "vehicle_info": f"{vehicle.make} {vehicle.model}",
                "license_plate": vehicle.license_plate,
                "reminder_type": reminder_type,
                **details
            }
        )
    
    def process_scheduled_notifications(self) -> int:
        """Process pending scheduled notifications"""
        now = datetime.now()
        
        # Get scheduled notifications that are due to be sent
        scheduled_notifications = self.db.query(Notification).filter(
            and_(
                Notification.status == NotificationStatus.PENDING,
                Notification.scheduled_for <= now,
                or_(
                    Notification.expires_at.is_(None),
                    Notification.expires_at > now
                )
            )
        ).all()
        
        sent_count = 0
        for notification in scheduled_notifications:
            if self.send_notification(notification.id):
                sent_count += 1
        
        logger.info(f"Processed {len(scheduled_notifications)} scheduled notifications, {sent_count} successfully sent")
        return sent_count
    
    def retry_failed_notifications(self) -> int:
        """Retry failed notifications"""
        failed_notifications = self.db.query(Notification).filter(
            and_(
                Notification.status == NotificationStatus.FAILED,
                Notification.attempts < Notification.max_attempts
            )
        ).all()
        
        retried_count = 0
        for notification in failed_notifications:
            if self.send_notification(notification.id):
                retried_count += 1
        
        logger.info(f"Retried {len(failed_notifications)} failed notifications, {retried_count} successful")
        return retried_count
    
    def get_notification_stats(self, user_id: Optional[str] = None) -> Dict:
        """Get notification statistics"""
        query = self.db.query(Notification)
        
        if user_id:
            query = query.filter(Notification.user_id == user_id)
        
        total = query.count()
        sent = query.filter(Notification.status == NotificationStatus.SENT).count()
        delivered = query.filter(Notification.status == NotificationStatus.DELIVERED).count()
        failed = query.filter(Notification.status == NotificationStatus.FAILED).count()
        pending = query.filter(Notification.status == NotificationStatus.PENDING).count()
        
        # Statistics by type
        type_stats = {}
        for notification_type in NotificationType:
            count = query.filter(Notification.type == notification_type).count()
            if count > 0:
                type_stats[notification_type.value] = count
        
        # Statistics by channel
        channel_stats = {}
        for channel in NotificationChannel:
            count = query.filter(Notification.channel == channel).count()
            if count > 0:
                channel_stats[channel.value] = count
        
        # Delivery rate
        delivery_rate = (delivered / sent * 100) if sent > 0 else 0
        
        return {
            "total_notifications": total,
            "sent": sent,
            "delivered": delivered,
            "failed": failed,
            "pending": pending,
            "delivery_rate": round(delivery_rate, 2),
            "notifications_by_type": type_stats,
            "notifications_by_channel": channel_stats
        }
    
    def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as read"""
        notification = self.db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        ).first()
        
        if not notification:
            return False
        
        notification.status = NotificationStatus.READ
        notification.read_at = datetime.now()
        self.db.commit()
        
        return True
    
    def cleanup_old_notifications(self, days_old: int = 90) -> int:
        """Clear old notifications"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        old_notifications = self.db.query(Notification).filter(
            or_(
                and_(
                    Notification.created_at < cutoff_date,
                    Notification.status.in_([NotificationStatus.SENT, NotificationStatus.DELIVERED, NotificationStatus.READ])
                ),
                and_(
                    Notification.expires_at < datetime.now(),
                    Notification.status == NotificationStatus.PENDING
                )
            )
        )
        
        count = old_notifications.count()
        old_notifications.delete()
        self.db.commit()
        
        logger.info(f"Deleted {count} old notifications")
        return count