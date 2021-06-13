from flask_sqlalchemy import SQLAlchemy
from fullyPost import fullyPost
from fullyPost.config import LENGTH
from flask_migrate import Migrate

db = SQLAlchemy(fullyPost)
migrate = Migrate(app=fullyPost,db=db)

@fullyPost.cli.command('create_all')
def create_all():
    '''run : db.create_all()'''
    with fullyPost.app_context():
        db.create_all(app=fullyPost)
    return True


class usersAuth(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(LENGTH['EMAIL']), nullable=False)
    password = db.Column(db.Text(), nullable=False)
    userId = db.Column(db.String(LENGTH['USER_ID']), nullable=False)
    lastPWDchanged = db.Column(db.Integer(), nullable=False)

    def __repr__(self):
        return f"id : {self.id}"


class profile_db(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    userId = db.Column(db.String(LENGTH['USER_ID']), nullable=False)
    name = db.Column(db.String(LENGTH['NAME']), nullable=False)
    description = db.Column(db.String(LENGTH['DESCRIPTION']), nullable=True)
    username = db.Column(db.String(LENGTH['USERNAME']), nullable=False)
    customProfilePhoto = db.Column(db.Boolean(), default=False)
    profileImageName = db.Column(db.Text(), nullable=True)
    totalPosts = db.Column(db.Integer(), nullable=False,default=0)
    isSuspended = db.Column(db.Boolean(), default=False)
    isEmailVerified = db.Column(db.Boolean(), default=False)
    isPubliclyVerified = db.Column(db.Boolean(), default=False)
    accountCreated = db.Column(db.Date(), nullable=False)
    accountCreatedTime = db.Column(db.Integer(), nullable=False)

    def __repr__(self):
        return f"id : {self.id}"


class verificationEmail(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    userId = db.Column(db.String(LENGTH['USER_ID']), nullable=False)
    verificationToken = db.Column(db.String(100), nullable=False)
    verificationSpecial = db.Column(db.String(80), nullable=False)
    genTime = db.Column(db.Integer(), nullable=False)

    def __repr__(self):
        return f"id : {self.id}"



class followErIng(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    Follower_userId = db.Column(db.String(LENGTH['USER_ID']), nullable=False)
    Following_userId = db.Column(db.String(LENGTH['USER_ID']), nullable=False)

    def __repr__(self):
        return f"id : {self.id}"


class allPosts(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    postById = db.Column(db.String(LENGTH['USER_ID']), nullable=False)
    postId = db.Column(db.String(LENGTH['POST_ID']), nullable=False)
    postText = db.Column(db.Text(), nullable=True)
    postBytesName = db.Column(db.Text(), nullable=True)
    postBytesType = db.Column(db.Text(), nullable=True)
    postBytesSize = db.Column(db.Float(), nullable=True)
    time = db.Column(db.Time(), nullable=False)
    postDate = db.Column(db.Date(), nullable=False)
    compareDate = db.Column(db.String(200), nullable=False)
    thumbs = db.Column(db.Integer(),default=0)
    commentsCounts = db.Column(db.Integer(),default=0)
    views = db.Column(db.Integer(),default=0)

    def __repr__(self):
        return f"id : {self.id}"


class postViewers(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    postId = db.Column(db.String(LENGTH['POST_ID']), nullable=False)
    viewerId = db.Column(db.String(LENGTH['USER_ID']), nullable=False)

    def __repr__(self):
        return f"id : {self.id}"


class thumbBy(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    postId = db.Column(db.String(LENGTH['POST_ID']), nullable=False)
    userId = db.Column(db.String(LENGTH['USER_ID']), nullable=False)

    def __repr__(self):
        return f"id : {self.id}"


class comments(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    postId = db.Column(db.String(LENGTH['POST_ID']), nullable=False)
    userId = db.Column(db.String(LENGTH['USER_ID']), nullable=False)
    comment = db.Column(db.Text() , nullable=False)
    commentTime = db.Column(db.Date() , nullable=False)

    def __repr__(self):
        return f"id : {self.id}"



class forgotDB(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(LENGTH['EMAIL']), nullable=False)
    userId = db.Column(db.String(LENGTH['USER_ID']), nullable=False)
    forgotToken = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"id : {self.id}"