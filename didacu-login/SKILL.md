---
name: didacu-login
description: Log in to didacu or switch accounts. Clears saved credentials and re-authenticates via the browser. Use when the user says "login", "log in", "switch account", "re-authenticate", or "refresh credentials".
argument-hint: ""
allowed-tools: Bash(python3 *), Bash(rm *)
---

# Didacu Login

Re-authenticate with didacu.com. This clears any saved credentials and opens the browser for a fresh login — useful when switching accounts or if the current key has expired.

## Step 1: Clear existing credentials

```bash
rm -f ~/.didacu/credentials.json
```

Tell the user you're clearing their saved credentials and opening the browser to log in.

## Step 2: Authenticate

```bash
python3 ~/.claude/skills/didacu-create-course/scripts/auth.py
```

This starts a local server and opens the browser to `didacu.com/cli-auth`. The user logs in (or switches accounts) and authorizes the CLI. New credentials are saved automatically.

## Step 3: Confirm

If `"authenticated": true`, tell the user they're logged in and ready to go. Mention they can now use `/didacu-create-course` or `/didacu-create-course-now` to create courses.

If authentication fails, show the error and suggest trying again with `/didacu-login`.
