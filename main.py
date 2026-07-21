import os
import sys
import json
import subprocess
import time
import termios
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

_ROOT = Path(__file__).resolve().parent
load_dotenv(_ROOT / ".env", override=True)

@tool
def bash(command: str, background: bool = False) -> str:
	"""Execute a bash command and return the output.

	Args:
		command: the shell command to run
		background: if true, start detached and return immediately with PID + log path
	"""
	if background:
		log_path = f"/tmp/agent-bash-{int(time.time() * 1000)}.log"
		log_f = open(log_path, "w")
		proc = subprocess.Popen(
			command,
			shell=True,
			stdin=subprocess.DEVNULL,
			stdout=log_f,
			stderr=subprocess.STDOUT,
			start_new_session=True,
		)
		log_f.close()
		time.sleep(0.4)
		if proc.poll() is not None:
			tail = Path(log_path).read_text(errors="replace")[-2000:]
			return f"Background process exited immediately code={proc.returncode}\nlog={log_path}\n{tail}"
		return f"Started in background\nPID={proc.pid}\nlog={log_path}\ncommand={command}"

	result = subprocess.run(command, shell=True, capture_output=True, text=True, stdin=subprocess.DEVNULL)
	output = result.stdout
	if result.stderr:
		output += "\nSTDERR:\n" + result.stderr
	if result.returncode != 0:
		output += f"\n(exit code {result.returncode})"
	return output or "(no output)"

@tool
def todowrite(todos: list[dict]) -> str:
	"""Create and manage a structured task list. Each todo has: content (str), status ('pending'|'in_progress'|'completed'), activeForm (str)."""
	return "Todos have been modified successfully. Ensure that you continue to use the todo list to track your progress. Please proceed with the current tasks if applicable"

with open(_ROOT / "prompts/bash.txt") as f:
	bash.description = f.read()
with open(_ROOT / "prompts/todowrite.txt") as f:
	todowrite.description = f.read()

tools = [bash, todowrite]
tools_by_name = {t.name: t for t in tools}

llm = ChatOpenAI(
	model="deepseek-v4-flash",
	base_url="https://api.deepseek.com",
	api_key=os.getenv("DEEPSEEK_API_KEY"),
	extra_body={"thinking": {"type": "disabled"}},
).bind_tools(tools)

with open(_ROOT / "prompts/system_prompt.txt") as f:
	system_prompt = f.read()
messages = [SystemMessage(content=system_prompt)]

def chat(user_input: str):
	messages.append(HumanMessage(content=user_input))
	while True:
		response = llm.invoke(messages)
		messages.append(response)

		if not response.tool_calls:
			return response.content

		for tc in response.tool_calls:
			print(f"  [Tool: {tc['name']}] {json.dumps(tc['args'], ensure_ascii=False)[:120]}")
			result = tools_by_name[tc["name"]].invoke(tc["args"])
			print(f"  [Result] {str(result)[:200]}")
			messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

def clear_stdin():
	# Drop keystrokes/paste buffered while the agent was busy.
	if sys.stdin.isatty():
		try:
			termios.tcflush(sys.stdin, termios.TCIFLUSH)
		except termios.error:
			pass

if __name__ == "__main__":
	print("Available tools:")
	for t in tools:
		print(f"  - {t.name}: {t.description[:80]}...")
	print("\n--- Mini Claw Code ---")
	print("An educational minimal clone of Claude Code")
	print("Tools: bash, todowrite")
	print("Type 'quit' to exit\n")

	while True:
		clear_stdin()
		user_input = input("You: ")
		if user_input.strip().lower() == "quit":
			break
		if not user_input.strip():
			continue
		print(chat(user_input))
		print("=" * 40)
