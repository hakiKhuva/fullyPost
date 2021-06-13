from datetime import datetime
import os
import threading
from PIL import Image, ImageFilter
from fullyPost import config
from fullyPost.models import allPosts, comments, db, postViewers, profile_db, thumbBy
from flask.globals import session
from fullyPost.helpers import RequiredEmailVerfied, deletePost, loginRequired, randomString
from flask import Blueprint , request, Markup, render_template, abort
from flask.helpers import flash, make_response, send_file, url_for
from werkzeug.utils import redirect
import magic
import shutil

posts = Blueprint('posts',__name__)


@posts.route('/newPost',methods=['POST'])
@loginRequired
@RequiredEmailVerfied
def new_post():
    formToken = request.form.get("allInOneToken")
    sessionToken = session.get("allInOneToken")
    if not formToken or not sessionToken or formToken != sessionToken:
        flash("Something went wrong when posting your post try again !",{
            "signal" : "red",
            "id" : randomString(15)
        })
        return redirect(url_for("profile.profile_page"))
    
    textPost = str(Markup(request.form.get('text-post')))
    wannaAttachFile = request.form.get('wanna-attach-files')
    fileToPost = request.files.get('file-to-post')

    FileData = fileToPost.stream.read()

    if(not textPost and not wannaAttachFile):
        flash("You need to post atleast one Text or a file !",{
            "signal":"red",
            "id" : randomString(15)
        })
        return redirect(url_for("profile.profile_page"))

    if(wannaAttachFile == "on" and not fileToPost):
        flash("You have selected to post file but file is not selected !",{
            "signal" : "red",
            "id" : randomString(15)
        })
        return redirect(url_for("profile.profile_page"))

    if(len(textPost) > config.POST_TEXT_MAX_CHAR):
        flash(f"Post Text can maximum contains {config.POST_TEXT_MAX_CHAR} characters !",{
            "signal":"red",
            "id" : randomString(15)
        })
        return redirect(url_for("profile.profile_page"))

    FileDataContentType = None
    FileDataLength = None
    FileDataName = None

    if wannaAttachFile == "on":
        if len(FileData)/1024 > config.POST_FILE_SIZE_KB:
            flash(f"You can post file with maximum size {config.POST_FILE_SIZE_KB/1024} MB !",{
                "signal":"red",
                "id" : randomString(15)
            })
            return redirect(url_for("profile.profile_page"))

        FileDataContentType = magic.from_buffer(FileData,mime=True)
        FileDataLength = len(FileData)
        FileDataName = fileToPost.filename

    if(not os.path.exists(os.path.join(config.STORE_UPLOAD_FILES_FOLDER_PATH,session.get('userId')))):
        os.mkdir(os.path.join(config.STORE_UPLOAD_FILES_FOLDER_PATH, session.get('userId')))

    postId = randomString(30)
    if wannaAttachFile == "on":
        POST_ID_FOLDER = os.path.join(config.STORE_UPLOAD_FILES_FOLDER_PATH, session.get('userId'),postId)
        os.mkdir(POST_ID_FOLDER)
        open(os.path.join(config.STORE_UPLOAD_FILES_FOLDER_PATH,session.get('userId'),postId,FileDataName),'wb').write(FileData)
    
        if FileDataContentType[0:5] == "image":
            im = Image.open(os.path.join(config.STORE_UPLOAD_FILES_FOLDER_PATH,session.get('userId'),postId,FileDataName))
            im = im.filter(ImageFilter.BLUR())
            im = im.filter(ImageFilter.BLUR())
            im = im.filter(ImageFilter.BLUR())
            im = im.filter(ImageFilter.BLUR())
            im.save(os.path.join(config.STORE_UPLOAD_FILES_FOLDER_PATH,session.get('userId'),postId,f"blur--{FileDataName}"))

    data = allPosts(
        postById = session.get('userId'),
        postId = postId,
        postText = textPost,
        postBytesName = FileDataName,
        postBytesType = FileDataContentType,
        postBytesSize = FileDataLength,
        time= datetime.time(datetime.now()),
        postDate = datetime.now(),
        compareDate= datetime.now()
    )

    db.session.add(data)
    db.session.commit()

    data = profile_db.query.filter_by(userId=session.get('userId')).first()
    data.totalPosts += 1
    db.session.commit()

    x = threading.Thread(target=deletePost,args=(postId,))
    x.start()

    flash("Your post successfully posted !",{
        "signal":"green",
        "id" : randomString(15)
    })
    return redirect(url_for("profile.profile_page"))


