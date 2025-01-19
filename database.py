import firebase_admin
from firebase_admin import firestore

db = firestore.client()

def get_user_progress(user_id):
    doc_ref = db.collection('user_progress').document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None

def update_user_progress(user_id, lesson_id):
    doc_ref = db.collection('user_progress').document(user_id)
    doc_ref.set({
        lesson_id: firestore.SERVER_TIMESTAMP
    }, merge=True)

