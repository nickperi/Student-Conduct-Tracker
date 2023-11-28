from App.models import Review, Karma, Student
from App.database import db
from App.models.staff import Staff

def get_reviews(): 
    return db.session.query(Review).all()

def get_reviews_for_student(studentID):
    return db.session.query(Review).filter_by(studentID=studentID).all()

def get_review(reviewID):
    return Review.query.filter_by(ID=reviewID).first()

def get_reviews_by_staff(staffID):
    return db.session.query(Review).filter_by(reviewerID=staffID).all()


def edit_review(review, staff, is_positive, comment):
    if review.reviewer == staff:
        review.isPositive = is_positive
        review.comment = comment
        db.session.add(review)
        db.session.commit()
        return review
    return None


def delete_review(review, staff):
    if review.reviewer == staff:
        db.session.delete(review)
        db.session.commit()
        return True
    return None


def downvoteReview(reviewID, staff):
    review = db.session.query(Review).get(reviewID)
    
    if staff in review.staffDownvoters:
        return review.downvotes  # If they downvoted the review already, return current votes

    review.downvotes += 1
    review.staffDownvoters.append(staff)

    if staff in review.staffUpvoters:
        review.upvotes -= 1
        review.staffUpvoters.remove(staff)

    db.session.add(review)
    db.session.commit()

    update_karma(review.studentID)

    return review.downvotes


def upvoteReview(reviewID, staff):
    review = db.session.query(Review).get(reviewID)

    if staff in review.staffUpvoters:
        return review.upvotes  # If they upvoted the review already, return current votes

    review.upvotes += 1
    review.staffUpvoters.append(staff)

    if staff in review.staffDownvoters:
        review.downvotes -= 1
        review.staffDownvoters.remove(staff)

    db.session.add(review)
    db.session.commit()

    update_karma(review.studentID)

    return review.upvotes


def update_karma(studentID):
    student = db.session.query(Student).get(studentID)
    if student:
        if student.karmaID is None:
            karma = Karma(studentID=studentID, score=0.0, rank=-99)
            db.session.add(karma)
            db.session.flush()
            db.session.commit()
            student.karmaID = karma.karmaID

        student_karma = db.session.query(Karma).get(student.karmaID)
        student_karma.calculateScore(student)
        student_karma.updateRank()

        db.session.add(student_karma)
        db.session.commit()
