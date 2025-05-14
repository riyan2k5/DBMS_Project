import json
import os
import datetime
import psycopg2
import firebase_admin
from firebase_admin import credentials, db as firebase_db
from config import DB_PARAMS

FIREBASE_CREDENTIALS_PATH = '/Users/riyan/Desktop/firebase-credentials.json'

def get_firebase_db_url(json_path):
    try:
        with open(json_path, 'r') as f:
            key_data = json.load(f)
        project_id = key_data.get('project_id')

        if project_id == 'dbms-project-bb35e':
            return 'https://dbms-project-bb35e-default-rtdb.asia-southeast1.firebasedatabase.app/'
        else:
            return f'https://{project_id}-default-rtdb.firebaseio.com/'

    except FileNotFoundError:
        raise FileNotFoundError(f"Firebase credentials file not found: {json_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in credentials file: {e}")

firebase_ref = None
try:
    if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
        print(f"ERROR: Firebase credentials file not found at: {FIREBASE_CREDENTIALS_PATH}")
        print("Please download the service account key from Firebase Console.")
    else:
        print(f"Found credentials file: {FIREBASE_CREDENTIALS_PATH}")
        FIREBASE_DATABASE_URL = get_firebase_db_url(FIREBASE_CREDENTIALS_PATH)
        print(f"Database URL: {FIREBASE_DATABASE_URL}")
        BACKUP_ROOT_NODE = 'postgres_backup'

        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_DATABASE_URL})

        firebase_ref = firebase_db.reference(BACKUP_ROOT_NODE)
        print("✅ Firebase initialized successfully!")

except Exception as e:
    print(f"❌ Firebase initialization failed: {e}")
    print("Make sure you:")
    print("1. Downloaded the service account JSON file")
    print("2. Created a Realtime Database in Firebase Console")
    print("3. Updated the FIREBASE_CREDENTIALS_PATH with correct path")
    firebase_ref = None

def serialize_datetime(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    return str(obj) if obj is not None else None

def backup_table_to_firebase(table_name, query):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()

                table_data = []
                for row in rows:
                    row_dict = {}
                    for i, value in enumerate(row):
                        row_dict[columns[i]] = serialize_datetime(value)
                    table_data.append(row_dict)

                return table_data
    except Exception as e:
        print(f"Error backing up table {table_name}: {e}")
        return []

def backup_all_tables_to_firebase():
    if not firebase_ref:
        return False, "Firebase not initialized"

    try:
        backup_data = {}

        tables_to_backup = {
            'users': "SELECT username, password FROM users",
            'posts': "SELECT id, username, content, created_at FROM posts ORDER BY created_at DESC",
            'follows': "SELECT follower_username, following_username, created_at FROM follows",
            'likes': "SELECT id, post_id, username, created_at FROM likes",
            'replies': "SELECT id, post_id, username, content, created_at, parent_reply_id FROM replies",
            'direct_messages': "SELECT id, sender_username, receiver_username, content, created_at, is_read FROM direct_messages",
            'conversations': "SELECT id, user1_username, user2_username, last_message_at FROM conversations",
            'recently_deleted_users': "SELECT username, password, deleted_at FROM recently_deleted_users",
            'recently_deleted_posts': "SELECT id, username, content, created_at, deleted_at FROM recently_deleted_posts"
        }

        for table_name, query in tables_to_backup.items():
            print(f"Backing up table: {table_name}")
            backup_data[table_name] = backup_table_to_firebase(table_name, query)

        backup_data['_metadata'] = {
            'backup_timestamp': datetime.datetime.now().isoformat(),
            'total_tables': len(tables_to_backup)
        }

        firebase_ref.set(backup_data)
        return True, "Backup completed successfully"

    except Exception as e:
        return False, f"Backup failed: {str(e)}"