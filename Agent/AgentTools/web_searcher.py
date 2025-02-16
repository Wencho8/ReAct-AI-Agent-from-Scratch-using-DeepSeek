import os
from dotenv import load_dotenv
from tavily import TavilyClient
from .base_tool import BaseTool

class Searcher(BaseTool):
    def __init__(self):
        load_dotenv()
        super().__init__(
            name="websearch",
            description="Search the web for information. Input is a query. e.g. 'Champion of the 2024 Champions League'."
        )
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    def use(self, query):
        """Performs a web search for a given query."""
        if not query:
            raise ValueError("Query cannot be empty.")
        search_results = self.tavily_client.search(query=query, max_results=2)

        if search_results and "results" in search_results:
            formatted_results = []
            for result in search_results["results"]:
                formatted_result = {
                    "title": result.get("title"),
                    "content": result.get("content"),
                    "url": result.get("url"),
                    "score": result.get("score"),
                }
                formatted_results.append(formatted_result)
            return formatted_results if formatted_results else "No results found."
        return "No search results available."


### For testing running directly the script
if __name__ == '__main__':
    queries = ["F1 winner 2024"]

    def run_search():
        searcher = Searcher()
        for query in queries:
            result = searcher.use(query)
            if result:
                print(f"Context for '{query}':\n{result}\n")
            else:
                print(f"No context found for '{query}'\n")

    run_search()