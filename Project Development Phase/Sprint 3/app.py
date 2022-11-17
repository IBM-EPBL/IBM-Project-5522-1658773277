import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import datetime
import requests
import ibm_db
from flask import *
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=ea286ace-86c7-4d5b-8580-3fbfa46b1c66.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31505;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=rfq88127;PWD=2StNU0MRGzKdytAN", '', '')
app = Flask(__name__)

donor_vs_patient_compatability = {
    'O+':"('O+','O-')",
    'O-':"('O+','O-')",
    "A+":"('O+','A+','O-','A-')",
    "A-":"('O+','A+','O-','A-')",
    "B+":"('O+','B+','O-','B-')",
    "B-":"('O+','B+','O-','B-')",
    "AB+":"('O+','A+','B+','AB+','O-','A-','B-','AB-')",
    "AB+":"('O+','A+','B+','AB+','O-','A-','B-','AB-')",
}

patient_vs_donor_compatability = {
    "O+":"('O+','A+','B+','AB+','O-','A-','B-','AB-')",
    "O-":"('O+','A+','B+','AB+','O-','A-','B-','AB-')",
    "A+":"('A+','AB+','A-','AB-')",
    "A-":"('A+','AB+','A-','AB-')",
    "B+":"('B+','AB+','B-','AB-')",
    "B-":"('B+','AB+','B-','AB-')",
    "AB+":"('AB+','AB-')",
    "AB-":"('AB+','AB-')",

}


@app.route('/')
def home():
      return render_template('index.html')


@app.route('/sign_up')
def signUp():
      return render_template('sign_up.html')


@app.route('/sign_in')
def signIn():
      return render_template('sign_in.html')


@app.route('/request')
def requests():
      email = request.cookies.get('email')  
      name = request.cookies.get('name') 
      if email != None:
            resp = make_response(render_template('request.html',email = email, name = name, logged_in = True))
      else:
            resp = make_response(render_template('request.html',email = email, name = name, logged_in = False))
      return resp


@app.route('/donor_registration')
def donor_registration():
      email = request.cookies.get('email')  
      name = request.cookies.get('name')
      isDonor = False
      if email != None:
            sql = 'select * from donors where email='+'\''+email+'\''
            stmt = ibm_db.exec_immediate(conn, sql)
            dictionary = ibm_db.fetch_assoc(stmt)
            isDonor = False

            if dictionary != False:
                  isDonor = True 
      
      if isDonor:
            resp = make_response(render_template('donor_registration.html',email = email, name = name, isDonor = True, logged_in = True))
      elif email != None:
            resp = make_response(render_template('donor_registration.html',email = email, name = name, logged_in = True))
      else:
            resp = make_response(render_template('donor_registration.html',email = email, name = name, logged_in = False))
      return resp





      
@app.route('/add_user', methods=['POST', 'GET'])
def add_user():
    if request.method == 'POST':
        try:
            
            name = request.form['name']
            email = request.form['email']
            password = request.form['pass']
            
            sql = "select * from users where email = "+"'"+email+"'"
            stmt = ibm_db.exec_immediate(conn, sql)
            user = ibm_db.fetch_assoc(stmt)
            if user:
                  msg = "Account already exists"
            else:
                  sql = "insert into users values(?,?,?)"
                  param = name, email, password,
                  stmt = ibm_db.prepare(conn, sql)
                  ibm_db.execute(stmt, param)
                  msg = "You're successfully signed up!"

        except Exception as e:
            print("exception occured!",e)
            msg = e

        finally:
            return render_template('post_signup.html', msg = msg)

@app.route('/validate_user',methods = ['POST', 'GET'])
def validate_user():
   if request.method == 'GET':
      try:
            args = request.args
            email = args.get('email')
            password = args.get('password')
   
            sql = 'select * from users where email='+'\''+email+'\''
            stmt = ibm_db.exec_immediate(conn, sql)
            dictionary = ibm_db.fetch_assoc(stmt)
            print("executed")
            print(dictionary)
            if dictionary != False:
                        if(dictionary["PASSWORD"]== password):
                               print("success")
                               resp = make_response(render_template("post_signin.html"))  
                               resp.set_cookie('email', dictionary["EMAIL"]) 
                               resp.set_cookie('name',dictionary["NAME"])  
                               print("success")
                               return resp

                               
                        else:
                              return "Incorrect Password"
            else:
                  return "User does not exists"

      except Exception as e :
         print("error",e)
         return repr(e)


