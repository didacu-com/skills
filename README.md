# didacu Skills for Claude Code

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills that generate [didacu](https://didacu.com) courses from your terminal — including courses built around your own codebase.

Since these run inside Claude Code, they can read your project files, understand your architecture, and generate courses tailored to what's actually in front of you.

```
/didacu-create-course how does the auth flow work in this project
/didacu-create-course explain our database schema and data model
/didacu-create-course onboard me to this repo's API layer
```

Or use it for any topic:

```
/didacu-create-course distributed consensus algorithms
/didacu-create-course-now TypeScript generics
```

## Skills

### `didacu-create-course`

Interactive mode. Claude reads your codebase if relevant, asks clarifying questions about what you want to learn, then generates a course with slides, quizzes, and progress tracking.

Works great for:
- **Onboarding** — "walk me through how this service handles payments"
- **Deep dives** — "I want to understand the state machine in `src/workflow/`"
- **Learning from your code** — "teach me the patterns this project uses for error handling"
- **Any topic** — works without a codebase too

Three depth levels: overview (~10 min), standard (~25 min), comprehensive (60+ min).

### `didacu-create-course-now`

Quick mode — no questions asked. Provide a topic and it generates immediately with sensible defaults (standard depth, intermediate difficulty).

```
/didacu-create-course-now distributed systems
```

## Installation

Clone the repo into your Claude Code skills directory:

```bash
git clone https://github.com/didacu-com/skills.git ~/.claude/skills/didacu
```

The skills will be available as slash commands (`/didacu-create-course`, `/didacu-create-course-now`) in your next Claude Code session.

## Authentication

On first use, the skill opens your browser to `didacu.com/cli-auth` where you log in and authorize the CLI. Credentials are saved to `~/.didacu/credentials.json` and reused for subsequent runs.

## How it works

1. You invoke the skill with a topic
2. Claude authenticates with the didacu API
3. (Interactive mode) Claude asks clarifying questions to understand your learning goals
4. Claude calls the didacu course generation API
5. You get a URL to your course, which generates in 1-5 minutes depending on depth

## Credits

- **Overview** courses: 1 credit (3 free per week)
- **Standard** courses: 3 credits
- **Comprehensive** courses: 5 credits

Purchase credits at [didacu.com/pricing](https://didacu.com/pricing).

## License

MIT
