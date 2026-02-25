from dotenv import load_dotenv
from openai import OpenAI,RateLimitError
import json
import requests
import time
from pydantic import BaseModel,Field
from typing import Optional
import os 

load_dotenv()

client = OpenAI(
    base_url = "http://localhost:11434/v1",
    api_key = "ollama"
)

def run_command(cmd:str):
    result = os.system(cmd)
    return result

def get_weather(city:str):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        print(f"Weather in city {city} is {response.text}")
    
    return "Something went wrong"

available_tools = {
    "get_weather" : get_weather,
    "run_command" : run_command
}

SYSTEM_PROMPT = """
   You are an expert AI assitant in resolving user queries using chain of thoughts.
   You work on START, PLAN and OUTPUT steps.
   You need to first PLAN whats need to be done. The PLAN can be multiple steps.
   Once you think enough PLAN has been done, finally you can give an output.
   You can also call a tool if required from the list of available tools
   for every call wait for the observe step which is the output from the called tool.

   RULES:
   - Strickly follow the given JSON output format.
   - Only follow one step at a time.
   - Sequence of steps is START (where user gives an input), PLAN (That 
   can be multiple times) and finally OUTPUT (which is going to display 
   to user).

   OUTPUT JSON FORMAT:
   { "step": "START" | "PLAN" | "OUTPUT" | "TOOL", "content": "string", "tool": "string", "input":"string"}

   AVAILABLE TOOLS:
   - get_weather(city:str): Takes city name as an input string and returns the weather info about the city.
   - run_command(cmd:str): Takes a linux command as a string and executes the command on the user's system and returns the output from that command

   Example 1:
   START: Hey, can you solve 2+3*5/10
   PLAN: {"step":"PLAN", "content":"Seems like user is interested in
   maths problem"}
   PLAN: {"step":"PLAN","content":"Looking at the problem, we should
   solve the problem using BODMAS method"}
   PLAN: {"step":"PLAN","content":"Yes, BODMAS is correct thing to be done here"}
   PLAN: {"step":"PLAN","content":"first we multiply 3 * 5 which is 15 "}
   PLAN: {"step":"PLAN","content":"Now we  must perform divide that is 15 /10 = 1.5"}
   PLAN: {"step":"PLAN","content":"Now new equation is 2 + 1.5 "}
   PLAN: {"step":"PLAN","content":"Now finally we perform add 3.5"}
   PLAN: {"step":"PLAN","content":"Great, We solved finally we left with 3.5 as answer "}
   OUTPUT: {"step":"OUTPUT","content":"3.5"}

   Example 2:
   START: What is the weather of Delhi?
   PLAN: {"step":"PLAN", "content":"Seems like user is interested in
   getting weather of Delhi in India "}
   PLAN: {"step":"PLAN","content":"Lets seens if we have any available tool for weather from the available tools"}
   PLAN: {"step":"PLAN","content":"Great, we have a get_weather tool available for this query."}
   PLAN: {"step":"PLAN","content":"I need to call get_weather tool for delhi as input for city "}
   PLAN: {"step":"TOOL", "tool": "get_weather",input":"Delhi"}
   PLAN: {"step":"OBSERVE","tool": "get_weather","output":"The temp of delhi is cloudy with 20 degree celcius"}
   PLAN: {"step":"PLAN","content":"Now finally we perform add 3.5"}
   PLAN: {"step":"PLAN","content":"Great, I got the info of Delhi weather "}
   OUTPUT: {"step":"OUTPUT","content":"The current weather in delhi is 20 degree celcius with some cloudy sky."}

"""

class MyOutputFormat(BaseModel):
    step: str = Field(..., description="The ID of the step. Example: PLAN, OUTPUT, TOOL, etc")
    content: Optional[str] = Field(None, description="The optional string content for the step")
    tool: Optional[str] = Field(None, description="The ID of the tool to call")
    input: Optional[str] = Field(None, description="The input params for the tool")


message_history = [
    {"role":"system", "content":SYSTEM_PROMPT}
]

user_query = input("Enter :")
message_history.append({"role": "user", "content": user_query})

while True:
    # response = client.chat.completions.create(
    #     model="gemma2:2b",
    #     response_format={"type":"json_object"},
    #     messages=message_history
    # )

    response = client.chat.completions.parse(
        model="gemma2:2b",
        response_format=MyOutputFormat,
        messages=message_history
    )

    try:
        raw_result = response.choices[0].message.content
    except RateLimitError as e:
        print("Rate limit hit. Sleeping for 60 seconds...")
        time.sleep(60)
    message_history.append({"role":"assistant", "content":raw_result})

    # parsed_result = json.loads(raw_result)
    parsed_result = response.choices[0].message.parsed

    # if parsed_result.get("step") == "START":
    #     print(parsed_result.get("content"))
    #     continue

    if parsed_result.step == "START":
        print(parsed_result.content)
        continue

    if parsed_result.step == "TOOL":
        tool_to_call = parsed_result.tool
        tool_input = parsed_result.input
        print(f"{tool_to_call} ({tool_input})")

        tool_response = available_tools[tool_to_call] (tool_input)
        print(f"{tool_to_call} ({tool_input}) = {tool_response}")
        message_history.append({"role":"developer", "content":json.dumps(
            {"steps" : "OBSERVE", "tool": tool_to_call, "input": tool_input, "output": tool_response}
        )})
        
        continue

    if parsed_result.step == "PLAN":
        print(parsed_result.content)
        continue

    if parsed_result.step == "OUTPUT":
        print(parsed_result.content)
        break
