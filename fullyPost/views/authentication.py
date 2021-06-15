from datetime import datetime
import threading
from fullyPost import config
from fullyPost.helpers import RedirectIfLoggedIn, checkItPrimary, deleteAccIfUnverified, deleteForgotLink, randomString
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
import time
import re
from fullyPost.models import db, forgotDB, profile_db, usersAuth, verificationEmail
import hashlib
import smtplib

auth = Blueprint('authentication',__name__)

@auth.route('/login',methods=['POST','GET'])
@RedirectIfLoggedIn
def login_auth():
    if request.method == "POST":
        csrf = request.form.get('csrf')
        email = request.form.get('email')
        password = request.form.get('password')

        if not session.get('time') or not csrf or not session.get('csrf') or not email or not password:
            flash("All fields are required !",{
                "id" : randomString(10),
                "signal" : "red"
            })
            return redirect(url_for('.login_auth'))

        
        if csrf != session.get('csrf'):
            flash("Something went wrong Try again !",{
                "id" : randomString(10),
                "signal" : "red"
            })
            return redirect(url_for('.login_auth'))
        
        
        if (time.time()-session.get('time')) > config.TIME_LIMITED_FOR_AUTHENTICATION:
            flash("Something went wrong Try again !",{
                "id" : randomString(10),
                "signal" : "red"
            })
            return redirect(url_for('.login_auth'))
        
        
        regexEmail = re.compile(config.REGEX_EMAIL)
        regexPassword = re.compile(config.REGEX_PASSWORD)

        if(len(email) > config.LENGTH['EMAIL']):
            flash(f"Error : Your email length is more than {config.LENGTH['EMAIL']} !")

        if( not regexEmail.match(email)):
            if(config.EMAIL == "ALL"):
                flash("Invalid email received!",{
                    "id" : randomString(10),
                    "signal" : "red"
                })
            else:
                flash("Invalid email received! Make sure you have entered gmail.",{
                    "id" : randomString(10),
                    "signal" : "red"
                })
            return redirect(url_for('.login_auth'))
        
        if( not regexPassword.match(password)):
            flash(f"Password must contains minimum {config.MINIMUM_PASSWORD_LENGTH} characters and maximum {config.MAXIMUM_PASSWORD_LENGTH} characters including uppercase, lowercase alphabets, digits and special symbols from [@$!#%*?&] and without spaces.",{
                "id" : randomString(10),
                "signal" : "red"
            })
            return redirect(url_for('.login_auth'))

        data = usersAuth.query.filter_by(email=email).first()
        
        if data:
            data = usersAuth.query.filter_by(email=email,password=hashlib.md5(str(config.PASSWORD_SALT+password).encode()).hexdigest()).first()
            if not data:
                flash("Incorrect Password for entered email",{
                    "id" : randomString(10),
                    "signal" : "red"
                })
                session['email'] = email
                return redirect(url_for('.login_auth'))

            _userId = data.userId
            lastPWDchanged = int(data.lastPWDchanged)

            browser = request.user_agent.browser
            platform = request.user_agent.platform
            TIME = datetime.now()

            server = smtplib.SMTP_SSL('smtp.gmail.com',465)
            server.login(config.MAIN_EMAIL, config.MAIN_PASSWORD)

            receiver = email

            message = f"""From: {config.MAIN_EMAIL}
To: {receiver}
MIME-Version: 1.0
Content-type: text/html
Subject: Account login - fullyPost

<h1>Account login</h1>
<p>Noticed a login to your account.</p>
<table>
    <tr style="padding: 2.5px;">
        <th style="padding: 2.5px;">browser</th>
        <th style="padding: 2.5px;">platform</th>
        <th style="padding: 2.5px;">time</th>
    </tr>
    <tr style="padding: 2.5px;">
        <td style="padding: 2.5px;">{browser}</td>
        <td style="padding: 2.5px;">{platform}</td>
        <td style="padding: 2.5px;">{TIME} UTC</td>
    </tr>
</table>
<div>
    <b>Ignore</b> this email if this was you.
    <br/><br/>
    else <b>change your account password</b> from your account
    <br/>
    all account will be loggedout automatically.
</div>
"""
            server.sendmail(config.MAIN_EMAIL,receiver, message)
            server.quit()


        else:
            _name = randomString(config.LENGTH['RANDOM_NAME'])
            _email = email
            _password = hashlib.md5(str(config.PASSWORD_SALT+password).encode()).hexdigest()
            _userId = randomString(config.LENGTH['USER_ID'])
            _username = randomString(config.LENGTH['RANDOM_USERNAME'])
            data = profile_db.query.filter_by(username=_username).first()
            
            while data:
                _username = randomString(10)
                data = profile_db.query.filter_by(username=_username).first()

            lastPWDchanged = int(time.time())

            data = usersAuth(
                email = _email,
                password = _password,
                userId = _userId,
                lastPWDchanged=lastPWDchanged
            )

            db.session.add(data)
            db.session.commit()

            data = profile_db(
                userId = _userId,
                name = _name,
                description = None,
                username = _username,
                accountCreated = datetime.now(),
                accountCreatedTime = time.time()
            )

            db.session.add(data)
            db.session.commit()
            
            verificationToken = randomString(50)
            specialToken = hashlib.md5(str(_userId+verificationToken+email).encode()).hexdigest()
            data = verificationEmail(
                userId= _userId,
                verificationToken=verificationToken,
                verificationSpecial = specialToken,
                genTime=time.time()
            )

            db.session.add(data)
            db.session.commit()

            x = threading.Thread(target=deleteAccIfUnverified,args=(_email,_userId))
            x.start()

            # Sending email verification to user
            
            server = smtplib.SMTP_SSL('smtp.gmail.com',465)
            server.login(config.MAIN_EMAIL, config.MAIN_PASSWORD)

            receiver = email

            message = f"""From: {config.MAIN_EMAIL}
To: {receiver}
MIME-Version: 1.0
Content-type: text/html
Subject: Email verification - fullyPost

<h1>Email verification</h1>
<p><b>Hey, {receiver} you need to verify your email to use fullyPost.</b></p>
<p>Click below link to verify your email.</p>

<a href="{request.host_url}verification/{email}/{verificationToken}/{specialToken}">Click here to verify</a>
<br/><br/>
<b>OR</b>
<br/>
<br/>
Copy below link and open in your browser
{request.host_url}verification/{email}/{verificationToken}/{specialToken}

<p>
Above link only will expire after 20 minutes.
</p>

<p>
This email is sent to <b><i>{receiver}</i></b>.
<br/>
Ignore if you are not.
</p>

<p>
After 20 minutes your unverified account automatically deleted if not verified.
</p>
"""
            server.sendmail(config.MAIN_EMAIL,receiver, message)
            server.quit()


        session.permanent = True
        session['lastChanged'] = int(lastPWDchanged)
        session['userId'] = _userId

        
        return redirect(url_for('home.homepage'))


    csrf = randomString(50)
    session['csrf'] = csrf
    session['time'] = time.time()
    return render_template('authentication.html',title="Authentication",csrf=csrf,config=config)




