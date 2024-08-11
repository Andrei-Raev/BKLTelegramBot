FROM python:3.12-alpine

WORKDIR /bot

RUN apt install python3-dev default-libmysqlclient-dev build-essential -y

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "main.py"]
