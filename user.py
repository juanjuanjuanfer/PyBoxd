from bs4 import BeautifulSoup
from requests import get as requests_get, exceptions as requests_exceptions
from re import findall, compile, DOTALL
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import chain


class User():

    def __init__(self) -> None: 
        self.username = None
        self.films = 0
        self.thisYear = 0
        self.following = 0
        self.followers = 0
        self.favoriteFilms = []
        self.mainResponse = None
        self.mainSoup = None
        self.filmsResponse = None
        self.filmsSoup = None
        self.watchedFilms = []
        self.watchlist = []
        self.userNetwork = {}
        self.isPatron = False
        self.isPro = False
        self.userLists = 0
        self.userImage = None


    def __str__(self):
        userInfo = f'Username: {self.username}\nFilms: {self.films}\nThis Year:{self.thisYear}\nLists: {self.userLists}\nFollowing: {self.following}\nFollowers: {self.followers}\nFavorite Films: {self.favoriteFilms}\nPatron: {self.isPatron}\nPro: {self.isPro}'
        return userInfo
    
    def set_username(self, username) -> None:
        try:
            self.mainResponse = requests_get(f'https://letterboxd.com/{username}/')
            self.mainSoup =  BeautifulSoup(self.mainResponse.text, 'html.parser')
            self.username = username
        except requests_exceptions.RequestException as e:
            print(f"Failed to retrieve data: {e}")
            return
    
    def get_profile_stats(self) -> None:
        
        self.profileStats = User.scrape_profile_stats(soup = self.mainSoup)
        self.films = self.profileStats[0]['Films']
        self.thisYear = self.profileStats[0]['This year']
        self.following = self.profileStats[0]['Following']
        self.followers = self.profileStats[0]['Followers']
        self.userLists = self.profileStats[0]['Lists']   
        self.favoriteFilms = self.profileStats[1]
        self.isPatron = self.profileStats[2][0]
        self.isPro = self.profileStats[2][1]

    def get_user_watched_films(self) -> None:
        self.filmsResponse = requests_get(f'https://letterboxd.com/{self.username}/films/').text
        self.filmsSoup = BeautifulSoup(self.filmsResponse, 'html.parser')
        self.watchedFilms = User.scrape_watched_films(user = self.username, soup = self.filmsSoup)

    def get_user_watchlist(self) -> None:
        self.filmsResponse = requests_get(f'https://letterboxd.com/{self.username}/watchlist/').text
        self.filmsSoup = BeautifulSoup(self.filmsResponse, 'html.parser')
        self.watchlist = User.scrape_watchlist(user = self.username, soup = self.filmsSoup)

    def get_user_network(self) -> None:
        self.networkFollowingResponse = requests_get(f'https://letterboxd.com/{self.username}/following/').text
        self.networkFollowerResponse = requests_get(f'https://letterboxd.com/{self.username}/followers/').text
        self.networkFollowingSoup = BeautifulSoup(self.networkFollowingResponse, 'html.parser')
        self.networkFollowerSoup = BeautifulSoup(self.networkFollowerResponse, 'html.parser')
        self.userNetwork = User.scrape_user_network(user = self.username, soup = self.networkFollowingSoup, soup2 = self.networkFollowerSoup)

    def get_user_bio(self) -> None:
        self.userBio = User.scrapeBio(soup = self.mainSoup)

    def get_user_image(self) -> None:
        self.userImage = findall(r'<img\s+[^>]*src="([^"]+)"', str(self.mainSoup.find('span', class_='avatar -a110 -large')))




    @staticmethod
    def scrape_profile_stats(soup:BeautifulSoup) -> list:
        base_dict = {'Films': 0, 'This year': 0, 'Following': 0, 'Followers': 0, 'Lists': 0}
        stats = findall(r'<span class="value">([\d,]+)</span>', str(soup))
        defintion = findall(r'<span class="definition">([\w\s]+)</span>', str(soup))
        stats_dict = dict(zip(defintion, stats))
        base_dict.update(stats_dict)

        favorite_films = findall(r'data-film-slug="([^"]+)"', str(soup.find('section', {'id': 'favourites'})))

        badges = []
        badges.append([True if soup.find('span', class_='badge -patron') else False])
        badges.append([True if soup.find('span', class_='badge -pro') else False])

        return [base_dict, favorite_films, badges]

    @staticmethod
    def process_page(user:str, i:int, page_type:str='films') -> list:
        try:
            response = requests_get(f'https://letterboxd.com/{user}/{page_type}/page/{i}/')
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return findall(r'data-film-slug="([^"]+)"', str(soup))
        except requests_exceptions as e:
            print(f"Error fetching page {i}: {e}")
            return []

    @staticmethod
    def scrape_watched_films(user: str, soup: BeautifulSoup) -> list:
        pages = findall(r'films/page/(\d+)/', str(soup))
        if len(pages) == 0:
            pages = ['1']
        last_page = max([int(page) for page in pages])
        
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(user.process_page, user, i, page_type="films") for i in range(1, last_page + 1)]
        
            film_slugs = []
            for future in as_completed(futures):
                film_slugs.append(future.result())

        return list(chain.from_iterable(film_slugs))

    @staticmethod
    def scrape_watchlist(user:str, soup:BeautifulSoup) -> list:
        pages = findall(r'watchlist/page/(\d+)/', str(soup))
        if len(pages) == 0:
            pages = ['1']
        last_page = max([int(page) for page in pages])
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(user.process_page, user, i, page_type="watchlist") for i in range(1, last_page + 1)]

            film_slugs = []
            for future in as_completed(futures):
                film_slugs.append(future.result())
        
        return list(chain.from_iterable(film_slugs))

    @staticmethod    
    def scrape_user_network(user:str,soup:BeautifulSoup, soup2:BeautifulSoup) -> dict:
        dataFollowing = []
        dataFollowers = []
        pages =  findall(r'following/page/(\d+)/', str(soup))
        if len(pages) == 0:
            pages = ['1']
        last_page = max([int(page) for page in pages])
        for i in range(1, last_page + 1):
            response = requests_get(f'https://letterboxd.com/{user}/following/page/{i}/').text
            soup = BeautifulSoup(response, 'html.parser')
            pattern = compile(r'href="/([A-Za-z0-9_-]+)/"')
            tags = soup.find_all('a', class_='name')
            hrefs = [href for tag in tags for href in findall(pattern, str(tag))]
            dataFollowing.extend(hrefs)

        pages =  findall(r'followers/page/(\d+)/', str(soup2))
        if len(pages) == 0:
            pages = ['1']
        last_page = max([int(page) for page in pages])
        for i in range(1, last_page + 1):
            response = requests_get(f'https://letterboxd.com/{user}/followers/page/{i}/').text
            soup = BeautifulSoup(response, 'html.parser')
            pattern = compile(r'href="/([A-Za-z0-9_-]+)/"')
            tags = soup.find_all('a', class_='name')
            hrefs = [href for tag in tags for href in findall(pattern, str(tag))]
            dataFollowers.extend(hrefs)

        return {"following": dataFollowing, "followers": dataFollowers}

    @staticmethod
    def scrapeBio(soup:BeautifulSoup) -> str:
        bio = soup.find('div', class_ = "collapsible-text body-text -small js-bio-content")
        bio = bio.find_all('p')
        bio = [x.text for x in bio]
        return bio

    @staticmethod
    def process_diary_page(user, i):
        try:
            response = requests_get(f'https://letterboxd.com/{user}/films/diary/page/{i}/')
            response.raise_for_status()  # Raise an error for bad status codes
            soup = BeautifulSoup(response.text, 'html.parser')
            return {
                "dates": user.find_dates(soup),
                "film_slugs": user.find_film_slugs(soup),
                "ratings": user.find_ratings(soup),
                "likes": user.find_likes(soup),
                "rewatches": user.find_rewatches(soup),
                "reviews": user.find_reviews(soup)
            }
        except requests_exceptions as e:
            print(f"Error fetching page {i}: {e}")
            return {
                "dates": [], "film_slugs": [], "ratings": [],
                "likes": [], "rewatches": [], "reviews": []
            }
        
    @staticmethod    
    def scrape_user_diary(user:str, soup:BeautifulSoup) -> list:
        pages = findall(r'films/diary/page/(\d+)/', str(soup))
        if len(pages) == 0:
            pages = ['1']
        last_page = max([int(page) for page in pages])

        diary_data = {
            "dates": user.find_dates(soup),
            "film_slugs": user.find_film_slugs(soup),
            "ratings": user.find_ratings(soup),
            "likes": user.find_likes(soup),
            "rewatches": user.find_rewatches(soup),
            "reviews": user.find_reviews(soup)
        }

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(user.process_diary_page, user, i) for i in range(2, last_page + 1)]
            
            for future in as_completed(futures):
                page_data = future.result()
                diary_data["dates"].extend(page_data["dates"])
                diary_data["film_slugs"].extend(page_data["film_slugs"])
                diary_data["ratings"].extend(page_data["ratings"])
                diary_data["likes"].extend(page_data["likes"])
                diary_data["rewatches"].extend(page_data["rewatches"])
                diary_data["reviews"].extend(page_data["reviews"])

        return [
            {
                "date": diary_data["dates"][j],
                "film_slug": diary_data["film_slugs"][j],
                "rating": diary_data["ratings"][j],
                "like": diary_data["likes"][j],
                "rewatch": diary_data["rewatches"][j],
                "review": diary_data["reviews"][j]
            }
            for j in range(len(diary_data["film_slugs"]))
        ]

    @staticmethod
    def find_dates(soup:object) -> list:
        return findall(r'films/diary/for/(\d{4}/\d{2}/\d{2})/', str(soup))

    @staticmethod    
    def find_film_slugs(soup:object) -> list:
        return findall(r'data-film-slug="([^"]+)"', str(soup))[::2]

    @staticmethod    
    def find_ratings(soup:object) -> list:
        rating_list = []
        for rating_tag in soup.find_all('span', class_= 'rating'):
            rating_class = rating_tag.get('class', [])
            rated_value = next((cls.split('-')[-1] for cls in rating_class if cls.startswith('rated-')), None)

            if rated_value:
                rating_list.append(int(rated_value))
            else:
                rating_list.append('NA')
        return rating_list

    @staticmethod
    def find_likes(soup:object) -> list:
        return [True if 'icon-liked' in like else False for like in findall(r'<td class="td-like center diary-like">(.*?)</td>', str(soup))]

    @staticmethod    
    def find_rewatches(soup:object) -> list:
        return [False if 'icon-status' in rewatch else True for rewatch in findall(r'<td class="td-rewatch center( icon-status-off)?">', str(soup))]        

    @staticmethod    
    def find_reviews(soup:object) -> list:
        return [
            f'https://letterboxd.com{findall(r"href=\"([^\"]+)\"", td)[0]}reviews/' 
            if findall(r'href="([^"]+)"', td) 
            else 'NA' 
            for td in findall(r'<td class="td-review center(?: [^"]*)?">(.*?)</td>', str(soup), DOTALL)
        ]

class user_diary():
    
    def __init__(self, user:object) -> None:
        self.user = user.username
        self.userDiary = None

    def __str__(self) -> str:
        userDriaryInfo = f'Username: {self.user}'
        return userDriaryInfo

    def get_user_diary(self) -> None:
        self.userDiaryResponse = requests_get(f'https://letterboxd.com/{self.user}/films/diary/').text
        self.userDiarySoup = BeautifulSoup(self.userDiaryResponse, 'html.parser')
        self.userDiary = User.scrape_user_diary(user = self.user, soup = self.userDiarySoup)




