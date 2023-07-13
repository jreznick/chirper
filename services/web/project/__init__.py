from datetime import datetime
from flask import (
    redirect,
    render_template,
    request as postrequest,
    send_from_directory,
    session,
    url_for
)
import uuid

from .app import app
from .logger import DEBUG_ROUTE, mylogger, timeit, version
from .model import (
    db,
    UserAccount,
    Login,
    Browser,
    Device,
    Chirp,
    Following,
    ReChirp,
    DirectMessage,
    Block
)


@app.route("/")
def hello_world():
    return redirect(url_for('login', now=datetime.utcnow()))


def feed():
    user_id = session['user_id']
    # assemble followed accounts
    following_list = []
    query = db.session.query(Following). \
        filter(Following.follower == user_id)
    for row in query.all():
        following_list.append(row['following'])
    query = db.session.query(UserAccount). \
        filter(
        UserAccount.user_id in following_list,
        UserAccount.visible is True)
    # reduce to visible followed accounts
    visible_to_follow = []
    for row in query.all():
        visible_to_follow.append(row['user_id'])
    # remove blocked accounts
    query = db.session.query(Block). \
        filter(
            Block.blocked_user_id == user_id,
            Block.user_id in visible_to_follow
    )
    for row in query.all():
        visible_to_follow.remove(row['user_id'])
    # ToDo: 'private' accounts are only visible to accounts followed by author, implement
    # populate visible chirps from followed, visible accounts
    chirps = []
    query = db.session.query(Chirp). \
        filter(
        Chirp.user_id in visible_to_follow,
        Chirp.visible is True
    )
    for row in query.all():
        chirps.append(row)

    return render_template('feed.html', chirps=chirps)


@app.route('/unhide', methods=['GET', 'POST'])
def unhide():
    """Unide a chirp, a rechirp, or an account profile"""
    if postrequest.method == 'POST':
        with app.app_context():
            domain = postrequest.form['domain']
            if domain == 'chirp':
                db.session.query(Chirp). \
                    filter(
                        Chirp.chirp_id == postrequest.form['chirp_id'],
                        Chirp.visible is False
                ). \
                    update(
                        {
                            Chirp.visible: True,
                            Chirp.touched_ts: datetime.utcnow()
                        },
                        synchronize_session=False
                )
            elif domain == 'rechirp':
                db.session.query(ReChirp). \
                    filter(
                    ReChirp.re_chirp_id == postrequest.form['re_chirp_id'],
                    ReChirp.visible is False
                ). \
                    update(
                    {
                        ReChirp.visible: True,
                        ReChirp.touched_ts: datetime.utcnow()
                    },
                    synchronize_session=False
                )
            elif domain == 'user_account':
                db.session.query(ReChirp). \
                    filter(
                    UserAccount.user_id == postrequest.form['user_id'],
                    UserAccount.visible is False
                ). \
                    update(
                    {
                        UserAccount.visible: True,
                        UserAccount.touched_ts: datetime.utcnow()
                    },
                    synchronize_session=False
                )
            db.session.commit()


@app.route('/hide', methods=['GET', 'POST'])
def hide():
    """Hide a chirp or an account profile"""
    if postrequest.method == 'POST':
        with app.app_context():
            domain = postrequest.form['domain']
            if domain == 'chirp':
                db.session.query(Chirp). \
                    filter(
                        Chirp.chirp_id == postrequest.form['chirp_id'],
                        Chirp.visible is True
                ). \
                    update(
                        {
                            Chirp.visible: False,
                            Chirp.touched_ts: datetime.utcnow()
                        },
                        synchronize_session=False
                )
            elif domain == 'user_account':
                db.session.query(ReChirp). \
                    filter(
                    UserAccount.user_id == postrequest.form['user_id'],
                    UserAccount.visible is True
                ). \
                    update(
                    {
                        UserAccount.visible: False,
                        UserAccount.touched_ts: datetime.utcnow()
                    },
                    synchronize_session=False
                )
            db.session.commit()


