FROM ubuntu:latest

# Install prerequisites
RUN apt-get update
RUN apt-get -y install python-pip
RUN pip install flask arrow requests

# Install pip requirements
RUN mkdir -p /app/twitter-rss
WORKDIR /app/twitter-rss

ADD docker /app/twitter-rss/

# Expose port, set volume & start command
EXPOSE 5000
WORKDIR /app/twitter-rss/webserver
CMD python -B server.py
