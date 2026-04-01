# Mini Claw Code

**Educational toy to illustrate context engineering -- the core idea behind Claude Code.**

> **Disclaimer**: This is a stick figure, not human anatomy. The real Claude Code is a massive engineering effort (sandboxing, permissions, streaming, LSP, IDE integrations, etc.) by a world-class team. Respect the execution.

## What Is Context Engineering?

One sentence:

> **Push the right thing, at the right time.**

Or even shorter: **what** and **when**.

You decide WHAT information the model needs, and WHEN to inject it into the context window.

```
Context Window = System Prompt + Tool Descriptions + Conversation History + Tool Results
```

Every token influences the model's next decision. This project demonstrates 3 levers, using just 2 tools (`bash` + `todowrite`) and 3 prompt files.

## Lever 1: System Prompt

Static context. Injected once. Defines WHO the agent is -- identity, constraints, judgment rules.

## Lever 2: Tool Descriptions

**Not API docs. Behavioral instructions disguised as documentation.**

`todowrite.txt` teaches the model WHEN to use it, WHEN NOT to, and HOW. Claude Code's real tool descriptions are 100+ lines each -- encoding expertise and guardrails directly into the context.

## Lever 3: Tool Results (the real magic)

The agent engineers its own context in real-time. Each tool call = a "what and when" decision.

### Example: Why TodoWrite Gets Called Repeatedly

LLMs have a well-known problem: **lost in the middle**. Like humans -- after 30 minutes of conversation, you remember the start and the last few things, but the middle is fuzzy.

If the agent plans 10 steps, by step 7 it has forgotten steps 8-10.

Solution: **keep pushing the task list back into context.**

```
[TodoWrite] Plan: 5 tasks             <- Tasks enter context
[bash: work on task 1...]
[TodoWrite] Mark task 1 done           <- Full task list refreshed
[bash: work on task 2...]
[TodoWrite] Mark task 2 done           <- Refreshed again, near the END
...                                       where the model pays most attention
```

Even the return message is context engineering:
```
"Todos have been modified successfully. Ensure that you continue 
to use the todo list to track your progress."
```
Not a confirmation -- a **behavioral nudge** injected at the perfect moment.

**What**: the task list. **When**: repeatedly, throughout the work.

### Beyond This Toy: How Claude Code Reads Codebases

Claude Code uses no indexing. No embeddings. No vector DB. **Intentional.**

It uses primitives -- `Read`, `Grep`, `Glob` -- to search adaptively based on the current task. The agent decides what to pull into context, when it needs it.

This is why it outperforms index-based tools despite having no index. The right information at the right time beats a static dump of "everything that might be relevant."

Same model, different engineering, wildly different results. Don't underestimate that.

## How It Works

```
main.py              -- Agentic loop (~68 lines)
prompts/
  system_prompt.txt  -- WHO the agent is
  bash.txt           -- HOW bash behaves  
  todowrite.txt      -- HOW todowrite behaves
```

```python
while True:
    response = llm.invoke(messages)       # Ask the LLM
    if not response.tool_calls:           # No tools? Done.
        return response.content
    for tc in response.tool_calls:        # Execute tools
        result = tools[tc["name"]].invoke(tc["args"])
        messages.append(ToolMessage(...)) # Feed result back, loop
```

## Quick Start

```bash
cd ~/dev/mini-claw-code && uv sync
cp .env.example .env  # add XAI_API_KEY
uv run python main.py
```

## Key Takeaway

> Context engineering = the right thing, at the right time. That's it.
