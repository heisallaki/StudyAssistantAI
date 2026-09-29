from unittest.mock import MagicMock, patch

import pytest

from app.services import email_service
from app.services.email_service import EmailSendError


def test_send_email_raises_when_smtp_not_configured(monkeypatch):
    monkeypatch.setattr(email_service.settings, "SMTP_USERNAME", None)
    monkeypatch.setattr(email_service.settings, "SMTP_PASSWORD", None)

    with pytest.raises(EmailSendError):
        email_service.send_email("student@example.com", "Subject", "Body")


def test_send_email_uses_smtp_starttls_and_login(monkeypatch):
    monkeypatch.setattr(email_service.settings, "SMTP_USERNAME", "kal.projects.dev@gmail.com")
    monkeypatch.setattr(email_service.settings, "SMTP_PASSWORD", "app-password")
    monkeypatch.setattr(email_service.settings, "SMTP_HOST", "smtp.gmail.com")
    monkeypatch.setattr(email_service.settings, "SMTP_PORT", 587)

    mock_server = MagicMock()
    mock_smtp = MagicMock()
    mock_smtp.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp.__exit__ = MagicMock(return_value=False)

    with patch("app.services.email_service.smtplib.SMTP", return_value=mock_smtp) as mock_smtp_class:
        email_service.send_email("student@example.com", "Verify your account", "Your code is 123456")

    mock_smtp_class.assert_called_once_with("smtp.gmail.com", 587, timeout=30)
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("kal.projects.dev@gmail.com", "app-password")
    mock_server.send_message.assert_called_once()


def test_send_email_wraps_smtp_exceptions(monkeypatch):
    import smtplib

    monkeypatch.setattr(email_service.settings, "SMTP_USERNAME", "kal.projects.dev@gmail.com")
    monkeypatch.setattr(email_service.settings, "SMTP_PASSWORD", "app-password")

    with patch("app.services.email_service.smtplib.SMTP", side_effect=smtplib.SMTPAuthenticationError(535, b"bad creds")):
        with pytest.raises(EmailSendError):
            email_service.send_email("student@example.com", "Subject", "Body")


def test_send_email_wraps_connection_errors(monkeypatch):
    monkeypatch.setattr(email_service.settings, "SMTP_USERNAME", "kal.projects.dev@gmail.com")
    monkeypatch.setattr(email_service.settings, "SMTP_PASSWORD", "app-password")

    with patch("app.services.email_service.smtplib.SMTP", side_effect=OSError("network unreachable")):
        with pytest.raises(EmailSendError):
            email_service.send_email("student@example.com", "Subject", "Body")