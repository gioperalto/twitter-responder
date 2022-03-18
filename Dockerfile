# set base image (host OS)
FROM python:3.8

# set env variables
ENV TWITTER_ID "0123456789876543210"
ENV BEARER_TOKEN "AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE"
ENV OPENAI_API_KEY "AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE"
ENV TWITTER_API_KEY "AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE"
ENV TWITTER_API_SECRET "AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE"
ENV OAUTH_TOKEN "AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE"
ENV OAUTH_TOKEN_SECRET "AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE"
ENV LOTTERY "1"

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY src .
COPY seeds seeds

# command to run on container start
CMD [ "sh", "-c", "python ./bot.py" ]