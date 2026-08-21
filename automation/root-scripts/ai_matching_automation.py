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

def clear_existing_data(cursor):
    print("Clearing existing dummy data...")
    cursor.execute("DELETE FROM ai_roles")
    cursor.execute("DELETE FROM jobs WHERE title LIKE '%%Software Engineer%%' OR title LIKE '%%Data Scientist%%' OR title LIKE '%%Digital Marketing%%'")
    cursor.execute("DELETE FROM companies WHERE name IN ('TechCorp', 'DataVision', 'MarketPro')")
    print("Old dummy data cleared.")

def insert_companies(cursor):
    comps = [
        {"id": generate_uuid(), "name": "TechCorp", "description": "A leading tech company."},
        {"id": generate_uuid(), "name": "DataVision", "description": "Data analytics and AI."},
        {"id": generate_uuid(), "name": "MarketPro", "description": "Global digital marketing agency."}
    ]
    for c in comps:
        cursor.execute("INSERT INTO companies (id, name, description) VALUES (%s, %s, %s)", (c["id"], c["name"], c["description"]))
    return comps

def insert_jobs(cursor, companies):
    c_tech = companies[0]["id"]
    c_data = companies[1]["id"]
    c_market = companies[2]["id"]

    jobs = [
        (generate_uuid(), c_tech, "Software Engineer", "Software Engineer", "Remote", "120k-150k", "OPEN"),
        (generate_uuid(), c_tech, "Senior Software Engineer", "Software Engineer", "New York, NY", "150k-180k", "OPEN"),
        (generate_uuid(), c_data, "Data Scientist", "Data Scientist", "Remote", "130k-160k", "OPEN"),
        (generate_uuid(), c_data, "Lead Data Scientist", "Data Scientist", "San Francisco, CA", "160k-200k", "OPEN"),
        (generate_uuid(), c_market, "Digital Marketing Specialist", "Digital Marketing Specialist", "Remote", "70k-90k", "OPEN"),
        (generate_uuid(), c_market, "Digital Marketing Manager", "Digital Marketing Specialist", "Chicago, IL", "90k-120k", "OPEN")
    ]

    for j in jobs:
        cursor.execute(
            "INSERT INTO jobs (id, company_id, title, category, location_text, salary_range, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            j
        )
    print("Accurate jobs matching roles inserted.")

