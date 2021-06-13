import os
import time
from fullyPost import config
import re
from flask.helpers import flash, url_for
from fullyPost.models import allPosts, comments, followErIng, postViewers, profile_db, thumbBy, usersAuth, db
from flask import Blueprint, redirect
from flask.globals import request, session
from flask.templating import render_template
from fullyPost.helpers import RequiredEmailVerfied, loginRequired, randomString
from hashlib import md5
import shutil

settings = Blueprint('settings',__name__)

@settings.route('/settings',methods=['GET','POST'])
@loginRequired
@RequiredEmailVerfied
def settings_page():
    if request.method == "POST":
        settingsToken = request.form.get('settings-token')
        typeChange = request.form.get('TypeChange')

        if not session.get('settingsToken') or not settingsToken or not typeChange:
            flash("Cannot submit your request! tryagain later.",{
                'signal' : 'red',
                'id' : randomString(15)
            })
            return redirect(url_for('.settings_page'))

        if typeChange == "delete-account":
            passwd = request.form.get('current-password')
            if not passwd:
                flash("You need to enter your password to delete your account !",{
                    'signal' : 'red',
                    'id' : randomString(15)
                })
                return redirect(url_for('.settings_page'))

            data = usersAuth.query.filter_by(userId=session.get('userId')).first()
            if (md5(str(config.PASSWORD_SALT+passwd).encode()).hexdigest() != data.password):
                flash("Incorrect Password for account !",{
                    'signal' : 'red',
                    'id' : randomString(15)
                })
                return redirect(url_for('.settings_page'))

                
            data = usersAuth.query.filter_by(userId=session.get('userId')).first()
            db.session.delete(data)
            db.session.commit()

            data = profile_db.query.filter_by(userId=session.get('userId')).first()
            db.session.delete(data)
            db.session.commit()

            
            data = followErIng.query.filter_by(Follower_userId=session.get('userId')).all()
            if data:
                [db.session.delete(block) for block in data]
                db.session.commit()
            data = followErIng.query.filter_by(Following_userId=session.get('userId')).all()
            if data:
                [db.session.delete(block) for block in data]
                db.session.commit()

            
            data = postViewers.query.filter_by(viewerId=session.get('userId')).all()
            if data:
                for block in data:
                    query = allPosts.query.filter_by(postId=block.postId).first()
                    query.views -= 1
                    db.session.delete(block)
                    db.session.commit()


            data = thumbBy.query.filter_by(userId=session.get('userId')).all()
            if data:
                for block in data:
                    query = allPosts.query.filter_by(postId=block.postId).first()
                    query.thumbs -= 1
                    db.session.delete(block)
                    db.session.commit()

            data = comments.query.filter_by(userId=session.get('userId')).all()
            if data:
                for block in data:
                    query = allPosts.query.filter_by(postId=block.postId).first()
                    query.commentsCounts -= 1
                    db.session.delete(block)
                    db.session.commit()


            if(os.path.exists(os.path.join(config.STORE_UPLOAD_FILES_FOLDER_PATH,session.get('userId')))):
                shutil.rmtree(os.path.join(config.STORE_UPLOAD_FILES_FOLDER_PATH,session.get('userId')))

            if(os.path.exists(os.path.join(config.STORE_PROFILE_IMAGE_PATH,session.get('userId')))):
                shutil.rmtree(os.path.join(config.STORE_PROFILE_IMAGE_PATH,session.get('userId')))

            session.clear()

            flash("Your account successfully deleted !",{
                'signal' : 'blue',
                'id' : randomString(15)
            })
            return redirect(url_for('authentication.login_auth'))


        elif typeChange == "logout-user":
            session.clear()
            flash("Logged out successfully !",{
                'signal' : 'blue',
                'id' : randomString(15)
            })
            return redirect(url_for('authentication.login_auth'))

        
        
        elif typeChange == "change-user-password":
            currentPassword = request.form.get('current-password')
            newPassword = request.form.get('new-password')

            regexPassword = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
            regexPassword = re.compile(regexPassword)

            if(not regexPassword.match(currentPassword)):
                flash("Password must contains minimum 8 characters and maximum 50 characters including uppercase, lowercase alphabets, digits and special symbols from [@$!#%*?&] and without spaces. <= Current Password ",{
                    "id" : randomString(10),
                    "signal" : "red"
                })
                return redirect(url_for('.settings_page'))

            if(not regexPassword.match(newPassword)):
                flash("Password must contains minimum 8 characters and maximum 50 characters including uppercase, lowercase alphabets, digits and special symbols from [@$!#%*?&] and without spaces. <= New Password ",{
                    "id" : randomString(10),
                    "signal" : "red"
                })
                return redirect(url_for('.settings_page'))

            
            data = usersAuth.query.filter_by(userId=session.get('userId')).first()
            if md5(str(config.PASSWORD_SALT+currentPassword).encode()).hexdigest() != data.password:
                flash("Incorrect Password received !",{
                    'signal' : 'red',
                    'id' : randomString(15)
                })
                return redirect(url_for('.settings_page'))

            if md5(str(config.PASSWORD_SALT+newPassword).encode()).hexdigest() == data.password:
                flash("Cannot change password to old password !",{
                    'signal' : 'red',
                    'id' : randomString(15)
                })
                return redirect(url_for('.settings_page'))

            data.password = md5(str(config.PASSWORD_SALT+newPassword).encode()).hexdigest()
            lastPWDchanged = int(time.time())
            data.lastPWDchanged = lastPWDchanged
            session['lastChanged'] = lastPWDchanged
            
            db.session.commit()

            flash("Password changed successfully !",{
                    'signal' : 'green',
                    'id' : randomString(15)
                })
            return redirect(url_for('.settings_page'))


    data = usersAuth.query.filter_by(userId=session.get('userId')).first()
    emailVerified = profile_db.query.filter_by(userId=data.userId).first()

    token = randomString(50)
    session['settingsToken'] = token
    return render_template(
        'settings.html',
        title="Settings",
        settingsToken = token,
        email = data.email,
        emailVerified = emailVerified.isEmailVerified,
        config=config
    )