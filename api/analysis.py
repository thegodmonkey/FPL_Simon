import google.generativeai as genai

def get_llm_insight(prompt: str, context: str):
    """Generates insights from a Large Language Model (LLM) based on a given prompt and context.

    Args:
        prompt: The prompt to send to the LLM.
        context: The context to provide to the LLM.

    Returns:
        A string containing the LLM's generated insight.
    """
    # Note: It's assumed that genai.configure(api_key="YOUR_API_KEY") is called
    # at the application's startup.
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(f"{prompt}\n\nContext:\n{context}")
    return response.text
