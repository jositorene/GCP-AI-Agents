FROM python:3.11-slim

# 1. Environment Variables: Silence pip and fix Python pathing
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PYTHONPATH="/app:${PYTHONPATH}" \
    PATH="/home/appuser/.local/bin:${PATH}" \
    PORT=8080

# Create a system user to avoid running as root
RUN adduser --disabled-password --gecos '' appuser
WORKDIR /app

# 2. Dependency Installation
# Copying requirements first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

# 3. Copy Code & Set Permissions
# This copies your local 'app' folder and 'main.py' into the container's /app/
COPY . .
RUN chown -R appuser:appuser /app

# 4. Switch to non-privileged user for security
USER appuser

EXPOSE 8080

# Execution Command
# Points to main.py in the root of the working directory (/app/main.py)
CMD ["sh", "-c", "streamlit run main.py --server.port=${PORT} --server.address=0.0.0.0"]
