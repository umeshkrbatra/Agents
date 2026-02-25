from openai import OpenAI
from dotenv import load_dotenv
import requests 
import time

load_dotenv()

client = OpenAI(
    base_url = "http://localhost:11434/v1",
    api_key = "ollama"
)


def get_weather(city:str):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        print(f"Weather in city {city} is {response.text}")
    
    return "Something went wrong"



def main():
    
    user_query = input("Enter :")
    try: 
        response = client.chat.completions.create(
            model="gemma3:1b",
            messages=[
            {"role":"user", "content":user_query}
            ]
        )
   
        print(f'response : {response.choices[0].message.content}')
    except Exception as e:
        print("Rate limited, retrying...")
        time.sleep(35)

#main()
get_weather("goa")


