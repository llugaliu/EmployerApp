from flask import Flask,redirect,render_template,session,url_for,flash,request
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import re
app = Flask(__name__)

app.secret_key = "hfkdsafs"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emplo.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(150),nullable=False)
    email = db.Column(db.String(150),unique=True,nullable=False)
    password = db.Column(db.String(150),nullable=False)

    def __init__(self,username,email,password):
        self.username = username
        self.email = email
        self.password = password
    def __repr__(self):
        return "<User %s>" % self.email
    
class Employer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    address = db.Column(db.String(150), nullable=False)
    position = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer(),nullable=False)

    def __init__(self, name, address, position,user_id):
        self.name = name
        self.address = address
        self.position = position
        self.user_id = user_id

    def __repr__(self):
        return "<Employer %s>" % self.name
@app.route('/')
def homepage():
   return render_template('homepage.html')
@app.route('/employer',methods=['GET','POST'])
def employer():
    if 'is_logged_in' in session:      
        employers = Employer.query.all()         
        if request.method == "POST":
            if not_empty(['name','address','position']):
                name = request.form['name']
                address = request.form['address']
                position = request.form['position']
                employers = Employer(name,address,position,session.get('user_id'))
                db.session.add(employers)
                db.session.commit()
                flash('employer was created successfuly')
                return redirect(url_for('employer'))
            else:
                flash('All fields required')
        
        return render_template('employer.html',employers=employers)
    else:
        return redirect(url_for('login'))
    return render_template('employer.html')


@app.route('/employer/<int:employer_id>/delete')
def delete_employer(employer_id):
    employer = Employer.query.get_or_404(employer_id)
    db.session.delete(employer)
    db.session.commit()
    flash('Employer was deleted successfuly!.')
    return redirect(url_for('employer'))

@app.route("/edit<int:id>",methods = ['GET','POST'])
def edit_employer(id):
    employer = Employer.query.get_or_404(id)
    if request.method == "POST":
        employer.name = request.form['name']
        employer.address = request.form['address']
        employer.postion = request.form['position']
        
        db.session.commit()
        return redirect(url_for('employer'))
    
    return render_template('edit.html',employer=employer)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        if not_empty([email,password]):
            if is_email(email):
                user = User.query.filter_by(email=email).first()
                if user:
                    if bcrypt.check_password_hash(user.password,password):
                        session['is_logged_in']=True
                        session['email'] = email
                        session['user_id'] = user.id
                        session['username'] = user.username

                        return redirect(url_for('employer'))
                        
                    else:
                        flash('password is incorrect')

                else:
                    flash('User doesnt exist')
             
            else:
                flash('email is not valid')
        else:
            flash('all fields are required!')
        return redirect(url_for('login'))  
    else:
        if 'is__logged_in' in session:
            return redirect(url_for('employer'))   
        return render_template('login.html')

   

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == "POST":
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        password1 = request.form['confirm_password']
        if not_empty([username,email,password,password1]):
            if is_email(email):
                if password_match(password,password1):
                    password_hash = bcrypt.generate_password_hash(password)
                    user = User(username=username,email=email,password=password_hash)
                    db.session.add(user)
                    db.session.commit()

                    session['is_logged_in']=True
                    session['email'] = email
                    session['username'] = username
                    
                    return redirect(url_for('login'))

                else:
                    flash('password doesnt match')
            else:
                flash('email is not valid')
        else:
            flash('all fields are required!')
        return redirect(url_for('register'))
        

    return render_template('register.html')


@app.route('/logout')
def logout():
    session['username'] = ""
    session['email'] = ""
    session['is_logged_in'] = False
    return redirect(url_for('login'))

def not_empty(form_fields):
    for field in form_fields:
        if len(field) == 0 :
            return False
    return True
        
def is_email(email):
    return re.search("[\w\.\_\-]\@[\w\-]+\.[a-z]{2,5}",email) !=None
def password_match(password,password1):
    return password == password1 




if __name__ == "__main__":
    app.run(debug=True)
