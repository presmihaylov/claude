#!/usr/bin/env python3
"""
Submit a complete pull request review with multiple inline comments.
Usage: python submit_review.py <pr_number> --repo owner/repo --comments-file comments.json [--event APPROVE|REQUEST_CHANGES|COMMENT] [--body "Review summary"]
"""

import sys
import json
import subprocess
import argparse


def submit_review(pr_number, repo, comments, event='COMMENT', body=None, commit_sha=None):
    """
    Submit a pull request review with multiple inline comments.

    Args:
        pr_number: PR number
        repo: Repository in format owner/repo
        comments: List of comment objects with {path, line, body, start_line (optional)}
        event: Review event type (APPROVE, REQUEST_CHANGES, COMMENT)
        body: Optional overall review summary
        commit_sha: Optional commit SHA (defaults to PR head)

    Returns:
        dict: Response from GitHub API
    """
    # Get commit SHA if not provided
    if not commit_sha:
        cmd = ['gh', 'pr', 'view', pr_number, '--repo', repo, '--json', 'headRefOid', '--jq', '.headRefOid']
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            commit_sha = result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error fetching commit SHA: {e.stderr}", file=sys.stderr)
            sys.exit(1)

    # Build API request
    api_path = f"repos/{repo}/pulls/{pr_number}/reviews"

    # Prepare review comments in GitHub API format
    formatted_comments = []
    for comment in comments:
        formatted_comment = {
            'path': comment['path'],
            'line': comment['line'],
            'body': comment['body'],
            'side': 'RIGHT'
        }

        # Add start_line for multi-line comments
        if 'start_line' in comment and comment['start_line'] is not None:
            formatted_comment['start_line'] = comment['start_line']
            formatted_comment['start_side'] = 'RIGHT'

        formatted_comments.append(formatted_comment)

    # Build request payload
    payload = {
        'commit_id': commit_sha,
        'event': event,
        'comments': formatted_comments
    }

    if body:
        payload['body'] = body

    # Write payload to temp file for gh api
    payload_json = json.dumps(payload)

    # Execute API call
    cmd = [
        'gh', 'api',
        '--method', 'POST',
        '-H', 'Accept: application/vnd.github+json',
        '-H', 'X-GitHub-Api-Version: 2022-11-28',
        api_path,
        '--input', '-'
    ]

    try:
        result = subprocess.run(
            cmd,
            input=payload_json,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error submitting review: {e.stderr}", file=sys.stderr)
        print(f"Payload: {payload_json}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Submit a complete pull request review with multiple inline comments'
    )
    parser.add_argument('pr_number', help='PR number')
    parser.add_argument('--repo', required=True, help='Repository in format owner/repo')
    parser.add_argument(
        '--comments-file',
        required=True,
        help='JSON file containing array of comments [{path, line, body, start_line?}, ...]'
    )
    parser.add_argument(
        '--event',
        choices=['APPROVE', 'REQUEST_CHANGES', 'COMMENT'],
        default='COMMENT',
        help='Review event type (default: COMMENT)'
    )
    parser.add_argument('--body', help='Optional overall review summary')
    parser.add_argument('--commit-sha', help='Commit SHA (defaults to PR head)')

    args = parser.parse_args()

    # Load comments from file
    try:
        with open(args.comments_file, 'r') as f:
            comments = json.load(f)
    except FileNotFoundError:
        print(f"Error: Comments file not found: {args.comments_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in comments file: {e}", file=sys.stderr)
        sys.exit(1)

    result = submit_review(
        args.pr_number,
        args.repo,
        comments,
        args.event,
        args.body,
        args.commit_sha
    )

    print(json.dumps(result, indent=2))
    print(f"\n✅ Review submitted successfully with {len(comments)} comments", file=sys.stderr)


if __name__ == '__main__':
    main()
