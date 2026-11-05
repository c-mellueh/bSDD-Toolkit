from __future__ import annotations

import argparse
import os


def main() -> None:
    import uvicorn

    parser = argparse.ArgumentParser(description="bSDD Toolkit web server")
    parser.add_argument("--host", default=os.environ.get("HOST", "0.0.0.0"))  # noqa: S104
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")))
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()
    # A single worker is required: open projects live in process memory.
    uvicorn.run("bsdd_web.app:app", host=args.host, port=args.port, reload=args.reload, workers=1)


if __name__ == "__main__":
    main()
