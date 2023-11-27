from App.models import Karma, Student
from App.database import db

def get_karma_by_id(karma_id):
    return db.session.query(Karma).get(karma_id)

#associate the karma subject to the student observer
def createKarma(studentID, score, rank):

    student = db.session.query(Student).get(studentID)

    if student:
        karma = Karma(studentID, score, rank)
        karma = calculate_student_karma(student)
        db.session.add(karma)
        db.session.commit()
        return karma
    return None

def get_all_karma():
    karma_list = Karma.query.all()
    return karma_list

def get_all_karma_json():
    karma_list = Karma.query.all()

    karma_list = [karma.to_json() for karma in karma_list]
    return karma_list

def calculate_student_karma(student):
    good_karma = 0
    bad_karma = 0

    for review in student.reviews:
        if review.isPositive:
            good_karma += review.upvotes
            bad_karma += review.downvotes
        else:
            bad_karma += review.upvotes
            good_karma += review.downvotes

    karma_score = good_karma - bad_karma

    if student is not None:
        karma = Karma(studentID=student.ID, score=karma_score, rank=-99)
        db.session.add(karma)
        db.session.flush() 
        student.score = karma.score
        db.session.commit()
        return karma
    
    return None

#notify
def update_student_scores():
    students = Student.query.all()

    if students:
        for student in students:
            calculate_student_karma(student)


def update_student_karma_rankings():
    students_with_karma = db.session.query(Student, Karma)\
        .join(Karma, Student.karmaID == Karma.karmaID)\
        .order_by(db.desc(Karma.score))\
        .all()

    rank = 1
    prev_score = None

    for student, karma in students_with_karma:
        if prev_score is None:
            prev_score = karma.score
            karma.rank = rank
        elif prev_score == karma.score:
            karma.rank = rank
        else:
            rank += 1
            karma.rank = rank
            prev_score = karma.score

        student.karmaID = karma.karmaID
    db.session.commit()