@posts.route('/download/<username>/<post_id>')
@loginRequired
@RequiredEmailVerfied
def download_post(post_id,username):
    if post_id == "%" or username == "" or not post_id or not username:
        return ""
    data = profile_db.query.filter_by(username=username).first()
    if not data:
        return ""
    post = allPosts.query.filter_by(postId=post_id).first()
    if not post:
        return ""

    if post.postBytesType[0:5] == "image" and request.args.get('blur') and str(request.args.get('blur')).lower() == "true":
        file = make_response(send_file(os.path.join(config.FILES_UPLOAD_FOLDER_PATH,data.userId,post.postId,f'blur--{post.postBytesName}')))
        file.headers['Content-Disposition'] = f"attachment; filename={post.postBytesName}"
    else:
        file = make_response(send_file(os.path.join(config.FILES_UPLOAD_FOLDER_PATH,data.userId,post.postId,post.postBytesName)))
        file.headers['Content-Disposition'] = f"attachment; filename={post.postBytesName}"
    
    file.headers['Cache-Control'] = config.MAX_CACHE_CONTROL
    return file
    


@posts.route('/posts')
@loginRequired
@RequiredEmailVerfied
def all_posts_self():
    data = profile_db.query.filter_by(userId=session.get('userId')).first()
    return redirect(url_for('.all_posts',username=data.username))


@posts.route('/posts/<username>')
@loginRequired
@RequiredEmailVerfied
def all_posts(username):
    data = profile_db.query.filter_by(username=username).first()
    if not data:
        flash("User doesn't exists !",{
            "signal" : "red",
            "id" : randomString(15)
        })
        return redirect(url_for('profile.profile_page'))
    
    isSelf = data.userId == session.get('userId')
    profileData = {
        "username" : data.username,
        "name" : data.name,
        "customImage" : data.customProfilePhoto,
        "joinDate" : data.accountCreated,
        "userId" : data.userId
    }
    if profileData["customImage"]:
        profileData['userImage'] = data.profileImageName
    data = allPosts.query.filter_by(postById=data.userId).all()
    allPostsToRender = []
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
        allPostsToRender.append({
            "_postId" : post.postId,
            "_postText" : post.postText,
            "_postBytesType" : post.postBytesType,
            "_postBytesName" : post.postBytesName,
            "_postBytesSize" : post.postBytesSize,
            "_time" : post.time,
            "_postDate" : post.postDate,
            "_compareDate" : post.compareDate,
            "_thumbs" : post.thumbs,
            "_views" : post.views,
            "_comments" : post.commentsCounts
        })

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
    
    return render_template(
        'posts.html',
        title=f"@{username} : Posts",
        userProfile=profileData,
        posts=allPostsToRender,
        postToken=postToken,
        isSelf=isSelf,
        allThumbs=allThumbs
    )


@posts.route('/remove-post',methods=['POST'])
@loginRequired
@RequiredEmailVerfied
def remove_post():
    post_id = request.form.get('postId')
    username = request.form.get('username')
    postToken = request.form.get('postToken')

    if not post_id or not username or not postToken or not session.get('postToken'):
        flash("Something went wrong tryagain later!",{
            'signal' : 'red',
            'id' : randomString(15)
        })
        return redirect(url_for('.all_posts',username=username))

    post = allPosts.query.filter_by(
        postId=post_id,
        postById=session.get('userId')
    ).first()

    if not post:
        flash("Post not found !",{
            'signal' : 'red',
            'id' : randomString(15)
        })
        return redirect(url_for('.all_posts',username=username))
    
    query = postViewers.query.filter_by(postId=post.postId).all()
    for q in query:
        db.session.delete(q)
        db.session.commit()
    query = thumbBy.query.filter_by(postId=post.postId).all()
    for q in query:
        db.session.delete(q)
        db.session.commit()
    query = comments.query.filter_by(postId=post.postId).all()
    for q in query:
        db.session.delete(q)
        db.session.commit()

    db.session.delete(post)
    db.session.commit()

    if os.path.exists(os.path.join(config.STORE_UPLOAD_FILES_FOLDER_PATH,post.postById,post.postId)):
        shutil.rmtree(os.path.join(config.STORE_UPLOAD_FILES_FOLDER_PATH,post.postById,post.postId))

    data = profile_db.query.filter_by(username=username,userId=session.get('userId')).first()
    if not data:
        flash("Something went wrong tryagain later!",{
            'signal' : 'red',
            'id' : randomString(15)
        })
        return redirect(url_for('.all_posts',username=username))

    data.totalPosts -= 1
    db.session.commit()

    flash("Post deleted successfully !",{
            'signal' : 'green',
            'id' : randomString(15)
        })
    return redirect(url_for('.all_posts',username=username))


