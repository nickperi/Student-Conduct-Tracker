from App.models import Student
from App.database import db

#add student to the database
def addStudent(id, firstname, lastname, contact, studentType, yearofStudy):
	newStudent= Student(id, firstname, lastname, contact, studentType, yearofStudy)
		
	db.session.add(newStudent)
	db.session.commit()  # Commit to save the new student to the database
	return newStudent 

def search_student(studentID):
    student = db.session.query(Student).get(studentID)
    if student:
        return student
    return None

def get_all_students():
    return Student.query.all()
