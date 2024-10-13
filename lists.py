from bs4 import BeautifulSoup
from requests import get as requests_get, exceptions as requests_exceptions
from re import findall, compile, IGNORECASE, search, sub
from user import User


class UserList:

    def __init__(self, username:str) -> None:

        try:

            contructor = User()
            contructor.set_username(username)

        except requests_exceptions.RequestException as e:

            print(f"Failed to retrieve data: {e}")

        self.username = contructor.username
        self.userMainResponse = contructor.mainResponse
        self.userMainSoup = contructor.mainSoup

        self.userList = []
    

    def get_user_list(self) -> BeautifulSoup:

        try:

            response = requests_get(f"https://letterboxd.com/{self.username}/lists/")
            soup = BeautifulSoup(response.text, "html.parser")

            if soup.find("section", class_="ui-block-header empty-text body-text -small"):

                raise Exception("User has no lists")

            else:

                self.userList = UserList.scrape_user_list(username=self.username, soup=soup)

        except requests_exceptions.RequestException as e:

            print(f"Failed to retrieve data: {e}")


    @staticmethod
    def scrape_user_list(username:str,soup:BeautifulSoup) -> list:
        
        all_lists = []
        pages = soup.find("div", class_="paginate-pages")

        for page in pages.find_all("a"):
            continue

        last_page = int(page.text)
        list_set = soup.find("section", class_="list-set")
                
        for row in list_set.find_all("section", class_="list -overlapped -summary"):

            name = row.find("h2", class_="title-2 title prettify").text.strip()
            all_lists.append(name)

        for p in range(2, last_page + 1):
            
            response = requests_get(f"https://letterboxd.com/{username}/lists/page/{p}/")
            soup = BeautifulSoup(response.text, "html.parser")
            list_set = soup.find("section", class_="list-set")

            for row in list_set.find_all("section", class_="list -overlapped -summary"):

                name = row.find("h2", class_="title-2 title prettify").text.strip()
                all_lists.append(name)

        return all_lists

class LbxdList:

    def __init__(self) -> None:
        pass
