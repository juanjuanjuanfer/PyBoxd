from bs4 import BeautifulSoup
from requests import get as requests_get, exceptions as requests_exceptions
from re import findall, compile, IGNORECASE, search, sub


class Film:

    def __init__(self) -> None:
        """
            Constructor.
            
            Initialize the Film class.
        """

        self.filmName: str = ""
        self.filmReleaseYear: int = 0
        self.filmDirectors: list = []
        self.filmSynopsis: str = []
        self.filmPoster: str = ""
        self.filmGenres: dict = {}
        self.filmStats: dict = {}
        self.filmRating: dict = {}
        self.filmMainResponse: str = None
        self.filmMainSoup: BeautifulSoup = None
        self.filmAverageRating: int = 0
        self.filmTrailerLink = ""
        self.filmCast: list = []
        self.filmCrew: dict = {}
        self.filmDetails: dict = {}
        self.filmReleases: dict = {}
        self.filmDuration: int = 0
        self.filmSimilars: dict = []


    def __str__(self) -> str:
        film_status = self.filmName
        return str(film_status)
    
    def set_film_name(self, film_name:str, auto_scrape:bool = True) -> None:
        
        """
            Set film name.

            ### Parameters:
                **film_name** 
                A string indicating the name of the film. Should follow Letterboxd's data-film-slug style.<br>

                **auto_scrape**
                Boolean. If `True`, scrape film data. Defaults to `True`.
        """

        if " " in film_name:

            raise Exception("Film name cannot contain spaces")
        
        try:

            self.filmName = film_name
            self.filmMainResponse = requests_get(f'https://letterboxd.com/film/{self.filmName}/')

            if self.filmMainResponse.status_code == 200:

                self.filmMainSoup = BeautifulSoup(self.filmMainResponse.text, 'html.parser')

            else:

                raise requests_exceptions.RequestException(f"Film name not on Letterboxd or Letterboxd is not available. {self.filmMainResponse.status_code}")

            if auto_scrape:

                self.get_film_data()
    
            return
        
        except requests_exceptions.RequestException as e:

            print(f"Failed to retrieve data: {e}")

            return

    def get_film_data(self, releaseyear:bool=True, directors:bool=True, synopsis:bool=True, rating:bool=True, poster:bool=True, genres:bool=True) -> None:

        """
            Scrapes film data.

            ### Parameters:
                **releaseyear**
                Boolean. If `True`, scrape release year. Defaults to `True`.

                **directors**
                Boolean. If `True`, scrape directors. Defaults to `True`.

                **synopsis**
                Boolean. If `True`, scrape synopsis. Defaults to `True`.

                **rating**
                Boolean. If `True`, scrape rating and average rating. Defaults to `True`.

                **poster**
                Boolean. If `True`, scrape poster. Defaults to `True`.

                **genres**
                Boolean. If `True`, scrape genres. Defaults to `True`.
            
            
        """
        if self.filmName == "":

            raise Exception("Film name not set")
        
        else:

            if releaseyear:
                try:
                    self.filmReleaseYear = Film.scrape_film_release_year(soup = self.filmMainSoup) 
                except:
                    raise Exception("Failed to scrape release year")
                
            if directors:
                try:
                    self.filmDirectors = Film.scrape_film_directors(soup = self.filmMainSoup)
                except:
                    raise Exception("Failed to scrape directors")
                
            if synopsis:
                try:
                    self.filmSynopsis = Film.scrape_film_synopsis(soup=self.filmMainSoup)
                except:
                    raise Exception("Failed to scrape synopsis")
                
            if rating:
                try:
                    self.filmRating = Film.scrape_film_rating(film_name=self.filmName)
                    self.filmAverageRating = (sum([key * value for key, value in enumerate(self.filmRating.values(), start=1)]) / sum(self.filmRating.values())).__round__(3)
                except:
                    raise Exception("Failed to scrape rating")
                
            if poster:
                try:
                    self.filmPoster = Film.scrape_film_poster(soup=self.filmMainSoup, film_name=self.filmName)
                except:
                    raise Exception("Failed to scrape poster")
                
            if genres:
                try:
                    self.filmGenres = Film.scrape_film_genres(film_name=self.filmName) if self.filmGenres == {} else print("Genres already set")
                except:
                    raise Exception("Failed to scrape genres")

    def get_film_stats(self) -> None:

        """
            Scrape film stats.

            Uses the film name to scrape the number of members, fans, likes, reviews, and lists.

            Directly use `def scrape_film_stats` to scrape the data without setting the film name.

        """
        
        if self.filmName == "":

            raise Exception("Film name not set")
        
        else:

            self.filmStats = Film.scrape_film_stats(film_name=self.filmName)

    def get_film_reviews(self, pages:int=1) -> None:

        """
            Scrape film reviews in batches of 12.

            Uses the `Film.filmName` to scrape the reviews. 

            Directly use `def scrape_film_reviews` to scrape the data without setting the film name.

            ### Parameters:
                **pages**
                `int`. Number of pages to scrape. Defaults to 1. Each page has 12 reviews.
        """

        if self.filmName == "":

            raise Exception("Film name not set")
        
        else:
            
            self.filmReviews = Film.scrape_film_reviews(film_name=self.filmName, pages=pages)

    def get_film_genres(self) -> None:

        """
            Scrape film genres.

            Uses the `Film.filmName` to scrape the genres.

            Directly use `def scrape_film_genres` to scrape the data without setting the film name.
        """

        if self.filmName == "":

            raise Exception("Film name not set")
        
        else:
            self.filmGenres = Film.scrape_film_genres(film_name=self.filmName) if self.filmGenres == {} else print("Genres already set")

    def get_film_trailer(self) -> None:

        """
            # STILL IN DEVELOPMENT
            Scrape film trailer link.

            Uses the `Film.filmMainSoup` to scrape the trailer link.

            Directly use `def scrape_trailer_link` to scrape the data without setting the film name.
        """

        if self.filmName == "":
                
                raise Exception("Film name not set")
        
        else:

            self.filmTrailerLink = Film.scrape_trailer_link(soup=self.filmMainSoup)

    def get_film_cast(self) -> None:

        """
            Scrape film cast.

            Uses the `Film.filmMainSoup` to scrape the cast.

            Directly use `def scrape_film_cast` to scrape the data without setting the film name.
        """

        if self.filmName == "":
            
            raise Exception("Film name not set")
        
        else:

            self.filmCast = Film.scrape_film_cast(soup = self.filmMainSoup)

    def get_film_crew(self) -> None:

        """
            Scrape film crew.

            Uses the `Film.filmMainSoup` to scrape the crew.

            Directly use `def scrape_film_crew` to scrape the data without setting the film name.
        """

        if self.filmName == "":

            raise Exception("Film name not set")
        
        else:
            
            self.filmCrew = Film.scrape_film_crew(soup=self.filmMainSoup)

    def get_film_details(self) -> None:

        """
            Scrape film details.

            Uses the `Film.filmMainSoup` to scrape the details.

            Directly use `def scrape_film_details` to scrape the data without setting the film name.
        """

        if self.filmName == "":

            raise Exception("Film name not set")
        
        else:
            
            self.filmDetails = Film.scrape_film_details(soup=self.filmMainSoup)

    def get_film_releases(self) -> None:

        """
            Scrape film releases.

            Uses the `Film.filmMainSoup` to scrape the releases.

            Directly use `def scrape_film_releases` to scrape the data without setting the film name.
        """

        if self.filmName == "":

            raise Exception("Film name not set")
        
        else:
            
            self.filmReleases = Film.scrape_film_releases(soup=self.filmMainSoup)

    def get_film_duration(self) -> None:
        
        """
            Scrape film duration.

            Uses the `Film.filmMainSoup` to scrape the duration.

            Directly use `def scrape_film_duration` to scrape the data without setting the film name.
        """

        if self.filmName == "":
        
            raise Exception("Film name not set")
        
        else:

            self.filmDuration = Film.scrape_film_duration(soup=self.filmMainSoup)

    def get_film_similars(self) -> None:
        
        """
            Scrape film similars.

            Uses the `Film.filmName` to scrape the similars.

            Directly use `def scrape_film_similars` to scrape the data without setting the film name.
        """

        if self.filmName == "":

            raise Exception("Film name not set")

        else:

            self.filmSimilars = Film.scrape_film_similars(film_name=self.filmName)

    @staticmethod
    def scrape_film_stats(film_name:str) -> dict:

        """
            Scrape film stats.

            ### Parameters:
                **film_name**
                `str`. The name of the film to scrape.

            ### Returns:
                `dict`. The film stats. Keys: `members`, `fans`, `likes`, `reviews`, `lists`.
        """
        try:
            watched_response = requests_get(f'https://letterboxd.com/film/{film_name}/members/')

            if watched_response.status_code != 200:
                
                raise Exception("Failed to scrape film stats")

            watched_soup = BeautifulSoup(watched_response.text, 'html.parser')
            data = str(watched_soup.find('ul', class_="sub-nav"))
            pattern = r'title="([\d,]+)'
            matches = findall(pattern, data)
            cleaned_numbers = [int(number.replace(",", "")) for number in matches]

            stats = {
                "members": cleaned_numbers[0],
                "fans": cleaned_numbers[1],
                "likes": cleaned_numbers[2],
                "reviews": cleaned_numbers[3],
                "lists": cleaned_numbers[4]
            }

            return stats
        
        except requests_exceptions.RequestException as e:
            raise Exception(f"Failed to scrape film stats: {e}")
    @staticmethod
    def scrape_film_release_year(soup:BeautifulSoup) -> int:

        """
            Scrape film release year.

            ### Parameters:
                **soup**
                `BeautifulSoup`. The soup object of the film page.

            ### Returns:
                `int`. The release year of the film.
        """
    
        release_year = soup.find('div', class_="releaseyear")

        return int(release_year.find('a')['href'].split('/')[-2])
    @staticmethod
    def scrape_film_directors(soup:BeautifulSoup) -> list:

        """
            Scrape film directors.

            ### Parameters:
                **soup**
                `BeautifulSoup`. The soup object of the film page.

            ### Returns:
                `list`. The directors of the film.
        """

        directors = soup.find('span', class_="directorlist")
        directors_list = directors.find('a')['href'].split('/')[-2]

        return {"Directors":directors_list}
    @staticmethod
    def scrape_film_synopsis(soup:BeautifulSoup) -> str:

        """
            Scrape film synopsis.

            ### Parameters:
                **soup**
                `BeautifulSoup`. The soup object of the film page.

            ### Returns:
                `str`. The synopsis of the film.
        """

        synopsis = soup.find('div', class_="review body-text -prose -hero prettify").text
        synopsis = synopsis.replace("Synopsis", "").strip()

        return synopsis
    @staticmethod
    def scrape_film_rating(film_name:str) -> int:

        """
            Scrape film rating.
            ### Parameters:
                **film_name**
                `str`. The name of the film to scrape.

            ### Returns:
                `dict`. A dict containing rating and count for a film. 
                    Keys: `half-★`, `★`, `★½`, `★★`, `★★½`, `★★★`, `★★★½`, `★★★★`, `★★★★½`, `★★★★★`. 
                    Example: `{'half-★': 12, '★': 55, '★½': 334, '★★': 443, '★★½': 523, '★★★': 6234, '★★★½': 7634, '★★★★': 8634, '★★★★½': 923, '★★★★★': 1023}`
        """

        ratings = {}
        response = requests_get(f'https://letterboxd.com/csi/film/{film_name}/rating-histogram/')

        if response.status_code != 200:

            raise Exception("Failed to scrape film rating")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        rating_items = soup.select('section.ratings-histogram-chart ul li a')

        for item in rating_items:
    
            title = item['title']
            match = search(r'([\d,]+)\s([\S]+)\sratings\s\((\d+%)\)', title)

            if match:
        
                rating_count = int(match.group(1).replace(',', ''))
                rating_type = match.group(2)
                ratings[rating_type] = rating_count

        return ratings
    @staticmethod
    def scrape_film_poster(soup:BeautifulSoup, film_name:str) -> str:

        """
            STILL IN DEVELOPMENT
            Scrape film poster link.

            ### Parameters:
                **soup**
                `BeautifulSoup`. The soup object of the film page.

                **film_name**
                `str`. The name of the film.

            ### Returns:
                `str`. The URL of the film poster.
        """

        film_poster_div = soup.find('div', {'class': 'really-lazy-load'})

        if film_poster_div and 'data-film-id' in film_poster_div.attrs:

            film_id = film_poster_div['data-film-id']

        split_id = list(film_id)
        poster_path = '/'.join(split_id)
        url = f'https://a.ltrbxd.com/resized/film-poster/{poster_path}/{film_id}-{film_name}-0-1000-0-1500-crop.jpg'

        return url
    @staticmethod
    def scrape_film_reviews(film_name:str, pages:int=1) -> dict:

        """
            Scrape film reviews in batches of 12.

            ### Parameters:
                **film_name**
                `str`. The name of the film to scrape.

                **pages**
                `int`. The number of pages to scrape. Defaults to 1. Each page has 12 reviews.

            ### Returns:
                `list`. A list of dictionaries containing the review information.
                    The dictionary keys are `username`, `review_text`, `rating`, `date`, `review_id`.
        """

        reviews_list = []

        for i in range(1, pages + 1):

            response = requests_get(f'https://letterboxd.com/film/{film_name}/reviews/page/{i}/')

            if response.status_code != 200:
                    
                    raise Exception("Failed to scrape film reviews. Seems like the film name is incorrect or the page is not available.")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            reviews = soup.find_all('li', class_='film-detail')
            
            for review in reviews:

                review_info = {}
                pattern = r'href="/(\w+)/"'
                username = search(pattern, str(review))

                if username:

                    review_info['username'] = username.group(1)

                review_body = review.find('div', class_='body-text -prose collapsible-text')
        
                if review_body:

                    review_text_element = review_body.find('p')

                    if review_text_element:

                        review_text = review_text_element.get_text(strip=True)
                        review_info['review_text'] = review_text
                        
                rating_span = review.find('span', class_=compile(r'rating -green \S+'))

                if rating_span:

                    review_info['rating'] = rating_span.get_text(strip=True)

                date_span = review.find('span', class_='_nobr')

                if date_span:

                    review_info['date'] = date_span.get_text(strip=True)

                like_link_target = review.find('p', class_='like-link-target')

                if like_link_target and 'data-likeable-uid' in like_link_target.attrs:

                    review_info['review_id'] = like_link_target['data-likeable-uid']

                reviews_list.append(review_info)

        return reviews_list   
    @staticmethod
    def scrape_film_genres(film_name:str) -> list:

        """
            Scrape film genres.

            ### Parameters:
                **film_name**
                `str`. The name of the film to scrape.

            ### Returns:
                `list`. The genres of the film.
        """

        response = requests_get(f'https://letterboxd.com/film/{film_name}/genres/')

        if response.status_code != 200:

            raise Exception("Failed to scrape film genres")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        genre_pattern = compile(r'/films/genre/[\w-]+/') 
        genres = soup.find_all('a', href=genre_pattern)
        genres = [i.text for i in genres]
        
        return genres
    @staticmethod
    def scrape_trailer_link(soup:BeautifulSoup) -> str:

        """
            STILL IN DEVELOPMENT.
            Not working for all films.

            Scrape film trailer link.

            ### Parameters:
                **soup**
                `BeautifulSoup`. The soup object of the film page.

            ### Returns:
                `str`. The URL of the film trailer.
        """

        trailer_paragraph = soup.find('p', class_='trailer-link js-watch-panel-trailer')

        if trailer_paragraph:

            trailer_link = trailer_paragraph.find('a', class_='play track-event js-video-zoom')

            if trailer_link:

                youtube_url = trailer_link.get('href')

                if youtube_url.startswith('//'):

                    youtube_url = 'https:' + youtube_url

                return youtube_url
    @staticmethod
    def scrape_film_cast(soup:BeautifulSoup) -> list:

        """
            Scrape film cast.

            ### Parameters:
                **soup**
                `BeautifulSoup`. The soup object of the film page.

            ### Returns:
                `list`. A list containing `dicts` with the cast of the film and their characters.
        """

        cast = []

        cast_paragraph = soup.find('div', class_='cast-list text-sluglist')
        
        if cast_paragraph:

            for actor_link in cast_paragraph.find_all('a', class_='text-slug tooltip'):

                character_match = search(r'title="([^"]+)"', str(actor_link)).group(1) if search(r'title="([^"]+)"', str(actor_link)) else "No Information"
                actor_name = actor_link.text.strip()

                if character_match and actor_name:

                    cast.append( {
                                'actor': actor_name,
                                'character': character_match
                                })
        
        return cast
    @staticmethod
    def scrape_film_crew(soup:BeautifulSoup) -> dict:

        """
            Scrape film crew.

            ### Parameters:
                **soup**
                `BeautifulSoup`. The soup object of the film page.

            ### Returns:
                `dict`. A dictionary containing the crew of the film.
        """

        crew = []
        cleaned_crew = []
        final_crew = {}

        crew_paragraph = soup.find('div', id='tab-crew')

        for i in crew_paragraph:

            if i.text == " " or i.text == "\n" or i.text == "\t":

                continue

            else:

                crew.append(i.text)

        for item in crew:

            cleaned_item = sub(r'\s+', ' ', item).strip()
            cleaned_item = sub(r'\b(\w+)(\s+\1\b)+', r'\1', cleaned_item, flags=IGNORECASE)

            if cleaned_item:

                cleaned_crew.append(cleaned_item)

        for i in range(0, len(cleaned_crew), 2):

            if i + 1 < len(cleaned_crew):

                final_crew[cleaned_crew[i]] = cleaned_crew[i + 1]

        return final_crew
    @staticmethod
    def scrape_film_details(soup:BeautifulSoup) -> dict:

        """
            Scrape film details.

            ### Parameters:
                **soup**
                `BeautifulSoup`. The soup object of the film page.

            ### Returns:
                `dict`. A dictionary containing the details of the film.

        """

        crew = []

        cleaned_crew = []

        final_crew = {}

        crew_paragraph = soup.find('div', id='tab-details')

        for i in crew_paragraph:

            if i.text == " " or i.text == "\n" or i.text == "\t":

                continue

            else:

                crew.append(i.text)

        for item in crew:

            cleaned_item = sub(r'\s+', ' ', item).strip()

            if cleaned_item:

                cleaned_crew.append(cleaned_item)

        for i in range(0, len(cleaned_crew), 2):

            if i + 1 < len(cleaned_crew):

                final_crew[cleaned_crew[i]] = cleaned_crew[i + 1]

        return final_crew
    @staticmethod
    def scrape_film_releases(soup:BeautifulSoup) -> dict:

        """
            STILL IN DEVELOPMENT.

            Scrape film releases.
            ### Parameters:
                **soup**
                `BeautifulSoup`. The soup object of the film page.

            ### Returns:
                `dict`. A dictionary containing the releases of the film.
        """
        releases_div = soup.find("div", id="tab-releases")
    
        if releases_div:
            
            release_dates = releases_div.find_all("h5", class_ = "date")
            release_dates_ = [date.text.strip() for date in release_dates]
            release_countries = releases_div.find_all("span", class_="name")
            release_countries_ = [country.text.strip() for country in release_countries]

        return dict(zip(release_dates_, release_countries_))
    @staticmethod
    def scrape_film_duration(soup:BeautifulSoup) -> int:

        """
            Scrape film duration in minutes.

            ### Parameters:
                **soup**
                `BeautifulSoup`. The soup object of the film page.

            ### Returns:
                `int`. The duration of the film in minutes.
        """

        tag = soup.find("section", class_="section col-10 col-main")
        duration = tag.find("p", class_="text-link text-footer").text
        pattern = r'(\d+)\s+mins'
        duration = search(pattern, duration).group(1)

        return duration
    @staticmethod
    def scrape_film_similars(film_name:str) -> dict:
        
        """
            Scrape similar films.

            ### Parameters:
                **film_name**
                `str`. The name of the film to scrape.

            ### Returns:
                `list`. A list containing similar films based on Letterboxd.
        """

        similar_films = []
        response = requests_get(f'https://letterboxd.com/film/{film_name}/similar/')

        if response.status_code != 200:
                
                raise Exception("Failed to scrape similar films")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        tags = soup.find("ul", class_="poster-list -p125 -grid film-list")
        tag = tags.find_all("li", class_="poster-container")

        for i in tag:

            pattern = r'data-film-slug="([\w-]+)"'
            film_slug = search(pattern, str(i))
            similar_films.append(film_slug.group(1))

        return similar_films

a = Film.scrape_film_releases(BeautifulSoup(requests_get('https://letterboxd.com/film/the-substance/').text, 'html.parser'))
print(a)