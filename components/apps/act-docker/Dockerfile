FROM python:3.11-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy ACT application
COPY act/ /app/act/

# Copy flow file (will be mounted as volume in docker-compose)
# Create empty flow file as placeholder
RUN touch /app/flow

# Default port 9999 (can be overridden by flow file)
ENV ACT_PORT=9999

# Use production runner with hot reload, MiniACT, and empty flow support
CMD ["python", "-m", "act.production_runner"]
