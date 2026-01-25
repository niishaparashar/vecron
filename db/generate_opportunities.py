import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

# ---------------- CONFIG ----------------
NUM_OPPORTUNITIES = 120

job_roles = {
    "Data Analyst": {
        "skills": "Python, SQL, Excel, Pandas, Data Visualization, Statistics",
        "department": "Data",
        "category": "Data"
    },
    "Data Scientist": {
        "skills": "Python, Machine Learning, SQL, Statistics, Pandas, Scikit-learn",
        "department": "Data",
        "category": "Data"
    },
    "Machine Learning Engineer": {
        "skills": "Python, TensorFlow, PyTorch, MLOps, SQL, Docker",
        "department": "Data",
        "category": "Data"
    },
    "Software Engineer": {
        "skills": "Python, Java, Data Structures, Algorithms, Git, REST APIs",
        "department": "Engineering",
        "category": "Engineering"
    },
    "Backend Developer": {
        "skills": "Python, SQL, APIs, Microservices, Git, Docker",
        "department": "Engineering",
        "category": "Engineering"
    },
    "Frontend Developer": {
        "skills": "HTML, CSS, JavaScript, React, Git, Responsive Design",
        "department": "Engineering",
        "category": "Engineering"
    },
    "Business Analyst": {
        "skills": "SQL, Excel, Business Analysis, Stakeholder Management, Documentation",
        "department": "Product",
        "category": "Product"
    },
    "DevOps Engineer": {
        "skills": "AWS, Docker, Kubernetes, CI/CD, Linux, Monitoring",
        "department": "Operations",
        "category": "Operations"
    }
}

companies = [
    "Infosys", "TCS", "Wipro", "Accenture", "Cognizant",
    "Capgemini", "Tech Mahindra", "IBM", "Oracle",
    "Deloitte", "PwC", "EY", "KPMG",
    "Flipkart", "Amazon", "Google", "Microsoft",
    "Zoho", "Freshworks", "Paytm", "PhonePe",
    "StartupLabs", "NextGen Tech", "CloudNova", "DataEdge"
]

employment_types = ["Full-time", "Internship", "Part-time"]
experience_levels = ["Fresher", "Junior", "Mid"]
workplace_types = ["Remote", "Hybrid", "On-site"]
locations = ["Bangalore", "Hyderabad", "Pune", "Chennai", "Remote"]

# ---------------- GENERATE DATA ----------------
rows = []

for i in range(1, NUM_OPPORTUNITIES + 1):
    title = random.choice(list(job_roles.keys()))
    role_info = job_roles[title]

    rows.append([
        i,  # opportunity_id
        random.choice(companies),
        title,
        random.choice(employment_types),
        random.choice(experience_levels),
        role_info["skills"],
        role_info["department"],
        role_info["category"],
        random.choice(locations),
        random.choice(workplace_types),
        (datetime.now() - timedelta(days=random.randint(0, 60))).date()
    ])

# ---------------- SAVE CSV ----------------
df = pd.DataFrame(rows, columns=[
    "opportunity_id",
    "company_name",
    "title",
    "employment_type",
    "experience_level",
    "skills_required",
    "department",
    "category",
    "location",
    "workplace_type",
    "posted_on"
])

df.to_csv("db/opportunity.csv", index=False)

print("✅ opportunity.csv generated successfully")
print(df.head())
