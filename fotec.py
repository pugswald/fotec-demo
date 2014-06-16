import os
import random
import sqlite3
import string
from passlib.apps import custom_app_context
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify

AUTH_FAILURE = {'error': 'Authentication failed'}
INVALID_AMOUNT = {'error': 'Amount invalid'}
INVALID_MERCHANT = {'error': 'Merchant invalid'}
INVALID_CARD = {'error': 'Card invalid'}
TRANSACTION_FAILURE = {'error': 'Transaction failed'}

# Temp names until proper list available
VALID_MERCHANTS = [ 'My Merchant' ]

app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'fotec_test.db'),
    DEBUG=True,
    SECRET_KEY='development key',
))
app.config.from_envvar('FOTEC_SETTINGS', silent=True)

@app.route('/card', methods=['GET'])
def get_cards():
    try:
        u_id = validate_user(request.args.get('device'),request.args.get('pin'))
    except:
        return jsonify(AUTH_FAILURE)
    db = get_db()
    cur = db.execute('select id, name, bank, network, last_four from cards where user_id = ?', [u_id])
    cdata = cur.fetchall()
    cards = [ dict(card) for card in cdata ]
    return jsonify({'data':cards})

@app.route('/pay', methods=['POST'])
def post_pay():
    try:
        u_id = validate_user(request.form['device'],request.form['pin'])
    except:
        return jsonify(AUTH_FAILURE)
    # Input validation
    try:
        # TODO: Make sure there's no numbers after the cent column.
        amt = float(request.form['amount'])
        if amt < .01:
            raise Exception()
    except:
        return jsonify(INVALID_AMOUNT)
    if request.form['merchant'] not in VALID_MERCHANTS:
        return jsonify(INVALID_MERCHANT)
    db = get_db()
    # Verify user owns this card
    try:
        cur = db.execute('SELECT id FROM cards WHERE user_id = ? AND id = ?',[u_id,request.form['card_id']])
        cards = cur.fetchall()
        if len(cards) != 1:
            print(cards)
            raise Exception()
        card_id = cards[0]['id']
    except:
        return jsonify(INVALID_CARD)

    # TODO: Do merchant transaction here
    # Until then, fail about half the transactions
    transaction_success = bool(random.getrandbits(1))
    if not transaction_success:
        return jsonify(TRANSACTION_FAILURE)
    approval = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    db.execute('insert into transactions (card_id, merchant, amount, approval) VALUES (?, ?, ?, ?)', 
                     [card_id, request.form['merchant'], amt, approval])
    db.commit() # TODO: Rollback logic
    return jsonify({'approval':approval})


def validate_user(device, pin):
    ''' Quick way to validate user.  Returns id on success, raises exception on failure '''
    db = get_db()
    cur = db.execute('select id, passhash from users where device = ?',[device])
    entries = cur.fetchall()
    if len(entries) != 1:
        raise Exception('Wrong number of users (%s) returned for device %s'%(len(entries),device))
    user = entries[0]
    if custom_app_context.verify(pin,user['passhash']):
        return user['id']
    raise Exception('Device %s failed authentication'%device)





def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    ''' Clear the database and build the schema '''
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def create_user(user_name, device, pin):
    ''' Create a new user
        No input validation - be careful '''
    with app.app_context():
        db = get_db()
        db.execute('insert into users (name, device, passhash) values (?, ?, ?)',
                [user_name, device, custom_app_context.encrypt(pin)])
        db.commit()

def add_card(device, pin, card_data):
    ''' Add a card to the database.
        No input validation - be careful '''
    with app.app_context():
        db = get_db()
        cur = db.execute('select id, passhash from users where device = ?',[device])
        entries = cur.fetchall()
        user = entries[0]
        if custom_app_context.verify(pin,user['passhash']):
            db.execute('insert into cards (user_id, name, bank, network, last_four) values (?, ?, ?, ?, ?)',
                    [user['id'], card_data['name'], card_data['bank'], card_data['network'], card_data['last_four']])
            db.commit()
        else:
            print "Error in user authentication"
            print user

if __name__ == '__main__':
    app.run()