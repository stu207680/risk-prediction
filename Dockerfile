FROM python:3.10.14

WORKDIR /source_code

COPY /source_code /source_code

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /source_code/risk-prediction/code/.settings/requirements.txt

CMD ["python", "/source_code/risk-prediction/code/src/frame/runner.py"]