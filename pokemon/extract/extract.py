import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_session() ->object:
    """
    Session creation for entire data extraction,
    so that no need of defining settings again and again.
    """

    session = requests.Session()

    # Accept JSON type of data
    session.headers.update({
        "Accept": "application/json"
    })

    # Retry engine setup for handling timeouts and server crashes automatically
    retry_strategy = Retry(
        total=3,  # Total number of retries
        backoff_factor=2,  # Exponential backoff (wait 2s, 4s, 8s...)
        status_forcelist=[429, 500, 501, 502, 503],# Retry ONLY on these status codes
        # raise_on_status=False,# Do not throw exception immediately on error codes
        respect_retry_after_header=True # Automatically read and wait for Retry-After headers
    )

    # Attach adapter settings to session object
    adapter = HTTPAdapter(max_retries=retry_strategy)

    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


def get_json(session, url) ->dict:
    """
    Implemented:
    - timeout
    - retry mechanism
    - retry after when 429 status code

    PARAMETERS:
    session object created for the extraction in main.py module
    url which is sent to extract the data inside it

    RETURN:
    Return the URL data in JSON format or None.
    """

    try:
        # Get URL data
        timeout = 10

        response = session.get(url, timeout=timeout)

        # If there are 404 errors or other non-retried errors,
        # handle it cleanly
        # if response.status_code != 200:
        #     return None

        response.raise_for_status()

        # Check content type before parsing
        if "application/json" not in response.headers.get(
            "Content-Type", ""
        ):
            logger.warning("Response is not JSON")
            logger.warning(f"raw: {response.text}")
            return None

        # Returning the response in JSON format
        return response.json()

    # If internet connection dropped out completely
    except requests.exceptions.ConnectionError:
        logger.error(
            "Connection failed - check URL and internet connection"
        )
        return None

    # If timeout failed completely
    except requests.exceptions.Timeout:
        logger.error(
            f"Request timed out after {timeout} seconds"
        )
        return None

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code

        logger.error(
            f"HTTP Error {status}: {e}"
        )

        error_messages = {
            400: "Bad request — check your data",
            401: "Unauthorized — check your API key",
            403: "Forbidden — you don't have access",
            404: "Not found — check the URL",
        }

        print(
            error_messages.get(
                status,
                f"Server error: {status}"
            )
        )

        return None

    # If the server returned a 200 OK successfully
    # but sent back HTML or text
    # (like Wi-Fi login walls)
    except requests.exceptions.JSONDecodeError:
        return None

    # If any further error
    except requests.exceptions.RequestException:
        return None


def get_pokemon(session , logger)->list:
    """
    END POINT:
    pokemon

    We are getting data from this endpoint
    and returning the URLs of pokemon present in results.

    PARAMETERS:
    Takes the session object which is created
    for this entire data extraction.

    RETURNS:
    Data in list format containing all the pokemon URLs.

    Implemented pagination here.
    The URL provides pagination using offset and limit
    mechanism in the next and previous fields.
    """

    url = "https://pokeapi.co/api/v2/pokemon/"

    # Empty list for appending the required data
    pokemon_data = []
    failed_pages=[]
    # Loop until the next URL is present
    while url:

        # Call the get_json function,
        # which gives us the data of the URL in JSON format
        data = get_json(session, url)

        if data is None:
            logger.error("failed to extract data")
            failed_pages.append(url)
        else:

            # Get the results field inside the API information
            results = data.get("results", [])

            # Append the URLs of the pokemon present in the results
            # if the URL is not None
            pokemon_data.extend(
                items["url"]
                for items in results
                if items.get("url")
            )

        # Getting the next page URL.
        # If it is not present, it returns None.
        url = data.get("next")

    # Return the URLs of the pokemon
    return pokemon_data , failed_pages

def extract_pokemon(session , urls , logger)->list:
    """
    Extract individual pokemon records
    failed records doesnt stop the pipeline and gets saved a side
    """
    pokemon_data=[]
    failed_urls=[]

    total=len(urls)


    #looping around an enumerate with urls
    for index,url in enumerate(urls, start=1):
        data=get_json(session , url )

        #if there is an error attacked the api then we get None
        if data is None:
            failed_urls.append(url)
            logger.error("pokemon extraction failed | progress= %s / %s | url=%s" , index , total , url)
            continue

        #if we got data successfully
        pokemon_data.append(data)
        logger.info("pokemon extraction completed | success=%s failed=%s" , len(pokemon_data) , len(failed_urls))

        return pokemon_data , failed_urls


def extract_species(session , urls , logger):

    """
    extract the species data from the species url 
    """
    #save the species data
    species_data=[]
    #save the failed data
    failed_species=[]
    total=len(urls)

    #looping around an enumerate with urls
    for index,url in enumerate(urls, start=1):
        data=get_json(session , url  )

        #if there is an error occurred attacked the api then we get None
        if data is None:
            failed_species.append(url)
            logger.error("pokemon species extraction failed | progress=%s / %s | url = %s " , index , total , url)
            continue

        #if we get successfull data 
        species_data.append(data)
        logger.info("pokemon species extraction completed | success=%s | failed=%s ", len(species_data) , len(failed_species))

        return species_data, failed_species


def get_move(pokemon_data):
    """
    get all move urls
    """

    #unique set of moves from the pokemons
    move_urls=set()

    #pokemon -> moves-> move -> url
    for pokemon in pokemon_data:
        for item in pokemon.get("moves") or []:
            move_info=item.get("move") or {}
            move_url=move_info.get("url")

            #add only if the url is present
            if move_url:
                move_urls.add(move_url)
    return sorted(move_urls)



def extract_moves(session , urls , logger):
    """
    extract move details from the move urls
    """
    move_data=[]
    failed_urls=[]
    total=len(urls)

    #looping in move urls and getting its data
    for index,url in enumerate(urls , start=1):
        data=get_json(session , url )

        #move url data fetching failed
        if data is None:
            failed_urls.append(url)
            logger.error("pokemon move extraction failed | progress=%s /%s | url=%s " , index , total , url)
            continue

        #successfull retreival of pokemon move data
        move_data.append(data)
        logger.info("pokemon move successfully extracted | success=%s | failed =%s" , len(move_data) , len(failed_urls))

    return move_data , failed_urls
