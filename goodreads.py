import requests

KEY = "rX3vKLsj4JzA9Us9JAMHIA"

def get_ratings(isbn):
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": isbn})
    data = res.json()['books'][0]
    return {'ratings_cnt': data['work_ratings_count'], 'av_rating': data['average_rating']}
