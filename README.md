# didacu Skills for Claude Code

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills that let you generate [didacu](https://didacu.com) courses directly from your terminal.

## Skills

### `didacu-create-course`

Interactive course creation. Claude interviews you about what you want to learn — topic, depth, difficulty, focus areas — then generates a tailored course with slides, quizzes, and progress tracking.

```
/didacu-create-course React server components
```

Features:
- Conversational topic refinement
- Codebase-aware — can read your project files and build a course around them
- Three depth levels: overview (~10 min), standard (~25 min), comprehensive (60+ min)

### `didacu-create-course-now`

Quick course generation with no questions asked. Provide a topic and it fires immediately with sensible defaults (standard depth, intermediate difficulty).

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
