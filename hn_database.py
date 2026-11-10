from bs4 import BeautifulSoup
import pandas as pd
import requests
import sqlite3


def scrape_and_store_hn():
    print("Stepp 1: Harvesting live tech date from Hacker News...")
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    url = "https://news.ycombinator.com/"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch page/ Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, "html.parser")
    story_rows = soup.find_all("tr", class_="athing")
    data = []

    for row in story_rows:
        title_tag = row.find("span", class_="titleline").find("a")
        title = title_tag.text if title_tag else "No Title"

        subtext_row = row.find_next_sibling("tr")
        score_tag = subtext_row.find("span", class_="score")
        points = int(score_tag.text.split()[0]) if score_tag else 0

        subtext_links = subtext_row.find_all("a")
        comments = 0
        for link in subtext_links:
            if "comment" in link.text:
                comment_text = "".join(filter(str.isdigit, link.text))
                if comment_text:
                    comments = int(comment_text)
        data.append({"title": title, "points": points, "comments": comments})

    # Convert to Pandas DataFrame
    df = pd.DataFrame(data)
    print(f"Successfully harvested {len(df)} stories.")

    print("\nStep 2: Connecting to SQLite database and storing data...")

    # This creates a file name 'hacker_news.db' in your folder automatically
    conn = sqlite3.connect("hacker_news.db")

    # Write the Pandas DataFrame directly into an SQLite table named 'top_stories'
    # if_exists='replace' overwrites the table if it run the script again

    df.to_sql("top_stories", conn, if_exists="replace", index=False)
    print("[Success] Data successfully written to SQLite table 'top_stories'!")

    print("\nStep 3: Running a SQL Query directly on the database....")

    # Write a SQL query to find stories with more than 50 points
    query = """
    SELECT Title, points, Comments
    FROM top_stories
    WHERE points > 50
    ORDER BY points DESC
    """

    # Execute the query and load results back into a new Pandas DataFrame
    filtered_df = pd.read_sql_query(query, conn)

    print(f"\nFound {len(filtered_df)} stories with more than 50 points:")
    print(filtered_df.head(10))  # Display the first 10 results

    # Always close the database connection when finished

    conn.close()


# Run the script
scrape_and_store_hn()
