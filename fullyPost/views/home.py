from fullyPost import config
from flask.globals import session
from fullyPost.models import allPosts, followErIng, profile_db, postViewers, db, thumbBy
from fullyPost.helpers import RequiredEmailVerfied, loginRequired, randomString
from flask import Blueprint
from flask.templating import render_template

home = Blueprint('home',__name__)

@home.route('/')
@loginRequired
@RequiredEmailVerfied
def homepage():
    followings = followErIng.query.filter_by(Following_userId=session.get('userId')).all()
    allPostsToRender = []

    for following in followings:
        data = allPosts.query.filter_by(postById=following.Follower_userId).all()
        for post in data:
            postsV = postViewers.query.filter_by(
                viewerId=session.get('userId'),
                postId=post.postId
            ).first()
            if not postsV:
                saveData = postViewers(
                    viewerId=session.get('userId'),
                    postId=post.postId
                )
                db.session.add(saveData)
                post.views += 1
                db.session.commit()

            profileData = profile_db.query.filter_by(userId=post.postById).first()
            appendData = {
                "username" : profileData.username,
                "name" : profileData.name,
                "customImage" : profileData.customProfilePhoto,
                "_postId" : post.postId,
                "_postText" : post.postText,
                "_postBytesType" : post.postBytesType,
                "_postBytesName" : post.postBytesName,
                "_postBytesSize" : post.postBytesSize,
                "_time" : post.time,
                "_postDate" : post.postDate,
                "_compareDate" : post.compareDate,
                "_views" : post.views,
                "_thumbs" : post.thumbs,
                "_comments" : post.commentsCounts
            }
            if appendData["customImage"]:
                appendData['userImage']  = profileData.profileImageName
            allPostsToRender.append(appendData)
            
            

    for i in range(len(allPostsToRender)-1):
        for j in range(len(allPostsToRender)-1):
            if allPostsToRender[j]['_compareDate'] < allPostsToRender[j+1]['_compareDate']:
                temp_var = allPostsToRender[j+1]
                allPostsToRender[j+1] = allPostsToRender[j]
                allPostsToRender[j] = temp_var


    postToken = randomString(50)
    session['postToken'] = postToken

    thumbs = thumbBy.query.filter_by(userId=session.get('userId')).all()
    allThumbs = [post.postId for post in thumbs]

    session['allInOneToken'] = randomString(50)
    return render_template(
        "home.html",
        title="Home",
        posts=allPostsToRender,
        postToken=postToken,
        allThumbs=allThumbs,
        config=config
    )