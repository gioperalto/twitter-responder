import os, openai, json, random, re, requests
from http.client import responses
from requests_oauthlib import OAuth1Session

def is_lottery_winner(chance):
    raffle = [False] * chance
    raffle[len(raffle)//2] = True

    return random.choice(raffle)

def bearer_oauth(r):
    bearer_token = os.environ.get("BEARER_TOKEN")
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "Azuki Bot"

    return r

def get_mentions():
    twitter_id = os.environ.get("TWITTER_ID")
    url = f'https://api.twitter.com/2/users/{twitter_id}/mentions'
    response = requests.request("GET", url, auth=bearer_oauth)

    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    
    return response.json()['data']

def pick_candidates(tweets):
    candidates = []
    replies = open('data/replies.txt', 'r').read().splitlines()

    for tweet in tweets:
        if not (tweet['id'] in replies):
            url = f"https://api.twitter.com/2/tweets/search/recent?tweet.fields=author_id&query=conversation_id:{tweet['id']}"
            response = requests.request("GET", url, auth=bearer_oauth)
            
            if response.status_code != 200:
                raise Exception(
                    "Request returned an error: {} {}".format(
                        response.status_code, response.text
                    ) 
                )
            
            if bool(filter_tweet(tweet['text']).strip()):
                candidates.append(tweet)

    return candidates

def inject_context(tweet):
    tweet_stack, context = [], ''
    url = f"https://api.twitter.com/2/tweets?ids={tweet['id']}&tweet.fields=author_id,conversation_id,created_at,in_reply_to_user_id,referenced_tweets&expansions=author_id,in_reply_to_user_id,referenced_tweets.id&user.fields=name,username"
    response = json.loads(requests.request("GET", url, auth=bearer_oauth).text)

    for i in range(len(response['includes']['tweets'])):
        for user in response['includes']['users']:
            if user['id'] == response['includes']['tweets'][i]['author_id']:
                item = { 'name': user['name'], 'text': response['includes']['tweets'][i]['text'] }
                tweet_stack.append(item)

    for i in range(len(tweet_stack)):
        item = tweet_stack.pop()
        context += f"{item['name']}: {filter_tweet(item['text'])}"

    context += f"\nYou: {filter_tweet(tweet['text'])}"

    return context

def filter_tweet(tweet):
    tweet = re.sub("@AzukiOfficial", "Azuki", tweet)
    tweet = re.sub("@[a-zA-Z0-9_]+", "", tweet)
    tweet = re.sub("https://[a-zA-Z0-9\.\/]+", "", tweet)
    tweet = re.sub("http://[a-zA-Z0-9\.\/]+", "", tweet)

    return tweet.strip()

def generate_response(question):
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    personality = open('seeds/personality.txt', 'r').read()

    # Filter out mentions from question
    context = inject_context(question)

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"{personality}\n\n{context}\nKai:",
        temperature=0.9,
        max_tokens=60,
        top_p=1,
        frequency_penalty=0.5,
        presence_penalty=0.6
    )

    story = response['choices'][0]['text']
    return story

def create_oath_session():
    twitter_api_key = os.environ.get("TWITTER_API_KEY")
    twitter_api_secret = os.environ.get("TWITTER_API_SECRET")
    oauth_token = os.environ.get("OAUTH_TOKEN")
    oauth_token_secret = os.environ.get("OAUTH_TOKEN_SECRET")

    oauth = OAuth1Session(
        twitter_api_key,
        client_secret=twitter_api_secret,
        resource_owner_key=oauth_token,
        resource_owner_secret=oauth_token_secret,
    )

    return oauth

def tweet_response(oauth, resp, tweet_id):
    payload = { "text": resp, "reply": { "in_reply_to_tweet_id": tweet_id } }

    print('Payload:', payload)

    # Making the request
    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
    )

    if response.status_code != 201:
        raise Exception("Request returned an error: {} {}".format(response.status_code, response.text))

    print("Response code: {}".format(response.status_code))

    # Saving the response as JSON
    json_response = response.json()
    print(json.dumps(json_response, indent=4, sort_keys=True))
    
    # Write tweet ID to replies file
    open('data/replies.txt', 'a').write(f'{tweet_id}\n')



if __name__ == "__main__":
    lottery = os.getenv("LOTTERY", '1')

    if is_lottery_winner(int(lottery)):
        oauth = create_oath_session()
        mentions = get_mentions()
        candidates = pick_candidates(mentions)

        if len(candidates) > 0:
            tweet = random.choice(candidates)
            print('Tweet chosen:', tweet)
            response = generate_response(tweet['text'])
            tweet_response(oauth=oauth, resp=response, tweet_id=tweet['id'])
        else:
            print('No candidates left from mentions.')
    else:
        print('Lost raffle. Tweet won\'t be sent.')