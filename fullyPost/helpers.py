from functools import wraps
from random import choice
from string import ascii_letters, digits
from flask import session, redirect, url_for
from flask.templating import render_template
from fullyPost.models import allPosts, comments, forgotDB, postViewers, profile_db, thumbBy, usersAuth, db, verificationEmail
import time
import shutil
import os
from . import config

def randomString(size):
    return "".join([choice(choice([ascii_letters,digits])) for _ in range(size)])

def loginRequired(f):
    @wraps(f)
    def fun(*args, **kwargs):
        if 'userId' not in session:
            return redirect(url_for('authentication.login_auth'))

        data = usersAuth.query.filter_by(userId=session.get('userId'),lastPWDchanged=session.get('lastChanged')).first()
        if not data:
            try:
                session.pop('userId')
            except:
                pass
            return redirect(url_for('authentication.login_auth'))

        return f(*args,**kwargs)
    return fun


def RedirectIfLoggedIn(f):
    @wraps(f)
    def fun(*args, **kwargs):
        if 'userId' in session:
            data = usersAuth.query.filter_by(userId=session.get('userId'),lastPWDchanged=session.get('lastChanged')).first()
            if not data:
                try:
                    session.pop('userId')
                except:
                    pass
                return redirect(url_for('authentication.login_auth'))
            return redirect(url_for('home.homepage'))

        return f(*args,**kwargs)
    return fun


def checkItPrimary(f):
    @wraps(f)
    def fun(*args, **kwargs):
        if 'userId' not in session:
            return f(*args,**kwargs)
        data = usersAuth.query.filter_by(userId=session.get('userId'),lastPWDchanged=session.get('lastChanged')).first()
        if not data:
            try:
                session.pop('userId')
            except:
                pass
            return f(*args,**kwargs)

        return f(*args,**kwargs)
    return fun


def RequiredEmailVerfied(f):
    @wraps(f)
    def fun(*args, **kwargs):
        if 'userId' not in session:
            return f(*args,**kwargs)
        data = usersAuth.query.filter_by(userId=session.get('userId'),lastPWDchanged=session.get('lastChanged')).first()
        if not data:
            try:
                session.pop('userId')
            except:
                pass
            return f(*args,**kwargs)
        else:
            query = profile_db.query.filter_by(userId=session.get('userId')).first()
            if not query.isEmailVerified:
                return render_template('needEmailVerified.html',title="You need to verify your email.")

        return f(*args,**kwargs)
    return fun


def deleteAccIfUnverified(account_email,account_userId):
    time.sleep(config.ACCOUNT_VER_TIME_LIMIT)

    query = usersAuth.query.filter_by(email=account_email,userId=account_userId).first()

    if not query:
        return False
    
    query1 = profile_db.query.filter_by(userId=query.userId).first()

    if not query1:
        return False
    
    if not query1.isEmailVerified:
        db.session.delete(query)
        db.session.commit()

        query2 = verificationEmail.query.filter_by(userId=query1.userId).first()
        if query2:
            db.session.delete(query2)
            db.session.commit()

        db.session.delete(query1)
        db.session.commit()
        return False
    
    return True



def deleteForgotLink(account_email,account_userId):
    time.sleep(config.FORGOT_LINK_TIME_LIMIT)

    query = usersAuth.query.filter_by(email=account_email,userId=account_userId).first()

    if not query:
        return False
    
    query1 = profile_db.query.filter_by(userId=query.userId).first()

    if not query1:
        return False
    
    query2 = forgotDB.query.filter_by(email=account_email,userId=account_userId).first()
    if query2:
        db.session.delete(query2)
        db.session.commit()
        return True
    
    return False


def deletePost(postId):
    time.sleep(config.DELETE_POSTS_AFTER)

    query = allPosts.query.filter_by(postId=postId).first()
    if not query:
        return False
    
    query1 = profile_db.query.filter_by(userId=query.postById).first()
    if query1:
        query1.totalPosts -= 1
        db.session.commit()

    query2 = postViewers.query.filter_by(postId=postId).first()
    if query2:
        db.session.delete(query2)
        db.session.commit()

    query2 = thumbBy.query.filter_by(postId=postId).first()
    if query2:
        db.session.delete(query2)
        db.session.commit()
    
    query2 = comments.query.filter_by(postId=postId).first()
    if query2:
        db.session.delete(query2)
        db.session.commit()

    shutil.rmtree(os.path.join(config.STORE_UPLOAD_FILES_FOLDER_PATH, query1.userId,postId))

    db.session.delete(query)
    db.session.commit()