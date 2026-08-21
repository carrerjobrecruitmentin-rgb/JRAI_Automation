import pymysql
import json
import uuid
import os
import random

# Database Connection
try:
    connection = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASS', ''),
        database=os.getenv('DB_NAME', 'job_recruitment_ai'),
        cursorclass=pymysql.cursors.DictCursor
    )
except Exception as e:
    print(f"Error connecting to database: {e}")
    exit(1)

def generate_uuid():
    return str(uuid.uuid4())

def add_more_questions(cursor):
    cursor.execute("SELECT id, role_name FROM ai_roles")
    roles = cursor.fetchall()
    
    for r in roles:
        role_id = r['id']
        cursor.execute("SELECT id, category_name FROM ai_question_categories WHERE role_id = %s", (role_id,))
        categories = cursor.fetchall()
        
        if not categories:
            continue
            
        print(f"Adding 50 more questions for {r['role_name']}...")
        
        for i in range(1, 51):
            cat = random.choice(categories)
            q_id = generate_uuid()
            text = f"Advanced scenario {i} for {r['role_name']}: How would you optimize the workflow in {cat['category_name']}?"
            opts = {
                "A": "Use standard best practices for efficiency",
                "B": "Rewrite the entire infrastructure",
                "C": "Ignore it until it breaks",
                "D": "Outsource the problem completely"
            }
            correct = "A"
            opts_json = json.dumps(opts)
            
            cursor.execute(
                "INSERT INTO ai_questions (id, role_id, category_id, difficulty, question_text, options_json, correct_option, marks, negative_marks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (q_id, role_id, cat['id'], "hard", text, opts_json, correct, 10, 0)
            )

try:
    with connection.cursor() as cursor:
        add_more_questions(cursor)
    connection.commit()
    print("Successfully added 50 more unique questions per role to ensure randomization!")
except Exception as e:
    connection.rollback()
    print(f"An error occurred: {e}")
finally:
    connection.close()
