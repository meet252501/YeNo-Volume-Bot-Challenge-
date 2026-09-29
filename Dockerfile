FROM python:3.11-slim

WORKDIR /app

# Zero external dependencies — bot.py uses only Python stdlib
COPY bot.py .

EXPOSE 8080

# Start the bot on port 8080
# No outbound network needed — matches evaluator constraint
CMD ["python", "bot.py", "8080"]
