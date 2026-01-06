import os
from google import genai


def ask(prompt: str, model: str = "gemini-3-flash-preview") -> str:
    """Send a prompt to Gemini and return the response text.

    Args:
        model: The Gemini model name to use (e.g., "gemini-3-flash-preview")
        prompt: The prompt to send to the model

    Returns:
        The response text from the model

    Raises:
        ValueError: If GEMINI_API_KEY environment variable is not set
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text


SUMMARIZE_PROMPT = """
Your job is to summarize the given YouTube video transcript. 

- Make your summary concise and information-dense.
- Organize it into a list of bullet points.
- Do not include any additional text or formatting.
- Only use the information provided in the transcript.

Transcript:
{transcript}
"""
