#!/usr/bin/env python3
"""
Script to create default notification templates
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.config.database import SessionLocal
from app.models.notification import (
    NotificationTemplate, NotificationType, NotificationChannel
)

def create_default_templates():
    """Create default notification templates"""
    
    db = SessionLocal()
    
    templates = [
        # APPOINTMENT REMINDER
        {
            "name": "appointment_reminder_email",
            "type": NotificationType.APPOINTMENT_REMINDER,
            "channel": NotificationChannel.EMAIL,
            "subject_template": "Reminder: Your appointment at {{workshop_name}} is in {{hours_before}} hour(s)",
            "message_template": """Hi!

This is a reminder that you have an upcoming appointment:

📅 Date and time: {{appointment_datetime}}
🏪 Workshop: {{workshop_name}}
🔧 Service: {{service_type}}
🚗 Vehicle: {{vehicle_info}}

📍 Address: {{workshop_address}}, {{workshop_city}}
📞 Phone: {{workshop_phone}}

See you soon!

The MechLink Team""",
            "html_template": """
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #2563eb; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0;">🔧 MechLink</h1>
            <p style="margin: 10px 0 0 0;">Appointment Reminder</p>
        </div>
        
        <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 8px 8px;">
            <h2 style="color: #1e40af; margin-top: 0;">Hi!</h2>
            <p>This is a reminder that you have an upcoming appointment:</p>
            
            <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2563eb;">
                <p><strong>📅 Date and time:</strong> {{appointment_datetime}}</p>
                <p><strong>🏪 Workshop:</strong> {{workshop_name}}</p>
                <p><strong>🔧 Service:</strong> {{service_type}}</p>
                <p><strong>🚗 Vehicle:</strong> {{vehicle_info}}</p>
            </div>
            
            <div style="background: #ecfdf5; padding: 15px; border-radius: 8px; border-left: 4px solid #10b981;">
                <p style="margin: 0;"><strong>📍 Address:</strong> {{workshop_address}}, {{workshop_city}}</p>
                <p style="margin: 5px 0 0 0;"><strong>📞 Phone:</strong> {{workshop_phone}}</p>
            </div>
            
            <p style="margin-top: 30px; text-align: center; color: #6b7280;">See you soon!</p>
            <p style="text-align: center; color: #9ca3af; font-size: 14px;">The MechLink Team</p>
        </div>
    </div>
</body>
</html>""",
            "available_variables": ["workshop_name", "appointment_datetime", "service_type", "vehicle_info", "workshop_address", "workshop_city", "workshop_phone", "hours_before"]
        },

        # APPOINTMENT CONFIRMATION
        {
            "name": "appointment_confirmation_email",
            "type": NotificationType.APPOINTMENT_CONFIRMATION,
            "channel": NotificationChannel.EMAIL,
            "subject_template": "✅ Appointment confirmed at {{workshop_name}} - MechLink",
            "message_template": """Your appointment has been confirmed!

📅 Date: {{appointment_datetime}}
🏪 Workshop: {{workshop_name}}
🔧 Service: {{service_type}}
🚗 Vehicle: {{vehicle_info}} ({{license_plate}})

📍 Address: {{workshop_address}}, {{workshop_city}}
📞 Phone: {{workshop_phone}}
💰 Estimated cost: {{estimated_cost}}

We’ll send reminders before your appointment.

Thank you for choosing MechLink!""",
            "html_template": """
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #10b981; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0;">✅ Appointment Confirmed</h1>
            <p style="margin: 10px 0 0 0;">MechLink</p>
        </div>
        
        <div style="background: #f0fdf4; padding: 30px; border-radius: 0 0 8px 8px;">
            <h2 style="color: #065f46; margin-top: 0;">Your appointment has been confirmed!</h2>
            
            <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #10b981;">
                <p><strong>📅 Date:</strong> {{appointment_datetime}}</p>
                <p><strong>🏪 Workshop:</strong> {{workshop_name}}</p>
                <p><strong>🔧 Service:</strong> {{service_type}}</p>
                <p><strong>🚗 Vehicle:</strong> {{vehicle_info}} ({{license_plate}})</p>
                <p><strong>💰 Estimated cost:</strong> {{estimated_cost}}</p>
            </div>
            
            <div style="background: #dbeafe; padding: 15px; border-radius: 8px;">
                <p style="margin: 0;"><strong>📍 Address:</strong> {{workshop_address}}, {{workshop_city}}</p>
                <p style="margin: 5px 0 0 0;"><strong>📞 Phone:</strong> {{workshop_phone}}</p>
            </div>
            
            <p style="margin-top: 20px; color: #065f46;">We’ll send reminders before your appointment.</p>
            <p style="text-align: center; margin-top: 30px; color: #6b7280;">Thank you for choosing MechLink!</p>
        </div>
    </div>
