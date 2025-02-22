from groq import Groq

def draft_message(content, role='user'):
    return {
        "role":role,
        "content":content
    }

api_key = "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"

client = Groq(api_key=api_key)

messages = [
    {
        "role":"system",
        "content": "you are a medical professional give some basic consultations to the symptoms. suggest some treatments. give 5 possible causes, and 5 treatments and some over the counter medicine information. also make sure to include a statement about consulting a doctor."
    }
]

prompt = "i have headache"

messages.append(draft_message(prompt))


completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=messages,
    temperature=1,
    max_completion_tokens=1024,
    top_p=1,
    stream=True,
    stop=None,
)

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")
