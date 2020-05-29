from flask import Flask, Response, render_template
from flask_caching import Cache
import uuid
import random
import collections
import json
import os
import copy

app = Flask(__name__)

# Cacheインスタンスの作成
cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379'),
    'CACHE_DEFAULT_TIMEOUT': 60 * 60 * 24,
})


answers = ['アパート', '宇宙人', 'チャーハン', 'フィリピン']


@app.route('/')
def homepage():
    return render_template('index.html')


# create the game group
@app.route('/create/<nickname>')
def create_game(nickname):
    game = {
        'status': 'waiting',
        'routeidx': 0,
        'once': False,
        'votedlist': [],
        'players': []}
    player = {}

    gameid = str(uuid.uuid4())
    game['gameid'] = gameid
    player['playerid'] = gameid
    player['nickname'] = nickname
    game['players'].append(player)

    app.logger.debug(gameid)
    app.logger.debug(game)
    cache.set(gameid, game)
    return gameid


# re:wait the game
@app.route('/<gameid>/waiting')
def waiting_game(gameid):
    game = cache.get(gameid)
    game['status'] = 'waiting'
    cache.set(gameid, game)
    return 'reset game status'


# join the game
@app.route('/<gameid>/join')
@app.route('/<gameid>/join/<nickname>')
def join_game(gameid, nickname='default'):
    game = cache.get(gameid)
    if game['status'] == 'waiting':
        player = {}

        playerid = str(uuid.uuid4())
        player['playerid'] = playerid
        if nickname == 'default':
            player['nickname'] = playerid
        else:
            player['nickname'] = nickname
        game['players'].append(player)

        cache.set(gameid, game)
        return playerid + ' ,' + player['nickname'] + ' ,' + game['status']
    else:
        return 'Already started'


# processing the game
@app.route('/<gameid>/start')
def start_game(gameid):
    game = cache.get(gameid)
    game['status'] = 'started'

    routelist = copy.copy(game['players'])
    random.shuffle(routelist)

    # auto select master
    n = random.randint(0, len(routelist) - 1)
    game['master'] = routelist.pop(n)

    game['votelist'] = copy.copy(routelist)

    # auto select insider
    n = random.randint(0, len(routelist) - 1)
    game['insider'] = routelist.pop(n)

    # auto select answer
    game['answer'] = answers[random.randint(0, len(answers) - 1)]

    cache.set(gameid, game)
    return json.dumps(game)


# vote insider the game
@app.route('/<gameid>/vote/<voteid>')
def vote_game(gameid, voteid):
    game = cache.get(gameid)

    game['votedlist'].append(voteid)

    cache.set(gameid, game)
    return 'ok'


# vote insider the game
@app.route('/<gameid>/results')
def vote_results(gameid):
    game = cache.get(gameid)

    game['status'] = 'end'

    c = collections.Counter(game['votedlist'])
    sortedlist = sorted(c.items(), key=lambda x:x[1], reverse=True)
    resultlists = []
    for vote in sortedlist:
        result = {}
        result['playerid'] = vote[0]
        result['vote'] = vote[1]
        player = [player for player in game['players'] if player['playerid'] == vote[0]][0]
        result['nickname'] = player['nickname']
        resultlists.append(result)

    game['results'] = resultlists

    cache.set(gameid, game)
    return 'ok'


# all status the game
@app.route('/<gameid>/status')
def game_status(gameid):
    game = cache.get(gameid)

    return json.dumps(game)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
