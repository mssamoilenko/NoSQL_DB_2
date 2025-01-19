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

#task2

import redis
from bcrypt import hashpw, gensalt, checkpw

db = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

def hash_password(password):
    return hashpw(password.encode(), gensalt()).decode()

def verify_password(password, hashed):
    return checkpw(password.encode(), hashed.encode())

def add_user(username, password):
    if db.hget(f'user:{username}', 'username'):
        return False
    db.hset(f'user:{username}', mapping={
        'username': username,
        'password': hash_password(password)
    })
    return True

def login(username, password):
    user_data = db.hgetall(f'user:{username}')
    if user_data and verify_password(password, user_data['password']):
        return True
    return False

def add_exhibit(name, description, type):
    exhibit_id = db.incr('exhibit_id')
    db.hset(f'exhibit:{exhibit_id}', mapping={
        'name': name,
        'description': description,
        'type': type
    })
    return exhibit_id

def delete_exhibit(exhibit_id):
    if not db.exists(f'exhibit:{exhibit_id}'):
        return False
    db.delete(f'exhibit:{exhibit_id}')
    return True

def edit_exhibit(exhibit_id, name=None, description=None, type=None):
    if not db.exists(f'exhibit:{exhibit_id}'):
        return False
    if name:
        db.hset(f'exhibit:{exhibit_id}', 'name', name)
    if description:
        db.hset(f'exhibit:{exhibit_id}', 'description', description)
    if type:
        db.hset(f'exhibit:{exhibit_id}', 'type', type)
    return True

def view_exhibit(exhibit_id):
    return db.hgetall(f'exhibit:{exhibit_id}')

def view_all_exhibits():
    exhibit_ids = db.keys('exhibit:*')
    return [db.hgetall(exhibit_id) for exhibit_id in exhibit_ids]

def add_person_to_exhibit(exhibit_id, person_name, relation):
    db.sadd(f'exhibit_people:{exhibit_id}', f"{person_name}:{relation}")

def view_exhibit_people(exhibit_id):
    return db.smembers(f'exhibit_people:{exhibit_id}')

def view_person_exhibits(person_name):
    exhibit_ids = db.keys('exhibit_people:*')
    person_exhibits = []
    for exhibit_id in exhibit_ids:
        if any(person_name in member for member in db.smembers(exhibit_id)):
            exhibit_id = exhibit_id.split(':')[1]
            person_exhibits.append(db.hgetall(f'exhibit:{exhibit_id}'))
    return person_exhibits

def view_exhibits_by_type(type):
    exhibit_ids = db.keys('exhibit:*')
    return [db.hgetall(exhibit_id) for exhibit_id in exhibit_ids if db.hget(exhibit_id, 'type') == type]

if __name__ == "__main__":
    add_user("user1", "password123")
    add_user("user2", "password456")

    login("user1", "password123")

    exhibit1_id = add_exhibit("Кобзар", "Збірка віршів Т.Г. Шевченка", "книга")
    exhibit2_id = add_exhibit("Перо Шевченка", "Перо, яким писав Т.Г. Шевченко", "артефакт")

    view_exhibit(exhibit1_id)

    edit_exhibit(exhibit1_id, description="Збірка поетичних творів Т.Г. Шевченка")
    view_exhibit(exhibit1_id)

    add_person_to_exhibit(exhibit1_id, "Тарас Шевченко", "автор")
    view_exhibit_people(exhibit1_id)

    view_all_exhibits()

    view_exhibits_by_type("книга")

    delete_exhibit(exhibit2_id)
    view_all_exhibits()

    view_person_exhibits("Тарас Шевченко")