</body>
</html>""",
            "available_variables": ["appointment_datetime", "workshop_name", "service_type", "vehicle_info", "license_plate", "workshop_address", "workshop_city", "workshop_phone", "estimated_cost"]
        },

        # REVIEW REQUEST
        {
            "name": "review_request_email",
            "type": NotificationType.REVIEW_REQUEST,
            "channel": NotificationChannel.EMAIL,
            "subject_template": "⭐ How was your experience at {{workshop_name}}?",
            "message_template": """Hi!

Your {{service_type}} service at {{workshop_name}} on {{appointment_date}} is now complete.

We’d love to hear about your experience. Your opinion helps others find the best workshops.

Could you rate your experience?

👍 Rate here: {{review_url}}

Thanks for using MechLink!""",
            "html_template": """
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #f59e0b; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0;">⭐ Your Opinion Matters</h1>
            <p style="margin: 10px 0 0 0;">MechLink</p>
        </div>
        
        <div style="background: #fffbeb; padding: 30px; border-radius: 0 0 8px 8px;">
            <h2 style="color: #92400e; margin-top: 0;">Hi!</h2>
            <p>Your <strong>{{service_type}}</strong> service at <strong>{{workshop_name}}</strong> on {{appointment_date}} is now complete.</p>
            
            <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; border: 2px solid #fbbf24;">
                <p style="margin: 0; font-size: 18px;">We’d love to hear your feedback</p>
                <p style="color: #6b7280; margin: 10px 0;">Your opinion helps others find the best workshops</p>
                
                <a href="{{review_url}}" style="display: inline-block; background: #f59e0b; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 15px; font-weight: bold;">⭐ Rate Experience</a>
            </div>
            
            <p style="text-align: center; margin-top: 30px; color: #6b7280;">Thanks for using MechLink!</p>
        </div>
    </div>
</body>
</html>""",
            "available_variables": ["workshop_name", "service_type", "appointment_date", "review_url"]
        },

        # MAINTENANCE REMINDER
        {
            "name": "maintenance_reminder_email",
            "type": NotificationType.MAINTENANCE_REMINDER,
            "channel": NotificationChannel.EMAIL,
            "subject_template": "🔧 Maintenance Reminder - {{vehicle_info}}",
            "message_template": """Time to take care of your vehicle!

Your {{vehicle_info}} ({{license_plate}}) is due for maintenance:

🔧 Recommended service: {{service_type}}
📊 Current mileage: {{current_mileage}} km
📅 Last service: {{last_service_date}}

Book your appointment now with MechLink to keep your vehicle in top condition!

Find workshops: https://mechlink.com/workshops""",
            "html_template": """
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #dc2626; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0;">🔧 Maintenance Reminder</h1>
            <p style="margin: 10px 0 0 0;">MechLink</p>
        </div>
        
        <div style="background: #fef2f2; padding: 30px; border-radius: 0 0 8px 8px;">
            <h2 style="color: #991b1b; margin-top: 0;">Time to take care of your vehicle!</h2>
            <p>Your <strong>{{vehicle_info}}</strong> ({{license_plate}}) is due for maintenance:</p>
            
            <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #dc2626;">
                <p><strong>🔧 Recommended service:</strong> {{service_type}}</p>
                <p><strong>📊 Current mileage:</strong> {{current_mileage}} km</p>
                <p><strong>📅 Last service:</strong> {{last_service_date}}</p>
            </div>
            
            <div style="text-align: center; margin-top: 25px;">
                <a href="https://mechlink.com/workshops" style="display: inline-block; background: #dc2626; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">🔍 Find Workshops</a>
            </div>
            
            <p style="text-align: center; margin-top: 20px; color: #6b7280;">Keep your vehicle in top condition!</p>
        </div>
    </div>
</body>
</html>""",
            "available_variables": ["vehicle_info", "license_plate", "service_type", "current_mileage", "last_service_date"]
        }
    ]
    
    try:
        for template_data in templates:
            # Check if it already exists
            existing = db.query(NotificationTemplate).filter(
                NotificationTemplate.name == template_data["name"]
            ).first()
            
            if not existing:
                template = NotificationTemplate(**template_data)
                db.add(template)
                print(f"✅ Created template: {template_data['name']}")
            else:
                print(f"⚠️  Template already exists: {template_data['name']}")
        
        db.commit()
        print(f"\n🎉 Notification templates successfully configured")
        
    except Exception as e:
        print(f"❌ Error creating templates: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔔 Setting up notification templates...")
    print("=" * 50)
    create_default_templates()