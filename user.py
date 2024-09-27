from bs4 import BeautifulSoup
from requests import get as requests_get, exceptions as requests_exceptions
from re import findall, compile, DOTALL

class PyBoxd():

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
            self.isPro = False
            self.userLists = 0


        def __str__(self):
            userInfo = f'Username: {self.username}\nFilms: {self.films}\nThis Year:{self.thisYear}\nLists: {self.userLists}\nFollowing: {self.following}\nFollowers: {self.followers}\nFavorite Films: {self.favoriteFilms}\nPatron: {self.isPatron}\nPro: {self.isPro}'
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
            
            self.profileStats = PyBoxd.scrape_profile_stats(soup = self.mainSoup)
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
            self.watchedFilms = PyBoxd.scrape_watched_films(user = self.username, soup = self.filmsSoup)

        def get_user_watchlist(self) -> None:
            self.filmsResponse = requests_get(f'https://letterboxd.com/{self.username}/watchlist/').text
            self.filmsSoup = BeautifulSoup(self.filmsResponse, 'html.parser')
            self.watchlist = PyBoxd.scrape_watchlist(user = self.username, soup = self.filmsSoup)

        def get_user_network(self) -> None:
            self.networkFollowingResponse = requests_get(f'https://letterboxd.com/{self.username}/following/').text
            self.networkFollowerResponse = requests_get(f'https://letterboxd.com/{self.username}/followers/').text
            self.networkFollowingSoup = BeautifulSoup(self.networkFollowingResponse, 'html.parser')
            self.networkFollowerSoup = BeautifulSoup(self.networkFollowerResponse, 'html.parser')
            self.userNetwork = PyBoxd.scrape_user_network(user = self.username, soup = self.networkFollowingSoup, soup2 = self.networkFollowerSoup)

        def get_user_bio(self) -> None:
            self.userBio = PyBoxd.scrapeBio(soup = self.mainSoup)

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
            self.userDiary = PyBoxd.scrape_user_diary(user = self.user, soup = self.userDiarySoup)

    @staticmethod

    def scrape_profile_stats(soup:BeautifulSoup) -> list:
        stats = findall(r'<span class="value">([\d,]+)</span>', str(soup))
        defintion = findall(r'<span class="definition">([\w\s]+)</span>', str(soup))
        stats_dict = dict(zip(defintion, stats))
        base_dict = {'Films': 0, 'This year': 0, 'Following': 0, 'Followers': 0, 'Lists': 0}
        # update the base_dict with the stats_dict
        base_dict.update(stats_dict)


        # find <section id="favourites" class="section"> 
        favs_soup = soup.find('section', {'id': 'favourites'})

        # find data-film-slug="([^"]+)" in the section
        favorite_films = findall(r'data-film-slug="([^"]+)"', str(favs_soup))

        badges = []
        # find <span class="badge -patron ">Patron</span> in the soup
        patron = soup.find('span', class_='badge -patron')
        if patron:
            badges.append(True)
        else:
            badges.append(False)
        
        pro = soup.find('span', class_='badge -pro')
        if pro:
            badges.append(True)
        else:
            badges.append(False)

        return [base_dict, favorite_films, badges]
       
    def scrape_watched_films(user:str, soup:BeautifulSoup) -> list:
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
    
    def scrape_watchlist(user:str, soup:BeautifulSoup) -> list:
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
    
    def scrape_user_diary(user:str, soup:BeautifulSoup) -> list:
        data = []
        pages = findall(r'films/diary/page/(\d+)/', str(soup))
        if len(pages) == 0:
            pages = ['1']
        last_page = max([int(page) for page in pages])
        
        for i in range(1, last_page + 1):
            dates_ = []
            film_slugs_ = []
            ratings_ = []
            likes_ = []
            rewatch_ = []
            review_ = []
            for i in range(1, last_page + 1):
                response = requests_get(f'https://letterboxd.com/{user}/films/diary/page/{i}/').text
                soup = BeautifulSoup(response, 'html.parser')
                dates = findall(r'films/diary/for/(\d{4}/\d{2}/\d{2})/', str(soup))
                film_slugs = findall(r'data-film-slug="([^"]+)"', str(soup))
                # delete repeated film slugs
                film_slugs = list(dict.fromkeys(film_slugs))
                #print(film_slugs)
                #print(film_slugs)
                ratings_list = []
                for rating_tag in soup.find_all('span', class_='rating'):
                    rating_class = rating_tag.get('class', [])
                    
                    # Check if the rating class contains a 'rated-X' value
                    rated_value = next((cls.split('-')[-1] for cls in rating_class if cls.startswith('rated-')), None)
                    
                    # Append the rating or 'NA' if no rating is found
                    if rated_value:
                        ratings_list.append(int(rated_value))
                    else:
                        ratings_list.append('NA')
                likes = findall(r'<td class="td-like center diary-like">(.*?)</td>', str(soup))

                likes_list = []
                for like in likes:
                    # Check if there's something inside the <td> (i.e., contains the icon-liked span)
                    if 'icon-liked' in like:
                        likes_list.append(True)
                    else:
                        likes_list.append(False)

                #print(likes_list)

                rewatches = findall(r'<td class="td-rewatch center( icon-status-off)?">', str(soup))

                rewatch_list = []
                for rewatch in rewatches:
                    # Check if the class 'icon-status-off' is present
                    if 'icon-status-off' in rewatch:
                        rewatch_list.append(False)  # Not rewatched
                    else:
                        rewatch_list.append(True)   # Rewatched
                #print(rewatch_list)
                # Step 1: Find all the <td> elements that have "td-review center" with or without additional classes
                td_reviews = findall(r'<td class="td-review center(?: [^"]*)?">(.*?)</td>', str(soup), DOTALL)
                #print(td_reviews)
                review_list = []
                for td in td_reviews:
                    # Step 2: Check if there's an <a> tag with an href inside the td block
                    #print(td)
                    href_match = findall(r'href="([^"]+)"', td)
                    #print(href_match)
                    if href_match:
                        # Step 3: If an href is found, construct the full URL
                        review_link = f"https://letterboxd.com{href_match[0]}reviews/"
                        review_list.append(review_link)
                    else:
                        # If no href is found, append 'NA'
                        review_list.append('NA')
            
            dates_.extend(dates)
            film_slugs_.extend(film_slugs)
            #print(film_slugs_)
            ratings_.extend(ratings_list)
            likes_.extend(likes_list)
            rewatch_.extend(rewatch_list)
            review_.extend(review_list)
            #print(len(dates_))
            #print(len(film_slugs_))
            #print(len(ratings_))
            #print(len(likes_))
            #print(len(rewatch_))
            #print(len(review_))

            for j in range(len(film_slugs)):
                #print(j)
                #print(dates_[j])
                entry = {
                    "date": dates_[j],
                    "film_slug": film_slugs_[j],
                    "rating": ratings_[j],
                    "like": likes_[j],
                    "rewatch": rewatch_[j],
                    "review": review_[j]
                }
                data.append(entry)
        return data

            





def main():
    user = PyBoxd.user()
    user.set_username('gerardo_tri') #kurstboy
    #user.get_profile_stats()
    #user.get_user_watched_films()
    #user.get_user_watchlist()
    #user.get_user_network()
    #user.get_user_bio()
    diary = PyBoxd.user_diary(user)
    print(diary)
    diary.get_user_diary()
    print(len(diary.userDiary))
    print(diary.userDiary[:5])
    print(diary.userDiary[-5:])
    
    #print(user)
    #print(user.watchedFilms)
    #print(user.watchlist)
    #print(user.userNetwork)
    #print(user.userBio)

main()