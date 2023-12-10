FROM ubuntu:latest
LABEL authors="13igor0241@gmail.com"

RUN apt-get update -y
RUN apt-get install -y python3-pip python3 build-essential
RUN apt-get install -y wget cron zip


# INSTALLING CHROME & CHROMEDRIVER
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb || true
RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/120.0.6099.71/linux64/chromedriver-linux64.zip
RUN unzip chromedriver-linux64.zip
RUN mv -f chromedriver-linux64/chromedriver /usr/bin/chromedriver
RUN chown root:root /usr/bin/chromedriver
RUN chmod +x /usr/bin/chromedriver

COPY . /app
WORKDIR /app

RUN pip3 install --no-cache-dir --upgrade -r requirements.txt
CMD ["python3", "scrappers/news.py"]
