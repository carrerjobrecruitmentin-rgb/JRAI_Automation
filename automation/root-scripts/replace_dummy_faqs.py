import pymysql
import json
import uuid
import os

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

def replace_dummy_questions(cursor):
    # Remove dummy questions
    cursor.execute("DELETE FROM ai_questions WHERE question_text LIKE 'Advanced scenario%%'")
    print("Deleted all dummy 'Advanced scenario' questions.")

    # Let's insert a pool of REAL questions for each role
    cursor.execute("SELECT id, role_name FROM ai_roles")
    roles = {r['role_name']: r['id'] for r in cursor.fetchall()}

    def get_cat_id(role_id, category_name):
        cursor.execute("SELECT id FROM ai_question_categories WHERE role_id = %s AND category_name = %s", (role_id, category_name))
        cat = cursor.fetchone()
        if cat:
            return cat['id']
        new_id = generate_uuid()
        cursor.execute("INSERT INTO ai_question_categories (id, category_name, role_id) VALUES (%s, %s, %s)", (new_id, category_name, role_id))
        return new_id

    # More real questions for Software Engineer
    se_questions = [
        ("Database Management", "What is the primary difference between INNER JOIN and LEFT JOIN?", {"A": "INNER JOIN returns all rows; LEFT JOIN returns matched rows", "B": "INNER JOIN returns matched rows in both tables; LEFT JOIN returns all rows from the left table", "C": "There is no difference", "D": "LEFT JOIN is faster"}, "B"),
        ("System Design", "Which caching strategy involves writing data to the cache and the backing store simultaneously?", {"A": "Write-Behind", "B": "Write-Around", "C": "Write-Through", "D": "Cache-Aside"}, "C"),
        ("Algorithms & DSA", "What is the time complexity of searching an element in a balanced Binary Search Tree?", {"A": "O(1)", "B": "O(N)", "C": "O(log N)", "D": "O(N^2)"}, "C"),
        ("Algorithms & DSA", "Which of the following sorting algorithms is NOT stable by default?", {"A": "Merge Sort", "B": "Insertion Sort", "C": "Quick Sort", "D": "Bubble Sort"}, "C"),
        ("Web Frameworks", "What is a 'Promise' in JavaScript?", {"A": "A boolean value", "B": "An object representing the eventual completion or failure of an async operation", "C": "A loop", "D": "A variable declaration"}, "B"),
        ("System Design", "In microservices, what is the role of an API Gateway?", {"A": "To compile the code", "B": "To act as a single entry point for all clients", "C": "To store user passwords directly", "D": "To render HTML"}, "B"),
        ("Database Management", "What is database normalization?", {"A": "Making backups of the database", "B": "Organizing data to minimize redundancy and dependency", "C": "Converting SQL to NoSQL", "D": "Encrypting the tables"}, "B"),
        ("Web Frameworks", "In React, what is the purpose of 'useMemo'?", {"A": "To memoize expensive calculations", "B": "To fetch API data", "C": "To update state", "D": "To navigate between pages"}, "A"),
        ("Algorithms & DSA", "Which data structure is typically used to implement a Breadth-First Search (BFS)?", {"A": "Stack", "B": "Queue", "C": "Tree", "D": "Graph"}, "B"),
        ("System Design", "What does 'Horizontal Scaling' mean?", {"A": "Adding more power (CPU, RAM) to an existing machine", "B": "Adding more machines to your pool of resources", "C": "Optimizing the code", "D": "Deleting old data"}, "B"),
        ("Web Frameworks", "What is the CSS Box Model?", {"A": "A JavaScript framework", "B": "A design pattern for routing", "C": "A box that wraps around every HTML element, consisting of margins, borders, padding, and content", "D": "A database schema"}, "C"),
        ("Database Management", "Which index type is best for full-text search in PostgreSQL?", {"A": "B-Tree", "B": "Hash", "C": "GIN", "D": "BRIN"}, "C")
    ]

    # More real questions for Data Scientist
    ds_questions = [
        ("Machine Learning", "What is overfitting?", {"A": "Model performs well on training data but poorly on unseen data", "B": "Model performs poorly on both training and unseen data", "C": "Model requires too much RAM", "D": "Model has too few parameters"}, "A"),
        ("Machine Learning", "Which metric is best for evaluating an imbalanced classification dataset?", {"A": "Accuracy", "B": "F1-Score", "C": "Mean Squared Error", "D": "R-squared"}, "B"),
        ("Statistics", "What is the Central Limit Theorem?", {"A": "Data always follows a normal distribution", "B": "The distribution of sample means approximates a normal distribution as sample size gets larger", "C": "Outliers should be removed", "D": "Variance must be zero"}, "B"),
        ("Programming", "What does the 'lambda' keyword do in Python?", {"A": "Declares a class", "B": "Creates an anonymous function", "C": "Imports a module", "D": "Handles exceptions"}, "B"),
        ("Data Wrangling", "What is standard scaling (Z-score normalization)?", {"A": "Scaling values between 0 and 1", "B": "Scaling data so it has a mean of 0 and standard deviation of 1", "C": "Removing null values", "D": "Converting text to lowercase"}, "B"),
        ("Machine Learning", "What is the purpose of the learning rate in Gradient Descent?", {"A": "Determines the size of the steps taken to reach the minimum", "B": "Sets the number of trees in a forest", "C": "Defines the batch size", "D": "Counts the epochs"}, "A"),
        ("Machine Learning", "What is an epoch in deep learning?", {"A": "A single parameter update", "B": "One complete pass through the entire training dataset", "C": "A type of neural network layer", "D": "The validation loss"}, "B"),
        ("Statistics", "What does correlation measure?", {"A": "Causation between variables", "B": "The strength and direction of a linear relationship between two variables", "C": "The average of a dataset", "D": "The difference between two means"}, "B"),
        ("Programming", "Which SQL clause is used to filter the results of a GROUP BY?", {"A": "WHERE", "B": "HAVING", "C": "ORDER BY", "D": "LIMIT"}, "B"),
        ("Data Wrangling", "What is SMOTE used for?", {"A": "Text preprocessing", "B": "Over-sampling minority classes in imbalanced datasets", "C": "Image compression", "D": "Database indexing"}, "B")
    ]

    # More real questions for Digital Marketing Specialist
    dm_questions = [
        ("SEO", "What is the purpose of an XML sitemap?", {"A": "To design the website layout", "B": "To help search engines discover and index pages on a site", "C": "To store user data", "D": "To run JavaScript scripts"}, "B"),
        ("SEO", "What is 'Keyword Stuffing'?", {"A": "Placing relevant keywords naturally", "B": "Overloading a webpage with keywords to manipulate ranking", "C": "Buying ads for keywords", "D": "Translating content"}, "B"),
        ("Content Marketing", "What is a 'Buyer Persona'?", {"A": "A semi-fictional representation of your ideal customer", "B": "The person who buys ads for the company", "C": "A type of discount code", "D": "A competitor analysis report"}, "A"),
        ("Social Media", "What does CPC stand for in paid advertising?", {"A": "Cost Per Click", "B": "Click Per Conversion", "C": "Cost Per Customer", "D": "Campaign Performance Cost"}, "A"),
        ("Analytics", "What is a 'Conversion Rate'?", {"A": "The speed at which a page loads", "B": "The percentage of visitors who complete a desired action", "C": "The exchange rate of currencies", "D": "The number of followers gained"}, "B"),
        ("Content Marketing", "What is the primary goal of a 'Lead Magnet'?", {"A": "To increase website load speed", "B": "To offer value in exchange for a prospect's contact information", "C": "To sell a premium product directly", "D": "To hide content from search engines"}, "B"),
        ("Social Media", "What is 'Retargeting'?", {"A": "Changing the target audience randomly", "B": "Serving ads to users who have previously interacted with your website or brand", "C": "Deleting old posts", "D": "Replying to comments"}, "B"),
        ("SEO", "Which HTTP status code signifies that a page has permanently moved?", {"A": "200", "B": "404", "C": "301", "D": "500"}, "C"),
        ("Analytics", "What does 'Bounce Rate' measure?", {"A": "How many emails bounced back", "B": "The percentage of single-page sessions where the user left without interacting", "C": "How often a link is clicked", "D": "The number of returning visitors"}, "B"),
        ("Social Media", "Which platform is primarily known for B2B marketing?", {"A": "TikTok", "B": "Snapchat", "C": "LinkedIn", "D": "Pinterest"}, "C")
    ]

    all_extra = {
        "Software Engineer": se_questions,
        "Data Scientist": ds_questions,
        "Digital Marketing Specialist": dm_questions
    }

    for role_name, qs in all_extra.items():
        if role_name not in roles:
            continue
        role_id = roles[role_name]
        for (cat, text, opts, correct) in qs:
            cat_id = get_cat_id(role_id, cat)
            q_id = generate_uuid()
            opts_json = json.dumps(opts)
            cursor.execute(
                "INSERT INTO ai_questions (id, role_id, category_id, difficulty, question_text, options_json, correct_option, marks, negative_marks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (q_id, role_id, cat_id, "medium", text, opts_json, correct, 10, 0)
            )

try:
    with connection.cursor() as cursor:
        replace_dummy_questions(cursor)
    connection.commit()
    print("Successfully replaced dummy questions with real varied questions!")
except Exception as e:
    connection.rollback()
    print(f"An error occurred: {e}")
finally:
    connection.close()
