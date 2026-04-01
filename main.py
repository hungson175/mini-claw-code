import os
import json
import subprocess
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

load_dotenv(override=True)

@tool
def bash(command: str) -> str:
	"""Execute a bash command and return the output."""
	result = subprocess.run(command, shell=True, capture_output=True, text=True)
	output = result.stdout
	if result.stderr:
		output += "\nSTDERR:\n" + result.stderr
	return output or "(no output)"

@tool
def todowrite(todos: list[dict]) -> str:
	"""Create and manage a structured task list. Each todo has: content (str), status ('pending'|'in_progress'|'completed'), activeForm (str)."""
	return "Todos have been modified successfully. Ensure that you continue to use the todo list to track your progress. Please proceed with the current tasks if applicable"

with open("prompts/bash.txt", "r") as f:
	bash.description = f.read()
with open("prompts/todowrite.txt", "r") as f:
	todowrite.description = f.read()

tools = [bash, todowrite]
llm = ChatOpenAI(model="grok-4-fast-non-reasoning", base_url="https://api.x.ai/v1", api_key=os.getenv("XAI_API_KEY")).bind_tools(tools)
tools_by_name = {t.name: t for t in tools}

print("Available tools:")
for t in tools:
	print(f"  - {t.name}: {t.description[:80]}...")

with open("prompts/system_prompt.txt", "r") as f:
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


print("\n--- Mini Claw Code ---")
print("An educational minimal clone of Claude Code")
print("Tools: bash, todowrite")
print("Type 'quit' to exit\n")

while True:
	user_input = input("You: ")
	if user_input.strip().lower() == "quit":
		break
	print(chat(user_input))
	print("=" * 40)