def insert_roles_and_questions(cursor):
    roles = [
        {
            "name": "Software Engineer",
            "categories": ["Algorithms & DSA", "System Design", "Web Frameworks", "Database Management"],
            "questions": [
                {"category": "Algorithms & DSA", "text": "Which data structure provides the fastest average time for looking up a value?", "options": {"A": "Linked List", "B": "Hash Table", "C": "Binary Search Tree", "D": "Array"}, "correct": "B"},
                {"category": "Algorithms & DSA", "text": "What is the worst-case time complexity of QuickSort?", "options": {"A": "O(N log N)", "B": "O(N)", "C": "O(N^2)", "D": "O(log N)"}, "correct": "C"},
                {"category": "System Design", "text": "Which architectural pattern is best suited for a highly scalable, distributed system where microservices communicate asynchronously?", "options": {"A": "Monolithic", "B": "Event-Driven", "C": "MVC", "D": "Singleton"}, "correct": "B"},
                {"category": "Web Frameworks", "text": "In React, which hook is used to perform side effects in functional components?", "options": {"A": "useState", "B": "useEffect", "C": "useContext", "D": "useReducer"}, "correct": "B"},
                {"category": "Database Management", "text": "Which of the following is an example of a NoSQL database?", "options": {"A": "PostgreSQL", "B": "MySQL", "C": "MongoDB", "D": "Oracle"}, "correct": "C"},
                {"category": "Database Management", "text": "What does the ACID property 'Isolation' ensure in database transactions?", "options": {"A": "Transactions are completely undone if they fail", "B": "Concurrent execution leaves the database in the same state as sequential", "C": "Data survives system crashes", "D": "Only valid data is written"}, "correct": "B"},
                {"category": "Algorithms & DSA", "text": "What algorithm is used to find the shortest path in a graph with non-negative edge weights?", "options": {"A": "Kruskal's", "B": "Dijkstra's", "C": "Depth First Search", "D": "Prim's"}, "correct": "B"},
                {"category": "System Design", "text": "What is the purpose of a Load Balancer?", "options": {"A": "To encrypt passwords", "B": "To distribute incoming network traffic", "C": "To cache database queries", "D": "To prevent SQL injection"}, "correct": "B"},
                {"category": "Web Frameworks", "text": "What does CORS stand for?", "options": {"A": "Cascading Object Render", "B": "Cross-Origin Resource Sharing", "C": "Client Object Request", "D": "Centralized Origin Routing"}, "correct": "B"},
                {"category": "Algorithms & DSA", "text": "Which sorting algorithm is most efficient for nearly sorted data?", "options": {"A": "Merge Sort", "B": "Insertion Sort", "C": "Quick Sort", "D": "Selection Sort"}, "correct": "B"}
            ]
        },
        {
            "name": "Data Scientist",
            "categories": ["Machine Learning", "Statistics", "Data Wrangling", "Programming"],
            "questions": [
                {"category": "Machine Learning", "text": "Which algorithm is commonly used for classification problems?", "options": {"A": "Linear Regression", "B": "K-Means", "C": "Logistic Regression", "D": "PCA"}, "correct": "C"},
                {"category": "Machine Learning", "text": "What is the purpose of cross-validation?", "options": {"A": "Increase dataset size", "B": "Assess model generalization", "C": "Train faster", "D": "Reduce features"}, "correct": "B"},
                {"category": "Statistics", "text": "What does a p-value less than the significance level typically indicate?", "options": {"A": "Accept null hypothesis", "B": "Reject null hypothesis", "C": "Test is inconclusive", "D": "Data is corrupted"}, "correct": "B"},
                {"category": "Data Wrangling", "text": "Which pandas method handles missing data by dropping rows/columns?", "options": {"A": "fillna()", "B": "dropna()", "C": "replace()", "D": "interpolate()"}, "correct": "B"},
                {"category": "Programming", "text": "Which library is heavily used for numerical operations on arrays in Python?", "options": {"A": "Requests", "B": "BeautifulSoup", "C": "NumPy", "D": "Flask"}, "correct": "C"},
                {"category": "Machine Learning", "text": "What problem does 'Random Forest' primarily address compared to a single Decision Tree?", "options": {"A": "Underfitting", "B": "Overfitting", "C": "Lack of data", "D": "Slow training"}, "correct": "B"},
                {"category": "Statistics", "text": "Which distribution is characterized by a bell-shaped curve?", "options": {"A": "Poisson", "B": "Binomial", "C": "Normal", "D": "Uniform"}, "correct": "C"},
                {"category": "Data Wrangling", "text": "Converting categorical data into binary variables is called?", "options": {"A": "Normalization", "B": "One-Hot Encoding", "C": "Standardization", "D": "Imputation"}, "correct": "B"},
                {"category": "Programming", "text": "How do you select a column named 'Salary' from a pandas DataFrame 'df'?", "options": {"A": "df.get('Salary')", "B": "df['Salary']", "C": "df.select('Salary')", "D": "df.Salary()"}, "correct": "B"},
                {"category": "Machine Learning", "text": "What evaluates how well an algorithm models the given data?", "options": {"A": "Activation Function", "B": "Loss Function", "C": "Transfer Function", "D": "Step Function"}, "correct": "B"}
            ]
        },
        {
            "name": "Digital Marketing Specialist",
            "categories": ["SEO", "Content Marketing", "Social Media", "Analytics"],
            "questions": [
                {"category": "SEO", "text": "Which tag is most critical for on-page SEO?", "options": {"A": "<body>", "B": "<title>", "C": "<div>", "D": "<footer>"}, "correct": "B"},
                {"category": "SEO", "text": "What does a high Bounce Rate typically indicate?", "options": {"A": "Users love the content", "B": "Users leave the site quickly", "C": "Fast load times", "D": "High conversion"}, "correct": "B"},
                {"category": "Content Marketing", "text": "What is a 'Call to Action' (CTA)?", "options": {"A": "Legal disclaimer", "B": "Prompt telling user to take specific action", "C": "Contact page", "D": "Blog title"}, "correct": "B"},
                {"category": "Social Media", "text": "Which metric measures unique users who saw your post?", "options": {"A": "Impressions", "B": "Engagement", "C": "Reach", "D": "CTR"}, "correct": "C"},
                {"category": "Analytics", "text": "In Google Analytics, what is an 'Event'?", "options": {"A": "Pageview", "B": "User interaction with content tracked independently", "C": "Calendar booking", "D": "Server error"}, "correct": "B"},
                {"category": "SEO", "text": "What is 'Link Building'?", "options": {"A": "Fixing code", "B": "Acquiring hyperlinks from other websites", "C": "Connecting servers", "D": "Internal navigation"}, "correct": "B"},
                {"category": "Content Marketing", "text": "What is considered Evergreen Content?", "options": {"A": "News", "B": "Comprehensive how-to guide", "C": "Holiday sale", "D": "Weather report"}, "correct": "B"},
                {"category": "Social Media", "text": "Primary benefit of A/B testing?", "options": {"A": "Spend budget", "B": "Compare two versions to see which performs better", "C": "Reach different countries", "D": "Bypass spam filters"}, "correct": "B"},
                {"category": "Analytics", "text": "What does CTR stand for?", "options": {"A": "Cost to Reach", "B": "Click-Through Rate", "C": "Customer Tracking", "D": "Content Translation"}, "correct": "B"},
                {"category": "SEO", "text": "Why is mobile responsiveness important for SEO?", "options": {"A": "It isn't", "B": "Search engines use mobile-first indexing", "C": "Reduces costs", "D": "Forces app downloads"}, "correct": "B"}
            ]
        }
    ]

    for role_data in roles:
        role_id = generate_uuid()
        cursor.execute("INSERT INTO ai_roles (id, role_name) VALUES (%s, %s)", (role_id, role_data["name"]))
        
        cat_map = {}
        for cat in role_data["categories"]:
            cat_id = generate_uuid()
            cursor.execute("INSERT INTO ai_question_categories (id, category_name, role_id) VALUES (%s, %s, %s)", (cat_id, cat, role_id))
            cat_map[cat] = cat_id

        for q in role_data["questions"]:
            opts_json = json.dumps(q["options"])
            cursor.execute(
                "INSERT INTO ai_questions (id, role_id, category_id, difficulty, question_text, options_json, correct_option, marks, negative_marks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (generate_uuid(), role_id, cat_map[q["category"]], "medium", q["text"], opts_json, q["correct"], 10, 0)
            )
    print("Roles and FAQs completely synced.")

try:
    with connection.cursor() as cursor:
        clear_existing_data(cursor)
        comps = insert_companies(cursor)
        insert_jobs(cursor, comps)
        insert_roles_and_questions(cursor)
    connection.commit()
    print("--- SUCCESS: Automation perfectly seeded all AI FAQs, Roles, and accurate Matching Jobs! ---")
except Exception as e:
    connection.rollback()
    print(f"An error occurred: {e}")
finally:
    connection.close()
