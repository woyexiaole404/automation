import os
import smtplib
from email.message import EmailMessage
from email.utils import formatdate
from pathlib import Path


REQUIRED_ENV_VARS = (
    "MAIL_HOST",
    "MAIL_PORT",
    "MAIL_USERNAME",
    "MAIL_PASSWORD",
    "MAIL_FROM",
    "MAIL_TO",
)


def _get_bool_env(name, default=False):
    value = os.environ.get(name)
    if value in (None, ""):
        return default
    return value.strip().lower() in ("1", "true", "yes", "y", "on")


def _get_required_env(name):
    value = os.environ.get(name)
    if value in (None, ""):
        raise RuntimeError(f"Missing required email environment variable: {name}")
    return value


def load_email_config():
    config = {name: _get_required_env(name) for name in REQUIRED_ENV_VARS}
    config["MAIL_PORT"] = int(config["MAIL_PORT"])
    config["MAIL_USE_SSL"] = _get_bool_env(
        "MAIL_USE_SSL",
        default=config["MAIL_PORT"] == 465,
    )
    config["MAIL_USE_TLS"] = _get_bool_env(
        "MAIL_USE_TLS",
        default=not config["MAIL_USE_SSL"],
    )
    config["MAIL_TO"] = [
        item.strip()
        for item in config["MAIL_TO"].split(",")
        if item.strip()
    ]
    if not config["MAIL_TO"]:
        raise RuntimeError("MAIL_TO must contain at least one recipient.")
    return config


def send_email(subject, body, attachment_path):
    config = load_email_config()
    attachment = Path(attachment_path)
    if not attachment.exists():
        raise FileNotFoundError(f"Email attachment not found: {attachment}")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = config["MAIL_FROM"]
    message["To"] = ", ".join(config["MAIL_TO"])
    message["Date"] = formatdate(localtime=True)
    message.set_content(body)

    message.add_attachment(
        attachment.read_bytes(),
        maintype="text",
        subtype="html",
        filename=attachment.name,
    )

    smtp_class = smtplib.SMTP_SSL if config["MAIL_USE_SSL"] else smtplib.SMTP

    with smtp_class(config["MAIL_HOST"], config["MAIL_PORT"]) as smtp:
        smtp.ehlo()
        if config["MAIL_USE_TLS"] and not config["MAIL_USE_SSL"]:
            smtp.starttls()
            smtp.ehlo()
        smtp.login(config["MAIL_USERNAME"], config["MAIL_PASSWORD"])
        smtp.send_message(message)
