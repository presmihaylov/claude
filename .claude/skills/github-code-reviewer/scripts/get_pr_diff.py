#!/usr/bin/env python3
"""
Get the full diff for a pull request.
Usage: python get_pr_diff.py <pr_url_or_number> [--file <filepath>]
"""

import sys
import subprocess
import argparse


def get_pr_diff(pr_identifier, repo=None, filepath=None):
    """
    Fetch PR diff using gh CLI.

    Args:
        pr_identifier: Either PR number or full PR URL
        repo: Optional repository in format owner/repo
        filepath: Optional specific file to get diff for

    Returns:
        str: The diff content
    """
    # Extract PR number and repo from identifier if it's a URL
    if pr_identifier.startswith('http'):
        parts = pr_identifier.rstrip('/').split('/')
        pr_number = parts[-1]
        if not repo:
            repo = f"{parts[-4]}/{parts[-3]}"
    else:
        pr_number = pr_identifier

    # Build gh command
    cmd = ['gh', 'pr', 'diff', pr_number]
    if repo:
        cmd.extend(['--repo', repo])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        diff = result.stdout

        # If specific file requested, filter the diff
        if filepath:
            diff = filter_diff_by_file(diff, filepath)

        return diff

    except subprocess.CalledProcessError as e:
        print(f"Error fetching PR diff: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def filter_diff_by_file(diff, filepath):
    """
    Filter unified diff to only show changes for a specific file.

    Args:
        diff: The full diff content
        filepath: Path to filter for

    Returns:
        str: Filtered diff content
    """
    lines = diff.split('\n')
    result = []
    in_target_file = False

    for line in lines:
        if line.startswith('diff --git'):
            # Check if this is the file we want
            in_target_file = filepath in line

        if in_target_file:
            result.append(line)

    return '\n'.join(result)


def main():
    parser = argparse.ArgumentParser(
        description='Get the full diff for a pull request'
    )
    parser.add_argument(
        'pr_identifier',
        help='PR number or full PR URL'
    )
    parser.add_argument(
        '--repo',
        help='Repository in format owner/repo (optional if using URL)'
    )
    parser.add_argument(
        '--file',
        help='Specific file to get diff for (optional)'
    )

    args = parser.parse_args()

    diff = get_pr_diff(args.pr_identifier, args.repo, args.file)
    print(diff)


if __name__ == '__main__':
    main()
