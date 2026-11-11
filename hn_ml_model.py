import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split


def analyze_and_predict_hn():
    print("Step 1: Connecting to SQLite database...")
    conn = sqlite3.connect("hacker_news.db")
    df = pd.read_sql_query("SELECT * FROM top_stories", conn)
    conn.close()

    if len(df) == 0:
        print("Your database is empty! Run your scraper script first.")
        return

    # Standardize column names to capitalize first letters
    df.columns = [c.capitalize() for c in df.columns]

    print(f"Successfully loaded {len(df)} records from database.")

    print("\n--- Step 2: Feature Engineering & Statistical Analysis ---")
    df["Title_Length"] = df["Title"].str.len()
    df["Word_Count"] = df["Title"].apply(lambda x: len(str(x).split()))
    df["Mentions_Python"] = (
        df["Title"].str.contains("Python", case=False, na=False).astype(int)
    )
    df["Mentions_AI"] = (
        df["Title"]
        .str.contains("AI|Artificial Intelligence|LLM", case=False, na=False)
        .astype(int)
    )

    # Calculate correlation with Points
    correlation = df[
        [
            "Points",
            "Comments",
            "Title_Length",
            "Word_Count",
            "Mentions_Python",
            "Mentions_AI",
        ]
    ].corr()
    points_corr = correlation["Points"].drop("Points")  # Exclude self-correlation
    print(points_corr.round(3))

    print("\n--- Step 3: Generating Matplotlib Visual Chart ---")
    # Create a visual bar chart of the correlations
    plt.figure(figsize=(8, 5))
    colors = ["green" if val > 0 else "crimson" for val in points_corr]
    points_corr.plot(kind="bar", color=colors, edgecolor="black")

    plt.title(
        "Correlation of Article Features with Hacker News Points",
        fontsize=12,
        fontweight="bold",
    )
    plt.xlabel("Features", fontsize=10)
    plt.ylabel("Correlation Coefficient (-1 to 1)", fontsize=10)
    plt.axhline(0, color="grey", linewidth=0.8, linestyle="--")
    plt.grid(axis="y", linestyle=":", alpha=0.7)
    plt.xticks(rotation=15)
    plt.tight_layout()

    # Save the chart as an image file and show it
    plt.savefig("hacker_news_correlations.png")
    print("[Success] Chart saved as 'hacker_news_correlations.png'!")
    plt.show()

    print(
        "\n--- Step 4: Machine Learning Model (Predicting High-Engagement Stories) ---"
    )
    median_points = df["Points"].median()
    df["Is_Popular"] = (df["Points"] > median_points).astype(int)
    print(
        f"Median benchmark for popularity: {median_points} points (1 = High"
        " Engagement, 0 = Low Engagement)"
    )

    X = df[["Title_Length", "Word_Count", "Mentions_Python", "Mentions_AI"]]
    y = df["Is_Popular"]

    if y.nunique() < 2:
        print("\n[Notice] Not enough variation in points yet to train a classifier.")
        return

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model = LogisticRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print("\n--- Step 5: Model Evaluation ---")
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy * 100:.1f}%")


# Run the script
analyze_and_predict_hn()
