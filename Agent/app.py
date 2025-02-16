from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import Agent
from AgentTools.wiki import Wiki
from AgentTools.web_searcher import Searcher
from AgentTools.weather import Weather

app = FastAPI()
agent = Agent()

def register_default_tools():
    """Registers the default tools to the agent."""
    for tool in [Wiki(), Searcher(), Weather()]:
        agent.register_tool(tool)


register_default_tools()


class QueryRequest(BaseModel):
    query: str


@app.post("/chat")
async def chat(request: QueryRequest):
    try:
        result_messages = agent.execute(request.query)

        return {"response": result_messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


