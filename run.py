#!/usr/bin/env python3
"""Run the PodFilter application."""

import uvicorn

from podfilter.app import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)