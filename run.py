#!/usr/bin/env python3
"""Run the PodFilter application."""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("podfilter.app:app", host="0.0.0.0", port=8000, reload=True)