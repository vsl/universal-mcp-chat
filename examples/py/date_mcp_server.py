from mcp.server.fastmcp import FastMCP

mcp = FastMCP("date_mcp_server")

@mcp.tool()
async def get_date():
    """Returns the current date and time."""
    from datetime import datetime
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

@mcp.tool()
async def get_time_for_user(name: str):
    """Get time for user.

    Args:
        name: The name of the account holder
    """
    if not name or name != "Alex":
        return "Need to provide user name. Ask user to provide his name."
    from datetime import datetime
    now = datetime.now()
    return f"Hello {name}, the current time is {now.strftime('%H:%M:%S')}."

if __name__ == "__main__":
    mcp.run(transport='stdio')