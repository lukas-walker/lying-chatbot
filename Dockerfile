FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gradio_modal

COPY . .

# Expose Gradio default port
EXPOSE 7860

# Run your app
CMD ["python", "gradio_app.py"]