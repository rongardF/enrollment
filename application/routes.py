from application import app, api
from application.models import User, Course, Enrollment
from flask import render_template, request, json, jsonify, Response, flash, redirect, url_for, session
from application.forms import LoginForm, RegisterForm
from flask_restx import Resource # flas-restplus project is dead, flask-restx is dropin replacement by the same dev team
from application.course_list import course_list

@api.route("/api","/api/")
class GetAndPost(Resource):
    
    #GET ALL
    def get(self):
        return jsonify(User.objects.all())
    
    # POST to add new data
    def post(self):
        data=api.payload # api.payload comes form the POST call and object is defined and provided by Resource (no input parameter needed to function)
        user=User(user_id=data["user_id"],email=data["email"], first_name=data["first_name"], last_name=data["last_name"])
        user.set_password(data["password"])
        user.save()
        return jsonify(User.objects(user_id=data["user_id"]))
    
@api.route("/api/<idx>")
class GetUpdateDelete(Resource):
    
    # GET ONE
    def get(self, idx):
        return jsonify(User.objects(user_id=idx))
    
    #PUT
    def put(self, idx):
        data=api.payload
        # we can pass in all the data and the system will check and update only those values which have been modified
        User.objects(user_id=idx).update(**data) # unpack data and pass into update method
        return jsonify(User.objects(user_id=idx))
    
    # DELETE
    def delete(self, idx):
        User.objects(user_id=idx).delete()
        return jsonify("User is deleted")
    
# we can stack the URI routes on top of the rendering function - "/", "/index" and "/home" in this case will point to same index() function
@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html", index=True)

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("username"): # if already logged in then not None
        return redirect(url_for("index")) # redirect to home_page
    
    form=LoginForm() # create a Login form object
    if form.validate_on_submit(): # if validate fails then False will be returned and login.html will be rendered again
        email=form.email.data
        password=form.password.data
        
        user=User.objects(email=email).first() # get the user from the database directly
        if user and user.get_password(password): # if user exists and provided password matches
            flash(f"{user.first_name}, you are successfully logged in!", "success") # flash method generates a messages which will be displayed only 1 time (will go away upon refresh)
            session["user_id"]=user.user_id # start a user session - we will keep track of logged in user wherever they navigate on page
            session["username"]=user.first_name
            return redirect("index") # redirect user back to home page
        else:
            flash("Sorry, try again.", "danger")
    return render_template("login.html", form=form, title="Login", login=True)

@app.route("/logout")
def logout():
    session["user_id"]=False # two ways how we can remove an element from session
    session.pop("username", None)
    return redirect(url_for("index"))

@app.route("/courses")
@app.route("/courses/<term>")
def courses(term="Spring 2019"):
    # classes=Course.objects.all()   # retrieve courses data from database
    classes=Course.objects.order_by("+courseID") # retrieve data and sort in ascending order (- would do in descending order)
    
    return render_template("courses.html", courseData=classes, courses=True, term=term)

@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("username"): # cannot register anymore if logged in
        return redirect(url_for("index")) 
    
    form=RegisterForm()
    if form.validate_on_submit():
        user_id=User.objects.count()+1
        
        email=form.email.data
        password=form.password.data
        first_name=form.first_name.data
        last_name=form.last_name.data
        
        user=User(user_id=user_id, email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()
        flash("You are registered!", "success")
        return redirect(url_for("index"))
    return render_template("register.html", form=form, title="Register", register=True)


@app.route("/enrollment", methods=["GET", "POST"])
def enrollment(): # we can end up in this function from courses when enrolled (form action redirects) or user can come here directly using URL
    if not session.get("username"): # must be logged in
        return redirect(url_for("login")) 
    
    courseID=request.form.get("courseID") # need to use form (instead of args) here because it is POST method
    courseTitle=request.form.get("title")
    user_id=session.get("user_id")
    
    if courseID: # if coming from course->enroll (user is enrolling)
        if Enrollment.objects(user_id=user_id, courseID=courseID): # check that already enrolled (if exists then enrolled)
            flash(f"You are already enrolled to this course {courseTitle}!", "danger")
            return redirect(url_for("courses"))
        else: # not enrolled, create new entry in database
            Enrollment(user_id=user_id, courseID=courseID).save() # create and save at the same time - do not fogret teh save! otherwise it will not be put into database
            flash(f"You are enrolled to course {courseTitle}", "success")
            # dont't need to redirect as it will already go to enrollment page
    
    # get aggregate data about enrollment for the user from database - this code was created using mongoDB aggregate tool
    courses=course_list()
    
    return render_template("enrollment.html", enrollment=True, title="Enrollment", classes=classes)

# this is an example of creating an API using Flask - there are actually extensions which are better suited for this
# @app.route("/api/")
# @app.route("/api/<idx>")
# def api(idx=None):
#     if not idx:
#         jdata=courseData
#     else:
#         jdata=courseData[int(idx)]
#     return Response(json.dumps(jdata), mimetype="application/json")
    
@app.route("/user")
def user():
    # User(user_id=1, first_name="John", last_name="Doe", email="jdoe@gmail.com", password="qwerty").save()
    # User(user_id=2, first_name="Jane", last_name="Says", email="jane@gmail.com", password="qwerty").save()
    
    users=User.objects.all()
    return render_template("user.html", users=users)

