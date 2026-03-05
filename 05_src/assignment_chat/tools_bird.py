from langchain.tools import tool
import json
import requests


@tool
def get_bird_facts(n:int=1):
    """
    Returns n bird facts from the Birds API.
    """
    url = "https://jsongpt.com/api/birds"
    params = {"count": n}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return "Sorry, I couldn't fetch bird facts right now."
    
    resp_dict = json.loads(response.text)
    facts_list = resp_dict.get("data", [])
    first_items = facts_list[:n]

    facts = "\n".join([f"{i+1}. {fact}\n" for i, fact in enumerate(first_items)])
    return facts