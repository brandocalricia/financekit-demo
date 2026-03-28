# FinanceKit Marketing Automation

Automated marketing post scheduler for FinanceKit using GitHub Actions.

## Overview

This system maintains a library of pre-written marketing posts (`posts.json`) and automatically publishes them on a schedule via GitHub Actions. It tracks what's been posted in `post_log.json` to avoid duplicates.

**Supported platforms:** Twitter/X, Reddit, LinkedIn
**Manual-only platforms:** Product Hunt, Hacker News, Instagram/TikTok (posts are in the library for copy-paste use)

## Quick Start

1. Get your API credentials (see below)
2. Add them as GitHub Secrets
3. Enable the workflow — it posts to Twitter daily and Reddit every 3 days
4. Or trigger manually from the Actions tab

---

## Step 1: Get API Credentials

### Twitter/X API Keys

1. Go to [developer.twitter.com](https://developer.twitter.com) and sign in
2. Create a new Project and App (or use an existing one)
3. In your App settings, go to **Keys and Tokens**
4. Generate or regenerate:
   - **API Key** (Consumer Key)
   - **API Key Secret** (Consumer Secret)
   - **Access Token**
   - **Access Token Secret**
5. Make sure your App has **Read and Write** permissions:
   - Go to App Settings > User authentication settings > Edit
   - Set App permissions to **Read and Write**
   - Save changes, then regenerate your Access Token and Secret

**Important:** After changing permissions, you MUST regenerate your access token and secret.

### Reddit API Credentials

1. Go to [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Scroll to the bottom and click **"create another app..."**
3. Fill in:
   - **Name:** FinanceKit Marketing Bot
   - **Type:** Select **script**
   - **Description:** Marketing automation for FinanceKit
   - **redirect uri:** `http://localhost:8080` (required but not used for script apps)
4. Click **Create app**
5. Note down:
   - **Client ID** — the string under the app name (looks like: `aBcDeFg1234`)
   - **Client Secret** — labeled "secret"
6. You'll also need your Reddit **username** and **password**

**Important:** Your Reddit account must meet subreddit posting requirements (minimum karma, account age, etc.). Consider building karma on your account before automating posts.

### LinkedIn API

1. Go to [linkedin.com/developers](https://www.linkedin.com/developers/)
2. Create a new App
3. Request the **Share on LinkedIn** and **Sign In with LinkedIn using OpenID Connect** products
4. In the **Auth** tab, generate an OAuth 2.0 access token with `w_member_social` and `openid` scopes
5. Note: LinkedIn access tokens expire (typically 60 days). You'll need to refresh them periodically.

**Note:** LinkedIn API access for posting requires an approved app. This may take a few days.

---

## Step 2: Add GitHub Secrets

1. Go to your repo: `github.com/brandocalricia/financekit-demo`
2. Click **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret** for each:

| Secret Name | Value |
|---|---|
| `TWITTER_API_KEY` | Your Twitter API Key |
| `TWITTER_API_SECRET` | Your Twitter API Key Secret |
| `TWITTER_ACCESS_TOKEN` | Your Twitter Access Token |
| `TWITTER_ACCESS_SECRET` | Your Twitter Access Token Secret |
| `REDDIT_CLIENT_ID` | Your Reddit app Client ID |
| `REDDIT_CLIENT_SECRET` | Your Reddit app Secret |
| `REDDIT_USERNAME` | Your Reddit username |
| `REDDIT_PASSWORD` | Your Reddit password |
| `LINKEDIN_ACCESS_TOKEN` | Your LinkedIn OAuth access token |

---

## Step 3: How the Schedule Works

The GitHub Action (`.github/workflows/daily-marketing.yml`) runs on this schedule:

| Platform | Frequency | Time |
|---|---|---|
| Twitter | Daily | 10:00 AM EST (3:00 PM UTC) |
| Reddit | Every 3 days | 10:00 AM EST (3:00 PM UTC) |
| LinkedIn | Manual only | Trigger from Actions tab |

The scheduler picks the next unposted message from `posts.json` and logs it in `post_log.json`.

---

## Step 4: Manually Trigger a Post

1. Go to your repo on GitHub
2. Click the **Actions** tab
3. Select **"Daily Marketing Posts"** from the left sidebar
4. Click **"Run workflow"**
5. Choose:
   - **Platform:** twitter, reddit, or linkedin
   - **Dry run:** Check this to preview without posting
   - **Post ID:** Optionally specify a post ID (e.g., `twitter_05`)
6. Click **"Run workflow"**

---

## Running Locally

### Setup

```bash
# Install dependencies
pip install tweepy praw

# Set environment variables (use your actual keys)
export TWITTER_API_KEY="your_key"
export TWITTER_API_SECRET="your_secret"
export TWITTER_ACCESS_TOKEN="your_token"
export TWITTER_ACCESS_SECRET="your_token_secret"
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
export REDDIT_USERNAME="your_username"
export REDDIT_PASSWORD="your_password"
export LINKEDIN_ACCESS_TOKEN="your_token"
```

### Dry Run (preview without posting)

```bash
# Preview the next Twitter post
python marketing/post_scheduler.py --platform twitter --dry-run

# Preview the next Reddit post
python marketing/post_scheduler.py --platform reddit --dry-run

# Preview a specific post
python marketing/post_scheduler.py --platform twitter --post-id twitter_05 --dry-run
```

### Preview All Unposted Messages

```bash
# See all unposted Twitter messages
python marketing/post_scheduler.py --platform twitter --preview-all

# See all unposted Reddit messages
python marketing/post_scheduler.py --platform reddit --preview-all
```

### Post for Real

```bash
# Post the next Twitter message
python marketing/post_scheduler.py --platform twitter

# Post a specific Reddit message
python marketing/post_scheduler.py --platform reddit --post-id reddit_03
```

---

## Adding New Posts

Edit `marketing/posts.json` and add new entries to the appropriate platform array.

### Reddit post format:
```json
{
  "id": "reddit_13",
  "title": "Your post title",
  "body": "Your post body with **markdown** support.",
  "target_subreddit": "r/subredditname",
  "tone": "description_of_tone"
}
```

### Twitter post format:
```json
{
  "id": "twitter_13",
  "text": "Your tweet text (max 280 characters). #hashtags",
  "tone": "description_of_tone"
}
```

### LinkedIn post format:
```json
{
  "id": "linkedin_07",
  "text": "Your LinkedIn post text. Can be longer form.",
  "tone": "description_of_tone"
}
```

**Rules:**
- Keep IDs unique and sequential (e.g., `twitter_13`, `reddit_13`)
- Twitter posts must be under 280 characters
- Reddit posts should sound authentic, not like ads
- Test with `--dry-run` before enabling automated posting

---

## File Structure

```
marketing/
├── README.md              # This file
├── posts.json             # All marketing posts (30+ messages)
├── post_scheduler.py      # Python script that picks and posts
├── post_log.json          # Tracks which posts have been sent
├── seo_content.md         # SEO blog outlines and descriptions
└── email_templates.md     # Email templates for campaigns

.github/
└── workflows/
    └── daily-marketing.yml  # GitHub Actions workflow
```

---

## Troubleshooting

**"All posts have been sent"** — Add more posts to `posts.json` or clear entries from `post_log.json`.

**Twitter 403 error** — Your app likely doesn't have Write permissions. Go to developer.twitter.com > App Settings > User authentication > set to Read and Write > regenerate tokens.

**Reddit 403 error** — Check that your account meets the subreddit's posting requirements (karma, account age). Some subreddits also block bot accounts.

**LinkedIn token expired** — LinkedIn OAuth tokens expire after ~60 days. Generate a new one and update the GitHub Secret.

**Workflow not running on schedule** — GitHub Actions cron jobs can be delayed by up to 15 minutes. Also, workflows on the default branch must be enabled in the Actions tab.

**Post log conflicts** — If two workflows try to commit `post_log.json` at the same time, one will fail. Re-run the failed workflow.
