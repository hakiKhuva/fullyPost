from flask.globals import request
from flask.helpers import flash, make_response, send_file
from fullyPost.helpers import RequiredEmailVerfied, checkItPrimary, loginRequired, randomString
from flask import Blueprint, session, redirect, url_for, abort
from flask.templating import render_template
from fullyPost.models import db, profile_db, followErIng
import magic
import os
from fullyPost import config
from PIL import Image
import shutil

profile = Blueprint('profile',__name__)


@profile.route('/profile',methods=['GET','POST'])
@loginRequired
@RequiredEmailVerfied
def profile_page():
    if request.method == "POST":
        wantToUsePhoto = request.form.get("profile-usePhoto")
        photo = request.files.get('profile-photo')
        username = request.form.get("profile-username")
        name = request.form.get("profile-name")
        desc = request.form.get('profile-desc')
        tokenForm = request.form.get("userEditProfileToken")

        if not tokenForm or not session.get('userEditProfileToken'):
            return redirect(url_for('.profile_page'))
        
        if tokenForm != session.get('userEditProfileToken'):
            return redirect(url_for('.profile_page'))

        if not wantToUsePhoto and not username and not name and not desc:
            flash("Something went wrong!",{
                "id" : randomString(10),
                "signal" : "red"
            })
            return redirect(url_for('.profile_page'))

        if len(name) < config.MIN_PROFILE_NAME_LEN or len(name) > config.MAX_PROFILE_NAME_LEN:
            flash(f"Minimum {config.MIN_PROFILE_NAME_LEN} and Maximum {config.MAX_PROFILE_NAME_LEN} characters can be used in name!",{
                    "id" : randomString(10),
                    "signal" : "red"
                })
            return redirect(url_for('.profile_page'))

        if len(username) < config.MIN_PROFILE_USERNAME_LEN or len(username) > config.MAX_PROFILE_USERNAME_LEN:
            flash(f"Minimum {config.MIN_PROFILE_USERNAME_LEN} and Maximum {config.MAX_PROFILE_USERNAME_LEN} characters can be used in username!",{
                    "id" : randomString(10),
                    "signal" : "red"
                })
            return redirect(url_for('.profile_page'))
        
        if len(username.strip()) == 0 or ' ' in username:
            flash(f"Your username should not contains any whitespace!",{
                    "id" : randomString(10),
                    "signal" : "red"
                })
            return redirect(url_for('.profile_page'))

        ImageData = photo.stream.read()

        if len(desc) > config.MAX_DESCRIPTION_LEN:
            flash(f"Your description can maximum contains {config.MAX_DESCRIPTION_LEN} characters!",{
                    "id" : randomString(10),
                    "signal" : "red"
                })
            return redirect(url_for('.profile_page'))
        
        if wantToUsePhoto == "on":
            if not photo:
                flash("'Use photo' selected but image not selected!",{
                    "id" : randomString(10),
                    "signal" : "red"
                })
                return redirect(url_for('.profile_page'))
            
            if(len(ImageData)/1024 > config.MAX_PROFILE_IMAGE_SIZE_KB):
                flash(f"Image size must be under {config.MAX_PROFILE_IMAGE_SIZE_KB/1024} MB!",{
                    "id" : randomString(10),
                    "signal" : "red"
                })
                return redirect(url_for('.profile_page'))

            if magic.from_buffer(ImageData,mime=True)[0:5] != "image":
                flash("'User Profile Photo' must be an Image!",{
                    "id" : randomString(10),
                    "signal" : "red"
                })
                return redirect(url_for('.profile_page'))

        change = 0
        data = profile_db.query.filter_by(userId=session.get('userId')).first()
        if wantToUsePhoto == "on":
            if data.customProfilePhoto == True:
                try:
                    shutil.rmtree(os.path.join(config.STORE_PROFILE_IMAGE_PATH,data.userId))
                except Exception as e:
                    print(e)
                    pass

            if not os.path.exists(os.path.join(config.STORE_PROFILE_IMAGE_PATH,data.userId)):
                os.mkdir(os.path.join(config.STORE_PROFILE_IMAGE_PATH,data.userId))


            data.customProfilePhoto = True
            userImageName = randomString(50)
            data.profileImageName = userImageName+"."+magic.from_buffer(ImageData,mime=True)[6:]
            open(os.path.join(config.STORE_PROFILE_IMAGE_PATH,data.userId,f"{userImageName}.{magic.from_buffer(ImageData,mime=True)[6:]}"),'wb').write(ImageData)

            im = Image.open(os.path.join(config.STORE_PROFILE_IMAGE_PATH,data.userId,f"{userImageName}.{magic.from_buffer(ImageData,mime=True)[6:]}"))
            im.save(os.path.join(config.STORE_PROFILE_IMAGE_PATH,data.userId,f"{userImageName}.{magic.from_buffer(ImageData,mime=True)[6:]}"),quality=40,optimize=True)
            change += 1

        if data.username != username:
            data1 = profile_db.query.filter_by(username=username).first()
            if data1:
                flash("Username is already used by someone choose another!",{
                    "id" : randomString(10),
                    "signal" : "red"
                })
                return redirect(url_for('.profile_page'))
            data.username = username
            change += 1
        if data.name != name:
            data.name = name
            change += 1
        if data.description != desc:
            data.description = desc
            change += 1
        
        db.session.commit()

        if change == 0:
            flash("No changes detected!",{
                "id" : randomString(10),
                "signal" : "blue"
            })
            return redirect(url_for('.profile_page'))


        flash("Changes successfully changed!",{
                "id" : randomString(10),
                "signal" : "green"
            })
        return redirect(url_for('.profile_page'))


    data = profile_db.query.filter_by(userId=session.get('userId')).first()
    if not data:
        session.pop('userId')
        flash("Your account may be deleted or logged out try again to login.")
        return redirect(url_for('authentication.login_page'))

    user_information = {
        "name" : data.name,
        "desc" : data.description,
        "username" : data.username,
        "joinDate" : data.accountCreated
    }
    user_information['textAreaDesc'] = user_information['desc']

    user_profile = {
        "customProfilePhoto" : data.customProfilePhoto,
        "posts" : data.totalPosts,
    }
    if user_profile['customProfilePhoto']:
        user_profile['profileImage'] = data.profileImageName

    data = followErIng.query.filter_by(Follower_userId=session.get('userId')).all()
    if data:
        user_profile['followers'] = len(data)
    else:
        user_profile['followers'] = 0

    data = followErIng.query.filter_by(Following_userId=session.get('userId')).all()
    if data:
        user_profile['following'] = len(data)
    else:
        user_profile['following'] = 0

    
    userEditProfileToken = randomString(100)
    session['userEditProfileToken'] = userEditProfileToken

    allInOneToken = randomString(200)
    session['allInOneToken'] = allInOneToken

    return render_template(
        'profile.html',
        title="Profile",
        userInformation = user_information,
        userProfile = user_profile,
        isSelf = True,
        userEditProfileToken=userEditProfileToken,
        allInOneToken=allInOneToken,
        maxFileSize = config.POST_FILE_SIZE_KB/1024,
        maxCharacterSizeInText=config.POST_TEXT_MAX_CHAR,
        config=config
    )



