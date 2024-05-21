FROM python:3.9-slim

WORKDIR /

#First install deps
RUN apt-get update && apt-get install -y gcc libpq-dev
COPY ./requirements.txt /
RUN pip install --no-cache-dir --upgrade -r /requirements.txt

#Cleanup
RUN rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

#Then code
COPY ./src/ /

#Then exec
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]