@posts.route('/post/<username>/<post_id>')
@loginRequired
@RequiredEmailVerfied
def specific_post(username,post_id):
    data = profile_db.query.filter_by(username=username).first()
    if not data:
        flash("User doesn't exists !",{
            'signal' : 'red',
            'id' : randomString(15)
        })
        return redirect(url_for('home.homepage'))

    userProfile = {
        "username" : data.username,
        "name" : data.name,
        "customImage" : data.customProfilePhoto
    }
    if userProfile['customImage']:
        userProfile['userImage'] = data.profileImageName

    data = allPosts.query.filter_by(
        postId=post_id,
        postById=data.userId
    ).first()

    if not data:
        flash("Post not found !",{
            'signal' : 'red',
            'id' : randomString(15)
        })
        return redirect(url_for('home.homepage'))

    postsV = postViewers.query.filter_by(
        viewerId=session.get('userId'),
        postId=data.postId
    ).first()
    if not postsV:
        saveData = postViewers(
            viewerId=session.get('userId'),
            postId=data.postId
        )
        db.session.add(saveData)
        
        data.views += 1
        db.session.commit()

    postToken = randomString(15)
    session['postToken'] = postToken

    ThumbDone = thumbBy.query.filter_by(userId=session.get('userId'),postId=post_id).first()
    ThumbsByUsers = thumbBy.query.filter_by(postId=post_id).all()
    ThumbsByUsers = [ profile_db.query.filter_by(userId=user.userId).first() for user in ThumbsByUsers]

    Comments = comments.query.filter_by(postId=post_id).all()
    FinalComments = []
    for cmnt in Comments:
        profile = profile_db.query.filter_by(userId=cmnt.userId).first()
        FinalComments.append({
            'username' : profile.username,
            'comment' : cmnt.comment,
            'time' : cmnt.commentTime
        })

    if len(FinalComments) > 1:
        FinalComments.reverse()

    if len(ThumbsByUsers) > 1:
        ThumbsByUsers.reverse()

    return render_template(
        'post.html',
        user=userProfile,
        post= data,
        postToken=postToken,
        ThumbDone=ThumbDone,
        ThumbsByUsers=ThumbsByUsers,
        Comments=FinalComments,
        title=f"Post : {username}"
    )



@posts.route('/thumbs/<username>/<post_id>')
@RequiredEmailVerfied
def all_thumbs(username,post_id):
    data = profile_db.query.filter_by(username=username).first()
    if not data:
        abort(404)

    data = allPosts.query.filter_by(
        postId=post_id,
        postById=data.userId
    ).first()

    if not data:
        abort(404)

    ThumbsByUsers = thumbBy.query.filter_by(postId=post_id).all()
    ThumbsByUsers = [ profile_db.query.filter_by(userId=user.userId).first() for user in ThumbsByUsers]

    if len(ThumbsByUsers) > 1:
        ThumbsByUsers.reverse()

    returnData = []
    for user in ThumbsByUsers:
        returnData.append({
            'username' : user.username,
            'name' : user.name
        })

    return {
        "status" : "ok",
        "thumbs" : returnData,
    }



@posts.route('/thumb',methods=['POST'])
@loginRequired
@RequiredEmailVerfied
def thumb():
    if not request.json:
        abort(403)

    redirection = request.json.get('redirection')
    postId = request.json.get('postId')
    postToken = request.json.get('postToken')

    if not redirection or not postId or not postToken or not session.get('postToken') or postToken != session.get('postToken'):
        abort(403)
    
    data = allPosts.query.filter_by(postId=postId).first()

    if not data:
        return {
            'status' : 'error',
            'error' : 'Post doesn\'t exists !',
            'id' : randomString(15),
        }

    thumbs = thumbBy.query.filter_by(
        postId=postId,
        userId=session.get('userId')
    ).first()

    if thumbs:
        db.session.delete(thumbs)
        db.session.commit()
        data.thumbs = data.thumbs - 1
        db.session.commit()
        
        return {
            'status' : 'ok',
            'total' : data.thumbs,
            'isUserLike' : False,
        }

    thumbs = thumbBy(
        postId=postId,
        userId=session.get('userId')
    )
    db.session.add(thumbs)
    db.session.commit()
    data.thumbs = data.thumbs + 1
    db.session.commit()

    return {
        'status' : 'ok',
        'total' : data.thumbs,
        'isUserLike' : True,
    }


@posts.route('/comment',methods=['POST'])
@loginRequired
@RequiredEmailVerfied
def post_comment():
    postId = request.form.get('postId')
    comment = request.form.get('comment')
    postToken = request.form.get('postToken')
    redirection = request.form.get('redirection')

    if not session.get('postToken') or not postToken or postToken != session.get('postToken') or not redirection or not comment or not postId:
        flash("You need to enter text in comment-box !",{
            'signal' : 'red',
            'id' : randomString(20)
        })
        if redirection:
            return redirect(redirection)
        else:
            return redirect(url_for('home.homepage'))


    data = allPosts.query.filter_by(postId=postId).first()
    if not data:
        flash("Post not found !",{
            'signal' : 'red',
            'id' : randomString(20)
        })
        return redirect(redirection)

    if len(comment) > config.COMMENT_LENGTH:
        flash(f"You can only enter maximum {config.COMMENT_LENGTH} characters in a comment !",{
            'signal' : 'red',
            'id' : randomString(20)
        })
        return redirect(redirection)

    data.commentsCounts += 1
    db.session.commit()

    data = comments(
        postId = data.postId,
        userId = session.get('userId'),
        comment = comment,
        commentTime = datetime.now()
    )
    db.session.add(data)
    db.session.commit()

    flash("Comment posted successfully !",{
        'signal' : 'green',
        'id' : randomString(15)
    })
    return redirect(redirection)