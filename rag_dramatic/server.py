from fastapi import FastAPI, Query
from rag_dramatic.worker import process_query
from rag_dramatic.broker import broker
from dramatiq.results.errors import ResultMissing

app = FastAPI()


@app.post("/chat")
async def chat(user_query: str = Query(...)):

    message = process_query.send(user_query)

    return {
        "status": "queued",
        "message_id": message.message_id
    }


@app.get("/job-status")
async def get_result(message_id: str = Query(...)):

    message = process_query.message_with_options(
        args=(),
        kwargs={},
        message_id=message_id
    )

    try:
        result = message.get_result(block=False)

        return {
            "status": "completed",
            "result": result
        }

    except ResultMissing:

        return {
            "status": "processing"
        }