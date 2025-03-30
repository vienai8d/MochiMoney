# Use a lightweight Python 3.12 image based on Debian Bookworm
FROM python:3.12-slim-bookworm

# Copy the uv package manager binary from the official container image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Add the current project directory to the image under /app
ADD . /app

# Set the working directory to /app
WORKDIR /app

# Install dependencies based on the lockfile (uv.lock)
RUN uv sync --frozen

# Add the virtual environment's bin directory to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Run the Streamlit app when the container starts
CMD ["streamlit", "run", "app/main.py"]