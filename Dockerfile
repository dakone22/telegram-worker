FROM python:3.9-slim

ADD ./ /telegram-worker
WORKDIR /telegram-worker/

CMD exec apt-get update
RUN pip install --no-cache-dir -r ./requirements.txt

CMD python ./main.py