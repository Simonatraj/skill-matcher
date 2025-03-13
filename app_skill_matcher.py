import mysql.connector
from difflib import SequenceMatcher
from nltk.corpus import wordnet
from sentence_transformers import SentenceTransformer, util


model = SentenceTransformer('all-MiniLM-L6-v2')


DEFAULT_SKILLS = ['Python', 'relational database', 'Software engineering',
                  'data science', 'NLP', 'natural language processing']


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=##,
        database="skill_matcher"
    )

def execute_query(query, params=None):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(query, params or ())
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def fetch_all(query, params=None):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(query, params or ())
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

# Initialize the database with default skills
def initialize_default_skills():
    existing_skills = {skill[0] for skill in fetch_all("SELECT skill_name FROM Skill")}
    for skill in DEFAULT_SKILLS:
        if skill not in existing_skills:
            execute_query("INSERT INTO Skill (skill_name) VALUES (%s)", (skill,))
    print("Default skills initialized.")

def admin_menu():
    print("--- Admin Menu ---")
    print("1. Add a new skill")
    print("2. View all skills")
    print("3. Replace a skill")
    print("4. Delete a skill")
    choice = input("Enter your choice: ").strip()

    if choice == "1":
        new_skill = input("Enter the new skill to add: ").strip()
        execute_query("INSERT INTO Skill (skill_name) VALUES (%s)", (new_skill,))
        print(f"Skill '{new_skill}' added successfully!")
    elif choice == "2":
        skills = fetch_all("SELECT skill_name FROM Skill")
        print("--- Existing Skills ---")
        for skill in skills:
            print(skill[0])
    elif choice == "3":
        old_skill = input("Enter the skill you want to replace: ").strip()
        new_skill = input("Enter the new skill: ").strip()
        execute_query("UPDATE Skill SET skill_name = %s WHERE skill_name = %s", (new_skill, old_skill))
        print(f"Skill '{old_skill}' replaced with '{new_skill}' successfully!")
    elif choice == "4":
        skill_to_delete = input("Enter the skill you want to delete: ").strip()
        execute_query("DELETE FROM Skill WHERE skill_name = %s", (skill_to_delete,))
        print(f"Skill '{skill_to_delete}' deleted successfully!")
    else:
        print("Invalid choice.")

def register_user():
    print("--- User Registration ---")
    username = input("Enter a username: ").strip()
    email = input("Enter your email: ").strip()
    execute_query("INSERT INTO User (username, email) VALUES (%s, %s)", (username, email))
    user_id = fetch_all("SELECT LAST_INSERT_ID()")
    print("User registered successfully!")
    return user_id[0][0]

def login_user():
    print("--- User Login ---")
    username = input("Enter your username: ").strip()
    email = input("Enter your email: ").strip()
    user = fetch_all("SELECT user_id FROM User WHERE username = %s AND email = %s", (username, email))
    if user:
        print("Login successful!")
        return user[0][0]
    else:
        print("Invalid credentials.")
        return None

# Synonym matching using WordNet
def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return synonyms

def synonym_match(user_skill, admin_skill):
    user_synonyms = get_synonyms(user_skill)
    admin_synonyms = get_synonyms(admin_skill)
    return len(user_synonyms.intersection(admin_synonyms)) > 0

# Semantic matching using Hugging Face Transformers
def semantic_match(user_skill, admin_skill):
    # Encode the skills into embeddings
    user_embedding = model.encode(user_skill, convert_to_tensor=True)
    admin_embedding = model.encode(admin_skill, convert_to_tensor=True)
    # Compute cosine similarity
    similarity = util.cos_sim(user_embedding, admin_embedding).item()
    return similarity

def match_skill(user_skill, admin_skill):
    methods = []
    similarity = 0

    # Exact match
    if user_skill.lower() == admin_skill.lower():
        methods.append("Exact match")
        similarity = 1.0

    # Partial match
    if user_skill.lower() in admin_skill.lower() or admin_skill.lower() in user_skill.lower():
        methods.append("Partial match")
        similarity = max(similarity, 0.8)

    # Fuzzy match
    fuzzy_similarity = SequenceMatcher(None, user_skill, admin_skill).ratio()
    if fuzzy_similarity >= 0.7:
        methods.append("Fuzzy match")
        similarity = max(similarity, fuzzy_similarity)

    # Synonym match
    if synonym_match(user_skill, admin_skill):
        methods.append("Synonym match")
        similarity = max(similarity, 0.75)

    # Semantic match
    semantic_similarity = semantic_match(user_skill, admin_skill)
    if semantic_similarity >= 0.7:
        methods.append("Semantic match")
        similarity = max(similarity, semantic_similarity)

    return methods, similarity

def submit_query(user_id, input_string):
    admin_skills = fetch_all("SELECT skill_name FROM Skill")
    results = []
    for skill in admin_skills:
        admin_skill = skill[0]
        methods, similarity = match_skill(input_string, admin_skill)
        if methods:
            results.append({
                "admin_skill": admin_skill,
                "matching_methods": methods,
                "matching_score": similarity
            })
    return sorted(results, key=lambda x: x["matching_score"], reverse=True)

# Main program
if __name__ == "__main__":
    print("Welcome to the Skill Matching System!")

    # Initialize default skills
    initialize_default_skills()

    role = input("Are you an administrator or a user? (admin/user): ").strip().lower()

    if role == "admin":
        admin_menu()
    elif role == "user":
        action = input("Do you want to register or log in? (register/login): ").strip().lower()
        if action == "register":
            user_id = register_user()
        elif action == "login":
            user_id = login_user()
        else:
            print("Invalid choice. Please restart the program.")
            exit()

        if user_id:
            input_string = input("Enter the skill you want to match: ").strip()
            results = submit_query(user_id, input_string)
            print("\n--- Matching Results ---")
            for result in results:
                print(f"Skill: {result['admin_skill']}")
                print(f"Matching Methods: {', '.join(result['matching_methods'])}")
                print(f"Matching Score: {result['matching_score']:.2f}")
    else:
        print("Invalid role. Please restart the program.")


