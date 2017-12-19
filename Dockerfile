FROM python:3.6.3
RUN apt-get update && apt-get install cron vim -y
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
ADD requirements.txt /code/
WORKDIR /code
RUN pip install -r requirements.txt
ADD . /code/
WORKDIR /code/textify
CMD ["python", "bot.py"]
