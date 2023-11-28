from App.models.review import Review
from App.models.staff import Staff
from App.views.index import generate_random_contact_number
import click, pytest, sys
from flask import Flask, jsonify
from flask.cli import with_appcontext, AppGroup
import random
import randomname
from App.database import db, get_migrate
from App.main import create_app
from App.controllers import ( create_user, create_staff, get_staff, create_student, get_all_users_json, get_all_users, get_all_students, get_all_students_json )
from App.controllers import (addStudent, create_review, get_reviews, createKarma, get_all_karma, get_all_karma_json, upvoteReview, downvoteReview)
from App.views import (generate_random_contact_number)

# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def initialize():
  db.drop_all()
  db.create_all()
  admin= create_user('bob', 'boblast' , 'bobpass')
  for ID in  range(2, 50): 
    staff= create_staff(admin, 
          randomname.get_name(), 
          randomname.get_name(), 
          randomname.get_name(), 
          str(ID), 
          randomname.get_name() + '@schooling.com'
      )
    db.session.add(staff)
    db.session.commit()

  for ID in range(50, 150): 
      contact= generate_random_contact_number()
      student= create_student(admin, str(ID),
          randomname.get_name(), 
          randomname.get_name(), 
          randomname.get_name(),
          contact,
          random.choice(['Full-Time','Part-Time', 'Evening'])
      )
      db.session.add(student)
      db.session.commit()

  return jsonify({'message': 'Database initialized'}),201

'''
User Commands
'''

# Commands can be organized using groups

# create a group, it would be the first argument of the comand
# eg : flask user <command>
user_cli = AppGroup('user', help='User object commands') 

# Then define the command and any parameters and annotate it with the group (@)
@user_cli.command("create", help="Creates a user")
@click.argument("firstname", default="rob")
@click.argument("lastname", default="roblast")
@click.argument("password", default="robpass")
def create_user_command(firstname, lastname, password):
    create_user(firstname, lastname, password)
    print(f'{firstname} created!')

# this command will be : flask user create bob bobpass

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli) # add the group to the cli



student_cli = AppGroup('student', help='Student object commands') 
@student_cli.command("add", help="adds a student")
@click.argument("studentid", default="200")
@click.argument("firstname", default="rob")
@click.argument("lastname", default="williams")
@click.argument("contact", default=generate_random_contact_number)
@click.argument("studenttype", default="full-time")
@click.argument("yearofstudy", default=1)

def add_student_command(studentid, firstname, lastname, contact, studenttype, yearofstudy):
    addStudent(studentid, firstname, lastname, contact, studenttype, yearofstudy)
    print(f'student {firstname} {lastname} added!')


# Then define the command and any parameters and annotate it with the group (@)
@student_cli.command("list", help="Lists students in the database")
@click.argument("format", default="string")
def list_student_command(format):
    if format == 'string':
        print(get_all_students())
    else:
        print(get_all_students_json)

app.cli.add_command(student_cli) # add the group to the cli



#review
review_cli = AppGroup('review', help='Review object commands') 

# Then define the command and any parameters and annotate it with the group (@)
@review_cli.command("create", help="Creates a review")
@click.argument("staffid", default="45")
@click.argument("studentid", default="100")
@click.argument("is_positive", default=True)
@click.argument("comment", default="staff comment")
def create_review_command(staffid, studentid, is_positive, comment):
    review = create_review(staffid, studentid, is_positive, comment)
    print(f'staff {staffid} created review {review.ID}')

#upvotes
@review_cli.command("upvote", help="Upvotes a review")
@click.argument("reviewid", default="1")
@click.argument("staffid", default="40")
def upvote_review_command(reviewid, staffid):

    review = db.session.query(Review).get(reviewid)
    staff = db.session.query(Staff).filter_by(ID=staffid).first()
    
    upvoteReview(reviewid, staff)
    print(f'staff {staffid} upvoted review {reviewid}')

#downvotes
@review_cli.command("downvote", help="Downvotes a review")
@click.argument("reviewid", default="1")
@click.argument("staffid", default="41")
def downvote_review_command(reviewid, staffid):

    review = db.session.query(Review).get(reviewid)
    staff = db.session.query(Staff).filter_by(ID=staffid).first()
    
    downvoteReview(reviewid, staff)
    print(f'staff {staffid} downvoted review {reviewid}')


@review_cli.command("list", help="Lists reviews in the database")
@click.argument("format", default="string")
def list_review_command(format):
    if format == 'string':
        print(get_reviews())
    #else:
    #    print(get_all_users_json())

app.cli.add_command(review_cli) # add the group to the cli



#karma
karma_cli = AppGroup('karma', help='Karma object commands') 

# Then define the command and any parameters and annotate it with the group (@)
@karma_cli.command("create", help="Creates karma for a student")
@click.argument("studentid", default="200")
@click.argument("score", default=0.0)
@click.argument("rank", default=-99)
def create_karma_command(studentid, score, rank):
    karma = createKarma(studentid, score, rank)
    print(f'karma {karma.karmaID} created!')

# this command will be : flask karma create

@karma_cli.command("list", help="Lists karmas in the database")
@click.argument("format", default="string")
def list_karma_command(format):
    #if format == 'string':
    #    print(get_all_karma())
    #else:
    print(get_all_karma_json())

app.cli.add_command(karma_cli) # add the group to the cli

'''
Test Commands
'''

test = AppGroup('test', help='Testing commands') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))


app.cli.add_command(test)