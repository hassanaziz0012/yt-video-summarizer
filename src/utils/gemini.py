import os
import requests
# from google import genai


# def ask(prompt: str, model: str = "gemini-3-flash-preview") -> str:
#     """Send a prompt to Gemini and return the response text.
# 
#     Args:
#         model: The Gemini model name to use (e.g., "gemini-3-flash-preview")
#         prompt: The prompt to send to the model
# 
#     Returns:
#         The response text from the model
# 
#     Raises:
#         ValueError: If GEMINI_API_KEY environment variable is not set
#     """
#     api_key = os.environ.get("GEMINI_API_KEY")
#     if not api_key:
#         raise ValueError("GEMINI_API_KEY environment variable is not set")
# 
#     client = genai.Client(api_key=api_key)
#     response = client.models.generate_content(model=model, contents=prompt)
#     return response.text

GEMINI_ARMY_BASE_URL = "https://gemini-army.vercel.app"


def ask(prompt: str, model: str = "gemini-3-flash-preview", system_prompt: str = None) -> str:
    """Send a prompt to the Gemini Army API and return the response text.

    Args:
        prompt: The prompt to send to the model
        model: The Gemini model name to use (default: "gemini-3-flash-preview")
        system_prompt: Optional system prompt to guide the model's behavior

    Returns:
        The response text from the model

    Raises:
        ValueError: If ARMY_ACCESS_KEY is not set or API call fails
    """
    api_key = os.environ.get("ARMY_ACCESS_KEY")
    if not api_key:
        raise ValueError("ARMY_ACCESS_KEY environment variable is not set")

    url = f"{GEMINI_ARMY_BASE_URL}/generate"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "model": model
    }
    
    if system_prompt:
        payload["system_prompt"] = system_prompt

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result.get("text", "")
    except requests.exceptions.RequestException as e:
        # Try to get more details from the response if possible
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
                error_msg = f"{e} - Details: {error_details}"
            except:
                error_msg = f"{e} - Content: {e.response.text}"
        
        raise ValueError(f"Error calling Gemini Army API: {error_msg}")


SUMMARIZE_PROMPT = """
Your job is to summarize the given YouTube video transcript. 

- Make your summary concise and information-dense.
- Organize it into a list of bullet points.
- Do not include any additional text or formatting.
- Only use the information provided in the transcript.

Transcript:
{transcript}
"""
