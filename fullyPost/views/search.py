from flask import Blueprint
from flask.globals import request, session
from flask.helpers import url_for
from flask.templating import render_template
from werkzeug.utils import redirect
from fullyPost.helpers import loginRequired, randomString
from fullyPost.models import profile_db

search = Blueprint('search',__name__)

@search.route('/search')
@loginRequired
def search_page():
    search_query = request.args.get('search')
    search_token = request.args.get('strT')

    dataToRender = []
    resultCount = None

    if search_query == "":
        return redirect(url_for(".search_page"))
    else:
        if search_query:
            if(len(search_query.strip()) == 0):
                return redirect(url_for(".search_page"))

            if not search_token or not session.get('searchToken'):
                return redirect(url_for(".search_page"))

            if search_token != session.get('searchToken') and search_token != session.get('lastSearchToken'):
                return redirect(url_for(".search_page"))

            session['lastSearchToken'] = search_token
            
            while True:
                if len(search_query.replace("%","")) == 0:
                    resultCount = 0
                    break
                    
                DB_search_query = search_query.replace("%","")

                likeQuery = '{}%'.format(DB_search_query)
                data = profile_db.query.filter(profile_db.username.like(likeQuery)).all()

                for user in data:
                    if user.userId != session.get('userId'):
                        appendData = {
                            "name" : user.name,
                            "username" : user.username,
                            "customProfilePhoto" : user.customProfilePhoto,
                        }
                        if user.customProfilePhoto:
                            appendData['userImage'] = user.profileImageName
                        dataToRender.append(appendData)
                resultCount = len(dataToRender)
                break

    token = randomString(25)
    session['searchToken'] = token
    return render_template(
        'search.html',
        title="Search",
        searchToken=token,
        search_query=search_query,
        users=dataToRender,
        resultCount=resultCount
    )