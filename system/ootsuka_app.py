from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)




@app.route('/home')
def index():
    return render_template(
        'P001-2_home.html'
    )


# ログイン業務
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        studentID = request.form['studentID']
        password = request.form['password']
        user = User.query.filter_by(username=studentID).first()

        if user and user.check_password(password):
            login_user(user)
            session["user_name"] = user.username
            return redirect(url_for('dashboard', username=user.username))

        return "パスワードが違います", 401
    
     # GET の場合
    return render_template('P001-1_login.html')


# 利用者登録業務
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(username=request.form["studentID"])
        new_user.set_password(request.form["password"])
        db.session.add(new_user)
        db.session.commit()
        return render_template("userregistercomplate.html")

    return render_template('P003-1_userregister.html')

#エクスポート業務
@app.route('/export')
def show_db():
    users = db.session.query(User.username, User.password).all()
    return render_template("show_db.html", users=users)


if __name__ == "__main__":
    app.run(debug=True)
