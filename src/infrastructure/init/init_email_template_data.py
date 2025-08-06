from src.modules.email.models import EmailTemplate


async def init_email_template_data() -> None:
    email_template_data: list[EmailTemplate] = [
        EmailTemplate(
            subject="{{ subject }}",
            body="{{ body }}",
            from_name="{{ from_name }}",
            from_email="{{ from_email }}",
            template_name="empty",
        ),
        EmailTemplate(
            subject="Reset password",
            body='<!DOCTYPE html>\n<html lang="en">\n  <head>\n    <meta charset="UTF-8" />\n    <title>Password Reset</title>\n    <style>\n      body {\n        font-family: \'Helvetica Neue\', Arial, sans-serif;\n        background-color: #f5f6fa;\n        margin: 0;\n        padding: 0;\n        color: #333;\n      }\n      .email-wrapper {\n        max-width: 600px;\n        margin: 40px auto;\n        background: #ffffff;\n        border-radius: 8px;\n        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);\n        overflow: hidden;\n      }\n      .email-header {\n        background-color: #007bff;\n        color: white;\n        padding: 24px;\n        text-align: center;\n      }\n      .email-header h1 {\n        margin: 0;\n        font-size: 24px;\n      }\n      .email-body {\n        padding: 24px;\n        font-size: 16px;\n        line-height: 1.6;\n      }\n      .email-body p {\n        margin-bottom: 16px;\n      }\n      .cta-button {\n        display: inline-block;\n        padding: 12px 24px;\n        background-color: #28a745;\n        color: #ffffff;\n        text-decoration: none;\n        font-weight: bold;\n        border-radius: 6px;\n      }\n      .email-footer {\n        text-align: center;\n        font-size: 12px;\n        color: #999999;\n        padding: 16px;\n      }\n    </style>\n  </head>\n  <body>\n    <div class="email-wrapper">\n      <div class="email-header">\n        <h1>Password Reset Request</h1>\n      </div>\n      <div class="email-body">\n        <p>Hi {{ user_name or \'there\' }},</p>\n        <p>We received a request to reset your password. Click the button below to choose a new password:</p>\n        <p style="text-align: center;">\n          <a href="{{ reset_url }}" class="cta-button" target="_blank">Reset Password</a>\n        </p>\n        <p>If you didn’t request this, you can safely ignore this email. This link will expire in 30 minutes for your security.</p>\n        <p>Need help? Just reply to this email—we’re happy to help.</p>\n      </div>\n      <div class="email-footer">\n        &copy; 2025 Your Company. All rights reserved.\n      </div>\n    </div>\n  </body>\n</html>\n',
            from_name="NOIS2-192 Project",
            from_email="nois2.192.do.not.reply@gmail.com",
            template_name="reset_password",
        ),
        EmailTemplate(
            subject="Verify your email",
            body='<!DOCTYPE html>\n<html lang="en">\n  <head>\n    <meta charset="UTF-8" />\n    <title>Email Verification</title>\n    <style>\n      body {\n        font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif;\n        background-color: #f4f4f4;\n        color: #333;\n        margin: 0;\n        padding: 0;\n      }\n      .container {\n        max-width: 600px;\n        margin: 40px auto;\n        background-color: #fff;\n        padding: 30px;\n        border-radius: 8px;\n        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);\n      }\n      .header {\n        text-align: center;\n        padding-bottom: 20px;\n      }\n      .header h2 {\n        margin: 0;\n        color: #007bff;\n      }\n      .content p {\n        font-size: 16px;\n        line-height: 1.6;\n        margin-bottom: 20px;\n      }\n      .button {\n        display: inline-block;\n        background-color: #28a745;\n        color: #fff;\n        text-decoration: none;\n        padding: 12px 24px;\n        border-radius: 5px;\n        font-weight: bold;\n        margin: 0 auto;\n      }\n      .footer {\n        font-size: 13px;\n        color: #777;\n        text-align: center;\n        margin-top: 30px;\n      }\n      .link {\n        word-break: break-all;\n        color: #007bff;\n      }\n    </style>\n  </head>\n  <body>\n    <div class="container">\n      <div class="header">\n        <h2>Hello, {{ name }}</h2>\n      </div>\n      <div class="content">\n        <p>\n          Please verify your email address by clicking the button below:\n        </p>\n        <p style="text-align: center;">\n          <a href="{{ verify_email_url }}" class="button" target="_blank">Verify Email</a>\n        </p>\n        <p>If the button above doesn\'t work, copy and paste this URL into your browser:</p>\n        <p><a href="{{ verify_email_url }}" class="link">{{ verify_email_url }}</a></p>\n        <p>Thank you,<br />The Team</p>\n      </div>\n      <div class="footer">\n        If you didn\'t create an account, you can safely ignore this email.\n      </div>\n    </div>\n  </body>\n</html>\n',
            from_name="NOIS2-192 Project",
            from_email="nois2.192.do.not.reply@gmail.com",
            template_name="verify_email",
        ),
        EmailTemplate(
            subject="Forgot your account password",
            body='<!DOCTYPE html>\n<html lang="en">\n  <head>\n    <meta charset="UTF-8" />\n    <title>Forgot Password</title>\n    <style>\n      body {\n        font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif;\n        background-color: #f4f4f4;\n        color: #333;\n        margin: 0;\n        padding: 0;\n      }\n      .container {\n        max-width: 600px;\n        margin: 40px auto;\n        background-color: #ffffff;\n        padding: 30px;\n        border-radius: 8px;\n        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);\n      }\n      .header {\n        text-align: center;\n        padding-bottom: 20px;\n      }\n      .header h2 {\n        margin: 0;\n        color: #dc3545;\n      }\n      .content p {\n        font-size: 16px;\n        line-height: 1.6;\n        margin-bottom: 20px;\n      }\n      .button {\n        display: inline-block;\n        background-color: #007bff;\n        color: #fff;\n        text-decoration: none;\n        padding: 12px 24px;\n        border-radius: 5px;\n        font-weight: bold;\n        margin: 0 auto;\n      }\n      .footer {\n        font-size: 13px;\n        color: #777;\n        text-align: center;\n        margin-top: 30px;\n      }\n      .link {\n        word-break: break-all;\n        color: #007bff;\n      }\n    </style>\n  </head>\n  <body>\n    <div class="container">\n      <div class="header">\n        <h2>Hello, {{ name }}</h2>\n      </div>\n      <div class="content">\n        <p>\n          We received a request to reset your password. You can do so by clicking the button below:\n        </p>\n        <p style="text-align: center;">\n          <a href="{{ forgot_password_url }}" class="button" target="_blank">Reset Password</a>\n        </p>\n        <p>If the button above doesn\'t work, copy and paste this URL into your browser:</p>\n        <p><a href="{{ forgot_password_url }}" class="link">{{ forgot_password_url }}</a></p>\n        <p>Thank you,<br />The Team</p>\n      </div>\n      <div class="footer">\n        If you didn’t request a password reset, you can safely ignore this email.\n      </div>\n    </div>\n  </body>\n</html>\n',
            from_name="NOIS2-192 Project",
            from_email="nois2.192.do.not.reply@gmail.com",
            template_name="forgot_password",
        ),
        EmailTemplate(
            subject="You are invited to a company",
            body='<!DOCTYPE html>\n<html lang="en">\n  <head>\n    <meta charset="UTF-8" />\n    <title>You\'re Invited to Join {{ company_name }}</title>\n    <style>\n      body {\n        font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif;\n        background-color: #f4f4f4;\n        margin: 0;\n        padding: 0;\n        color: #333;\n      }\n      .container {\n        max-width: 600px;\n        margin: 40px auto;\n        background-color: #ffffff;\n        padding: 30px;\n        border-radius: 8px;\n        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);\n      }\n      .header {\n        text-align: center;\n        padding-bottom: 20px;\n      }\n      .header h2 {\n        margin: 0;\n        color: #007bff;\n      }\n      .content p {\n        font-size: 16px;\n        line-height: 1.6;\n        margin-bottom: 20px;\n      }\n      .cta-button {\n        display: inline-block;\n        background-color: #28a745;\n        color: #ffffff;\n        padding: 12px 24px;\n        border-radius: 5px;\n        text-decoration: none;\n        font-weight: bold;\n      }\n      .footer {\n        font-size: 13px;\n        color: #777;\n        text-align: center;\n        margin-top: 30px;\n      }\n      .link {\n        word-break: break-word;\n        color: #007bff;\n      }\n    </style>\n  </head>\n  <body>\n    <div class="container">\n      <div class="header">\n        <h2>You’re Invited!</h2>\n      </div>\n      <div class="content">\n        <p>Hello,</p>\n        <p>You have been invited to join <strong>{{ company_name }}</strong>.</p>\n        <p>Please click the button below to view and accept your invitation:</p>\n        <p style="text-align: center;">\n          <a href="{{ invitation_link }}" class="cta-button" target="_blank">View Invitation</a>\n        </p>\n        <p>If the button above doesn\'t work, copy and paste this URL into your browser:</p>\n        <p><a href="{{ invitation_link }}" class="link">{{ invitation_link }}</a></p>\n        <p>Best regards,<br/>The Team</p>\n      </div>\n      <div class="footer">\n        If you did not expect this invitation, you can safely ignore this email.\n      </div>\n    </div>\n  </body>\n</html>\n',
            from_name="NOIS2-192 Project",
            from_email="nois2.192.do.not.reply@gmail.com",
            template_name="company_invitation",
        ),
        EmailTemplate(
            subject="A new support ticket",
            body='<!DOCTYPE html>\n<html>\n  <head>\n    <meta charset="UTF-8">\n    <title>Support Ticket Received</title>\n    <style>\n      body {\n        font-family: Arial, sans-serif;\n        background-color: #f9f9f9;\n        color: #333;\n        margin: 0;\n        padding: 0;\n      }\n      .email-container {\n        max-width: 600px;\n        margin: 20px auto;\n        background-color: #ffffff;\n        border: 1px solid #ddd;\n        padding: 20px;\n        border-radius: 6px;\n      }\n      .header {\n        background-color: #007bff;\n        color: white;\n        padding: 10px 20px;\n        border-radius: 6px 6px 0 0;\n      }\n      .content {\n        padding: 20px;\n      }\n      .label {\n        font-weight: bold;\n      }\n      .button {\n        display: inline-block;\n        padding: 10px 20px;\n        margin-top: 20px;\n        background-color: #28a745;\n        color: white;\n        text-decoration: none;\n        border-radius: 5px;\n        font-weight: bold;\n      }\n      .footer {\n        font-size: 12px;\n        color: #999;\n        text-align: center;\n        padding-top: 20px;\n      }\n    </style>\n  </head>\n  <body>\n    <div class="email-container">\n      <div class="header">\n        <h2>Support Ticket Received</h2>\n      </div>\n      <div class="content">\n        <p>Hello Support Team,</p>\n\n        <p>You’ve received a new support request with the following details:</p>\n\n        <p><span class="label">User Email:</span> {{ user_email }}</p>\n        <p><span class="label">Issue:</span> {{ issue_description }}</p>\n\n        <a\n          href="mailto:{{ user_email }}?subject=Regarding%20Your%20Support%20Ticket&body=Hi%20there%2C%0A%0AWe%20received%20your%20support%20request%20about%20the%20following%20issue%3A%0A%0A{{ issue_description | urlencode }}%0A%0AOur%20team%20is%20looking%20into%20it%20and%20will%20update%20you%20shortly.%0A%0AThanks%20for%20your%20patience.%0A%0A--%0ASupport%20Team"\n          class="button"\n        >\n          Reply to User\n        </a>\n      </div>\n      <div class="footer">\n        This is an automated message from your support system.\n      </div>\n    </div>\n  </body>\n</html>\n',
            from_name="NOIS2-192 Project",
            from_email="nois2.192.do.not.reply@gmail.com",
            template_name="support_ticket",
        ),
        EmailTemplate(
            subject="New Login to NOIS2",
            body='<!DOCTYPE html>\n<html>\n  <head>\n    <meta charset="UTF-8" />\n    <title>Verify Login</title>\n  </head>\n  <body>\n    <p>Hello,</p>\n    <p>We received a login request for your account. Please use the following code to verify your login:</p>\n\n    <h2 style="font-size: 32px; letter-spacing: 4px;">{{ otp }}</h2>\n\n    <p>This code will expire in 5 minutes. If you did not request this, please ignore this email.</p>\n\n    <p>Thank you,<br />The Team</p>\n  </body>\n</html>',
            from_name="NOIS2-192 Project",
            from_email="nois2.192.do.not.reply@gmail.com",
            template_name="verify_login",
        ),
        EmailTemplate(
            subject="Issue - {{ issue_type }}",
            body='<!DOCTYPE html>\n<html>\n<head>\n<meta charset="UTF-8">\n<title>Issue Reported</title>\n<style>\nbody { font-family: Arial, sans-serif; background-color: #f9f9f9; color: #333; margin: 0; padding: 0; }\n.email-container { max-width: 700px; margin: 20px auto; background-color: #ffffff; border: 1px solid #ddd; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }\n.content { padding: 25px; }\n.info-section { background-color: #f8f9fa; border-left: 4px solid #007bff; padding: 15px; margin: 15px 0; border-radius: 0 5px 5px 0; }\n.label { font-weight: bold; color: #495057; display: inline-block; width: 120px; }\n.value { color: #212529; }\n.description-box { background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 15px 0; }\n</style>\n</head>\n<body>\n<div class="email-container">\n<div class="content">\n<p>Hello Support Team,</p>\n<p>You \'ve received a new support request from Lymex {{ environment }}</p>\n<div class="info-section">\n<p><span class="label">User Name:</span> <span class="value">{{ user_name }}</span></p>\n<p><span class="label">User Email:</span> <span class="value">{{ user_email }}</span></p>\n<p><span class="label">Company:</span> <span class="value">{{ company_name }}</span></p>\n</div>\n<div class="issue-type">📋 Issue Type: {{ issue_type }}</div>\n<div class="description-box">\n<p><strong>📝 Description:</strong></p>\n<p>{{ description }}</p>\n</div>\n</div>\n</body>\n</html>',
            from_name="NOIS2-192 Project",
            from_email="nois2.192.do.not.reply@gmail.com",
            template_name="enhanced_support_ticket",
        ),
        EmailTemplate(
            subject="Support Request",
            body='<!DOCTYPE html>\n<html>\n  <head>\n    <meta charset="UTF-8" />\n    <title>Verify Login</title>\n  </head>\n  <body>\n    <p>Hello, {{ user_name }}</p>\n\n    <p>We\'ve received your support request about <strong>{{ issue_type }}</strong>. Our support team has received your request and will get back to you shortly.</p>\n\n    <p>Thank you,<br />The Support Team</p>\n  </body>\n</html>',
            from_name="NOIS2-192 Project",
            from_email="nois2.192.do.not.reply@gmail.com",
            template_name="support_confirmation",
        ),
    ]

    for template in email_template_data:
        existing_template = await EmailTemplate.find_one(
            EmailTemplate.template_name == template.template_name
        )
        if existing_template:
            # Update existing template by setting new values
            await existing_template.set({
                "subject": template.subject,
                "body": template.body,
                "from_name": template.from_name,
                "from_email": template.from_email
            })
        else:
            # Create new template
            await template.insert()
