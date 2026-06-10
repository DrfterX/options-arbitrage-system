#!/bin/bash
cd /Users/ayong/options_arbitrage_system
export PYTHONPATH="/Users/ayong/options_arbitrage_system"
exec .venv/bin/python web/app.py 127.0.0.1 5100
