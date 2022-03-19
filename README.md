# Twitter Responder

This tool/service leverages Twitter automation to respond to tweets intelligently. The response service leverages OpenAI's GPT-3 API to respond to questions in a manner representitive of the account's personality. For instance, a bot with a sarcastic personality may respond to questions in a sarcastic way.

## Setup

You will need to get developer access to GPT-3's API and Twitter's API:
- https://beta.openai.com/docs/api-reference
- https://developer.twitter.com/en/docs/twitter-api

After you have your API keys (saved),  you will need Python (3.8) and/or Docker to run this service.

### OAuth

If you've set up OAuth for Twitter previously (e.g. using twitter-story-time) you can reuse the same OAuth token and token secret for this service.

Finally, you will need to an OAuth token and a token secret. This is how you can do that:
- Run (from the root of the repo) `python src/request_access.py` in your terminal
- You will be provided a website link to authorize the application, copy and paste it into your web browser
- Once you click "Authorize App", you will be provided a 6-digit code
- Enter that 6-digit code into the terminal and hit enter
- Your OAuth token and token secret will be displayed on the terminal screen

Your OAuth token and token secret should last you about 60 days. After that, you may need to regenerate them.

## Use

For manual use, you will need to save the following API keys as environment variables on the machine you are running from:
- TWITTER_ID (to access your mentions)
- BEARER_TOKEN (to use Twitter's read API)
- OPENAI_API_KEY (for AI outputs given inputs)
- TWITTER_API_KEY (for OAuth session)
- TWITTER_API_SECRET (for OAuth session)
- OAUTH_TOKEN (to use Twitter's write API)
- OAUTH_TOKEN_SECRET (to use Twitter's write API)
- LOTTERY (optional; for probablistic use)

You can set an environment variable like so: `export 'TWITTER_ID'='UUUVVVWWWXXXYYYZZZ'`

Once all of your environment variables are set, you should be ready to run the application. You can manually run Twitter Story Time by typing this in your terminal (from repo root): `python src/boy.py`

If your `bot.py` file runs successfully, you should see something like this in your terminal:
```
...
Response code: 201
Tweet chosen: {'id': 'XXXXXXXXXXXXXXXX', 'text': '@YourBot what is your favorite food?'}
Payload: {'text': "Ramen, of course!", 'reply': {'in_reply_to_tweet_id': 'XXXXXXXXXXXXXXXX'}}
{
    "data": {
        "id": "YYYYYYYYYYYYYYYYY",
        "text": "@RandomUser1234 Ramen, of course!"
    }
}
```

## Lottery

The lottery feature can be used for probablistic tweeting. The environment variable, `LOTTERY`, can be set to an integer number greater than `1` but it defaults to `1`.

You can set `LOTTERY=N` where `1/N` is the chance of your tweet being sent out (winning the "lottery"). `LOTTERY` defaults to `1`, so if you do not override this env variable it will behave the same as before.

However, let's say that you set `LOTTERY` to `4`. That will result in a quarter chance of your tweet being sent. So in the event that your automation is scheduled to run four times a day, your account will send (on average) a single tweet out daily.

## Automation

You may notice that there is a Dockerfile in the root of the repository. This service was designed to be run from a docker container. Here's how you can do it:

**Step one**: Install Docker (Engine)

**Step two**: Once docker is running, from the root of the repository run the following:

`docker build -t twitter-responder --no-cache .`

The command above creates the docker image that you can now build from.

**Step three**: To run a docker container (which runs the service once), put this command from your terminal (change out the letters with actual keys when you run these commands):

`docker run -e TWITTER_ID="12345" -e BEARER_TOKEN="AAA" -e OPENAI_API_KEY="BBB" -e TWITTER_API_KEY="CCC" -e TWITTER_API_SECRET="DDD" -e OAUTH_TOKEN="EEE" -e OAUTH_TOKEN_SECRET="FFF" -e LOTTERY="4" -v /home/<user>/twitter-responder/data:/data twitter-responder`

Switch the `/home/<user>` path with the absolute path to where you cloned the repository on your server.

**Important:** you may notice the `-v` argument being passed into docker run. That argument is used to mount and bind to the host filesystem. This allows the program to write to the `data/replies.txt` file on the host which persists beyond the lifespan of each container. The `data/replies.txt` file contains the IDs of all tweets the service has responded to so that it knows to avoid responding to those repeatedly.
 
 **Step four**: To run your docker container on a scheule, you can set up a cron job:
 1. `sudo crontab -e` (opens an editor)
 2. Add this line to your crontab: 
 `*/10 * * * * docker run -e TWITTER_ID="12345" -e BEARER_TOKEN="AAA" -e OPENAI_API_KEY="BBB" -e TWITTER_API_KEY="CCC" -e TWITTER_API_SECRET="DDD" -e OAUTH_TOKEN="EEE" -e OAUTH_TOKEN_SECRET="FFF" -e LOTTERY="4" -v /home/<user>/twitter-responder/data:/data twitter-responder`
 
 
The above cronjob will run every 10 minutes
 
**Quick cronjob overview**:

The above schedule will run your job every day at midnight.

Cronjobs are typically structured in this order:

`minute hour day-of-month month day-of-week`
