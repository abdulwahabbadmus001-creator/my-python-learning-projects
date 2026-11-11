import pandas as pd
import sqlite3
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split


def analyze_and_predict_hn():
  print(
      "Step 1: Connecting to SQLite database and loading stored Hacker News"
      " data..."
  )
  conn = sqlite3.connect("hacker_news.db")

  # Read data from our SQLite table into a Pandas DataFrame
  df = pd.read_sql_query("SELECT * FROM top_stories", conn)
  conn.close()

  # Standardize column names to capitalize first letters
  df.columns = [c.capitalize() for c in df.columns]

  if len(df) == 0:
    print(
        "Your database is currently empty! Run your scraper script first to"
        " populate data."
    )
    return

  print(f"Successfully loaded {len(df)} records from database.")

  print("\n--- Step 2: Feature Engineering & Statistical Analysis ---")
  # Feature 1: Length of the article title (characters count)
  df["Title_Length"] = df["Title"].str.len()

  # Feature 2: Word count in the title
  df["Word_Count"] = df["Title"].apply(lambda x: len(x.split()))

  # Feature 3: Check if specific tech keywords are in the article
  df["Mentions_Python"] = (
      df["Title"].str.contains("Python", case=False, na=False).astype(int)
  )
  df["Mentions_AI"] = (
      df["Title"]
      .str.contains("AI|Artificial Intelligence", case=False, na=False)
      .astype(int)
  )

  # Statistical Correlation Matrix
  print("\nCorrelation between Title Features and Article Points:")
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
  print(correlation["Points"].round(3))

  print(
      "\n--- Step 3: Machine Learning Model (Predicting High-Engagement Stories) ---"
  )
  # Define a target: Is the article "Popular" (Points > Median Points)?
  median_points = df["Points"].median()
  df["Is_Popular"] = (df["Points"] > median_points).astype(int)
  print(
      f"Median benchmark for popularity: {median_points} points (1 = High"
      " Engagement, 0 = Low Engagement)"
  )

  # Select features (X) and target (y)
  X = df[["Title_Length", "Word_Count", "Mentions_Python", "Mentions_AI"]]
  y = df["Is_Popular"]

  # Check if we have enough variance to train
  if y.nunique() < 2:
      print(
          "\n[Notice] Not enough variation in points yet to train a classifier."
          " Try scraping again later when points vary more!"
      )
      return

  # Split data into Training set (80%) and Testing set (20%)
  X_train, X_test, y_train, y_test = train_test_split(
      X, y, test_size=0.2, random_state=42
  )

  # Initialize and train a Machine Learning classifier (Logistic Regression)
  model = LogisticRegression()
  model.fit(X_train, y_train)

  # Make predictions on the test set
  y_pred = model.predict(X_test)

  print("\n--- Step 4: Model Evaluation ---")
  accuracy = accuracy_score(y_test, y_pred)
  print(f"Model Accuracy: {accuracy * 100:.1f}%")
  print("\nDetailed Classification Report:")
  print(classification_report(y_test, y_pred, zero_division=0))


# Run the script
analyze_and_predict_hn()
