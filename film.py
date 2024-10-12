from bs4 import BeautifulSoup
from requests import get as requests_get, exceptions as requests_exceptions
from re import findall, compile, IGNORECASE, search, sub
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import chain


class Film:

    def __init__(self) -> None:
        self.filmName: str = ""
        self.filmReleaseYear: int = 0
        self.filmDirectors: list = []
        self.filmSynopsis: str = ""
        self.filmPoster: str = ""
        self.filmGenres: dict = {}
        self.filmStats: dict = {}
        self.filmRating: dict = {}
        self.filmMainResponse: str = None
        self.filmMainSoup: BeautifulSoup = None
        self.filmAverageRating: int = 0
        self.filmTrailerLink = ""
        self.filmCast: dict = []
        self.filmCrew: dict = {}


        self.filmDetails: dict = {}
        self.filmReleases: dict = {}
        self.filmDuration: int = 0


    def __str__(self) -> str:
        film_status = self.filmName
        return str(film_status)
    
    def set_film_name(self, film_name:str, auto_scrape:bool = True) -> None:

        try:

            self.filmName = film_name
            self.filmMainResponse = requests_get(f'https://letterboxd.com/film/{self.filmName}/').text
            self.filmMainSoup = BeautifulSoup(self.filmMainResponse, 'html.parser')

            if auto_scrape:
                self.get_film_data()
    
            return
        
        except requests_exceptions.RequestException as e:

            print(f"Failed to retrieve data: {e}")
            return

    def get_film_data(self) -> None:

        self.filmReleaseYear = Film.scrape_film_release_year(soup = self.filmMainSoup)
        
        self.filmDirectors = Film.scrape_film_directors(soup = self.filmMainSoup)

        self.filmSynopsis = Film.scrape_film_synopsis(soup=self.filmMainSoup)

        self.filmRating = Film.scrape_average_rating(film_name=self.filmName)

        self.filmAverageRating = (sum([key * value for key, value in enumerate(self.filmRating.values(), start=1)]) / sum(self.filmRating.values())).__round__(3)

        self.filmPoster = Film.scrape_film_poster(soup=self.filmMainSoup, film_name=self.filmName)

        self.filmGenres = Film.scrape_film_genres(film_name=self.filmName) if self.filmGenres == {} else print("Genres already set")

    def get_film_stats(self) -> None:

        self.filmStats = Film.scrape_film_stats(film_name=self.filmName)

    def get_film_reviews(self, pages:int=1) -> None:

        self.filmReviews = Film.scrape_film_reviews(film_name=self.filmName, pages=pages)

    def get_film_genres(self) -> None:

        self.filmGenres = Film.scrape_film_genres(film_name=self.filmName) if self.filmGenres == {} else print("Genres already set")

    def get_film_trailer(self) -> None:

        self.filmTrailerLink = Film.scrape_trailer_link(soup=self.filmMainSoup)

    def get_film_cast(self) -> None:

        self.filmCast = Film.scrape_film_cast(soup = self.filmMainSoup)

    def get_film_crew(self) -> None:

        self.filmCrew = Film.scrape_film_crew(soup=self.filmMainSoup)

    @staticmethod
    def scrape_film_stats(film_name:str) -> dict:
        watched_response = requests_get(f'https://letterboxd.com/film/{film_name}/members/').text
        watched_soup = BeautifulSoup(watched_response, 'html.parser')
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
    @staticmethod
    def scrape_film_release_year(soup:BeautifulSoup) -> int:
        release_year = soup.find('div', class_="releaseyear")
        return int(release_year.find('a')['href'].split('/')[-2])
    @staticmethod
    def scrape_film_directors(soup:BeautifulSoup) -> list:
        directors = soup.find('span', class_="directorlist")
        directors_list = directors.find('a')['href'].split('/')[-2]
        return {"Directors":directors_list}
    @staticmethod
    def scrape_film_synopsis(soup:BeautifulSoup) -> list:
        synopsis = soup.find('div', class_="review body-text -prose -hero prettify").text
        synopsis = synopsis.replace("Synopsis", "").strip()
        return synopsis
    @staticmethod
    def scrape_average_rating(film_name:str) -> int:
        response = requests_get(f'https://letterboxd.com/csi/film/{film_name}/rating-histogram/')
        soup = BeautifulSoup(response.text, 'html.parser')
        ratings = {}


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
        film_poster_div = soup.find('div', {'class': 'really-lazy-load'})

        # Extract the data-film-id attribute
        if film_poster_div and 'data-film-id' in film_poster_div.attrs:
            film_id = film_poster_div['data-film-id']
        # template https://a.ltrbxd.com/resized/film-poster/8/3/8/1/4/0/838140-the-substance-0-1000-0-1500-crop.jpg
        # split the id into a list
        split_id = list(film_id)
        # make a string like '8/3/8/1/4/0'
        poster_path = '/'.join(split_id)
        url = f'https://a.ltrbxd.com/resized/film-poster/{poster_path}/{film_id}-{film_name}-0-1000-0-1500-crop.jpg'
        return url
    @staticmethod
    def scrape_film_reviews(film_name:str, pages:int=1) -> dict:
        reviews_list = []
        for i in range(1, pages + 1):
            response = requests_get(f'https://letterboxd.com/film/{film_name}/reviews/page/{i}/')
            soup = BeautifulSoup(response.text, 'html.parser')
            reviews = soup.find_all('li', class_='film-detail')
            
            for review in reviews:
                review_info = {}
                # find <a class="avatar -a40" href="/(\w+)/">
                pattern = r'href="/(\w+)/"'
                username = search(pattern, str(review))
                if username:
                    review_info['username'] = username.group(1)



                review_body = review.find('div', class_='body-text -prose collapsible-text')
        
                if review_body:
                    # Get the text from the first <p> inside this <div>
                    review_text_element = review_body.find('p')
                    if review_text_element:
                        # Get the text and strip it of extra whitespace

                        review_text = review_text_element.get_text(strip=True)
                        review_info['review_text'] = review_text
                        
                rating_span = review.find('span', class_=compile(r'rating -green \S+'))
                if rating_span:
                    review_info['rating'] = rating_span.get_text(strip=True)

                # Extract the date
                date_span = review.find('span', class_='_nobr')
                if date_span:   
                    review_info['date'] = date_span.get_text(strip=True)

                # Extract the review_id
                like_link_target = review.find('p', class_='like-link-target')
                if like_link_target and 'data-likeable-uid' in like_link_target.attrs:
                    review_info['review_id'] = like_link_target['data-likeable-uid']

                reviews_list.append(review_info)

        return reviews_list   
    @staticmethod
    def scrape_film_genres(film_name):
        response = requests_get(f'https://letterboxd.com/film/{film_name}/genres/')
        soup = BeautifulSoup(response.text, 'html.parser')
        genre_pattern = compile(r'/films/genre/[\w-]+/') 

        # Find all 'a' tags with an href that matches the genre pattern
        genres = soup.find_all('a', href=genre_pattern)
        genres = [i.text for i in genres]
        
        return genres
    @staticmethod
    def scrape_trailer_link(soup):
        # Find the 'a' tag with class 'play track-event js-video-zoom cboxElement' and data-track-category 'Trailer'
        # Find the 'p' tag containing the 'a' tag with the trailer link
        trailer_paragraph = soup.find('p', class_='trailer-link js-watch-panel-trailer')

        # Now, find the 'a' tag within this 'p' tag
        if trailer_paragraph:
            trailer_link = trailer_paragraph.find('a', class_='play track-event js-video-zoom')
            if trailer_link:
                youtube_url = trailer_link.get('href')
                # Ensure the URL is complete
                if youtube_url.startswith('//'):
                    youtube_url = 'https:' + youtube_url
                return youtube_url
    @staticmethod
    def scrape_film_cast(soup: BeautifulSoup) -> dict:
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
    def scrape_film_crew(soup: BeautifulSoup) -> dict:

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


movie = Film()
movie.set_film_name(film_name="chungking-express", auto_scrape=False)
movie.get_film_crew()
print(movie.filmCrew)


