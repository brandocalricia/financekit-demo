#!/usr/bin/env python3
"""
FinanceKit Marketing Post Scheduler

Reads marketing posts from posts.json, tracks posted history in post_log.json,
and posts to Bluesky and Mastodon via their respective APIs.

Usage:
    python post_scheduler.py --platform bluesky --dry-run
    python post_scheduler.py --platform mastodon
    python post_scheduler.py --platform bluesky --preview-all
    python post_scheduler.py --platform mastodon --post-id masto_05

Environment variables required:
    Bluesky:  BLUESKY_HANDLE, BLUESKY_APP_PASSWORD
    Mastodon: MASTODON_INSTANCE, MASTODON_ACCESS_TOKEN
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
        "bluesky": "bluesky",
        "mastodon": "mastodon",
        "producthunt": "product_hunt",
        "hackernews": "hacker_news",
        "instagram": "instagram_tiktok",
        "tiktok": "instagram_tiktok",
    }
    return mapping.get(platform)


def get_cycle_count(log, platform):
    """Count how many posts have been made for a platform."""
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

    if platform == "bluesky":
        print(f"\n{post['text']}")
        char_count = len(post["text"])
        print(f"\n[{char_count}/300 characters]")
    elif platform == "mastodon":
        print(f"\n{post['text']}")
        char_count = len(post["text"])
        print(f"\n[{char_count}/500 characters]")
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

def post_to_bluesky(post):
    """Post to Bluesky using the AT Protocol API."""
    import urllib.request
    import urllib.error

    handle = os.environ.get("BLUESKY_HANDLE")
    app_password = os.environ.get("BLUESKY_APP_PASSWORD")

    if not all([handle, app_password]):
        print("Error: Missing Bluesky credentials in environment variables.")
        print("Required: BLUESKY_HANDLE, BLUESKY_APP_PASSWORD")
        sys.exit(1)

    # Authenticate and get session token
    auth_url = "https://bsky.social/xrpc/com.atproto.server.createSession"
    auth_data = json.dumps({
        "identifier": handle,
        "password": app_password,
    }).encode("utf-8")

    req = urllib.request.Request(auth_url, data=auth_data, method="POST")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as response:
            session = json.loads(response.read().decode())
            access_token = session["accessJwt"]
            did = session["did"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Error authenticating with Bluesky: {e.code} {e.reason}")
        print(f"Details: {error_body}")
        sys.exit(1)

    # Create the post
    text = post["text"]
    if len(text) > 300:
        print(f"Warning: Post is {len(text)} characters (max 300). Truncating.")
        text = text[:297] + "..."

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    post_url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
    post_data = json.dumps({
        "repo": did,
        "collection": "app.bsky.feed.post",
        "record": {
            "$type": "app.bsky.feed.post",
            "text": text,
            "createdAt": now,
        },
    }).encode("utf-8")

    req = urllib.request.Request(post_url, data=post_data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {access_token}")

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            post_uri = result.get("uri", "unknown")
            print(f"Bluesky post published! URI: {post_uri}")
            return f"bsky_uri:{post_uri}"
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Error posting to Bluesky: {e.code} {e.reason}")
        print(f"Details: {error_body}")
        sys.exit(1)


def post_to_mastodon(post):
    """Post to Mastodon using the Mastodon API."""
    import urllib.request
    import urllib.error

    instance = os.environ.get("MASTODON_INSTANCE", "").rstrip("/")
    access_token = os.environ.get("MASTODON_ACCESS_TOKEN")

    if not all([instance, access_token]):
        print("Error: Missing Mastodon credentials in environment variables.")
        print("Required: MASTODON_INSTANCE (e.g. https://mastodon.social), MASTODON_ACCESS_TOKEN")
        sys.exit(1)

    text = post["text"]
    if len(text) > 500:
        print(f"Warning: Post is {len(text)} characters (max 500). Truncating.")
        text = text[:497] + "..."

    post_url = f"{instance}/api/v1/statuses"
    post_data = json.dumps({
        "status": text,
        "visibility": "public",
    }).encode("utf-8")

    req = urllib.request.Request(post_url, data=post_data, method="POST")
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            status_url = result.get("url", "unknown")
            status_id = result.get("id", "unknown")
            print(f"Mastodon post published! URL: {status_url}")
            return f"mastodon_url:{status_url}"
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Error posting to Mastodon: {e.code} {e.reason}")
        print(f"Details: {error_body}")
        sys.exit(1)


PLATFORM_POSTERS = {
    "bluesky": post_to_bluesky,
    "mastodon": post_to_mastodon,
}


def main():
    parser = argparse.ArgumentParser(
        description="FinanceKit Marketing Post Scheduler"
    )
    parser.add_argument(
        "--platform",
        required=True,
        choices=["bluesky", "mastodon", "producthunt", "hackernews", "instagram", "tiktok"],
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
        help="Post a specific post by ID (e.g., bsky_05)",
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
