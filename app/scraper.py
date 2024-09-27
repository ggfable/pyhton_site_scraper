import asyncio
import random
from seleniumbase import Driver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
    WebDriverException,
)
from fastapi.responses import JSONResponse
import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from urllib3.exceptions import NewConnectionError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("./logs/app.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def get_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--lang=en")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--auto-open-devtools-for-tabs")
    chrome_options.add_argument("--follow-redirects")
    return chrome_options


def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.58 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.72 Safari/537.36",
    ]
    return random.choice(user_agents)


async def get_job_data(country: str, job: str) -> JSONResponse:
    async def run_browser():
        return Driver(uc=True, headless=True)

    try:
        driver = await run_browser()
        driver.header_overrides = {
            "User-Agent": get_random_user_agent(),
        }
        logger.info("Driver is ready.")

        try:
            driver.get(f"https://{country}.jooble.org/SearchResult?date=2&ukw={job}")
            await asyncio.sleep(21)
            logger.info("Link successfully opened.")
            logger.info(driver.current_url)
        except WebDriverException as e:
            if "ERR_NAME_NOT_RESOLVED" in str(e):
                logger.info("ERR_NAME_NOT_RESOLVED error.")
                return JSONResponse(
                    content={"error": "ERR_NAME_NOT_RESOLVED", "message": str(e)}
                )
            else:
                logger.info("some other error in `WebDriverException`.")
                return JSONResponse(
                    content={"error": "Failed to load the page.", "message": str(e)}
                )
        except (ConnectionError, NewConnectionError) as e:
            logger.error(f"Error connecting to the server: {str(e)}")
            return JSONResponse(
                content={"error": "Connection error.", "message": str(e)}
            )
        except Exception as e:
            logger.info("Some other exeption in url opening")
            return JSONResponse(
                content={"error": "Not handled exception.", "message": str(e)}
            )

        try:
            alert = driver.switch_to.alert
            alert.dismiss()
            logger.info("Allert dismissed.")
        except:
            pass

        data = []

        try:
            parsed_url = urlparse(driver.current_url)
            query_params = parse_qs(parsed_url.query)
            if "p" not in query_params:
                query_params["p"] = ["5"]
            if "salaryMin" not in query_params:
                query_params["salaryMin"] = ["1"]
            if "salaryRate" not in query_params:
                query_params["salaryRate"] = ["3"]
            new_url = urlunparse(
                (
                    parsed_url.scheme,
                    parsed_url.netloc,
                    parsed_url.path,
                    parsed_url.params,
                    urlencode(query_params, doseq=True),
                    parsed_url.fragment,
                )
            )
        except Exception as e:
            logger.info("Error in url parsing.")
            return JSONResponse(
                content={"error": "Failed to parse the url.", "message": str(e)}
            )

        try:
            driver.get(new_url)
            logger.info("NewLink successfully opened.")
            logger.info(driver.current_url)
        except WebDriverException as e:
            if "ERR_NAME_NOT_RESOLVED" in str(e):
                logger.info("ERR_NAME_NOT_RESOLVED error.")
                return JSONResponse(
                    content={"error": "ERR_NAME_NOT_RESOLVED", "message": str(e)}
                )
            else:
                logger.info("some other error in `WebDriverException`.")
                return JSONResponse(
                    content={"error": "Failed to load the page.", "message": str(e)}
                )
        except (ConnectionError, NewConnectionError) as e:
            logger.error(f"Error connecting to the server: {str(e)}")
            return JSONResponse(
                content={"error": "Connection error.", "message": str(e)}
            )
        except Exception as e:
            logger.info("Some other exeption in url opening")
            return JSONResponse(
                content={"error": "Not handled exception.", "message": str(e)}
            )

        try:
            logger.info("Saved screenshot to screenshot.png for debugging.")
            articles = driver.find_elements(
                By.XPATH, '//div[@data-test-name="_jobCard"]'
            )
            logger.info(f"Found {new_url} {len(articles)} articles.")
        except TimeoutException:
            logger.info(f"Timeout while waiting for articles at {new_url}.")
            return JSONResponse(
                content={
                    "error": "Timeout waiting for elements.",
                    "message": "No articles found within the given time.",
                }
            )
        except NoSuchElementException as e:
            logger.info(f"Element is not found: {new_url} articles.")
            return JSONResponse(
                content={
                    "error": "Element is not found.",
                    "message": str(e.msg.strip()),
                }
            )
        except ElementNotInteractableException as e:
            logger.info(f"Element is not interactable: {new_url} articles.")
            return JSONResponse(
                content={
                    "error": "Element is not interactable.",
                    "message": str(e.msg.strip()),
                }
            )

        logger.info(f"Start collect data for {new_url}.")
        for index, article in enumerate(articles, start=1):
            logger.info(f"Collecting data from article {index}.")
            with ActionChains(driver) as action:
                action.scroll_to_element(article).perform()
                action.move_to_element(article).perform()

            try:
                alert = driver.switch_to.alert
                alert.dismiss()
                logger.info("Allert dismissed 2nd.")
            except:
                pass

            try:
                job_id = article.get_attribute("id")
                job_link = article.find_element(By.XPATH, ".//div/h2/a").get_attribute(
                    "href"
                )
                job_title = article.find_element(By.XPATH, ".//div/h2/a").text
                try:
                    job_salary = article.find_element(
                        By.XPATH, './/div//p[contains(@class, "W3cvaC")]'
                    ).text
                except NoSuchElementException as e:
                    job_salary = None
                try:
                    job_description = article.find_element(
                        By.XPATH, ".//div/div[1]/div[1]"
                    ).text
                except NoSuchElementException as e:
                    job_description = None
                try:
                    job_tags_list = article.find_elements(
                        By.XPATH, ".//div/div[1]/div[2]//div[@data-name]"
                    )
                    job_tags = (
                        [
                            job_tag.text.strip()
                            for job_tag in job_tags_list
                            if job_tag.text.strip() != ""
                        ]
                        if job_tags_list
                        else None
                    )
                except NoSuchElementException as e:
                    job_tags = None
                try:
                    job_company = article.find_element(
                        By.XPATH, ".//div/div[2]/div/div[1]/div"
                    ).text.strip()
                except NoSuchElementException as e:
                    job_company = None
                try:
                    captions = article.find_elements(
                        By.XPATH, './/div//div[contains(@class, "caption")]'
                    )
                except NoSuchElementException as e:
                    captions = None
                if len(captions) == 2:
                    verified = None
                    where = captions[0].text.strip() if captions else None
                elif len(captions) <= 1:
                    verified = None
                    where = captions[0].text.strip() if captions else None

            except NoSuchElementException as e:
                logger.info(f"Element is not found: {index}. {new_url}")
                return JSONResponse(
                    content={
                        "error": "Element is not found.",
                        "message": str(e.msg.strip()),
                    }
                )

            job_data = {
                "id": index,
                "job_id": job_id,
                "job_link": job_link,
                "job_title": job_title,
                "job_salary": job_salary,
                "job_description": job_description,
                "job_tags": job_tags,
                "job_company": job_company,
                "verified": verified,
                "where": where,
            }
            logger.info(f"Job data: {job_data}")

            data.append(job_data)
        if not data:
            return JSONResponse(status_code=404, content={"error": "No data found."})
        logger.info(f"Data collected: {data}")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        logger.info("Quiting from driver.")
        try:
            if driver:
                driver.quit()
        except WebDriverException as e:
            logger.error(f"Error during driver.quit(): {str(e)}")

    logger.info("Done.")
    logger.info(JSONResponse(content=data))
    return JSONResponse(content=data)
