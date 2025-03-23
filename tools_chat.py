from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool

# Define a web search tool for gardening-related questions
search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="plant_search",
    func=search.run,
    description="Search the web for plant care tips, watering schedules, pest control, and soil requirements."
)

# Define a Wikipedia tool focused on plants
api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=100)  # Increase plant-related content
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)
