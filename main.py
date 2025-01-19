import redis
from bcrypt import hashpw, gensalt, checkpw
#task1
db = redis.StrictRedis(host=' localhost', port=6379, decode_responses=True)

try:
    db.ping()
    print("З'єднання з Redis успішне!")
except redis.ConnectionError as e:
    print(f"Помилка підключення: {e}")

def hash_password(password):
    return hashpw(password.encode(), gensalt()).decode()

def verify_password(password, hashed):
    return checkpw(password.encode(), hashed.encode())

def add_user(username, password, full_name):
    if db.hget(f'user:{username}', 'username'):
        return
    db.hset(f'user:{username}', mapping={
        'username': username,
        'password': hash_password(password),
        'full_name': full_name
    })

def delete_user(username):
    if not db.hget(f'user:{username}', 'username'):
        return
    db.delete(f'user:{username}')
    db.delete(f'friends:{username}')
    db.delete(f'posts:{username}')

def edit_user(username, new_full_name):
    if not db.hget(f'user:{username}', 'username'):
        return
    db.hset(f'user:{username}', 'full_name', new_full_name)

def search_user(full_name):
    keys = db.keys('user:*')
    for key in keys:
        if db.hget(key, 'full_name') == full_name:
            return

def view_user(username):
    if not db.hget(f'user:{username}', 'username'):
        return
    user_data = db.hgetall(f'user:{username}')
    print(f"Інформація про користувача {username}: {user_data}")
    return user_data

def add_friend(username, friend_username):
    if not db.hget(f'user:{friend_username}', 'username'):
        return
    db.sadd(f'friends:{username}', friend_username)


def view_friends(username):
    friends = db.smembers(f'friends:{username}')
    if friends:
        print(f"Друзі користувача {username}: {friends}")
    else:
        print(f"Користувач {username} не має друзів.")
    return friends


def add_post(username, post_content):
    post_id = db.incr(f'post_id:{username}')
    db.hset(f'posts:{username}:{post_id}', mapping={
        'content': post_content,
        'author': username
    })


def view_posts(username):
    keys = db.keys(f'posts:{username}:*')
    if keys:
        print(f"Публікації користувача {username}:")
        for key in keys:
            post = db.hgetall(key)
            print(post)
    else:
        print(f"В користувача {username} немає публікацій.")


if __name__ == "__main__":
    add_user("user1", "password123", "Самойленко Алла Ігорівна")
    add_user("user2", "password456", "Попоков Микола Сергійович")

    print(view_user("user1"))

    add_friend("user1", "user2")

    print(view_friends("user1"))

    add_post("user1", "Це моя перша публікація!")
    add_post("user1", "Це моя друга публікація.")

    print(view_posts("user1"))