@app.route('/add_donor', methods=['POST', 'GET'])
def add_donor():
      if request.method == 'POST':
            try:
                  name = request.form['name']
                  email = request.form['email']
                  phone = request.form['phone']
                  bloodgroup = request.form['bloodgroup']
                  date = request.form['date']
                  address = request.form['address']
                  district = request.form['district']
                  state = request.form['state']
                  age = request.form['age']
 
                  sql = "insert into donors values(?,?,?,?,?,?,?,?,?)"
                  param = name, email,phone,bloodgroup,date,address,district,state,age,
                  stmt = ibm_db.prepare(conn, sql)
                  ibm_db.execute(stmt, param)
                  msg = "You're successfully registered as donor"
                  now =datetime.datetime.now()
                  now2 = now.strftime("%Y-%m-%d")
                  todays_fed_rate = random.randrange(20000,30000)
            
                  def sendgrid_email():
                        message = Mail(from_email='2k19cse091@kiot.ac.in',
                                          to_emails=email,
                                          subject='You Applied for Plasma Donation !!!' + now2,
                                          html_content="Thanks for Interest in Plasma Donation<br/>"\
                                                "Hi "+name+"<br><br><br>"
                                                "Your Reference number " + str(todays_fed_rate) +"<br>"\
                                                "Your Details are send to the Nearest plasma Donor centre From Your Location.<br><br>The Nearest Locations Showed in the Website<br><br>"\
                                                " Thanks!<br>"\
                                                "Plasma Donor Service")
                        sg = SendGridAPIClient("API")
                        response = sg.send(message)
                        print(response.status_code, response.body)
                  sendgrid_email()
                  if district=='chennai' or district=='Chennai' or district=='CHENNAI' or district=='madras' or district=='Madras' or district=='MADRAS':
                        return render_template('chennai.html', msg="Data saved successfuly")
                  elif district=='salem' or district =='Salem' or district == 'SALEM':
                        return render_template('salem.html', msg="Data saved successfuly")
                  elif district=='madurai' or district =='Madurai' or district == 'MADURAI':
                        return render_template('madurai.html', msg="Data saved successfuly")
                  elif district=='coimbatore' or district =='Coimbatore' or district == 'COIMBATORE':
                        return render_template('coimbatore.html', msg="Data saved successfuly")
                  elif district=='kanyakumari' or district =='Kanyakumari' or district == 'KANYAKUMARI':
                        return render_template('kanyakumari.html', msg="Data saved successfuly")
                  elif district=='trichy' or district =='Trichy' or district == 'TRICHY' or district=='thiruchirappalli' or district=='Thiruchirappalli' or district=='THIRUCHIRAPPALLI':
                        return render_template('trichy.html', msg="Data saved successfuly")
                  elif district=='erode' or district =='Erode' or district == 'ERODE':
                        return render_template('erode.html', msg="Data saved successfuly")
                  elif district=='namakkal' or district =='Namakkal' or district == 'NAMAKKAL':
                        return render_template('namakkal.html', msg="Data saved successfuly")
                  elif district=='dharmapuri' or district =='Dharmapuri' or district == 'DHARMAPURI':
                        return render_template('dharmapuri.html', msg="Data saved successfuly")
                  elif district=='karur' or district =='Karur' or district == 'KARUR':
                        return render_template('karur.html', msg="Data saved successfuly")
                  else:
                        return render_template('home.html', msg="Data saved successfuly")

            except Exception as e:
                  print("exception occured!",e)
                  msg = e
        

