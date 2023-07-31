import asyncio
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import  NoSuchElementException
from fastapi.responses import JSONResponse


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
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36", 
    ]
    return random.choice(user_agents)


async def get_job_data(country: str, job: str) -> JSONResponse:
    with webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'), options=get_chrome_options()) as driver:

        driver.delete_all_cookies()
        driver.header_overrides = {
            "User-Agent": get_random_user_agent(),
        }
        
        await asyncio.sleep(1)
     
        driver.get(f'https://{country}.jooble.org/SearchResult?date=2&p=5&ukw={job}')
        
        await asyncio.sleep(1)
        
        try:
            alert = driver.switch_to.alert
            alert.dismiss()
        except:
            pass

        data = []
          
        with ActionChains(driver) as action:
            try:
                salary_period = driver.find_element(By.XPATH, '//label[@for="period_3"]')
                action.scroll_to_element(salary_period).perform()
                action.move_to_element(salary_period).perform()
                action.click(salary_period).perform()
            except NoSuchElementException as e:
                pass
            
            await asyncio.sleep(0.5)
            
            try:
                salary_min = driver.find_element(By.XPATH, '//div[@class="-3rGFm"]//ul/li[2]/label')
                action.scroll_to_element(salary_min).perform()
                action.move_to_element(salary_min).perform()
                action.click(salary_min).perform()
            except NoSuchElementException as e:
                pass
        
        final_url = driver.current_url
        search_result_index = final_url.find("SearchResult?date=2")
        
        modified_url = final_url[:search_result_index + len("SearchResult?date=2")] + "&p=8" + final_url[search_result_index + len("SearchResult?date=2"):]
        driver.get(modified_url)
       
        await asyncio.sleep(1)

        try:
            articles = driver.find_elements(By.XPATH, '//article[@data-test-name="_jobCard"]')
        except NoSuchElementException as e:
            return JSONResponse(content={"error": "Element is not found.", "message": str(e.msg.strip())})

        for index, article in enumerate(articles, start=1):
            
            with ActionChains(driver) as action:
                action.scroll_to_element(article).perform()
                action.move_to_element(article).perform()

            try:
                alert = driver.switch_to.alert
                alert.dismiss()
            except:
                pass

            try:
                job_id = article.get_attribute("id")
                job_link = article.find_element(By.XPATH, './/header/h2/a').get_attribute("href")
                job_title = article.find_element(By.XPATH, './/header/h2/a').text
                try:
                    job_salary = article.find_element(By.XPATH, './/section//p[contains(@class, "p5Q1eF")]').text
                except NoSuchElementException as e:
                    job_salary = None
                # job_description = article.find_element(By.XPATH, './/section/div[1]/div[1]').text # this is deprecated
                job_tags_list = article.find_elements(By.XPATH, './/section/div[1]/div[2]//div[@data-name]')
                job_tags = [job_tag.text.strip() for job_tag in job_tags_list if job_tag.text.strip() != ""] if job_tags_list else None
                job_company = article.find_element(By.XPATH, './/section/div[2]/div/div[1]/div').text.strip()
                captions = article.find_elements(By.XPATH, './/section//div[contains(@class, "caption")]')
                where = captions[0].text.strip() if captions else None
                when = captions[1].text.strip() if len(captions) > 1 else None

            except NoSuchElementException as e:
                return JSONResponse(content={
                    "error": "Element is not found.",
                    "message": str(e.msg.strip()),
                    })

            job_data = {
                "id": index,
                "job_id": job_id,
                "job_link": job_link,
                "job_title": job_title,
                "job_salary": job_salary,
                # "job_description": job_description,
                "job_tags": job_tags,
                "job_company": job_company,
                "where": where,
                "when": when,   
            }


            data.append(job_data)
        driver.close()
              
    if not data:
        return JSONResponse(status_code=404, content={"erorr": "No data found."})
    
    return JSONResponse(content=data)