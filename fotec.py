import os
import sqlite3
from passlib.apps import custom_app_context
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify

AUTH_FAILURE = {'error': 'Authentication Failed'}
 
# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'fotec.db'),
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