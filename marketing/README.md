# FinanceKit Marketing Automation

Automated marketing post scheduler for FinanceKit using GitHub Actions.

## Overview

This system maintains a library of pre-written marketing posts (`posts.json`) and automatically publishes them on a schedule via GitHub Actions. It tracks what's been posted in `post_log.json` and cycles through posts infinitely — no maintenance required.

**Automated platforms:** Bluesky, Mastodon
**Manual-only platforms:** Product Hunt, Hacker News, Instagram/TikTok (posts are in the library for copy-paste use)

## Quick Start

1. Get your API credentials (see below)
2. Add them as GitHub Secrets
3. Enable the workflow — it posts to Bluesky and Mastodon daily at 10am EST
4. Or trigger manually from the Actions tab

---

## Step 1: Get API Credentials

### Bluesky App Password

1. Log into [bsky.app](https://bsky.app)
2. Go to **Settings** > **Privacy and Security** > **App Passwords**
3. Click **Add App Password**
4. Give it a name like "FinanceKit Marketing"
5. Copy the generated password — you won't see it again
6. Your handle is your Bluesky username (e.g., `yourname.bsky.social`)

### Mastodon Access Token

1. Log into your Mastodon instance (e.g., `mastodon.social`)
2. Go to **Preferences** > **Development** > **New Application**
3. Fill in:
   - **Application name:** FinanceKit Marketing
   - **Scopes:** Check `write:statuses` (minimum needed)
4. Click **Submit**
5. Click on your new application and copy the **Access Token**
6. Note your instance URL (e.g., `https://mastodon.social`)

---

## Step 2: Add GitHub Secrets

1. Go to your repo: `github.com/brandocalricia/financekit-demo`
2. Click **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret** for each:

| Secret Name | Value |
|---|---|
| `BLUESKY_HANDLE` | Your Bluesky handle (e.g., `yourname.bsky.social`) |
| `BLUESKY_APP_PASSWORD` | Your Bluesky app password |
| `MASTODON_INSTANCE` | Your Mastodon instance URL (e.g., `https://mastodon.social`) |
| `MASTODON_ACCESS_TOKEN` | Your Mastodon access token |

---

## Step 3: How the Schedule Works

The GitHub Action (`.github/workflows/daily-marketing.yml`) runs on this schedule:

| Platform | Frequency | Time |
|---|---|---|
| Bluesky | Daily | 10:00 AM EST (3:00 PM UTC) |
| Mastodon | Daily | 10:00 AM EST (3:00 PM UTC) |

The scheduler picks the next post from `posts.json` and logs it in `post_log.json`. After all posts have been used, it **cycles back to the beginning** and repeats forever.

---

## Step 4: Manually Trigger a Post

1. Go to your repo on GitHub
2. Click the **Actions** tab
3. Select **"Daily Marketing Posts"** from the left sidebar
4. Click **"Run workflow"**
5. Choose:
   - **Platform:** bluesky or mastodon
   - **Dry run:** Check this to preview without posting
   - **Post ID:** Optionally specify a post ID (e.g., `bsky_05`)
6. Click **"Run workflow"**

---

## Running Locally

### Setup

No external dependencies needed — uses Python standard library only.

```bash
# Set environment variables (use your actual keys)
export BLUESKY_HANDLE="yourname.bsky.social"
export BLUESKY_APP_PASSWORD="your_app_password"
export MASTODON_INSTANCE="https://mastodon.social"
export MASTODON_ACCESS_TOKEN="your_access_token"
```

### Dry Run (preview without posting)

```bash
# Preview the next Bluesky post
python marketing/post_scheduler.py --platform bluesky --dry-run

# Preview the next Mastodon post
python marketing/post_scheduler.py --platform mastodon --dry-run

# Preview a specific post
python marketing/post_scheduler.py --platform bluesky --post-id bsky_05 --dry-run
```

### Preview All Remaining Posts in Current Cycle

```bash
# See remaining Bluesky posts in the current cycle
python marketing/post_scheduler.py --platform bluesky --preview-all

# See remaining Mastodon posts in the current cycle
python marketing/post_scheduler.py --platform mastodon --preview-all
```

### Post for Real

```bash
# Post the next Bluesky message
python marketing/post_scheduler.py --platform bluesky

# Post a specific Mastodon message
python marketing/post_scheduler.py --platform mastodon --post-id masto_03
```

---

## Adding New Posts

Edit `marketing/posts.json` and add new entries to the appropriate platform array.

### Bluesky post format:
```json
{
  "id": "bsky_13",
  "text": "Your post text (max 300 characters).",
  "tone": "description_of_tone"
}
```

### Mastodon post format:
```json
{
  "id": "masto_13",
  "text": "Your post text (max 500 characters). Can include #hashtags.",
  "tone": "description_of_tone"
}
```

**Rules:**
- Keep IDs unique and sequential (e.g., `bsky_13`, `masto_13`)
- Bluesky posts must be under 300 characters
- Mastodon posts must be under 500 characters
- Test with `--dry-run` before enabling automated posting

---

## How Post Cycling Works

The scheduler uses modulo arithmetic to cycle through posts infinitely:

1. It counts how many posts have been made for a platform (from `post_log.json`)
2. It calculates the next index: `total_posted % total_posts`
3. After posting all 12 posts, it starts over from post #1
4. This continues forever with zero maintenance

Example: If you have 12 Bluesky posts, the cycle looks like:
- Posts 1-12: First cycle
- Posts 13-24: Same 12 posts again (cycle 2)
- Posts 25-36: Same 12 posts again (cycle 3)
- ...and so on forever

---

## File Structure

```
marketing/
├── README.md              # This file
├── posts.json             # All marketing posts (12 Bluesky + 12 Mastodon + manual platforms)
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

**Bluesky authentication error** — Make sure your handle and app password are correct. App passwords are different from your account password. Generate a new one at Settings > App Passwords.

**Mastodon 401/403 error** — Your access token may be invalid or missing the `write:statuses` scope. Create a new application and token.

**Workflow not running on schedule** — GitHub Actions cron jobs can be delayed by up to 15 minutes. Also, workflows on the default branch must be enabled in the Actions tab.

**Post log conflicts** — If both Bluesky and Mastodon workflows try to commit `post_log.json` at the same time, one may fail. Re-run the failed workflow.

**Posts cycling too fast** — If you notice the same posts repeating quickly, check `post_log.json` for duplicate entries. You can manually edit the log if needed.
