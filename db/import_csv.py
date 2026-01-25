import sqlite3
import pandas as pd

DB_NAME = "vecron.db"

def import_users(conn):
    users = pd.read_csv("db/users.csv")

    cursor = conn.cursor()

    cursor.executemany("""
        INSERT INTO users (
            user_id,
            full_name,
            email,
            password_hash,
            current_status,
            education_level,
            branch,
            experience_level,
            skills,
            preferred_category,
            preferred_workplace,
            preferred_employment_type,
            preferred_location,
            joined_on
        )
        VALUES (?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        (
            row["user_id"],
            row["full_name"],
            row["email"],
            "TEMP_HASH",  # placeholder (real hash added during registration)
            row["current_status"],
            row["education_level"],
            row["branch"],
            row["experience_level"],
            row["skills"],
            row["preferred_category"],
            row["preferred_workplace"],
            row["preferred_employment_type"],
            row["preferred_location"],
            row["joined_on"]
        )
        for _, row in users.iterrows()
    ])

    print(f"✅ Imported {len(users)} users")


def import_opportunities(conn):
    jobs = pd.read_csv("db/opportunity.csv")

    cursor = conn.cursor()

    cursor.executemany("""
        INSERT INTO opportunities (
            company_name,
            title,
            employment_type,
            experience_level,
            skills_required,
            department,
            category,
            location,
            workplace_type,
            posted_on
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        (
            row["company_name"],
            row["title"],
            row["employment_type"],
            row["experience_level"],
            row["skills_required"],
            row["department"],
            row["category"],
            row["location"],
            row["workplace_type"],
            row["posted_on"]
        )
        for _, row in jobs.iterrows()
    ])

    print(f"✅ Imported {len(jobs)} opportunities")


def import_interactions(conn):
    interactions = pd.read_csv("db/interactions.csv")

    cursor = conn.cursor()

    cursor.executemany("""
        INSERT INTO interactions (
            user_id,
            opportunity_id,
            interaction_type,
            interaction_weight,
            interacted_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, [
        (
            int(row["user_id"]),
            int(row["opportunity_id"]),
            row["interaction_type"],
            int(row["interaction_weight"]),
            row["interacted_at"]
        )
        for _, row in interactions.iterrows()
    ])

    print(f"✅ Imported {len(interactions)} interactions")


def main():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print("🚀 Starting CSV import...\n")

    #  Clear existing data
    cursor.execute("DELETE FROM interactions")
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM opportunities")
    conn.commit()

    import_users(conn)
    import_opportunities(conn)
    import_interactions(conn)

    conn.commit()
    conn.close()

    print("\n🎉 All CSVs imported successfully.")



if __name__ == "__main__":
    main()

