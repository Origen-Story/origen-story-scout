# Gmail API Setup for Newsletter Ingestion

This guide walks you through setting up Gmail API access so Origen Story Scout can fetch newsletters from your Gmail account.

## Overview

The app will:
1. Connect to your Gmail account (read-only access)
2. Fetch emails from a specific label (e.g., "Newsletters")
3. Extract content and process them alongside RSS feeds

## Prerequisites

- A Google account with Gmail
- A Gmail label set up for newsletters (e.g., "Newsletters")

## Step 1: Set Up Gmail Filter

First, create a filter to automatically label and archive incoming newsletters:

1. Open Gmail Settings (gear icon) > "See all settings"
2. Go to "Filters and Blocked Addresses" tab
3. Click "Create a new filter"
4. In the "From" field, enter your newsletter senders:
   ```
   from:substack.com OR from:bensbites.co OR from:newsletter@example.com
   ```
5. Click "Create filter"
6. Check these options:
   - [x] Skip the Inbox (Archive it)
   - [x] Apply the label: "Newsletters" (create if needed)
   - [x] Also apply filter to matching conversations
7. Click "Create filter"

Now newsletters will skip your inbox but be accessible via the label.

## Step 2: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" > "New Project"
3. Name it something like "Origen Story Scout"
4. Click "Create"

## Step 3: Enable Gmail API

1. In your new project, go to "APIs & Services" > "Library"
2. Search for "Gmail API"
3. Click on "Gmail API"
4. Click "Enable"

## Step 4: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Select "External" (unless you have Google Workspace)
3. Click "Create"
4. Fill in required fields:
   - App name: "Origen Story Scout"
   - User support email: Your email
   - Developer contact email: Your email
5. Click "Save and Continue"
6. On "Scopes" page, click "Add or Remove Scopes"
7. Find and select: `https://www.googleapis.com/auth/gmail.readonly`
8. Click "Update" then "Save and Continue"
9. On "Test users" page, click "Add Users"
10. Add your Gmail address
11. Click "Save and Continue"

## Step 5: Create OAuth Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Application type: "Desktop app"
4. Name: "Origen Story Scout Desktop"
5. Click "Create"
6. Click "Download JSON" on the popup
7. Rename the downloaded file to `credentials.json`
8. Move it to your project's `config/` folder:
   ```
   origen-story-scout/
   └── config/
       └── credentials.json  <-- Place here
   ```

## Step 6: First Run Authentication

1. Make sure Gmail is enabled in `config/sources.yaml`:
   ```yaml
   gmail:
     enabled: true
     label_name: "Newsletters"
     credentials_path: "config/credentials.json"
   ```

2. Run the scout:
   ```bash
   python -m src.main run
   ```

3. A browser window will open asking you to sign in to Google
4. Select your Gmail account
5. You'll see a warning "Google hasn't verified this app" - click "Continue"
6. Grant the requested permissions (read-only Gmail access)
7. The browser will show "Authentication successful"

A `gmail_token.pickle` file will be created in `config/` to remember your authentication.

## Troubleshooting

### "credentials.json not found"
Make sure you downloaded the OAuth credentials and placed them in `config/credentials.json`

### "Label 'Newsletters' not found"
Create the label in Gmail, or update `label_name` in `config/sources.yaml` to match your actual label name.

### "Access blocked: This app's request is invalid"
Your OAuth consent screen may not be properly configured. Ensure you've added yourself as a test user.

### Token expired
Delete `config/gmail_token.pickle` and run again to re-authenticate.

## Security Notes

- `credentials.json` contains your OAuth client secret - keep it private
- `gmail_token.pickle` contains your access token - keep it private
- Both files are gitignored by default
- The app only requests read-only access to Gmail
- Credentials are stored locally, never sent to any external service

## Disabling Gmail Integration

To disable Gmail fetching, set `enabled: false` in `config/sources.yaml`:

```yaml
gmail:
  enabled: false
```
