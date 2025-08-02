# Books MCP Server

A proper Model Context Protocol (MCP) server that provides a `getBooks` tool returning a static list of books. This server implements the MCP specification using JSON-RPC 2.0 over HTTP with the StreamableHTTPServerTransport in **stateless mode** for maximum compatibility.

## Features

- **getBooks tool**: Returns a static list of 5 books with details (id, title, author, year, genre)
- No parameters required for the tool
- **Proper MCP implementation**: Uses JSON-RPC 2.0 over HTTP (StreamableHTTPServerTransport)
- **Stateless operation**: Multiple clients can connect without session management
- **JSON responses**: Direct JSON responses (no SSE streaming for simplicity)
- **Multiple concurrent connections**: Unlimited clients can connect simultaneously

## Session Management

### The Problem
Initially, you might wonder: "Why can I connect to the server only once? Can we have only one session?"

### The Solution
The `StreamableHTTPServerTransport` can operate in two modes:

1. **Stateful mode** (with session management):
   - Each client gets a unique session ID
   - Session state is maintained server-side
   - More complex but supports advanced features like resumability

2. **Stateless mode** (current implementation):
   - No session IDs required
   - Each request is independent
   - Multiple clients can connect without limit
   - Simpler and more scalable

This server uses **stateless mode** by setting `sessionIdGenerator: undefined`, which allows unlimited concurrent connections without session management overhead.

## Installation

1. Install dependencies:
```bash
npm install
```

## Usage

1. Start the server:
```bash
npm start
# or
node books_server.js
```

2. Or specify a custom port:
```bash
PORT=3011 node books_server.js
```

The server runs on HTTP and communicates using JSON-RPC 2.0 messages at the `/mcp` endpoint.

## MCP Protocol

This server implements the Model Context Protocol specification:

- **Transport**: HTTP with StreamableHTTPServerTransport 
- **Protocol**: JSON-RPC 2.0
- **Capabilities**: tools
- **Session Management**: Stateless (no session IDs)
- **Response Format**: JSON (not SSE streaming)

### Available Tools

#### getBooks
- **Name**: `getBooks`
- **Description**: Returns a static list of books
- **Parameters**: None (empty object)
- **Returns**: List of 5 books with id, title, author, year, and genre

## Testing Multiple Connections

### Client 1:
```bash
# Initialize
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "client1", "version": "1.0.0"}}}'

# Get books
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "getBooks", "arguments": {}}}'
```

### Client 2 (simultaneously):
```bash
# Initialize
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "client2", "version": "1.0.0"}}}'

# Get books
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "getBooks", "arguments": {}}}'
```

Both clients work independently without interfering with each other!

## Protocol Responses

All responses are JSON objects:

### initialize Response
```json
{
  "result": {
    "protocolVersion": "2025-03-26",
    "capabilities": {"tools": {}},
    "serverInfo": {"name": "books-server", "version": "1.0.0"}
  },
  "jsonrpc": "2.0",
  "id": 1
}
```

### tools/list Response
```json
{
  "result": {
    "tools": [
      {
        "name": "getBooks",
        "description": "Returns a list of books",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
      }
    ]
  },
  "jsonrpc": "2.0",
  "id": 2
}
```

### tools/call Response
```json
{
  "result": {
    "content": [
      {
        "type": "text",
        "text": "[{\"id\":1,\"title\":\"To Kill a Mockingbird\",\"author\":\"Harper Lee\",\"year\":1960,\"genre\":\"Fiction\"}...]"
      }
    ]
  },
  "jsonrpc": "2.0",
  "id": 3
}
```
