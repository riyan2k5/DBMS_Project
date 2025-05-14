import psycopg2
from psycopg2 import sql, errors
from config import DB_PARAMS

def register_user(username, password):
    if not username or not password:
        return False, "Username and password cannot be blank"

    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("INSERT INTO users (username, password) VALUES (%s, %s)")
                cur.execute(query, (username, password))
                conn.commit()
                return True, "User registered successfully"
    except errors.UniqueViolation:
        return False, "Username already exists"
    except errors.DatabaseError as e:
        return False, f"Database error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"

def check_credentials(username, password):
    if not username or not password:
        return False, "Username and password cannot be blank"

    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("SELECT username FROM users WHERE username = %s AND password = %s")
                cur.execute(query, (username, password))
                user = cur.fetchone()
                if user:
                    return True, "Login successful", username
                else:
                    return False, "Invalid username or password", None
    except errors.DatabaseError as e:
        return False, f"Database error: {e}", None
    except Exception as e:
        return False, f"Unexpected error: {e}", None

def create_post(username, content):
    if not content.strip():
        return False, "Post content cannot be empty"

    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("INSERT INTO posts (username, content) VALUES (%s, %s)")
                cur.execute(query, (username, content))
                conn.commit()
                return True, "Post created successfully"
    except errors.DatabaseError as e:
        return False, f"Database error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"

def delete_post(post_id, username):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("SELECT username FROM posts WHERE id = %s")
                cur.execute(query, (post_id,))
                result = cur.fetchone()

                if not result:
                    return False, "Post not found"

                if result[0] != username:
                    return False, "You can only delete your own posts"

                query = sql.SQL("DELETE FROM posts WHERE id = %s")
                cur.execute(query, (post_id,))
                conn.commit()
                return True, "Post deleted successfully"
    except errors.DatabaseError as e:
        return False, f"Database error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"

def get_all_posts():
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("""
                    SELECT id, username, content, created_at 
                    FROM posts
                    ORDER BY created_at DESC
                """)
                cur.execute(query)
                return cur.fetchall()
    except errors.DatabaseError as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def follow_user(follower, following):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT follow_user(%s, %s)", (follower, following))
                result = cur.fetchone()[0]
                conn.commit()
                return result, "Followed successfully" if result else "Already following"
    except Exception as e:
        return False, f"Error: {str(e)}"

def unfollow_user(follower, following):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT unfollow_user(%s, %s)", (follower, following))
                result = cur.fetchone()[0]
                conn.commit()
                return result, "Unfollowed successfully" if result else "Not following"
    except Exception as e:
        return False, f"Error: {str(e)}"

def is_following(follower, following):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT is_following(%s, %s)", (follower, following))
                return cur.fetchone()[0]
    except Exception as e:
        print(f"Error checking follow status: {e}")
        return False

def get_following(username):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM get_following(%s)", (username,))
                return cur.fetchall()
    except Exception as e:
        print(f"Error getting following list: {e}")
        return []

def get_followers(username):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM get_followers(%s)", (username,))
                return cur.fetchall()
    except Exception as e:
        print(f"Error getting followers list: {e}")
        return []

def get_followed_posts(username):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM get_followed_posts(%s)", (username,))
                return cur.fetchall()
    except Exception as e:
        print(f"Error getting followed posts: {e}")
        return []

def send_message(sender, receiver, content):
    if not content.strip():
        return False, "Message content cannot be empty"

    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT send_message(%s, %s, %s)", (sender, receiver, content))
                conn.commit()
                return True, "Message sent successfully"
    except Exception as e:
        return False, f"Error sending message: {str(e)}"

def get_conversation(user1, user2):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM get_conversation(%s, %s)", (user1, user2))
                return cur.fetchall()
    except Exception as e:
        print(f"Error getting conversation: {e}")
        return []

def get_user_conversations(username):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM get_user_conversations(%s)", (username,))
                return cur.fetchall()
    except Exception as e:
        print(f"Error getting user conversations: {e}")
        return []

def check_admin_credentials(username, password):
    return username == "umbreon" and password == "3141592654"

def get_all_users():
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("SELECT username, password FROM users")
                cur.execute(query)
                return cur.fetchall()
    except Exception as e:
        print(f"Error getting users: {e}")
        return []

def get_all_posts_admin():
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("""
                    SELECT id, username, content, created_at 
                    FROM posts
                    ORDER BY created_at DESC
                """)
                cur.execute(query)
                return cur.fetchall()
    except Exception as e:
        print(f"Error getting posts: {e}")
        return []

def delete_user_admin(username):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT username, password FROM users WHERE username = %s", (username,))
                user_data = cur.fetchone()
                if not user_data:
                    return False, "User not found"

                cur.execute("""
                    INSERT INTO recently_deleted_posts (id, username, content, created_at, deleted_at)
                    SELECT id, username, content, created_at, CURRENT_TIMESTAMP
                    FROM posts
                    WHERE username = %s
                """, (username,))

                cur.execute("DELETE FROM follows WHERE follower_username = %s", (username,))
                cur.execute("DELETE FROM follows WHERE following_username = %s", (username,))
                cur.execute("DELETE FROM posts WHERE username = %s", (username,))
                cur.execute("DELETE FROM conversations WHERE user1_username = %s OR user2_username = %s",
                            (username, username))
                cur.execute("DELETE FROM direct_messages WHERE sender_username = %s OR receiver_username = %s",
                            (username, username))

                cur.execute("DELETE FROM users WHERE username = %s", (username,))

                cur.execute("""
                    INSERT INTO recently_deleted_users (username, password, deleted_at)
                    VALUES (%s, %s, CURRENT_TIMESTAMP)
                """, user_data)

                conn.commit()
                return True, "User deleted successfully"
    except Exception as e:
        return False, f"Error deleting user: {str(e)}"

