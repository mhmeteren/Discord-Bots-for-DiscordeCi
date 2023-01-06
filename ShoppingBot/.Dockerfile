FROM python:3.10.8-slim

WORKDIR /opt/app
COPY . .
ENV TOKEN=BotTOKEN
RUN pip install -r requirements.txt
CMD ["python", "main.py"]