#!/bin/bash
# 同时启动 FastAPI 后端和 Streamlit 前端

trap "kill $api_pid $web_pid 2>/dev/null" EXIT

uvicorn evo_flywheel.api.main:app --reload &
api_pid=$!

streamlit run src/evo_flywheel/web/app.py &
web_pid=$!

wait $api_pid $web_pid
