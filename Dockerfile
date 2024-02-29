FROM python:3.11

RUN apt-get update && apt-get install -y git
WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python", "-m", "bot.main"]