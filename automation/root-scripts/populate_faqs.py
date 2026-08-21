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
    print("Deleted all roles and cascaded down to categories and questions.")

def insert_data(cursor):
    roles = [
        {
            "name": "Software Engineer",
            "categories": ["Algorithms & DSA", "System Design", "Web Frameworks", "Database Management"],
            "questions": [
                {
                    "category": "Algorithms & DSA",
                    "text": "Which data structure provides the fastest average time for looking up a value?",
                    "options": {"A": "Linked List", "B": "Hash Table", "C": "Binary Search Tree", "D": "Array"},
                    "correct": "B"
                },
                {
                    "category": "Algorithms & DSA",
                    "text": "What is the worst-case time complexity of QuickSort?",
                    "options": {"A": "O(N log N)", "B": "O(N)", "C": "O(N^2)", "D": "O(log N)"},
                    "correct": "C"
                },
                {
                    "category": "System Design",
                    "text": "Which architectural pattern is best suited for a highly scalable, distributed system where microservices communicate asynchronously?",
                    "options": {"A": "Monolithic Architecture", "B": "Event-Driven Architecture", "C": "MVC Pattern", "D": "Singleton Pattern"},
                    "correct": "B"
                },
                {
                    "category": "Web Frameworks",
                    "text": "In React, which hook is used to perform side effects in functional components?",
                    "options": {"A": "useState", "B": "useEffect", "C": "useContext", "D": "useReducer"},
                    "correct": "B"
                },
                {
                    "category": "Web Frameworks",
                    "text": "What is the primary purpose of a Virtual DOM in modern web frameworks?",
                    "options": {"A": "To increase memory usage", "B": "To minimize direct manipulation of the real DOM for better performance", "C": "To create 3D graphics", "D": "To directly interact with the database"},
                    "correct": "B"
                },
                {
                    "category": "Database Management",
                    "text": "Which of the following is an example of a NoSQL database?",
                    "options": {"A": "PostgreSQL", "B": "MySQL", "C": "MongoDB", "D": "Oracle"},
                    "correct": "C"
                },
                {
                    "category": "Database Management",
                    "text": "What does the ACID property 'Isolation' ensure in database transactions?",
                    "options": {"A": "Transactions are completely undone if they fail", "B": "Concurrent execution of transactions leaves the database in the same state as if executed sequentially", "C": "Data survives system crashes", "D": "Only valid data is written to the database"},
                    "correct": "B"
                },
                {
                    "category": "Algorithms & DSA",
                    "text": "What algorithm is used to find the shortest path in a graph with non-negative edge weights?",
                    "options": {"A": "Kruskal's Algorithm", "B": "Dijkstra's Algorithm", "C": "Depth First Search", "D": "Prim's Algorithm"},
                    "correct": "B"
                },
                {
                    "category": "System Design",
                    "text": "What is the purpose of a Load Balancer?",
                    "options": {"A": "To encrypt user passwords", "B": "To distribute incoming network traffic across multiple servers", "C": "To cache database queries", "D": "To prevent SQL injection attacks"},
                    "correct": "B"
                },
                {
                    "category": "Web Frameworks",
                    "text": "What does CORS stand for in web development?",
                    "options": {"A": "Cascading Object Render System", "B": "Cross-Origin Resource Sharing", "C": "Client Object Request System", "D": "Centralized Origin Routing System"},
                    "correct": "B"
                }
            ]
        },
        {
            "name": "Data Scientist",
            "categories": ["Machine Learning", "Statistics", "Data Wrangling", "Programming"],
            "questions": [
                {
                    "category": "Machine Learning",
                    "text": "Which algorithm is commonly used for classification problems?",
                    "options": {"A": "Linear Regression", "B": "K-Means Clustering", "C": "Logistic Regression", "D": "Principal Component Analysis"},
                    "correct": "C"
                },
                {
                    "category": "Machine Learning",
                    "text": "What is the purpose of cross-validation in machine learning?",
                    "options": {"A": "To increase the size of the dataset", "B": "To assess how the results of a statistical analysis will generalize to an independent dataset", "C": "To train the model faster", "D": "To reduce the number of features"},
                    "correct": "B"
                },
                {
                    "category": "Statistics",
                    "text": "What does a p-value less than the significance level typically indicate?",
                    "options": {"A": "Accept the null hypothesis", "B": "Reject the null hypothesis", "C": "The test is inconclusive", "D": "Data is corrupted"},
                    "correct": "B"
                },
                {
                    "category": "Data Wrangling",
                    "text": "Which pandas method is used to handle missing data by dropping rows or columns?",
                    "options": {"A": "fillna()", "B": "dropna()", "C": "replace()", "D": "interpolate()"},
                    "correct": "B"
                },
                {
                    "category": "Programming",
                    "text": "In Python, which library is heavily used for numerical operations on large, multi-dimensional arrays and matrices?",
                    "options": {"A": "Requests", "B": "BeautifulSoup", "C": "NumPy", "D": "Flask"},
                    "correct": "C"
                },
                {
                    "category": "Machine Learning",
                    "text": "What problem does 'Random Forest' primarily address compared to a single Decision Tree?",
                    "options": {"A": "Underfitting", "B": "Overfitting", "C": "Lack of data", "D": "Slow training time"},
                    "correct": "B"
                },
                {
                    "category": "Statistics",
                    "text": "Which distribution is characterized by a bell-shaped curve where the mean, median, and mode are all equal?",
                    "options": {"A": "Poisson Distribution", "B": "Binomial Distribution", "C": "Normal Distribution", "D": "Uniform Distribution"},
                    "correct": "C"
                },
                {
                    "category": "Data Wrangling",
                    "text": "What is the process of converting categorical data into a format that could be provided to ML algorithms to do a better job in prediction?",
                    "options": {"A": "Normalization", "B": "One-Hot Encoding", "C": "Standardization", "D": "Imputation"},
                    "correct": "B"
                },
                {
                    "category": "Programming",
                    "text": "How do you select a column named 'Salary' from a pandas DataFrame 'df'?",
                    "options": {"A": "df.get('Salary')", "B": "df['Salary']", "C": "df.select('Salary')", "D": "df.Salary()"},
                    "correct": "B"
                },
                {
                    "category": "Machine Learning",
                    "text": "What is the term for the function used to evaluate how well a specific algorithm models the given data?",
                    "options": {"A": "Activation Function", "B": "Loss Function", "C": "Transfer Function", "D": "Step Function"},
                    "correct": "B"
                }
            ]
        },
        {
            "name": "Digital Marketing Specialist",
            "categories": ["SEO", "Content Marketing", "Social Media", "Analytics"],
            "questions": [
                {
                    "category": "SEO",
                    "text": "Which tag is most critical for on-page SEO to tell search engines what the page is about?",
                    "options": {"A": "<body> tag", "B": "<title> tag", "C": "<div> tag", "D": "<footer> tag"},
                    "correct": "B"
                },
                {
                    "category": "SEO",
                    "text": "What does a high Bounce Rate typically indicate?",
                    "options": {"A": "Users love the content and stay long", "B": "Users leave the site quickly without interacting", "C": "The site loads very fast", "D": "High conversion rate"},
                    "correct": "B"
                },
                {
                    "category": "Content Marketing",
                    "text": "What is a 'Call to Action' (CTA)?",
                    "options": {"A": "A legal disclaimer", "B": "A prompt telling the user to take a specific action", "C": "A contact page", "D": "A blog post title"},
                    "correct": "B"
                },
                {
                    "category": "Social Media",
                    "text": "Which metric measures the number of unique users who saw your post?",
                    "options": {"A": "Impressions", "B": "Engagement Rate", "C": "Reach", "D": "Click-Through Rate"},
                    "correct": "C"
                },
                {
                    "category": "Analytics",
                    "text": "In Google Analytics, what is an 'Event'?",
                    "options": {"A": "A pageview", "B": "A user interaction with content that can be tracked independently from a web page or screen load", "C": "A calendar booking", "D": "A server error"},
                    "correct": "B"
                },
                {
                    "category": "SEO",
                    "text": "What is 'Link Building'?",
                    "options": {"A": "Fixing broken code", "B": "Acquiring hyperlinks from other websites to your own", "C": "Connecting servers", "D": "Creating internal navigation"},
                    "correct": "B"
                },
                {
                    "category": "Content Marketing",
                    "text": "Which of the following is considered Evergreen Content?",
                    "options": {"A": "News about a recent event", "B": "A comprehensive guide on 'How to Tie a Tie'", "C": "A holiday sale announcement", "D": "A daily weather report"},
                    "correct": "B"
                },
                {
                    "category": "Social Media",
                    "text": "What is the primary benefit of A/B testing in marketing campaigns?",
                    "options": {"A": "To spend more budget", "B": "To compare two versions of a campaign to see which performs better", "C": "To reach audiences in different countries", "D": "To bypass spam filters"},
                    "correct": "B"
                },
                {
                    "category": "Analytics",
                    "text": "What does CTR stand for?",
                    "options": {"A": "Cost to Reach", "B": "Click-Through Rate", "C": "Customer Tracking Report", "D": "Content Translation Rate"},
                    "correct": "B"
                },
                {
                    "category": "SEO",
                    "text": "Why is mobile responsiveness important for SEO?",
                    "options": {"A": "It isn't important", "B": "Search engines like Google use mobile-first indexing", "C": "It reduces server costs", "D": "It forces users to buy mobile apps"},
                    "correct": "B"
                }
            ]
        }
    ]

    for role_data in roles:
        role_id = generate_uuid()
        cursor.execute("INSERT INTO ai_roles (id, role_name) VALUES (%s, %s)", (role_id, role_data["name"]))
        print(f"Inserted role: {role_data['name']}")

        cat_map = {}
        for cat in role_data["categories"]:
            cat_id = generate_uuid()
            cursor.execute("INSERT INTO ai_question_categories (id, category_name, role_id) VALUES (%s, %s, %s)", (cat_id, cat, role_id))
            cat_map[cat] = cat_id

        for q in role_data["questions"]:
            q_id = generate_uuid()
            c_id = cat_map[q["category"]]
            opts_json = json.dumps(q["options"])
            cursor.execute(
                "INSERT INTO ai_questions (id, role_id, category_id, difficulty, question_text, options_json, correct_option, marks, negative_marks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (q_id, role_id, c_id, "medium", q["text"], opts_json, q["correct"], 10, 0)
            )

try:
    with connection.cursor() as cursor:
        clear_existing_data(cursor)
        insert_data(cursor)
    connection.commit()
    print("Database successfully seeded with highly accurate role-based FAQs!")
except Exception as e:
    connection.rollback()
    print(f"An error occurred: {e}")
finally:
    connection.close()
