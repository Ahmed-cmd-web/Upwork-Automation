from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time


class SelenuimExtractor:


    def __init__(self,url,upwork_email,upwork_password,upwork_secret_answer):
        self.url=url
        self.email=upwork_email
        self.password=upwork_password
        self.secret_answer=upwork_secret_answer
        self.username_field_id='login_username'
        self.username_button_id='login_password_continue'
        self.password_field_id='login_password'
        self.password_button_id='login_control_continue'
        self.load_more_button_data_test='load-more-button'
        
    

    def __scroll_down(self):
        scroll_pos_init = self.driver.execute_script("return window.pageYOffset;")
        stepScroll = 300

        while True:
            self.driver.execute_script(f"window.scrollBy(0, {stepScroll});")
            scroll_pos_end = self.driver.execute_script("return window.pageYOffset;")
            time.sleep(0.75)
            if scroll_pos_init >= scroll_pos_end:
                break
            scroll_pos_init = scroll_pos_end
            yield self.driver.page_source
    
    def __load_more_posts(self):
        load_more=self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,f"button[data-test='{self.load_more_button_data_test}']")))
        load_more.click()
        time.sleep(2)
        

    def __extract_content_from_html(self,html):
        job_posts_data_test_attr='job-tile-list'
        soup=BeautifulSoup(html,'html.parser')
        job_posts=soup.find('div',**{'data-test':job_posts_data_test_attr}).find_all('section',**{'data-ev-sublocation':'job_feed_tile'})



        containers_and_classNames_and_wanted={
            'title':('a','link','data-ev-label','innerHtml'),
            'link':('a','link','data-ev-label','href'),
            'description':('span','job-description-text','data-test','innerHtml'),
            'proposals':('strong','proposals','data-test','innerHtml'),
            'country':('small','client-country','data-test','innerHtml')
        }

        for post in job_posts:
            res={}
            for key,(tag,used_attr_value,used_attr,attr) in containers_and_classNames_and_wanted.items():
                try:
                    if attr=='innerHtml':
                        res[key]=post.find(tag,**{used_attr:used_attr_value}).text.strip()
                    else:
                        res[key]=post.find(tag,**{used_attr:used_attr_value}).get(attr)
                except:
                    break
            if 'title' in res and 'description' in res:
                yield res
    


    def extract(self,max_results=20):
        self.driver = uc.Chrome()
        self.wait=WebDriverWait(self.driver, 20,poll_frequency=2)
        self.driver.get(self.url)
        username_field=self.wait.until(EC.element_to_be_clickable((By.ID,self.username_field_id)))
        username_field.send_keys(self.email)
        username_button=self.wait.until(EC.element_to_be_clickable((By.ID,self.username_button_id)))
        username_button.click()
        time.sleep(4)
        password_field=self.wait.until(EC.element_to_be_clickable((By.ID,self.password_field_id)))
        password_field.send_keys(self.password)
        password_button=self.wait.until(EC.element_to_be_clickable((By.ID,self.password_button_id)))
        password_button.click()
        time.sleep(4)

        try:
            secret_field=self.wait.until(EC.element_to_be_clickable((By.ID,'login_secret_answer')))
            secret_field.send_keys(self.secret_answer)
            secret_button=self.wait.until(EC.element_to_be_clickable((By.ID,'login_control_continue')))
            secret_button.click()
            time.sleep(2)
        except:
            pass


        results=[]
        titles=set()
        while len(results)<max_results:
            for page in self.__scroll_down():
                for job_post in self.__extract_content_from_html(page):
                    if job_post['title'] not in titles:
                        results.append(job_post)
                        titles.add(job_post['title'])
            self.__load_more_posts()
        self.driver.quit()

        return results

