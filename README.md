# Mini Claw Code

**An educational toy to illustrate the *idea* behind Claude Code -- nothing more.**

> **Important disclaimer**: This project exists solely to demonstrate the **core concept** -- the agentic loop and context engineering pattern that powers tools like Claude Code. It is NOT a recreation of Claude Code, nor does it claim to be. The real Claude Code is a massive engineering effort: hardened infrastructure, security sandboxing, permission systems, LSP integration, multi-model orchestration, context window management, streaming, caching, IDE extensions, and countless edge cases handled by a world-class engineering team at Anthropic. I have enormous respect for all of that work. What you see here is just the **idea distilled to its skeleton** -- like drawing a stick figure to explain human anatomy. The skeleton helps you *understand*, but it's not the real thing.

## The Core Idea

At its heart, Claude Code is an **agentic loop** with **tools**:

```
User Input -> LLM -> [Tool Call?] -> Execute Tool -> Feed Result Back -> LLM -> ... -> Final Answer
```

This project strips that idea down to just **2 tools** to make the concept crystal clear:

| Tool | What it does |
|------|-------------|
| `bash` | Runs any shell command and returns the output |
| `todowrite` | Tracks tasks with status (pending/in_progress/completed) |

With just these 2 tools, the LLM can already:
- Read files (`cat`, `ls`, `find`)
- Edit files (`sed`, `echo >`)
- Run tests (`pytest`, `npm test`)
- Install packages (`pip install`, `npm install`)
- Use git (`git add`, `git commit`, `git push`)
- Plan and track multi-step work (via todowrite)

That's the **idea**. But idea is only the starting point -- the real Claude Code has 20+ specialized tools (Read, Write, Edit, Grep, Glob, LSP, etc.) that are not just "wrappers around bash." They provide structured output, permission controls, performance optimization, better error handling, and UX that a raw bash command can never match. The engineering to make all of that work reliably at scale is where the real magic lives.

## The Art of Context Engineering

This project is a lesson in **context engineering** -- the craft of shaping what the LLM sees in its context window so it behaves the way you want.

### What is Context Engineering?

It's not just "prompt engineering." Context engineering is about designing the **entire information environment** the model operates in:

```
Context Window = System Prompt + Tool Descriptions + Conversation History + Tool Results
```

Every single token in that window influences the model's behavior. In this project, there are **3 levers** of context engineering:

### Lever 1: The System Prompt (`prompts/system_prompt.txt`)

This is **who the agent is**. It defines:
- **Identity**: "You are an interactive CLI tool that helps users with software engineering tasks"
- **Behavior constraints**: Be concise, don't add preamble, don't surprise the user
- **Decision-making rules**: When to be proactive vs. when to ask

The system prompt is context engineering at the **character level** -- you're shaping the model's personality and judgment.

### Lever 2: Tool Descriptions (`prompts/bash.txt`, `prompts/todowrite.txt`)

This is where context engineering gets interesting. Look at what tool descriptions actually do:

**bash.txt** doesn't just say "run a command." It teaches the model:
- Quote file paths with spaces
- Chain commands with `&&` or `;`
- Use absolute paths
- Verify parent directories before creating files

**todowrite.txt** doesn't just say "track tasks." It teaches the model:
- WHEN to use it (complex tasks, 3+ steps)
- WHEN NOT to use it (trivial tasks, informational questions)
- HOW to use it (one in_progress at a time, mark complete immediately)

> **Key insight**: Tool descriptions are not just API docs. They are **behavioral instructions disguised as documentation.** The model reads them and internalizes the rules as part of its decision-making.

This is why Claude Code's real tool descriptions are so long (100+ lines each) -- they're not just describing parameters. They're encoding expertise, guardrails, and workflow patterns into the context.

### Lever 3: Tool Results (the feedback loop)

Every tool result gets appended to the conversation history. This creates a **dynamic context** that grows as the agent works:

```
[System Prompt]                     <- Static context
[User: "fix the bug in auth.py"]   <- User intent
[LLM calls bash: "cat auth.py"]    <- Agent's plan
[Tool result: file contents...]     <- New knowledge
[LLM calls bash: "sed ..."]        <- Informed action
[Tool result: "(no output)"]       <- Confirmation
[LLM: "Fixed the bug."]            <- Final answer
```

The context is being **engineered in real-time** by the agent itself. Each tool call is a decision about what information to pull into the context window.

Even `todowrite`'s return message is context engineering:
```
"Todos have been modified successfully. Ensure that you continue to use 
the todo list to track your progress. Please proceed with the current 
tasks if applicable"
```
This isn't just a confirmation -- it's a **behavioral nudge** injected back into the context, reminding the model to keep using the todo list and keep working.

### Why This Matters

The difference between a bad AI agent and a great one is NOT the model. It's the context:

| Bad Context Engineering | Good Context Engineering |
|------------------------|------------------------|
| "You are a helpful assistant" | Specific identity + constraints + examples |
| "bash: runs commands" | Detailed tool docs with when/how/guardrails |
| No task tracking | TodoWrite nudges the model to plan and track |
| Raw tool results | Structured results with behavioral hints |

Context engineering is ONE pillar of what makes Claude Code great. But it's far from the only one. The real product also requires:
- **Infrastructure engineering**: Streaming, caching, context window management, model routing
- **Security engineering**: Sandboxing, permission systems, preventing code injection
- **Developer experience**: IDE integrations, keyboard shortcuts, hooks, slash commands
- **Reliability engineering**: Error recovery, retry logic, graceful degradation
- **Performance engineering**: Parallel tool calls, smart caching, token optimization

This project only demonstrates the context engineering pillar -- in ~60 lines of Python + 3 text files. Respect the iceberg beneath the surface.

## How it works

```
main.py                      -- The agentic loop (~60 lines)
prompts/
  system_prompt.txt           -- Who the agent is and how it behaves
  bash.txt                    -- Tool description for bash (behavioral rules)
  todowrite.txt               -- Tool description for todowrite (usage patterns)
```

### The Agent Loop (the heart of it all)

```python
while True:
    response = llm.invoke(messages)       # 1. Ask the LLM
    messages.append(response)

    if not response.tool_calls:           # 2. No tools? Done.
        return response.content

    for tc in response.tool_calls:        # 3. Execute each tool
        result = tools[tc["name"]].invoke(tc["args"])
        messages.append(ToolMessage(...)) # 4. Feed result back
                                          # 5. Loop back to step 1
```

This is the same pattern used by Claude Code, ChatGPT, Cursor, and every other AI coding agent. The only differences are:
- **Which tools** are available (context engineering)
- **How good the tool descriptions are** (context engineering)
- **How good the system prompt is** (context engineering)
- **Which model** powers it

## Quick Start

```bash
# 1. Setup
cd ~/dev/mini-claw-code
uv sync
cp .env.example .env
# Edit .env with your XAI_API_KEY

# 2. Run
uv run python main.py
```

## Key Takeaway

> The **idea** behind Claude Code = LLM + Tool Loop + Context Engineering
>
> But an idea is cheap. Execution is everything. The real Claude Code is thousands of engineering hours turning this simple idea into a product that millions of developers rely on daily. This project helps you understand the idea. Go use the real thing to appreciate the execution.
