import firebase_admin
from firebase_admin import firestore

db = firestore.client()

def get_lessons():
    lessons_ref = db.collection('lessons')
    return [doc.to_dict() for doc in lessons_ref.stream()]

def complete_lesson(user_id, lesson_id):
    from database import update_user_progress
    update_user_progress(user_id, lesson_id)