@auth.route('/verification/<email>/<verification_token>/<special_token>')
@checkItPrimary
def email_verification(verification_token, email, special_token):
    query = usersAuth.query.filter_by(email=email).first()
    
    if not query:
        flash("Broken link!",{
            "id" : randomString(10),
            "signal" : "red"
        })
        return redirect(url_for('home.homepage'))
    
    query = profile_db.query.filter_by(userId=query.userId).first()
    if query.isEmailVerified:
        flash("Email is already verified!",{
            "id" : randomString(10),
            "signal" : "blue"
        })
        return redirect(url_for('home.homepage'))

    query1 = verificationEmail.query.filter_by(
        userId=query.userId,
        verificationToken = verification_token,
        verificationSpecial= special_token
    ).first()

    if not query or not query1:
        flash("Broken link!",{
            "id" : randomString(10),
            "signal" : "red"
        })
        return redirect(url_for('home.homepage'))

    query.isEmailVerified = True
    db.session.commit()

    db.session.delete(query1)
    db.session.commit()

    return render_template(
        'verified.html',
        title="Verified"
    )




@auth.route('/forgot',methods=['GET','POST'])
@checkItPrimary
@RedirectIfLoggedIn
def forgot_password():
    if request.method == "POST":
        sessionToken = session.get('forgotPasswordToken')
        formToken = request.form.get('forgotToken')
        email = request.form.get('email')

        if not sessionToken or not formToken or sessionToken != formToken or not email or not re.compile(config.REGEX_EMAIL).match(email):
            flash("Something went wrong! try again.",{
                "id" : randomString(15),
                "signal" : "red"
            })
            return redirect(url_for('.forgot_password'))
    
        query = usersAuth.query.filter_by(email=email).first()

        if not query:
            flash("Reset Password link sent to the email.",{
                'signal' : 'green',
                'id' : randomString(15)
            })
            return redirect(url_for('.forgot_password'))

        USERID = query.userId
        EMAIL = email
        query = forgotDB.query.filter_by(email=EMAIL,userId=USERID).first()
        if query:
            db.session.delete(query)
            db.session.commit()
        
        TOKEN = randomString(67)

        data = forgotDB(
            email=EMAIL,
            userId=USERID,
            forgotToken=TOKEN
        )

        db.session.add(data)
        db.session.commit()

        server = smtplib.SMTP_SSL('smtp.gmail.com',465)
        server.login(config.MAIN_EMAIL, config.MAIN_PASSWORD)

        receiver = email

        message = f"""From: {config.MAIN_EMAIL}
To: {receiver}
MIME-Version: 1.0
Content-type: text/html
Subject: Forgot Password - fullyPost

<h1>Forgot Password</h1>
<div>
    Reset Password link : <a href="{request.host_url}{email}/{TOKEN}/{hashlib.md5(str(email+TOKEN+TOKEN+email).encode()).hexdigest()}">Click here</a>
    <br/><br/>or<br/><br/>
    Copy below link<br/>
    {request.host_url}reset/{email}/{TOKEN}/{hashlib.md5(str(email+TOKEN+TOKEN+email).encode()).hexdigest()}
</div>
<br/><br/>
<div>
    If you don't have requested to reset password do not click on it.
</div>
<br/>
<div>
    Above link will expire in next 10 minutes.
</div>
"""
        server.sendmail(config.MAIN_EMAIL,receiver, message)
        server.quit()

        x = threading.Thread(target=deleteForgotLink,args=(EMAIL,USERID))
        x.start()

        flash("Reset Password link sent to the email.",{
            'signal' : 'green',
            'id' : randomString(15)
        })
        return redirect(url_for('.forgot_password'))

    session['forgotPasswordToken'] = randomString(50)
    return render_template('forgot.html',title="Forgot password",pattern=config.REGEX_EMAIL)



