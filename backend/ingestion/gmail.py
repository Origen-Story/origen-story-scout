"""
Gmail API integration for fetching newsletters from a labeled folder.

Setup required:
1. Create a Google Cloud project at https://console.cloud.google.com/
2. Enable the Gmail API
3. Create OAuth 2.0 credentials (Desktop application)
4. Download credentials.json and place in config/ folder
5. Run the app once to complete OAuth flow (opens browser)
"""

import os
import base64
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup

from shared.base import ContentItem, ContentSource
from shared.config import settings

# Gmail API imports - will fail gracefully if not installed
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False


# If modifying scopes, delete token.pickle
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailSource(ContentSource):
    """Fetch newsletters from Gmail using a specific label."""

    def __init__(self, label_name: str = "Newsletters", credentials_path: str = "config/credentials.json"):
        if not GMAIL_AVAILABLE:
            raise ImportError(
                "Gmail API dependencies not installed. "
                "Run: pip install google-auth-oauthlib google-api-python-client"
            )

        self.label_name = label_name
        self.credentials_path = Path(credentials_path)
        self.token_path = Path("config/gmail_token.pickle")
        self.service = None

    def _authenticate(self) -> bool:
        """Authenticate with Gmail API using OAuth."""
        creds = None

        # Load existing token if available
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials, initiate OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Token refresh failed: {e}")
                    creds = None

            if not creds:
                if not self.credentials_path.exists():
                    print(f"Gmail credentials not found at {self.credentials_path}")
                    print("Please download OAuth credentials from Google Cloud Console")
                    print("See: docs/GMAIL_SETUP.md for instructions")
                    return False

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save token for future use
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)
        return True

    def _get_label_id(self) -> Optional[str]:
        """Get the Gmail label ID for the configured label name."""
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])

            for label in labels:
                if label['name'].lower() == self.label_name.lower():
                    return label['id']

            print(f"Label '{self.label_name}' not found in Gmail")
            print(f"Available labels: {[l['name'] for l in labels]}")
            return None
        except Exception as e:
            print(f"Error fetching labels: {e}")
            return None

    def _parse_email_content(self, msg_data: dict) -> tuple[str, str, Optional[str]]:
        """
        Extract subject, body text, and sender from email message.
        Returns (subject, body_text, sender)
        """
        headers = msg_data.get('payload', {}).get('headers', [])

        subject = ""
        sender = None
        date_str = None

        for header in headers:
            name = header.get('name', '').lower()
            if name == 'subject':
                subject = header.get('value', '')
            elif name == 'from':
                sender = header.get('value', '')
            elif name == 'date':
                date_str = header.get('value', '')

        # Extract body
        body_text = self._extract_body(msg_data.get('payload', {}))

        return subject, body_text, sender, date_str

    def _extract_body(self, payload: dict) -> str:
        """Recursively extract text content from email payload."""
        body_text = ""

        # Check for direct body data
        if 'body' in payload and payload['body'].get('data'):
            data = payload['body']['data']
            decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

            # If HTML, extract text
            if payload.get('mimeType') == 'text/html':
                body_text = self._html_to_text(decoded)
            else:
                body_text = decoded

        # Check for multipart content
        if 'parts' in payload:
            for part in payload['parts']:
                mime_type = part.get('mimeType', '')

                if mime_type == 'text/plain':
                    if part.get('body', {}).get('data'):
                        data = part['body']['data']
                        decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        body_text = decoded
                        break  # Prefer plain text

                elif mime_type == 'text/html':
                    if part.get('body', {}).get('data'):
                        data = part['body']['data']
                        decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        body_text = self._html_to_text(decoded)

                elif mime_type.startswith('multipart/'):
                    # Recurse into nested multipart
                    nested_text = self._extract_body(part)
                    if nested_text:
                        body_text = nested_text

        return body_text.strip()

    def _html_to_text(self, html: str) -> str:
        """Convert HTML newsletter content to clean text."""
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for element in soup(['script', 'style', 'head', 'meta', 'link']):
            element.decompose()

        # Get text with some structure preservation
        lines = []
        for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li', 'td', 'div']):
            text = element.get_text(strip=True)
            if text and len(text) > 10:  # Skip tiny fragments
                lines.append(text)

        # If structured extraction failed, fall back to raw text
        if not lines:
            text = soup.get_text(separator='\n', strip=True)
            lines = [line for line in text.split('\n') if line.strip()]

        return '\n'.join(lines[:100])  # Limit to first 100 lines

    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse email date header to datetime."""
        if not date_str:
            return datetime.now()

        try:
            return parsedate_to_datetime(date_str)
        except Exception:
            return datetime.now()

    def fetch(self) -> List[ContentItem]:
        """Fetch newsletters from Gmail label."""
        if not self._authenticate():
            print("Gmail authentication failed")
            return []

        label_id = self._get_label_id()
        if not label_id:
            return []

        # Calculate date filter (last N days based on config)
        days_back = settings.interests.preferences.time_window_days
        after_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')

        items = []

        try:
            # Search for messages in the label within time window
            query = f"label:{self.label_name} after:{after_date}"
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=50  # Limit to prevent overwhelming
            ).execute()

            messages = results.get('messages', [])
            print(f"Found {len(messages)} newsletters in '{self.label_name}' from last {days_back} days")

            for msg_info in messages:
                try:
                    # Fetch full message
                    msg = self.service.users().messages().get(
                        userId='me',
                        id=msg_info['id'],
                        format='full'
                    ).execute()

                    subject, body, sender, date_str = self._parse_email_content(msg)

                    if not subject or not body:
                        continue

                    # Extract sender name/email for source attribution
                    source_name = sender.split('<')[0].strip() if sender else "Newsletter"
                    source_name = source_name.strip('"')

                    published = self._parse_date(date_str)

                    item = ContentItem(
                        id=f"gmail-{msg_info['id']}",
                        title=subject,
                        content=body[:5000],  # Limit content length
                        url=f"https://mail.google.com/mail/u/0/#inbox/{msg_info['id']}",
                        source_name=source_name,
                        source_category="Newsletter",
                        published_date=published,
                        author=sender,
                        metadata={
                            'gmail_id': msg_info['id'],
                            'media_link': None
                        }
                    )
                    items.append(item)

                except Exception as e:
                    print(f"Error processing message {msg_info['id']}: {e}")
                    continue

        except Exception as e:
            print(f"Error fetching Gmail messages: {e}")

        return items
