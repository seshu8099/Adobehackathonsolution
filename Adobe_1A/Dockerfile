# Dockerfile

FROM python:3.9-slim

# 1. Create and switch to /app
WORKDIR /app

# 2. Copy and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy your extractor script (process_pdf.py) and any modules it uses
COPY process_pdf.py /app/
# If you have any helper files or modules, copy them here too:
# COPY advanced_outline_extractor.py /app/
# COPY utils/ /app/utils/

# 4. Make sure input/output dirs exist
RUN mkdir -p /app/input /app/output

# 5. Default command: run your script
ENTRYPOINT ["python", "process_pdf.py"]

# Usage:
#   cd D:\adobe_hackathon
#   docker build -t outline-extractor .
#   docker run --rm -v "${PWD}/input:/app/input" -v "${PWD}/output:/app/output" outline-extractor
