from openai import OpenAI
import base64

client = OpenAI(
    base_url = "http://localhost:11434/v1",
    api_key = "ollama"
)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


image_path = r"C:\Users\sunyn\Downloads\image.jpg"


base64_image = encode_image(image_path)



client.chat.completions.create(
    model="moondream",
    messages=[
        {
            "role":"user",
            "content": [
                {"type":"text","text":"Generate a caption for this image in a 50 words"},
                {"type":"image_url","image_url": f"data:image/jpeg;base64,{base64_image}"}
            ]
        }
    ]
)