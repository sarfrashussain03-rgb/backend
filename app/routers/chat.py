"""
Chat router with SSE streaming endpoint for the AI assistant.
"""

import json
import asyncio
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, SystemMessage
from app.ai.agent import get_agent, SYSTEM_PROMPT
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/stream")
async def chat_stream(
    message: str = Query(..., description="User message"),
    user_id: str = Query("anonymous", description="User ID"),
    session_id: str = Query("default", description="Session ID for conversation continuity"),
):
    """
    SSE endpoint that streams AI responses and cart updates to the Flutter app.

    Event types:
    - `message`: A chunk of the AI's text response
    - `cart_update`: Cart was updated by the AI
    - `tool_call`: AI is calling a tool (for UI feedback)
    - `done`: Stream complete
    - `error`: An error occurred
    """

    async def event_generator():
        logger.info(f"Incoming chat stream request. User: {user_id}, Message: {message}")
        try:
            agent = get_agent()

            # Build the system message with user context
            system_msg = SystemMessage(content=SYSTEM_PROMPT.format(user_id=user_id))
            human_msg = HumanMessage(content=message)

            # Stream the agent's response
            full_response = ""
            cart_updated = False
            cart_data = None

            # Use astream for streaming
            async for event in agent.astream_events(
                {"messages": [system_msg, human_msg]},
                version="v2",
                config={"configurable": {"thread_id": session_id, "user_id": user_id}},
            ):
                kind = event.get("event", "")

                # LLM is generating text tokens
                if kind == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk")
                    if chunk and hasattr(chunk, "content") and chunk.content:
                        content = chunk.content
                        text_val = ""
                        if isinstance(content, str):
                            text_val = content
                        elif isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and item.get("type") == "text":
                                    text_val += item.get("text", "")
                                elif isinstance(item, str):
                                    text_val += item
                        if text_val:
                            full_response += text_val
                            yield f"data: {json.dumps({'type': 'message', 'content': text_val})}\n\n"

                # Tool is being invoked
                elif kind == "on_tool_start":
                    tool_name = event.get("name", "")
                    tool_input = event.get("data", {}).get("input", {})
                    logger.info(f"--- AGENT TOOL START: {tool_name} ---")
                    logger.info(f"Input: {tool_input}")
                    yield f"data: {json.dumps({'type': 'tool_call', 'tool': tool_name, 'input': str(tool_input)[:200]})}\n\n"

                # Tool finished  
                elif kind == "on_tool_end":
                    tool_name = event.get("name", "")
                    tool_output = event.get("data", {}).get("output", "")
                    logger.info(f"--- AGENT TOOL END: {tool_name} ---")
                    # logger.debug(f"Output: {tool_output}")

                    # Check if cart was updated
                    if tool_name == "add_to_cart":
                        try:
                            output_data = {}
                            if hasattr(tool_output, 'content'):
                                output_data = json.loads(tool_output.content)
                            elif isinstance(tool_output, str):
                                output_data = json.loads(tool_output)
                            elif isinstance(tool_output, dict):
                                output_data = tool_output
                            
                            logger.info(f"add_to_cart output parsed successfully: {output_data.get('cart_updated')}")
                            if output_data.get("cart_updated"):
                                cart_updated = True
                                cart_data = output_data
                                # Send as a named event AND a message-like data for robustness
                                yield f"event: cart_update\ndata: {json.dumps({'type': 'cart_update', 'cart': output_data})}\n\n"
                        except Exception as e:
                            logger.error(f"Error parsing add_to_cart output: {str(e)}")
                            pass

            # Send completion event
            logger.info("Chat stream completed successfully.")
            yield f"data: {json.dumps({'type': 'done', 'cart_updated': cart_updated})}\n\n"

        except Exception as e:
            logger.error(f"Chat stream error: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/message")
async def chat_message(
    message: str = Query(..., description="User message"),
    user_id: str = Query("anonymous", description="User ID"),
):
    """
    Non-streaming chat endpoint (fallback).
    Returns the complete AI response at once.
    """
    try:
        agent = get_agent()

        system_msg = SystemMessage(content=SYSTEM_PROMPT.format(user_id=user_id))
        human_msg = HumanMessage(content=message)

        result = await asyncio.to_thread(
            agent.invoke,
            {"messages": [system_msg, human_msg]},
        )

        # Extract the final AI message
        messages = result.get("messages", [])
        ai_response = ""
        cart_updated = False

        for msg in messages:
            if hasattr(msg, "content") and msg.type == "ai":
                ai_response = msg.content
            elif hasattr(msg, "content") and msg.type == "tool":
                try:
                    tool_data = json.loads(msg.content)
                    if tool_data.get("cart_updated"):
                        cart_updated = True
                except (json.JSONDecodeError, AttributeError):
                    pass

        return {
            "response": ai_response,
            "cart_updated": cart_updated,
        }

    except Exception as e:
        return {"response": f"Sorry, I encountered an error: {str(e)}", "cart_updated": False}
