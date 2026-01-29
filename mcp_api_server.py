"""
Payment MCP Server - FastAPI HTTP Wrapper

This FastAPI application exposes the MCP server functionality as HTTP REST endpoints,
allowing you to use the MCP tools via HTTP requests instead of stdio.
Also supports MCP protocol with SSE for Azure AI Foundry integration.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import asyncio

from mcp_server import PaymentMCPServer, get_payment_tools, execute_payment_function

# Initialize FastAPI app
app = FastAPI(
    title="Payment MCP API",
    description="HTTP API wrapper for Payment MCP Server - exposes MCP tools as REST endpoints",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP server
payment_mcp = PaymentMCPServer()


# Request/Response Models
class MCPInitializeResponse(BaseModel):
    """MCP Initialize response"""

    protocolVersion: str
    serverInfo: Dict[str, str]
    capabilities: Dict[str, Any]


class MCPTool(BaseModel):
    """MCP Tool definition"""

    name: str
    description: str
    inputSchema: Dict[str, Any]


class MCPToolsListResponse(BaseModel):
    """MCP tools list response"""

    tools: List[MCPTool]


class MCPToolCallRequest(BaseModel):
    """MCP tool call request"""

    name: str = Field(..., description="Tool name to execute")
    arguments: Dict[str, Any] = Field(..., description="Tool arguments")


class MCPToolCallResponse(BaseModel):
    """MCP tool call response"""

    content: List[Dict[str, str]]
    isError: Optional[bool] = False


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    timestamp: str
    mcp_server: str
    payment_api: str


@app.get("/")
def read_root():
    """Root endpoint with API information"""
    return {
        "service": "Payment MCP API",
        "version": "1.0.0",
        "description": "HTTP wrapper for Payment MCP Server",
        "mcp_protocol": "stdio (also available)",
        "endpoints": {
            "health": "/health",
            "mcp_initialize": "/mcp/initialize",
            "mcp_tools_list": "/mcp/tools/list",
            "mcp_tools_call": "/mcp/tools/call",
            "docs": "/docs",
        },
    }


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "mcp_server": "running",
        "payment_api": "connected",
    }


@app.post("/mcp/initialize", response_model=MCPInitializeResponse)
def mcp_initialize():
    """
    MCP Initialize endpoint

    Mimics the MCP protocol initialize method.
    Returns server capabilities and information.
    """
    return {
        "protocolVersion": "0.1.0",
        "serverInfo": {"name": "payment-mcp-server", "version": "1.0.0"},
        "capabilities": {"tools": {}},
    }


@app.get("/mcp/tools/list", response_model=MCPToolsListResponse)
def mcp_list_tools():
    """
    MCP List Tools endpoint

    Returns all available MCP tools with their schemas.
    """
    tools = get_payment_tools()

    # Convert to MCP tool format
    mcp_tools = []
    for tool in tools:
        func = tool["function"]
        mcp_tools.append(
            {
                "name": func["name"],
                "description": func["description"],
                "inputSchema": func["parameters"],
            }
        )

    return {"tools": mcp_tools}


@app.post("/mcp/tools/call", response_model=MCPToolCallResponse)
def mcp_call_tool(request: MCPToolCallRequest):
    """
    MCP Call Tool endpoint

    Executes an MCP tool with the provided arguments.

    Available tools:
    - tokenize_payment_card
    - process_payment
    - get_transaction
    - get_customer_transactions
    - refund_transaction
    - get_token_info
    """
    try:
        # Execute the tool
        result = execute_payment_function(request.name, json.dumps(request.arguments))

        return {"content": [{"type": "text", "text": result}], "isError": False}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Tool execution failed: {str(e)}")


# Convenience endpoints for direct tool access
@app.post("/tools/tokenize")
def tokenize_card_direct(
    card_number: str,
    card_holder: str,
    expiry_month: int,
    expiry_year: int,
    cvv: str,
    customer_email: str,
    billing_street: str,
    billing_city: str,
    billing_state: str,
    billing_zip: str,
    billing_country: str = "US",
    customer_id: Optional[str] = None,
):
    """Direct endpoint for card tokenization (convenience wrapper)"""
    args = {
        "card_number": card_number,
        "card_holder": card_holder,
        "expiry_month": expiry_month,
        "expiry_year": expiry_year,
        "cvv": cvv,
        "customer_email": customer_email,
        "billing_street": billing_street,
        "billing_city": billing_city,
        "billing_state": billing_state,
        "billing_zip": billing_zip,
        "billing_country": billing_country,
    }
    if customer_id:
        args["customer_id"] = customer_id

    result = execute_payment_function("tokenize_payment_card", json.dumps(args))
    return json.loads(result)


@app.post("/tools/process-payment")
def process_payment_direct(
    token: str,
    amount: float,
    customer_id: str,
    currency: str = "USD",
    description: Optional[str] = None,
):
    """Direct endpoint for payment processing (convenience wrapper)"""
    args = {
        "token": token,
        "amount": amount,
        "currency": currency,
        "customer_id": customer_id,
    }
    if description:
        args["description"] = description

    result = execute_payment_function("process_payment", json.dumps(args))
    return json.loads(result)


@app.get("/tools/transaction/{transaction_id}")
def get_transaction_direct(transaction_id: str):
    """Direct endpoint for getting transaction details (convenience wrapper)"""
    args = {"transaction_id": transaction_id}
    result = execute_payment_function("get_transaction", json.dumps(args))
    return json.loads(result)


@app.get("/tools/customer/{customer_id}/transactions")
def get_customer_transactions_direct(customer_id: str):
    """Direct endpoint for getting customer transactions (convenience wrapper)"""
    args = {"customer_id": customer_id}
    result = execute_payment_function("get_customer_transactions", json.dumps(args))
    return json.loads(result)


@app.post("/tools/transaction/{transaction_id}/refund")
def refund_transaction_direct(transaction_id: str):
    """Direct endpoint for refunding a transaction (convenience wrapper)"""
    args = {"transaction_id": transaction_id}
    result = execute_payment_function("refund_transaction", json.dumps(args))
    return json.loads(result)


@app.get("/tools/token/{token}")
def get_token_info_direct(token: str):
    """Direct endpoint for getting token information (convenience wrapper)"""
    args = {"token": token}
    result = execute_payment_function("get_token_info", json.dumps(args))
    return json.loads(result)


# MCP Protocol SSE Endpoint for Azure AI Foundry
@app.post("/mcp")
async def mcp_protocol_endpoint(request: Request):
    """
    MCP Protocol endpoint with SSE support for Azure AI Foundry.

    This endpoint implements the MCP protocol over HTTP with Server-Sent Events.
    It handles JSON-RPC 2.0 messages for initialize, tools/list, and tools/call.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")

    jsonrpc = body.get("jsonrpc", "2.0")
    request_id = body.get("id")
    method = body.get("method")
    params = body.get("params", {})

    async def event_generator():
        """Generate SSE events for MCP protocol"""
        try:
            if method == "initialize":
                response = {
                    "jsonrpc": jsonrpc,
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": "payment-mcp-server",
                            "version": "1.0.0",
                        },
                    },
                }
                yield f"data: {json.dumps(response)}\n\n"

            elif method == "tools/list":
                tools = get_payment_tools()
                mcp_tools = []
                for tool in tools:
                    func = tool["function"]
                    mcp_tools.append(
                        {
                            "name": func["name"],
                            "description": func["description"],
                            "inputSchema": func["parameters"],
                        }
                    )

                response = {
                    "jsonrpc": jsonrpc,
                    "id": request_id,
                    "result": {"tools": mcp_tools},
                }
                yield f"data: {json.dumps(response)}\n\n"

            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                # Execute the tool
                result = execute_payment_function(tool_name, json.dumps(arguments))

                response = {
                    "jsonrpc": jsonrpc,
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": result}],
                        "isError": False,
                    },
                }
                yield f"data: {json.dumps(response)}\n\n"

            else:
                error_response = {
                    "jsonrpc": jsonrpc,
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}",
                    },
                }
                yield f"data: {json.dumps(error_response)}\n\n"

        except Exception as e:
            error_response = {
                "jsonrpc": jsonrpc,
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}",
                },
            }
            yield f"data: {json.dumps(error_response)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "mcp_api_server:app", host="0.0.0.0", port=8001, reload=True, log_level="info"
    )
 