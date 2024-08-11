FROM python:3.12-alpine

WORKDIR /bot

RUN apk update && \
    apk add --no-cache python3-dev musl-dev gcc libffi-dev

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "main.py"]