@auth.route('/reset/<email>/<token>/<mixer>/',methods=['GET','POST'])
@checkItPrimary
def reset_password(email,token,mixer):
    mixerAnother= hashlib.md5(str(email+token+token+email).encode()).hexdigest()
    if mixer != mixerAnother:
        flash("Broken link to reset password!",{
            'signal' : 'red',
            'id' : randomString(15)
        })
        return redirect(url_for('.login_auth'))
        
    query = forgotDB.query.filter_by(email=email,forgotToken=token).first()

    if not query:
        flash("Broken link to reset password!",{
            'signal' : 'red',
            'id' : randomString(15)
        })
        return redirect(url_for('.login_auth'))
    
    if request.method == "POST":
        passwordReset = request.form.get('resetPasswordToken')
        newPwd = request.form.get('nP')
        newPwdCnfrm = request.form.get('nPC')

        if not passwordReset or not session.get('passwordResetToken') or session.get('passwordResetToken') != passwordReset or not newPwd or not newPwdCnfrm or not re.compile(config.REGEX_PASSWORD).match(newPwd) or not re.compile(config.REGEX_PASSWORD).match(newPwdCnfrm):
            flash(f"Password must contains minimum {config.MINIMUM_PASSWORD_LENGTH} characters and maximum {config.MAXIMUM_PASSWORD_LENGTH} characters including uppercase, lowercase alphabets, digits and special symbols from [@$!#%*?&] and without spaces.",{
                "id" : randomString(10),
                "signal" : "red"
            })
            return redirect(url_for('.reset_password',email=email,token=token,mixer=mixer))

        if newPwd != newPwdCnfrm:
            flash(f"Password must match with another Password.",{
                "id" : randomString(10),
                "signal" : "red"
            })
            return redirect(url_for('.reset_password',email=email,token=token,mixer=mixer))
        
        query = usersAuth.query.filter_by(email=email).first()
        password = hashlib.md5(str(config.PASSWORD_SALT+newPwd).encode()).hexdigest()
        if query.password == password:
            flash(f"Password should not match with last password!",{
                "id" : randomString(10),
                "signal" : "red"
            })
            return redirect(url_for('.reset_password',email=email,token=token,mixer=mixer))
        
        query.password = password
        db.session.commit()

        query = forgotDB.query.filter_by(email=email).first()
        db.session.delete(query)
        db.session.commit()
        
        flash("Password successfully changed!",{
            'id' : randomString(15),
            'signal' : 'green'
        })
        return redirect(url_for('.login_auth'))

    session['passwordResetToken'] = randomString(80)
    return render_template(
        'resetPassword.html',
        title="Reset Password",
        pattern=config.REGEX_PASSWORD,
        email=email,
        token=token,
        mixer=mixer
    )