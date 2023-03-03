#!/bin/bash
uvicorn fastapi-url-shortener.main:app --host 0.0.0.0 --reload