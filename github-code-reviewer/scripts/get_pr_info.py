#!/usr/bin/env python3
"""
Get comprehensive PR information including metadata, files changed, and reviews.
Usage: python get_pr_info.py <pr_url_or_number>
"""

import sys
import json
import subprocess


def get_pr_info(pr_identifier):
    """
    Fetch PR information using gh CLI.

    Args:
        pr_identifier: Either PR number or full PR URL

    Returns:
        dict: PR information including title, body, files, reviews
    """
    # Extract PR number and repo from identifier
    if pr_identifier.startswith('http'):
        # Parse URL like https://github.com/owner/repo/pull/123
        parts = pr_identifier.rstrip('/').split('/')
        pr_number = parts[-1]
        repo = f"{parts[-4]}/{parts[-3]}"
    else:
        # Just a PR number, try to infer repo from current directory
        pr_number = pr_identifier
        repo = None

    # Build gh command
    cmd = ['gh', 'pr', 'view', pr_number]
    if repo:
        cmd.extend(['--repo', repo])

    cmd.extend([
        '--json',
        'number,title,body,state,author,headRefName,headRefOid,baseRefName,files,reviews,url,additions,deletions'
    ])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error fetching PR info: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python get_pr_info.py <pr_url_or_number>", file=sys.stderr)
        sys.exit(1)

    pr_identifier = sys.argv[1]
    pr_info = get_pr_info(pr_identifier)

    # Pretty print the JSON
    print(json.dumps(pr_info, indent=2))


if __name__ == '__main__':
    main()
