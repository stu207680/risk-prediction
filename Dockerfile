FROM python:3.10.14

WORKDIR /app
COPY code/ /app/code/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/code/.settings/requirements.txt

CMD ["python", "/app/code/src/frame/runner.py"]
