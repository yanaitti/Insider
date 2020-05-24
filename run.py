from flask import Flask, Response
from flask_caching import Cache
import uuid
import random
import collections
from flask_cors import CORS # CORS対策

# CORS対策 pip install flask-cors

app = Flask(__name__)
CORS(app) #CORS対策

# Cacheインスタンスの作成
cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 60 * 60 * 24,
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': '0'
})

answers = ['アパート', '宇宙人', 'チャーハン', 'フィリピン']


class Game:
    status = 'waiting' # waiting, started, end
    gameid = ''
    members = {}
    master = ''
    insider = ''
    answer = ''
    votelist = []
    votedlist = []


class Member:
    nickname = ''
    win = 0
    lose = 0
    game_count = 0


# create the game group
@app.route('/create')
def create_game():
    game = Game()
    member = Member()

    gameid = str(uuid.uuid4())
    game.gameid = gameid
    member.nickname = gameid
    game.members[gameid] = member

    cache.set(gameid, game)
    return gameid


# re:wait the game
@app.route('/<gameid>/waiting')
def waiting_game(gameid):
    game = cache.get(gameid)
    game.status = 'waiting'
    cache.set(gameid, game)
    return 'reset game status'


# join the game
@app.route('/<gameid>/join')
@app.route('/<gameid>/join/<nickname>')
def join_game(gameid, nickname='default'):
    if cache.get(gameid).status == 'waiting':
        game = cache.get(gameid)
        member = Member()

        clientid = str(uuid.uuid4())
        if nickname == 'default':
            member.nickname = clientid
        else:
            member.nickname = nickname
        game.members[clientid] = member

        cache.set(gameid, game)
        return clientid + ' ,' + member.nickname + ' ,' + game.status
    else:
        return 'Already started'


# processing the game
@app.route('/<gameid>/start')
def start_game(gameid):
    game = cache.get(gameid)
    game.status = 'started'

    members = [mid for mid in game.members.keys()]

    # auto select master
    n = random.randint(0, len(members) - 1)
    game.master = members.pop(n)

    game.votelist = members
    game.votedlist = []

    # auto select insider
    n = random.randint(0, len(members) - 1)
    game.insider = members.pop(n)

    # auto select answer
    game.answer = answers[random.randint(0, len(answers) - 1)]

    cache.set(gameid, game)
    return ' ,'.join(members) + ' ,master:' + game.master + ' ,insider:' + game.insider + ' ,answer:' + game.answer + ' original:' + ' ,'.join(game.members)


# playing the game
@app.route('/<gameid>/<clientid>/play')
def processing_game(gameid, clientid):
    game = cache.get(gameid)

    if clientid == game.master:
        return 'you are master. :' + clientid + ' the answer is:' + game.answer
    elif clientid == game.insider:
        return 'you are insider. :' + clientid + ' the master is:' + game.master + ' the answer is:' + game.answer
    else:
        return 'you are common. :' + clientid + ' the master is:' + game.master


# set user information the game
@app.route('/<gameid>/<clientid>/profile/set/<nickname>')
def edit_profile(gameid, clientid, nickname):
    game = cache.get(gameid)

    if clientid in game.members:
        member = game.members[clientid]
        member.nickname = nickname

        cache.set(gameid, game)
        return 'changed user name'
    else:
        return 'NG'


# get vote list the game
@app.route('/<gameid>/<clientid>/vote/list')
def get_profile(gameid, clientid):
    game = cache.get(gameid)

    return ' ,'.join(game.votelist)


# vote insider the game
@app.route('/<gameid>/vote/<voteid>')
def vote_game(gameid, voteid):
    game = cache.get(gameid)

    game.votedlist.append(voteid)

    cache.set(gameid, game)
    return ' ,'.join(game.votedlist)


# result vote insider the game
@app.route('/<gameid>/vote/result')
def vote_result_game(gameid):
    game = cache.get(gameid)

    votedlist = collections.Counter(game.votedlist)
    return 'most of vote is:' + str(votedlist.most_common()[0])


# members list the game
@app.route('/<gameid>/memberslist')
def memberslist_game(gameid):
    game = cache.get(gameid)

    response_list = []

    memberids = list(mid for mid in game.members.keys())

    for mid in memberids:
        member = game.members[mid]
        tmp = str(mid)
        tmp += ', ' + str(member.nickname)
        tmp += ', ' + str(member.win)
        tmp += ', ' + str(member.lose)
        tmp += ', ' + str(member.game_count)

        response_list.append(tmp)

    return ' & '.join(response_list)

# end of the game
@app.route('/<gameid>/end')
def end_game(gameid):
    game = cache.get(gameid)

    votedlist = game.votedlist
    memberids = list(mid for mid in game.members.keys())

    if len(votedlist) > 0:
        # exist vote(need to judge who is insider)
        memberids.remove(game.insider)

        votedlist = collections.Counter(game.votedlist)
        if game.insider == votedlist.most_common()[0][0]:
            # hit insider
            game.members[game.insider].lose += 1

            for mid in memberids:
                member = game.members[mid]
                member.win += 1
        else:
            # not hit insider
            game.members[game.insider].win += 1

            for mid in memberids:
                member = game.members[mid]
                member.lose += 1
    else:
        # not exist vote(all member lose)
        for mid in memberids:
            member = game.members[mid]
            member.lose += 1

    game.status = 'waiting'
    cache.set(gameid, game)

    response_list = []

    memberids = list(mid for mid in game.members.keys())

    for mid in memberids:
        member = game.members[mid]
        tmp = str(mid)
        tmp += ', ' + str(member.nickname)
        tmp += ', ' + str(member.win)
        tmp += ', ' + str(member.lose)
        tmp += ', ' + str(member.game_count)

        response_list.append(tmp)

    return ' & '.join(response_list) + ',' + game.master + ',' + game.insider