def delete_post_admin(post_id):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, username, content, created_at 
                    FROM posts WHERE id = %s
                """, (post_id,))
                post_data = cur.fetchone()
                if not post_data:
                    return False, "Post not found"

                cur.execute("""
                    INSERT INTO recently_deleted_posts (id, username, content, created_at, deleted_at)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, post_data)

                cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
                conn.commit()
                return True, "Post deleted successfully"
    except Exception as e:
        return False, f"Error deleting post: {str(e)}"

def get_recently_deleted_users():
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("""
                    SELECT username, deleted_at 
                    FROM recently_deleted_users
                    ORDER BY deleted_at DESC
                """)
                cur.execute(query)
                return cur.fetchall()
    except Exception as e:
        print(f"Error getting recently deleted users: {e}")
        return []

def get_recently_deleted_posts():
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("""
                    SELECT id, username, content, created_at, deleted_at 
                    FROM recently_deleted_posts
                    ORDER BY deleted_at DESC
                """)
                cur.execute(query)
                return cur.fetchall()
    except Exception as e:
        print(f"Error getting recently deleted posts: {e}")
        return []

def recover_user(username):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT username, password 
                    FROM recently_deleted_users 
                    WHERE username = %s
                """, (username,))
                user_data = cur.fetchone()
                if not user_data:
                    return False, "User not found in deleted users"

                cur.execute("""
                    INSERT INTO users (username, password)
                    VALUES (%s, %s)
                """, user_data)

                cur.execute("""
                    INSERT INTO posts (id, username, content, created_at)
                    SELECT id, username, content, created_at
                    FROM recently_deleted_posts
                    WHERE username = %s
                """, (username,))

                cur.execute("DELETE FROM recently_deleted_users WHERE username = %s", (username,))
                cur.execute("DELETE FROM recently_deleted_posts WHERE username = %s", (username,))

                conn.commit()
                return True, "User and their posts recovered successfully"
    except Exception as e:
        return False, f"Error recovering user: {str(e)}"

def recover_post(post_id):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, username, content, created_at 
                    FROM recently_deleted_posts 
                    WHERE id = %s
                """, (post_id,))
                post_data = cur.fetchone()
                if not post_data:
                    return False, "Post not found in deleted posts"

                cur.execute("""
                    INSERT INTO posts (id, username, content, created_at)
                    VALUES (%s, %s, %s, %s)
                """, post_data)

                cur.execute("DELETE FROM recently_deleted_posts WHERE id = %s", (post_id,))
                conn.commit()
                return True, "Post recovered successfully"
    except Exception as e:
        return False, f"Error recovering post: {str(e)}"

def permanently_delete_user(username):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM recently_deleted_users WHERE username = %s", (username,))
                conn.commit()
                return True, "User permanently deleted"
    except Exception as e:
        return False, f"Error permanently deleting user: {str(e)}"

def permanently_delete_post(post_id):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM recently_deleted_posts WHERE id = %s", (post_id,))
                conn.commit()
                return True, "Post permanently deleted"
    except Exception as e:
        return False, f"Error permanently deleting post: {str(e)}"

def like_post(post_id, username):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("""
                    INSERT INTO likes (post_id, username)
                    VALUES (%s, %s)
                    ON CONFLICT (post_id, username) DO NOTHING
                    RETURNING id
                """)
                cur.execute(query, (post_id, username))
                result = cur.fetchone()
                conn.commit()
                return True, "Post liked successfully" if result else "Already liked"
    except Exception as e:
        return False, f"Error liking post: {str(e)}"

def unlike_post(post_id, username):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("DELETE FROM likes WHERE post_id = %s AND username = %s")
                cur.execute(query, (post_id, username))
                conn.commit()
                return True, "Post unliked successfully"
    except Exception as e:
        return False, f"Error unliking post: {str(e)}"

def is_post_liked(post_id, username):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("SELECT EXISTS(SELECT 1 FROM likes WHERE post_id = %s AND username = %s)")
                cur.execute(query, (post_id, username))
                return cur.fetchone()[0]
    except Exception as e:
        print(f"Error checking like status: {e}")
        return False

def get_like_count(post_id):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("SELECT COUNT(*) FROM likes WHERE post_id = %s")
                cur.execute(query, (post_id,))
                return cur.fetchone()[0]
    except Exception as e:
        print(f"Error getting like count: {e}")
        return 0

def add_reply(post_id, username, content, parent_reply_id=None):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("""
                    INSERT INTO replies (post_id, username, content, parent_reply_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """)
                cur.execute(query, (post_id, username, content, parent_reply_id))
                conn.commit()
                return True, "Reply added successfully"
    except Exception as e:
        return False, f"Error adding reply: {str(e)}"

def get_replies(post_id):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("""
                    SELECT r.id, r.username, r.content, r.created_at, r.parent_reply_id,
                           COALESCE(p.username, '') as parent_username
                    FROM replies r
                    LEFT JOIN replies p ON r.parent_reply_id = p.id
                    WHERE r.post_id = %s
                    ORDER BY r.created_at ASC
                """)
                cur.execute(query, (post_id,))
                return cur.fetchall()
    except Exception as e:
        print(f"Error getting replies: {e}")
        return []

def delete_reply(reply_id, username):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("SELECT username FROM replies WHERE id = %s")
                cur.execute(query, (reply_id,))
                result = cur.fetchone()

                if not result:
                    return False, "Reply not found"

                if result[0] != username:
                    return False, "You can only delete your own replies"

                query = sql.SQL("DELETE FROM replies WHERE id = %s")
                cur.execute(query, (reply_id,))
                conn.commit()
                return True, "Reply deleted successfully"
    except Exception as e:
        return False, f"Error deleting reply: {str(e)}"