@profile.route('/image/profile/<username>/<fileName>')
@loginRequired
@RequiredEmailVerfied
def profileImageGetter(username,fileName):
    data = profile_db.query.filter_by(username=username).first()
    if not data or not session.get('allInOneToken'):
        return redirect(url_for('.profile_page'))
    
    if not data.customProfilePhoto:
        abort(404)

    if not os.path.exists(os.path.join(config.STORE_PROFILE_IMAGE_PATH,data.userId,fileName)):
        abort(404)

    resp = make_response(send_file(os.path.join(config.UPLOAD_PROFILE_IMAGE_PATH,data.userId,fileName)))
    resp.headers['Cache-Control'] = config.MAX_CACHE_CONTROL

    return resp



@profile.route('/p/<username>')
@loginRequired
@RequiredEmailVerfied
def profile_specific(username):
    data = profile_db.query.filter_by(username=username).first()

    if not data:
        flash("Account may be deleted or doesn't exists.",{
                "id" : randomString(10),
                "signal" : "blue"
            })
        return redirect(url_for('.profile_page'))
    
    userId = data.userId
    if 'userId' in session:
        if data.userId == session.get('userId'):
            return redirect(url_for('.profile_page'))

    user_information = {
        "name" : data.name,
        "desc" : data.description,
        "username" : data.username,
        "joinDate" : data.accountCreated
    }
    user_information['textAreaDesc'] = user_information['desc']

    user_profile = {
        "customProfilePhoto" : data.customProfilePhoto,
        "posts" : data.totalPosts,
    }

    if user_profile["customProfilePhoto"]:
        user_profile["profileImage"] = data.profileImageName
    followsData = followErIng.query.filter_by(Follower_userId=userId).all()
    userFollows = [user.Following_userId for user in followsData]
    followsData = followErIng.query.filter_by(Following_userId=userId).all()
    userFollowing = [user.Follower_userId for user in followsData]
    
    
    if userFollows:
        user_profile['followers'] = len(userFollows)
        if session.get('userId') != "" and session.get('userId') in userFollows:
            isFollowed = True
        else:
            isFollowed = False
    else:
        user_profile['followers'] = 0
        isFollowed = False


    if userFollowing:
        user_profile['following'] = len(userFollowing)
    else:
        user_profile['following'] = 0
    

    followUnfollowToken = randomString(100)
    session['followUnfollowToken'] = followUnfollowToken

    allInOneToken = randomString(200)
    session['allInOneToken'] = allInOneToken

    return render_template(
        'profile.html',
        title="Profile",
        userInformation = user_information,
        userProfile = user_profile,
        isFollowed=isFollowed,
        isSelf = False,
        followUnfollowToken=followUnfollowToken,
        config=config
    )


