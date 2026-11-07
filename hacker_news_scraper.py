from bs4 import BeautifulSoup
import requests
import pandas as pd


def scrape_hacker_news():
    print("Connecting to Hacker News to harvest live tech data...")

    # Real websites often block scripts that don't look like a real browser.
    # We add a USer-Agent header to identify our script ethically

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    url = "https://news.ycombinator.com/"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(
            f"Failed to retrieve data from Hacker News. Status code: {response.status_code}"
        )
        return
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all story rows on the page
    story_rows = soup.find_all("tr", class_="athing")

    data = []

    for row in story_rows:
        # Extract title
        title_tag = row.find("span", class_="titleline").find("a")
        title = title_tag.text if title_tag else "No Title"

        # Extract points (upvotes)
        subtext_row = row.find_next_sibling("tr")
        score_tag = subtext_row.find("span", class_="score")
        if score_tag:
            # Converts "54 points" into an integer 54
            points = int(score_tag.text.split()[0])
        else:
            points = 0  # Default if points aren't visible yet

        # Extract comments count
        subtext_links = subtext_row.find_all("a")
        comments_count = 0
        for link in subtext_links:
            if "comment" in link.text:
                # Extracts digits from text like "15 comments"
                comments_text = "".join(filter(str.isdigit, link.text))
                if comments_text:
                    comments_count = int(comments_text)
        data.append({"Title": title, "Points": points, "Comments": comments_count})

    # Convert into a Pandas DataFrame for data manipulation
    df = pd.DataFrame(data)

    print("\n--- First 5 Rows of Live Hacker News Data ---")
    print(df.head())

    print("\n--- Statistical Analysis & Insights ---")
    print(f"Total Stories Scraped: {len(df)}")
    print(f"Average Article Points (Upvotes): {df['Points'].mean():.1f}")
    print(f"Average Comments per Story: {df['Comments'].mean():.1f}")

    # Find the top-voted story
    top_story = df.loc[df["Points"].idxmax()]
    print(f"\n🔥 Top Voted Story:")
    print(f"   Title: {top_story['Title']}")
    print(f"   Points: {top_story['Points']}  |  Comments: {top_story['Comments']}")

    # Export clean dataset
    df.to_csv("hacker_news_analysis.csv", index=False)
    print("\n✅ Cleaned live dataset exported to 'hacker_news_analysis.csv'!")


# Run the script
scrape_hacker_news()
