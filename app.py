from flask import Flask,flash,redirect,render_template,url_for,request,jsonify,session,send_file
from flaskext.mysql import MySQL
from io import BytesIO
app=Flask(__name__)
app.secret_key="27@Messanger"
app.config['MYSQL_DATABASE_HOST'] ='localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD']='sravs1721'
app.config['MYSQL_DATABASE_DB']='project'
app.config["SESSION_TYPE"] = "filesystem"
mysql=MySQL(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/home/<id1>')
def chat(id1):
    cursor=mysql.get_db().cursor()
    cursor.execute('SELECT following from friends where followers=%s',[id1])
    data=cursor.fetchall()
    return render_template('chat.html',id1=id1,data=data)


@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=="POST":
        id1=request.form['id1']
        First_Name=request.form['First_Name']
        Last_Name=request.form['Last_Name']
        Email=request.form['Email']
        Password=request.form['Password']
        cursor=mysql.get_db().cursor()
        cursor.execute("select id from users")
        data=cursor.fetchall()
        if (id1,) in data:
            flash("id already exist")
            return redirect(url_for('home'))
        cursor.execute('insert into users(id,Frist_Name,Last_Name,Email,Password) values(%s,%s,%s,%s,%s)',[id1,First_Name,Last_Name,Email,Password])
        mysql.get_db().commit()
        cursor.close()
        flash('details registered')
        return redirect(url_for('home'))
    return render_template('Signup.html')


@app.route('/login', methods =['GET','POST'])
def login():
    if session.get('user'):
        return redirect(url_for('chat',id1=session['user']))
    if request.method=="POST":
        user=request.form['id']
        password=request.form['Password']
        cursor=mysql.get_db().cursor()
        cursor.execute('SELECT id from USERS')
        users=cursor.fetchall()            
        cursor.execute('select password from Users where id=%s',[user])
        data=cursor.fetchone()
        cursor.close()
        if (user,) in users:
            if password==data[0]:
                session["user"]=user
                return redirect(url_for('chat',id1=user))
            else:
                flash('Invalid Password')
                return render_template('login.html')
        else:
            flash('Invalid id')
            return render_template('login.html')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session['user']=None
    return redirect(url_for('home'))


@app.route('/addcontact',methods=['GET','POST'])
def addcontact():
    cursor=mysql.get_db().cursor()
    cursor.execute('SELECT id  from users where id!=%s',[session.get('user')])
    data=cursor.fetchall()
    cursor.execute('select following from friends where followers=%s',[session.get('user')])
    new_data=cursor.fetchall()
    data=tuple([i for i in data if i  not in new_data])
    print(data)
    if request.method=="POST":
        Enter_Username=request.form['option']
        cursor=mysql.get_db().cursor()
        cursor.execute('insert into friends values(%s,%s)',[session.get('user'),Enter_Username])
        mysql.get_db().commit()
        return redirect(url_for('chat',id1=session.get('user')))
    return render_template('Addcontact.html',data=data)


@app.route('/profile',methods=["GET","POST"])
def profilepage():
    if request.method=="POST":
        Name=request.form['Name']
        About=request.form['About']
        cursor=mysql.get_db().cursor()
        cursor.execute('select name,about from profile')
        cursor.execute('insert into profile(name,about) values(%s,%s)',[Name,About])
        data=cursor.fetchone()
        cursor.close()
        return redirect(url_for('chat',id1=session['user']))
    return render_template('Profile.html')


@app.route('/settings')
def settings():
    return render_template('setting.html')


@app.route('/back')
def back():
    return redirect(url_for('login'))


@app.route('/message/<id1>',methods=['GET','POST'])
def message(id1):
    if session.get('user'):
        cursor=mysql.get_db().cursor()
        cursor.execute("SELECT message,date_format(created_at,'%%h:%%i %%p') as date from messenger where followers=%s and following=%s order by date",(session.get('user'),id1))
        sender=cursor.fetchall()
        cursor.execute("SELECT message,date_format(created_at,'%%h:%%i %%p') as date from messenger where followers=%s and following=%s order by date",(id1,session.get('user')))
        reciever=cursor.fetchall()
        cursor.execute('select filename from files where follower=%s and following=%s',(session.get('user'),id1))
        sender_files=cursor.fetchall()
        cursor.execute('select filename from files where follower=%s and following=%s',(id1,session.get('user')))
        reciever_files=cursor.fetchall()
        cursor.close()
        if request.method=='POST':
            if 'file' in request.files:
                file=request.files['file']
                filename=file.filename
                cursor=mysql.get_db().cursor()
                cursor.execute('INSERT INTO files (follower,following,filename,file) values(%s,%s,%s,%s)',(session.get('user'),id1,filename,file.read()))
                mysql.get_db().commit()
                cursor.execute('select filename from files where follower=%s and following=%s',(session.get('user'),id1))
                sender_files=cursor.fetchall()
                cursor.execute('select filename from files where follower=%s and following=%s',(id1,session.get('user')))
                reciever_files=cursor.fetchall()
                return render_template('Messenger.html',id1=id1,sender=sender,reciever=reciever,sender_files=sender_files,reciever_files=reciever_files)
            message=request.form['Message']
            cursor=mysql.get_db().cursor()
            cursor.execute('INSERT INTO messenger(followers,following,message) values(%s,%s,%s)',(session['user'],id1,message))
            mysql.get_db().commit()
            cursor.execute("SELECT message,date_format(created_at,'%%h:%%i %%p') as date from messenger where followers=%s and following=%s order by date",(session.get('user'),id1))
            sender=cursor.fetchall()
            cursor.execute("SELECT message,date_format(created_at,'%%h:%%i %%p') as date from messenger where followers=%s and following=%s order by date",(id1,session.get('user')))
            reciever=cursor.fetchall()
        return render_template('Messenger.html',id1=id1,sender=sender,reciever=reciever,sender_files=sender_files,reciever_files=reciever_files)
    return redirect(url_for('login'))

@app.route('/download/<filename>')
def download(filename):
    cursor=mysql.get_db().cursor()
    cursor.execute('SELECT file from files where filename=%s',[filename])
    data=cursor.fetchone()[0]
    return send_file(BytesIO(data),download_name=filename,as_attachment=True)
app.run()
