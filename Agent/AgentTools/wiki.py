import wikipediaapi
import json
from .base_tool import BaseTool

class Wiki(BaseTool):
    def __init__(self, language="en", user_agent="ReAct Agent from Wencho"):
        super().__init__(
            name="wikipedia",
            description="Gets information from a Wikipedia entry. Specific Wikipedia input. e.g. 'Cristiano Ronaldo'."
        )
        self.wiki_api = wikipediaapi.Wikipedia(user_agent=user_agent, language=language)

    def use(self, query):
        """Fetches summary information from Wikipedia for a given topic."""
        if not query:
            raise ValueError("Query cannot be empty.")

        try:
            page = self.wiki_api.page(query)
            
            if page.exists():
                return json.dumps({
                    "query": query,
                    "title": page.title,
                    "summary": page.summary
                }, ensure_ascii=False, indent=2)
            return f"No Wikipedia page found for '{query}'."

        except Exception:
            return "An error occurred while searching Wikipedia."


### For testing running directly the script
if __name__ == '__main__':
    wiki = Wiki()
    queries = ["Julian Alvarez"]

    for query in queries:
        result = wiki.use(query)
        if result:
            print(f"JSON result for '{query}':\n{result}\n")
        else:
            print(f"No result found for '{query}'\n")
