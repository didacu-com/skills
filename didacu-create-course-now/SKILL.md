---
name: didacu-create-course-now
description: Instantly generate a didacu course without questions — just provide a topic and go. Use when the user wants a quick course without an interview.
argument-hint: "<topic>"
allowed-tools: Bash(python3 *), Bash(curl *)
---

# Create a Didacu Course (Quick)

Generate a course immediately with no interview. The user provides a topic, you call the API. That's it.

## Step 0: Authenticate

```bash
python3 ~/.claude/skills/didacu/didacu-create-course/scripts/auth.py
```

If `"authenticated": true`, extract `api_key` and `api_url`. If not, stop and tell the user to try again.

## Step 1: Get the topic

Use `$ARGUMENTS` as the topic. If no arguments were provided, ask the user for a topic — just the topic, nothing else.

## Step 2: Call the API

Use standard depth, intermediate difficulty, and English as defaults.

```bash
curl -s -X POST <api_url>/api/v1/courses/generate \
  -H "Authorization: Bearer <api_key>" \
  -H "Content-Type: application/json" \
  -d '{"topic": "<topic>", "depth": "standard", "difficulty": "intermediate", "language": "en"}'
```

## Step 3: Handle the response

Check the HTTP status and response JSON:

- **201 (success)**: Tell the user the course is generating (1-5 min) and share the URL. **Do NOT poll status.**
- **403 with credit error**: The response includes `error`, `creditBalance`, `creditCost`, `freeCoursesRemaining`, and `depth`. Show the user a clear message:
  - Display their current credit balance and the cost of the requested depth.
  - If `freeCoursesRemaining > 0`, suggest trying `"overview"` depth (costs 0 credits, uses a free slot).
  - If they have some credits but not enough, suggest a cheaper depth (overview=1, standard=3, comprehensive=5).
  - Always mention they can buy credits at https://didacu.com/pricing.
  - Offer to retry with a different depth if appropriate.
- **401**: Authentication issue — tell the user to re-authenticate.
- **400**: Invalid request — show the error message.
- **Other errors**: Show the raw error and suggest retrying.
