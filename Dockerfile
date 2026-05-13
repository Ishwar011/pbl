FROM python:3.10-slim

# Create a non-root user specifically for Hugging Face Spaces
RUN useradd -m -u 1000 user
USER user

# Set home and path environments
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set the working directory
WORKDIR $HOME/app

# Copy the application code and set ownership to the new user
COPY --chown=user . $HOME/app

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Hugging Face Spaces exposes port 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