@app.route('/create_request', methods=['POST', 'GET'])
def create_request():
    if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            bloodgroup = request.form['bloodgroup']
            date = request.form['date']
            address = request.form['address']
            district = request.form['district']
            state = request.form['state']
            age = request.form['age']
 
            sql = "insert into requests values(?,?,?,?,?,?,?,?,?)"
            param = name, email,phone,bloodgroup,date,address,district,state,age,
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.execute(stmt, param)
            msg = "You're successfully made a request!"
            todays_fed_rate = random.randrange(20000,30000)
            now =datetime.datetime.now()
            now2 = now.strftime("%Y-%m-%d")
            def sendgrid_emails():
                  message = Mail(from_email='2k19cse091@kiot.ac.in',
                                    to_emails=email,
                                    subject='You Applied for Plasma Booking !!!' + now2,
                                    html_content="Thanks for Plasma Booking<br/>"\
                                    "Hi "+name+"<br><br> We Know Your Emergency<br>"
                                    "Your Reference number " + str(todays_fed_rate) +"<br><br><br>"\
                                    "Your Details are send to the Nearest plasma Donor centre From Your Location. For Furthur deatails You may contact the Plasma Donation Centre.<br>and the details provided in the website.<br><br><br><br>"\
                                    " Thanks!<br>"\
                                    "Plasma Donor Service")
                  sg = SendGridAPIClient("API")
                  response = sg.send(message)
                  print(response.status_code, response.body)


            sendgrid_emails()
            if district=='chennai' or district=='Chennai' or district=='CHENNAI' or district=='madras' or district=='Madras' or district=='MADRAS':
                  return render_template('chennai.html', msg="Data saved successfuly")
            elif district=='salem' or district =='Salem' or district == 'SALEM':
                  return render_template('salem.html', msg="Data saved successfuly")
            elif district=='madurai' or district =='Madurai' or district == 'MADURAI':
                  return render_template('madurai.html', msg="Data saved successfuly")
            elif district=='coimbatore' or district =='Coimbatore' or district == 'COIMBATORE':
                  return render_template('coimbatore.html', msg="Data saved successfuly")
            elif district=='kanyakumari' or district =='Kanyakumari' or district == 'KANYAKUMARI':
                  return render_template('kanyakumari.html', msg="Data saved successfuly")
            elif district=='trichy' or district =='Trichy' or district == 'TRICHY' or district=='thiruchirappalli' or district=='Thiruchirappalli' or district=='THIRUCHIRAPPALLI':
                  return render_template('trichy.html', msg="Data saved successfuly")
            elif district=='erode' or district =='Erode' or district == 'ERODE':
                  return render_template('erode.html', msg="Data saved successfuly")
            elif district=='namakkal' or district =='Namakkal' or district == 'NAMAKKAL':
                  return render_template('namakkal.html', msg="Data saved successfuly")
            elif district=='dharmapuri' or district =='Dharmapuri' or district == 'DHARMAPURI':
                  return render_template('dharmapuri.html', msg="Data saved successfuly")
            elif district=='karur' or district =='Karur' or district == 'KARUR':
                  return render_template('karur.html', msg="Data saved successfuly")
            else:
                  return render_template('home.html', msg="Data saved successfuly")


@app.route('/profile')
def profile():
      email = request.cookies.get('email')  
      name = request.cookies.get('name') 
      if email != None:
            sql = 'select * from requests where email='+'\''+email+'\''
            stmt = ibm_db.exec_immediate(conn, sql)
            requests = []
            dictionary = ibm_db.fetch_assoc(stmt)
            
            while dictionary != False:
                  # print(dictionary["ID"])
                  requests.append(dictionary)
                  dictionary = ibm_db.fetch_assoc(stmt)
            print(requests)

            sql = 'select * from donors where email='+'\''+email+'\''
            stmt = ibm_db.exec_immediate(conn, sql)
            dictionary = ibm_db.fetch_assoc(stmt)
            isDonor = False
            return render_template('profile.html',name =name, email = email, logged_in= True)
      else:
            return render_template('profile.html', logged_in= False)

@app.route('/logout')  
def logout():  
      
      email = request.cookies.get('email')
      if email != None:
            resp = make_response(render_template('logout.html',loggedin = True))
            resp.set_cookie('name', '', expires=0)
            resp.set_cookie('email', '', expires=0)
            
      else:
            resp = make_response(render_template('logout.html',loggedin = False))

      return resp




if __name__ == '__main__':
      app.run(debug=True)
