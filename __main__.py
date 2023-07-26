import requests
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta


BALLSTON_URL = "https://www.regmovies.com/theatres/regal-ballston-quarter/0296"
BALLSTON_CODE = "0296"
TARGET_AUDITORIUM = "7"
# TARGET_FILMS = ["Barbie", "Oppenheimer", "Indiana Jones and the Dial of Destiny", "Mission: Impossible - Dead Reckoning - Part One"]
DAYS = 30


def generate_dates_from_today(num_days):
    today = datetime.today()
    for i in range(num_days):
        yield (today + timedelta(days=i)).strftime("%Y-%m-%d")


def get_day_name_from_date(date):
    return datetime.strptime(date, "%Y-%m-%d").strftime("%A")


def main():
    print(f"Showtimes in auditorium {TARGET_AUDITORIUM} at theatre {BALLSTON_CODE} for {DAYS} days:")
    homepage = requests.get(f"https://www.regmovies.com/theatres/regal-ballston-quarter/{BALLSTON_CODE}", 
                            headers={
                                "authority": "www.regmovies.com",
                                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                                "accept-language": "en-US,en;q=0.7",
                                "cache-control": "max-age=0",
                                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                                "compressed"
                            })
    tenant_id_loc = homepage.text.find("tenantId")
    tenant_id = homepage.text[tenant_id_loc + 12:tenant_id_loc + homepage.text[tenant_id_loc:].find("\n") - 2]
    for date in generate_dates_from_today(30):
        data = requests.get(f"https://www.regmovies.com/us/data-api-service/v1/quickbook/{tenant_id}/film-events/in-cinema/{BALLSTON_CODE}/at-date/{date}?attr=&lang=en_US", 
                            headers={
                                "authority": "www.regmovies.com",
                                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                                "accept-language": "en-US,en;q=0.7",
                                "cache-control": "max-age=0",
                                "referer": f"https://www.regmovies.com/theatres/regal-ballston-quarter/{BALLSTON_CODE}",
                                "sec-ch-ua": "^\"Not/A)Brand^\";v=\"99\", ^\"Brave^\";v=\"115\", ^\"Chromium^\";v=\"115\"",
                                "sec-ch-ua-mobile": "?0",
                                "sec-ch-ua-platform": "^\"Windows^\"",
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                            }).json()
        events = data["body"]["events"]
        films = data["body"]["films"]
        # targets = filter(lambda film: film["name"] in TARGET_FILMS, films)
        targets = films
        target_ids = list(map(lambda film: film["id"], targets))
        id_to_name = {film["id"]: film["name"] for film in films}
        for event in events:
            if event["auditoriumTinyName"] == TARGET_AUDITORIUM:
                if event["filmId"] in target_ids:
                    time_in_am_pm = datetime.strptime(event["eventDateTime"], "%Y-%m-%dT%H:%M:%S").strftime("%I:%M %p")
                    print(f"{id_to_name[event['filmId']]} on {get_day_name_from_date(date)} at {time_in_am_pm}")


if __name__ == "__main__":
    main()