from flask import Flask,render_template
app = Flask(__name__)

if __name__ == "__main__":
    app.run(debug=True)
@app.route("/")
@app.route("/index")
def home() :
    return render_template('home.html')
@app.route("/about")
def about() :
    return render_template('about.html')
@app.route("/signLn")
def sigin() :
    return render_template('signIn.html')
@app.route("/signup")
def signup() :
    return render_template('signup.html')