from flask import Flask, Response, render_template, url_for
from flask_caching import Cache
import uuid
import random
import collections
import json
import os
import copy

app = Flask(__name__)

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

# Cacheインスタンスの作成
cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379'),
    'CACHE_DEFAULT_TIMEOUT': 60 * 60 * 24,
})


answers = [
    'アパート',
    '宇宙人',
    'チャーハン',
    'フィリピン',
    'Tシャツ',
    'あいさつ',
    'おままごと',
    'おむつ',
    'かさ',
    'くつ',
    'くつした',
    'しょうゆ',
    'せっけん',
    'そら豆',
    'つえ',
    'つり橋',
    'はしご',
    'まばたき',
    'らせん階段',
    'アナウンサー',
    'インターネット',
    'エスカレーター',
    'エベレスト',
    'エレベーター',
    'オリンピック',
    'カジノ',
    'ガラパゴス諸島',
    'ガードレール',
    'コショウ',
    'コマーシャル',
    'コーヒー',
    'サイコロ',
    'サングラフ',
    'サンタクロース',
    'スキップ',
    'ストロー',
    'スポンジ',
    'スリップ',
    'タイムマシン',
    'タオル',
    'タクシー',
    'タトゥー',
    'チェス',
    'チョコレート',
    'テニスコート',
    'トイレ',
    'トウガラシ',
    'トウモロコシ',
    'トライアスロン',
    'トランプ',
    'トランポリン',
    'トンネル',
    'ドライヤー',
    'ニュージーランド',
    'ニュース',
    'ハワイ',
    'バジル',
    'バンジージャンプ',
    'パズル',
    'パラシュート',
    'パンツ',
    'ビール',
    'ピーナッツ',
    'フラフープ',
    'ヘリコプター',
    'ベビーカー',
    'ベランダ',
    'ボードゲーム',
    'ポップコーン',
    'マグカップ',
    'マラソン',
    'マンガ',
    'マンモス',
    'ミイラ',
    'ムー大陸',
    'メガネ',
    'メリーゴーランド',
    'ヨット',
    'ラジオ',
    'リップクリーム',
    'ロボット',
    'ワイン',
    'ワールドカップ',
    '一輪車',
    '丸太',
    '乾電池',
    '人魚',
    '休日',
    '会議',
    '住宅地',
    '信号機',
    '催眠術',
    '化石',
    '南国',
    '原始人',
    '台所',
    '図鑑',
    '国境',
    '地下室',
    '地球温暖化',
    '塩',
    '壁',
    '天井',
    '天気予報',
    '太陽電池',
    '女優',
    '妊婦',
    '妖精',
    '子守歌',
    '宇宙人',
    '実験',
    '寝室',
    '小説',
    '小麦',
    '屋上',
    '屋根',
    '帽子',
    '床',
    '庭',
    '恐竜',
    '悪魔',
    '手帳',
    '教科書',
    '散歩',
    '文化',
    '文明',
    '方眼紙',
    '暖炉',
    '望遠鏡',
    '柱',
    '横断歩道',
    '歩道',
    '歯ブラシ',
    '歴史',
    '気球',
    '水泳',
    '洗剤',
    '洗濯機',
    '潜水艦',
    '火力発電所',
    '牛乳',
    '畑',
    '真珠',
    '砂糖',
    '研究',
    '米',
    '紙コップ',
    '芸人',
    '落ち葉',
    '蒸気機関',
    '虫めがね',
    '試験管',
    '赤ちゃん',
    '辞書',
    '透明人間',
    '運動会',
    '金メダル',
    '雑誌',
    '雪男',
    '風呂',
    '風車',
    '飛行船',
    '食卓',
    '駐車場',
    '魔女'
]


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


@app.route('/<gameid>/join')
def invited_join_game(gameid):
    print('gameid:' + gameid)
    return render_template('index.html', gameid=gameid)


# join the game
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
