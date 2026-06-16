import json
import os
import re
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def generate_quiz(transcript: str) -> dict:
    """Generate a 10-question quiz from a transcript using the Gemini API.

    Returns a dict with title, description, and a list of questions."""
    prompt = f"""
Based on the following transcript, generate a quiz in valid JSON format.

The quiz must follow this exact structure:

{{

  "title": "Create a concise quiz title based on the topic of the transcript.",

  "description": "Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.",

  "questions": [

    {{

      "question_title": "The question goes here.",

      "question_options": ["Option A", "Option B", "Option C", "Option D"],

      "answer": "The correct answer from the above options"

    }},

    ...

    (exactly 10 questions)

  ]

}}

Requirements:

- Each question must have exactly 4 distinct answer options.

- Only one correct answer is allowed per question, and it must be present in 'question_options'.

- The output must be valid JSON and parsable as-is (e.g., using Python's json.loads).

- Do not include explanations, comments, or any text outside the JSON.


Transkript:
{transcript}
"""

    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)

    text = response.text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No valid JSON found in Gemini response.")

    return json.loads(match.group())
