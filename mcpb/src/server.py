"""Claude Desktop extension entry point; the server itself ships in stockdex."""

import sys

from stockdex.claude_mcp import main

if __name__ == "__main__":
    sys.exit(main())
