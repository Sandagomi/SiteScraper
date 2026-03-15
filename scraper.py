import os
import requests
from dotenv import load_dotenv
from IPython.display import Markdown, display
from openai import OpenAI
from bs4 import BeautifulSoup


# Load environment variables in a file called .env

load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

# Check the key

if not api_key:
    print("No API key was found - please head over to the troubleshooting notebook in this folder to identify & fix!")
elif not api_key.startswith("sk-proj-"):
    print("An API key was found, but it doesn't start sk-proj-; please check you're using the right key - see troubleshooting notebook")
elif api_key.strip() != api_key:
    print("An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them - see troubleshooting notebook")
else:
    print("API key found and looks good so far!")
    

system_prompt = """
You are a helpful assistant that analyzes the contents of a website,
and provides a short, snarky, humorous summary, ignoring text that might be navigation related.
Respond in markdown. Do not wrap the markdown in a code block - respond just with the markdown.
"""

user_prompt_prefix = """
Here are the contents of a website.
Provide a short summary of this website.
If it includes news or announcements, then summarize these to and present them in a bullet point list.

"""


def fetch_website_contents(url, max_chars=50000):
    """Fetch and extract the text contents of a website."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parse HTML and extract text
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Truncate to max length
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        return text
    except requests.exceptions.RequestException as e:
        return f"Error fetching website: {e}"


def summarize(url):
    """Fetch website contents and summarize using OpenAI API."""
    client = OpenAI(api_key=api_key)
    
    website_contents = fetch_website_contents(url)
    
    messages = messages_for(website_contents)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    
    return response.choices[0].message.content


def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_prefix + website}
    ]
def display_summary(url):
    summary = summarize(url)
    display(Markdown(summary))


if __name__ == "__main__":
    # Example usage
    summary = summarize("https://www.cinnamonhotels.com/cinnamon-life-city-of-dreams-sri-lanka/offers/a-winning-stay?gad_source=1&gad_campaignid=21788354070&gbraid=0AAAAADRZXZnTALVNLkGTz7UknLq9SixMY&gclid=CjwKCAjwjtTNBhB0EiwAuswYhslu2J0943aNvpJ4xbPnr2K4k8LWA-EiN2jhIo2-pSprot0R0Z9VKBoCSWEQAvD_BwE")
    print(summary)