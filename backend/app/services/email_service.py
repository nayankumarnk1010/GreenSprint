import smtplib
from email.message import EmailMessage

from app.core.config import settings


class EmailService:
    @staticmethod
    def _smtp_configured() -> bool:
        return all(
            [
                settings.SMTP_HOST,
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD,
                settings.SMTP_FROM_EMAIL,
            ]
        )

    @staticmethod
    def send_password_reset_email(
        to_email: str,
        full_name: str,
        reset_link: str,
    ) -> bool:
        subject = "Reset your GreenSprint password"

        plain_body = f"""
Hello {full_name},

We received a request to reset your GreenSprint account password.

Use this link to reset your password:
{reset_link}

This link will expire in {settings.PASSWORD_RESET_EXPIRE_MINUTES} minutes.

If you did not request this, you can safely ignore this email.

Regards,
GreenSprint Team
"""

        html_body = f"""
<!DOCTYPE html>
<html>
  <body style="font-family: Arial, sans-serif; background:#f4fff7; padding:24px;">
    <div style="max-width:560px; margin:auto; background:#ffffff; border-radius:18px; padding:28px; border:1px solid #d9f99d;">
      <h2 style="color:#047857; margin-top:0;">Reset your GreenSprint password</h2>

      <p>Hello <strong>{full_name}</strong>,</p>

      <p>
        We received a request to reset your GreenSprint account password.
      </p>

      <p style="margin:28px 0;">
        <a href="{reset_link}"
           style="background:#059669; color:#ffffff; padding:14px 22px; text-decoration:none; border-radius:12px; font-weight:bold;">
          Reset Password
        </a>
      </p>

      <p style="font-size:14px; color:#475569;">
        This link will expire in {settings.PASSWORD_RESET_EXPIRE_MINUTES} minutes.
      </p>

      <p style="font-size:14px; color:#64748b;">
        If you did not request this, you can safely ignore this email.
      </p>

      <p style="margin-bottom:0; color:#047857; font-weight:bold;">
        GreenSprint Team
      </p>
    </div>
  </body>
</html>
"""

        if not EmailService._smtp_configured():
            print("\n========== GREENSPRINT PASSWORD RESET ==========")
            print("SMTP is not configured.")
            print("Development reset link:")
            print(reset_link)
            print("================================================\n")
            return False

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = (
            f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        )
        message["To"] = to_email

        message.set_content(plain_body)
        message.add_alternative(html_body, subtype="html")

        try:
            with smtplib.SMTP(
                settings.SMTP_HOST,
                settings.SMTP_PORT,
                timeout=20,
            ) as smtp:
                if settings.SMTP_USE_TLS:
                    smtp.starttls()

                smtp_username = settings.SMTP_USERNAME.strip()
                smtp_password = settings.SMTP_PASSWORD.replace(" ", "").strip()

                smtp.login(
                    smtp_username,
                    smtp_password,
                )

                smtp.send_message(message)

            return True

        except Exception as exc:
            print("\n========== GREENSPRINT EMAIL ERROR ==========")
            print("Password reset email could not be sent.")
            print(str(exc))
            print("Reset link for development:")
            print(reset_link)
            print("=============================================\n")
            return False