@profile.route('/follow/<username>',methods=['POST'])
@loginRequired
@RequiredEmailVerfied
def follow_user(username):
    token = request.form.get('follow-unfollow-token')
    if not token:
        return redirect(url_for('.profile_specific',username=username))
    
    sessionToken = session.get("followUnfollowToken")
    if not sessionToken:
        return redirect(url_for('.profile_specific',username=username))
    
    if sessionToken != token:
        return redirect(url_for('.profile_specific',username=username))


    data = profile_db.query.filter_by(username=username).first()
    if not data:
        flash("User not found or account may be deleted!",{
            "signal" : "red",
            "id" : randomString(10)
        })
        return redirect(url_for('.profile_page'))

    toFollowUserId = data.userId
    FollowerUserId = session.get('userId')

    data = followErIng.query.filter_by(Follower_userId=toFollowUserId,Following_userId=FollowerUserId).first()
    if data:
        flash("Cannot follow anyone second time!",{
            "signal" : "red",
            "id" : randomString(10)
        })
        return redirect(url_for('.profile_specific',username=username))



    data = followErIng(
        Follower_userId =  toFollowUserId,
        Following_userId = FollowerUserId
    )
    db.session.add(data)
    db.session.commit()

    flash(f"Followed @{username} successfully!",{
        "signal" : "green",
        "id" : randomString(1)
    })
    return redirect(url_for('.profile_specific',username=username))



@profile.route('/unfollow/<username>',methods=['POST'])
@loginRequired
@RequiredEmailVerfied
def unfollow_user(username):
    token = request.form.get('follow-unfollow-token')
    if not token:
        return redirect(url_for('.profile_specific',username=username))
    
    sessionToken = session.get("followUnfollowToken")
    if not sessionToken:
        return redirect(url_for('.profile_specific',username=username))
    
    if sessionToken != token:
        return redirect(url_for('.profile_specific',username=username))

    data = profile_db.query.filter_by(username=username).first()
    if not data:
        flash("User not found or account may be deleted!",{
            "signal" : "red",
            "id" : randomString(10)
        })
        return redirect(url_for('.profile_page'))

    toUnFollowUserId = data.userId
    UnFollowerUserId = session.get('userId')

    data = followErIng.query.filter_by(
        Follower_userId =  toUnFollowUserId,
        Following_userId = UnFollowerUserId
    ).first()
    if not data:
        flash("Cannot unfollow anyone without following first!",{
            "signal" : "red",
            "id" : randomString(10)
        })
        return redirect(url_for('.profile_specific',username=username))


    data = followErIng.query.filter_by(
        Follower_userId =  toUnFollowUserId,
        Following_userId = UnFollowerUserId
    ).first()

    db.session.delete(data)
    db.session.commit()

    flash(f"Unfollowed @{username} successfully!",{
        "signal" : "green",
        "id" : randomString(1)
    })
    return redirect(url_for('.profile_specific',username=username))



@profile.route('/follow-er-ing/<username>')
@checkItPrimary
def followers_and_following(username):
    data = profile_db.query.filter_by(username=username).first()
    if not data:
        flash("User doesn't exists!",{
            'signal' : 'red',
            'id' : randomString(15)
        })
    
    following1 = followErIng.query.filter_by(Follower_userId=data.userId).all()
    followers1 = followErIng.query.filter_by(Following_userId=data.userId).all()

    followers = []
    following = []

    for follow in followers1:
        query = profile_db.query.filter_by(userId=follow.Follower_userId).first()
        following.append({
            'name' : query.name,
            'username' : query.username
        })
    
    for follow in following1:
        query = profile_db.query.filter_by(userId=follow.Following_userId).first()
        followers.append({
            'name' : query.name,
            'username' : query.username
        })


    return render_template(
        'follow-er-ing.html',
        followers=followers,
        following=following,
        config=config,
        title=f"@{username} : Followers and Following",
        username=username
    )