@app.route('/rechirp', methods=['GET', 'POST'])
def post_rechirp():
    """Embed a chirp record within a chirp"""
    if postrequest.method == 'POST':
        created_ts = datetime.utcnow(),
        # store the rechirp record
        staged_rechirp = {
            'rechirp_id': uuid.uuid4().hex,
            'user_id': session['user_id'],
            'chirp_id': postrequest.form['chirp_id'],
            'device_id': session['device_id'],
            'rechirp_quote': postrequest.form['rechirp_quote'],
            'created_ts': created_ts,
            'image_uri': postrequest.form['image_uri'],
            'visible': True
        }
        rechirp_record = ReChirp(**staged_rechirp)  # type: ignore
        with app.app_context():
            db.session.add(rechirp_record)
            db.session.commit()
        # place the rechirp in the regular chirp feed
        staged_chirp = {
            'chirp_id': uuid.uuid4().hex,
            'user_id': staged_rechirp['user_id'],
            'device_id': staged_rechirp['device_id'],
            'chirp_content': staged_rechirp['rechirp_quote'],  # ToDo: figure out widget embed style
            'created_ts': created_ts,
            'image_uri': staged_rechirp['image_uri'],
            'visible': True
        }
        chirp_record = Chirp(**staged_chirp)  # type: ignore
        with app.app_context():
            db.session.add(chirp_record)
            db.session.commit()


@app.route('/getchirp', methods=['GET'])
def get_chirp():
    """View a chirp record"""
    chirp_id = postrequest.form['chirp_id']
    query = db.session.query(Chirp). \
        filter(
            Chirp.user_id == chirp_id,
            Chirp.visible is True
        )
    chirp = query.first()  # ToDo: figure out widget embed style

    return render_template('view_chirp', chirp=chirp)


@app.route('/chirp', methods=['GET', 'POST'])
def post_chirp():
    """Create a chirp record"""
    if postrequest.method == 'POST':
        staged_chirp = {
            'chirp_id': uuid.uuid4().hex,
            'user_id': session['user_id'],
            'device_id': session['device_id'],
            'chirp_content': postrequest.form['chirp_content'],
            'created_ts': datetime.utcnow(),
            'image_uri': postrequest.form['image_uri'],
            'visible': True
        }
        chirp_record = Chirp(**staged_chirp)  # type: ignore
        with app.app_context():
            db.session.add(chirp_record)
            db.session.commit()


@app.route('/update_account', methods=['GET', 'POST'])  # ToDo: implement
def update_account():
    pass


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    """Create a user account"""
    if postrequest.method == 'POST':
        staged_new_account_record = {
            'username': postrequest.form['username'],  # ToDo: username validator
            'password': postrequest.form['password'],  # ToDo: implement maskpass
            'email': postrequest.form['email'],  # ToDo: wrap in email validator
            'display_name': postrequest.form['display_name'],  # ToDo: wrap in name validator
            'bio': postrequest.form['bio'],  # ToDo: word limit
            'location': postrequest.form['location'],
            'URL': postrequest.form['url'],
            'DOB': postrequest.form['DOB'],
            'visible': True,
            'private': False
        }
        new_account_record = UserAccount(**staged_new_account_record)  # type: ignore
        with app.app_context():
            db.session.add(new_account_record)
            db.session.commit()


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """Terminate a user session and go to `login`"""
    if session:
        session.clear()

    return redirect(url_for('login', now=datetime.utcnow()))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate a user session"""
    error = None
    if session:
        session.clear()
    if postrequest.method == 'POST':
        username = postrequest.form['username']
        password = postrequest.form['password']  # ToDo: implement maskpass
        # ToDo: SQLA select from users table to match encrypt w/ encrypt pw
        response = []

        if len(response) > 0:
            session['user_id'] = response[0]['user_id']
            session['username'] = response[0]['username']
            session['device_id'] = response[0]['device_id']
            session['browser_id'] = response[0]['browser_id']
            session['logged_in'] = True
            mylogger.info(f"{username} logs in")

            return redirect(url_for('feed', now=datetime.utcnow()))
        else:
            error = 'Login Failed'
            attempted_user = postrequest.form['username']
            log_string = f"{attempted_user} : {error} "
            mylogger.warning(f"{log_string}")

    return render_template('login.html', now=datetime.utcnow(), error=error)


@app.route("/static/<path:filename>")
def staticfiles(filename):
    """
    :param filename: The path to a file to download
    :return send_from_directory(): the file at the location requested
    """
    return send_from_directory(app.config["STATIC_FOLDER"], filename)
