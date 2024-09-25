from bs4 import BeautifulSoup
from requests import get as requests_get, exceptions as requests_exceptions
from re import findall, compile

class pyboxd():

    class user():

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


        def __str__(self):
            userInfo = f'Username: {self.username}\nFilms: {self.films}\nThis Year:{self.thisYear}\nFollowing: {self.following}\nFollowers: {self.followers}\nFavorite Films: {self.favoriteFilms}\nPatron: {self.isPatron}'
            return userInfo
        
        def set_username(self, username) -> None:
            try:
                self.mainResponse = requests_get(f'https://letterboxd.com/{username}/').text
                self.mainSoup =  BeautifulSoup(self.mainResponse, 'html.parser')
                self.username = username
            except requests_exceptions.RequestException as e:
                print(f"Failed to retrieve data: {e}")
                return
     
        def get_profile_stats(self) -> None:
            
            self.profileStats = pyboxd.scrape_profile_stats(soup = self.mainSoup)
            self.films = self.profileStats[0]
            self.thisYear = self.profileStats[1]
            self.following = self.profileStats[2]
            self.followers = self.profileStats[3]
            self.favoriteFilms = self.profileStats[4]
            self.isPatron = self.profileStats[5]
    
        def get_user_watched_films(self) -> None:
            self.filmsResponse = requests_get(f'https://letterboxd.com/{self.username}/films/').text
            self.filmsSoup = BeautifulSoup(self.filmsResponse, 'html.parser')
            self.watchedFilms = pyboxd.scrape_watched_films(user = self.username, soup = self.filmsSoup)

        def get_user_watchlist(self) -> None:
            self.filmsResponse = requests_get(f'https://letterboxd.com/{self.username}/watchlist/').text
            self.filmsSoup = BeautifulSoup(self.filmsResponse, 'html.parser')
            self.watchlist = pyboxd.scrape_watchlist(user = self.username, soup = self.filmsSoup)

        def get_user_network(self) -> None:
            self.networkFollowingResponse = requests_get(f'https://letterboxd.com/{self.username}/following/').text
            self.networkFollowerResponse = requests_get(f'https://letterboxd.com/{self.username}/followers/').text
            self.networkFollowingSoup = BeautifulSoup(self.networkFollowingResponse, 'html.parser')
            self.networkFollowerSoup = BeautifulSoup(self.networkFollowerResponse, 'html.parser')
            self.userNetwork = pyboxd.scrape_user_network(user = self.username, soup = self.networkFollowingSoup, soup2 = self.networkFollowerSoup)

        def get_user_bio(self) -> None:
            self.userBio = pyboxd.scrapeBio(soup = self.mainSoup)

    @staticmethod

    def scrape_profile_stats(soup) -> list:
        stats = findall(r'<span class="value">(\d+)</span>', str(soup))

        # find <section id="favourites" class="section"> 
        favs_soup = soup.find('section', {'id': 'favourites'})

        # find data-film-slug="([^"]+)" in the section
        favorite_films = findall(r'data-film-slug="([^"]+)"', str(favs_soup))
        stats.append(favorite_films)

        # find <span class="badge -patron ">Patron</span> in the soup
        patron = soup.find('span', class_='badge -patron')
        if patron:
            stats.append(True)
        else:
            stats.append(False)
        
        return stats
       
    def scrape_watched_films(user:str, soup:str) -> list:
        data = []
        pages = findall(r'films/page/(\d+)/', str(soup))
        if len(pages) == 0:
            pages = ['1']
        last_page = max([int(page) for page in pages])
        for i in range(1, last_page + 1):
            response = requests_get(f'https://letterboxd.com/{user}/films/page/{i}/').text
            soup = BeautifulSoup(response, 'html.parser')
            film_slugs = findall(r'data-film-slug="([^"]+)"', str(soup))
            data.extend(film_slugs)
        return data
    
    def scrape_watchlist(user:str, soup:str) -> list:
        data = []
        pages = findall(r'watchlist/page/(\d+)/', str(soup))
        if len(pages) == 0:
            pages = ['1']
        last_page = max([int(page) for page in pages])
        for i in range(1, last_page + 1):
            response = requests_get(f'https://letterboxd.com/{user}/watchlist/page/{i}/').text
            soup = BeautifulSoup(response, 'html.parser')
            film_slugs = findall(r'data-film-slug="([^"]+)"', str(soup))
            data.extend(film_slugs)
        return data
    
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

    def scrapeBio(soup:BeautifulSoup) -> str:
        bio = soup.find('div', class_ = "collapsible-text body-text -small js-bio-content")
        bio = bio.find_all('p')
        bio = [x.text for x in bio]
        return bio
    
def main():
    user = pyboxd.user()
    user.set_username('fer_nwn')
    user.get_profile_stats()
    #user.get_user_watched_films()
    #user.get_user_watchlist()
    #user.get_user_network()
    #user.get_user_bio()
    
    print(user)
    #print(user.watchedFilms)
    #print(user.watchlist)
    #print(user.userNetwork)
    #print(user.userBio)
main()