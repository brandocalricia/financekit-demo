#!/usr/bin/env python3
"""
FinanceKit Marketing Post Scheduler

Reads marketing posts from posts.json, tracks posted history in post_log.json,
and posts to Twitter, Reddit, or LinkedIn via their respective APIs.

Usage:
    python post_scheduler.py --platform twitter --dry-run
    python post_scheduler.py --platform reddit
    python post_scheduler.py --platform linkedin --preview-all
    python post_scheduler.py --platform twitter --post-id twitter_05

Environment variables required:
    Twitter:  TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
    Reddit:   REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD, REDDIT_USER_AGENT
    LinkedIn: LINKEDIN_ACCESS_TOKEN
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
POSTS_FILE = SCRIPT_DIR / "posts.json"
LOG_FILE = SCRIPT_DIR / "post_log.json"


def load_posts():
    """Load all posts from posts.json."""
    with open(POSTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_log():
    """Load the post log, creating it if it doesn't exist."""
    if LOG_FILE.exists():
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"posted": []}


def save_log(log):
    """Save the post log."""
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def get_posted_ids(log, platform=None):
    """Get set of already-posted post IDs, optionally filtered by platform."""
    entries = log.get("posted", [])
    if platform:
        entries = [e for e in entries if e.get("platform") == platform]
    return {entry["post_id"] for entry in entries}


def get_platform_key(platform):
    """Map platform argument to posts.json key."""
    mapping = {
        "twitter": "twitter",
        "reddit": "reddit",
        "linkedin": "linkedin",
        "producthunt": "product_hunt",
        "hackernews": "hacker_news",
        "instagram": "instagram_tiktok",
        "tiktok": "instagram_tiktok",
    }
    return mapping.get(platform)


def get_cycle_count(log, platform):
    """Count how many full cycles have been completed for a platform."""
    entries = [e for e in log.get("posted", []) if e.get("platform") == platform]
    return len(entries)


def get_next_post(platform, specific_id=None):
    """Get the next post for a platform. Cycles endlessly through all posts."""
    posts = load_posts()
    log = load_log()

    platform_key = get_platform_key(platform)
    if not platform_key or platform_key not in posts:
        print(f"Error: Unknown platform '{platform}'")
        sys.exit(1)

    platform_posts = posts[platform_key]

    if specific_id:
        posted_ids = get_posted_ids(log, platform)
        for post in platform_posts:
            if post["id"] == specific_id:
                if specific_id in posted_ids:
                    print(f"Warning: Post {specific_id} has already been posted.")
                return post
        print(f"Error: Post ID '{specific_id}' not found.")
        sys.exit(1)

    # Calculate which post is next using modulo to cycle forever
    total_posted = get_cycle_count(log, platform)
    total_posts = len(platform_posts)

    if total_posts == 0:
        print(f"No posts found for {platform}.")
        return None

    next_index = total_posted % total_posts
    cycle_number = (total_posted // total_posts) + 1
    post = platform_posts[next_index]

    if total_posted >= total_posts:
        print(f"[Cycle {cycle_number}] Recycling posts for {platform} (post {next_index + 1}/{total_posts})")

    return post


def get_remaining_in_cycle(platform):
    """Get remaining posts in the current cycle for a platform."""
    posts = load_posts()
    log = load_log()

    platform_key = get_platform_key(platform)
    if not platform_key or platform_key not in posts:
        print(f"Error: Unknown platform '{platform}'")
        sys.exit(1)

    platform_posts = posts[platform_key]
    total_posted = get_cycle_count(log, platform)
    total_posts = len(platform_posts)

    if total_posts == 0:
        return []

    current_index = total_posted % total_posts
    return platform_posts[current_index:]


def log_post(post_id, platform, result="success", details=""):
    """Log a posted message."""
    log = load_log()
    log["posted"].append({
        "post_id": post_id,
        "platform": platform,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "result": result,
        "details": details,
    })
    save_log(log)


def preview_post(post, platform):
    """Print a preview of a post."""
    print(f"\n{'='*60}")
    print(f"Platform: {platform.upper()}")
    print(f"Post ID:  {post['id']}")
    print(f"Tone:     {post.get('tone', 'N/A')}")
    print(f"{'='*60}")

    if platform == "reddit":
        print(f"Subreddit: {post.get('target_subreddit', 'N/A')}")
        print(f"Title:     {post['title']}")
        print(f"\n{post['body']}")
    elif platform == "twitter":
        print(f"\n{post['text']}")
        char_count = len(post["text"])
        print(f"\n[{char_count}/280 characters]")
    elif platform == "linkedin":
        print(f"\n{post['text']}")
    elif platform in ("producthunt", "hackernews"):
        print(f"Title: {post.get('title', post.get('tagline', 'N/A'))}")
        if "body" in post:
            print(f"\n{post['body']}")
        if "description" in post:
            print(f"\n{post['description']}")
    elif platform in ("instagram", "tiktok"):
        print(f"\n{post['text']}")
    print()


# --- Platform posting functions ---

def post_to_twitter(post):
    """Post a tweet using Twitter API v2 via tweepy."""
    try:
        import tweepy
    except ImportError:
        print("Error: tweepy is not installed. Run: pip install tweepy")
        sys.exit(1)

    api_key = os.environ.get("TWITTER_API_KEY")
    api_secret = os.environ.get("TWITTER_API_SECRET")
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    access_secret = os.environ.get("TWITTER_ACCESS_SECRET")

    if not all([api_key, api_secret, access_token, access_secret]):
        print("Error: Missing Twitter API credentials in environment variables.")
        print("Required: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET")
        sys.exit(1)

    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret,
    )

    text = post["text"]
    if len(text) > 280:
        print(f"Warning: Tweet is {len(text)} characters (max 280). Truncating.")
        text = text[:277] + "..."

    response = client.create_tweet(text=text)
    tweet_id = response.data["id"]
    print(f"Tweet posted successfully! ID: {tweet_id}")
    return f"tweet_id:{tweet_id}"


