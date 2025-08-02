from mcp.server.fastmcp import FastMCP

vpc_mcp_server = FastMCP("vpc_mcp_server")

@vpc_mcp_server.tool("get_products")
async def get_products():
    """Returns the list of products offered by VSL PVC company."""
    return [
        "PVC Pipes2025",
        "PVC Fittings",
        "PVC Sheets",
        "PVC Windows",
        "PVC Doors"
    ]

@vpc_mcp_server.tool("get_company_info")
async def get_company_info():
    """Returns information about VSL PVC company."""
    return {
        "name": "VSL PVC",
        "founded": "1995",
        "location": "Portugal",
        "employees": 500,
        "website": "https://vsl-pvc.com"
    }

if __name__ == "__main__":
    vpc_mcp_server.run(transport='stdio')