def post_to_reddit(post):
    """Post to Reddit using PRAW."""
    try:
        import praw
    except ImportError:
        print("Error: praw is not installed. Run: pip install praw")
        sys.exit(1)

    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    username = os.environ.get("REDDIT_USERNAME")
    password = os.environ.get("REDDIT_PASSWORD")
    user_agent = os.environ.get("REDDIT_USER_AGENT", f"FinanceKit Marketing Bot by /u/{username}")

    if not all([client_id, client_secret, username, password]):
        print("Error: Missing Reddit API credentials in environment variables.")
        print("Required: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD")
        sys.exit(1)

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password,
        user_agent=user_agent,
    )

    subreddit_name = post["target_subreddit"].replace("r/", "")
    subreddit = reddit.subreddit(subreddit_name)

    submission = subreddit.submit(
        title=post["title"],
        selftext=post["body"],
    )
    print(f"Reddit post submitted! URL: https://reddit.com{submission.permalink}")
    return f"reddit_url:https://reddit.com{submission.permalink}"


def post_to_linkedin(post):
    """Post to LinkedIn using the LinkedIn API."""
    import urllib.request
    import urllib.error

    access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    if not access_token:
        print("Error: Missing LINKEDIN_ACCESS_TOKEN environment variable.")
        sys.exit(1)

    # Get the user's LinkedIn profile ID
    profile_url = "https://api.linkedin.com/v2/userinfo"
    req = urllib.request.Request(profile_url)
    req.add_header("Authorization", f"Bearer {access_token}")

    try:
        with urllib.request.urlopen(req) as response:
            profile_data = json.loads(response.read().decode())
            person_id = profile_data["sub"]
    except urllib.error.HTTPError as e:
        print(f"Error fetching LinkedIn profile: {e.code} {e.reason}")
        sys.exit(1)

    # Create the post
    post_url = "https://api.linkedin.com/v2/ugcPosts"
    post_data = {
        "author": f"urn:li:person:{person_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post["text"]
                },
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        },
    }

    data = json.dumps(post_data).encode("utf-8")
    req = urllib.request.Request(post_url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Restli-Protocol-Version", "2.0.0")

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            post_urn = result.get("id", "unknown")
            print(f"LinkedIn post published! URN: {post_urn}")
            return f"linkedin_urn:{post_urn}"
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Error posting to LinkedIn: {e.code} {e.reason}")
        print(f"Details: {error_body}")
        sys.exit(1)


PLATFORM_POSTERS = {
    "twitter": post_to_twitter,
    "reddit": post_to_reddit,
    "linkedin": post_to_linkedin,
}


def main():
    parser = argparse.ArgumentParser(
        description="FinanceKit Marketing Post Scheduler"
    )
    parser.add_argument(
        "--platform",
        required=True,
        choices=["twitter", "reddit", "linkedin", "producthunt", "hackernews", "instagram", "tiktok"],
        help="Platform to post to",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be posted without actually posting",
    )
    parser.add_argument(
        "--preview-all",
        action="store_true",
        help="Preview all unposted messages for a platform",
    )
    parser.add_argument(
        "--post-id",
        type=str,
        default=None,
        help="Post a specific post by ID (e.g., twitter_05)",
    )

    args = parser.parse_args()

    if args.preview_all:
        remaining = get_remaining_in_cycle(args.platform)
        if not remaining:
            print(f"No posts found for {args.platform}.")
            return
        posts_data = load_posts()
        platform_key = get_platform_key(args.platform)
        total = len(posts_data[platform_key])
        log = load_log()
        posted_count = get_cycle_count(log, args.platform)
        cycle = (posted_count // total) + 1 if total > 0 else 1
        print(f"Cycle {cycle}: {len(remaining)} posts remaining in this cycle ({posted_count} total posted):\n")
        for post in remaining:
            preview_post(post, args.platform)
        return

    post = get_next_post(args.platform, specific_id=args.post_id)
    if not post:
        return

    if args.dry_run:
        print("[DRY RUN] Would post the following:")
        preview_post(post, args.platform)
        return

    # Actually post
    poster = PLATFORM_POSTERS.get(args.platform)
    if not poster:
        print(f"Automated posting not supported for {args.platform}.")
        print("Use --dry-run or --preview-all to view posts, then post manually.")
        preview_post(post, args.platform)
        return

    print(f"Posting to {args.platform}...")
    details = poster(post)
    log_post(post["id"], args.platform, result="success", details=details or "")
    print("Done! Post logged to post_log.json")


if __name__ == "__main__":
    main()
