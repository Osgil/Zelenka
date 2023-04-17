from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from random import choice
import undetected_chromedriver as uc
from datetime import datetime
import os
from undetected_chromedriver.options import ChromeOptions


if os.path.exists('lockfile'):
    # Файл блокировки уже существует - выходим
    print("Script is already running, exiting...")
    exit(1)

# Создаем файл блокировки
open('lockfile', "w").close()

options = ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu=chrome=new")
options.add_argument("--disable-popup-blocking=new")
contest_error = [i for i in range(100)]
participate_error = [i for i in range(100)]
part_delay = [i for i in range(5, 11)]
time_delay = [i for i in range(10, 16)]
try:
    with uc.Chrome(options=options) as browser:
            # аутентификация
        browser.get('https://zelenka.guru/login/')
        code = browser.execute_script(
        "var xhr = new XMLHttpRequest(); xhr.open('GET', arguments[0], false); xhr.send(null); return xhr.status;"
        ) # код ответа сервера # код ответа сервера
        if code == 429:
            now = datetime.now()
            current_time = now.strftime("%D %H:%M:%S")
            print(f'Время: {current_time} - Слишком много запросов, ждем минуту')
            time.sleep(60)
            browser.refresh()
        try:
            captcha_frame = (
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='loginForm--captcha captchaBlock']/div/iframe")))
            )
            browser.switch_to.frame(captcha_frame)
            WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.XPATH, "//span[@id='success-text']")))
            browser.switch_to.default_content()
            browser.find_element(By.ID, 'ctrl_pageLogin_login').send_keys('ruslanzalupa228@gmail.com')
            browser.find_element(By.ID, 'ctrl_pageLogin_password').send_keys('Lazisu22@')
            intro = browser.find_element(By.XPATH, '//div[@class="loginForm--bottomBar"]/input[@value="Вход"]')
            browser.execute_script("return arguments[0].scrollIntoView(true);", intro)
            time.sleep(2)
            intro.submit()
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print(f'{current_time}: Залогинились')
        except TimeoutException:
            os.remove('lockfile')
            exit(1)
        except:
            now = datetime.now()
            current_time = now.strftime("%D %H:%M:%S")
            browser.save_screenshot(f'Ошибка входа({current_time}).png')
            print(f'{current_time} Возникла при логине, завершаем программу')
            os.remove('lockfile')
            exit(1)
        
        
        try:
            browser.get('https://zelenka.guru/forums/contests/')
            last_page =int([page.text for page in browser.find_elements(By.XPATH, "//div[@class='PageNav']/nav/a")][-1])
            pages = [
                f'https://zelenka.guru/forums/contests/page-{page}?enabled=1&createTabButton=1' for page in range(1, last_page + 1)
                ]
        except:
            pages = [f'https://zelenka.guru/forums/contests/page-{page}?enabled=1&createTabButton=1' for page in range(1, 8)]
        

        while True:
            for page in pages:
                try:
                    browser.get(page)
                    code = browser.execute_script(
                    "var xhr = new XMLHttpRequest(); xhr.open('GET', arguments[0], false); xhr.send(null); return xhr.status;"
                    ) # код ответа сервера # код ответа сервера
                    if code == 429:
                        print(f'Слишком много запросов, не удалось подкючиться к странице {page}, ждем минуту')
                        time.sleep(60)
                        print(f'Пытаемся снова подключиться к странице {page}')
                        browser.refresh()
                    time.sleep(choice(time_delay))
                except:
                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    browser.save_screenshot(f'Ошибка итерации по страницам({current_time}).png')
                    print(f'{current_time}: возникла ошибка при итерации по страницам с розыгрышами')
                    os.remove('lockfile')
                    exit(1)

                treds = []
                treds += (browser.find_elements(
                By.XPATH, "//div[contains(@class, 'prefix') and not(contains(@class, 'contestParticipated'))]/div[@class='discussionListItem--Wrapper']/a"
                )) # ищем розыгрыши, в которых еще не приняли участие
                if len(treds) == 0:
                    continue

                links = [l.get_attribute('href') for l in treds] # извлекаем из них ссылки
                for link in links:
                    try:
                        browser.get(link)
                        code = browser.execute_script(
            "var xhr = new XMLHttpRequest(); xhr.open('GET', arguments[0], false); xhr.send(null); return xhr.status;"
            ) # код ответа сервера # код ответа сервера
                        if code == 429:
                            now = datetime.now()
                            current_time = now.strftime("%H:%M:%S")
                            print(f'Время: {current_time} - Слишком много запросов, ждем минуту')
                            time.sleep(60)
                            browser.refresh()
                        
                        captcha_frame = (
                        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='captchaBlock']/div/iframe")))
                            )
                        browser.switch_to.frame(captcha_frame)
                        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.XPATH, "//span[@id='success-text']")))
                        browser.switch_to.default_content()
                    except TimeoutException:
                        continue
                    except NoSuchElementException:
                        continue
                    except OSError:
                        continue
                    except:
                        now = datetime.now()
                        current_time = now.strftime("%D :%H:%M:%S")
                        browser.save_screenshot(f'Ошибка итерации по розыгрышам({current_time}).png')
                        print(f'Время: {current_time} - Ошибка при итерации по розыгрышам, завершаем программу') # делаем скрин, если не удалось получить доступ к странице
                        with open('errors.txt', 'a', encoding='utf-8') as file:
                            file.write(f'\nВремя {current_time} - {link} - не удалось получить доступ к странице с розыгрышем')
                        os.remove('lockfile')
                        exit(1)
                    
                    try:
                        button = browser.find_element(By.XPATH, "//div[@class='contestThreadBlock']/a")
                        browser.execute_script("return arguments[0].scrollIntoView(true);", button)
                        browser.execute_script("window.scrollBy(0, -150);")
                        time.sleep(choice(part_delay))
                        now = datetime.now()
                        current_time = now.strftime("%D %H:%M:%S")
                        button.click()
                        print(f'{current_time} Участие принято')
                        time.sleep(2)
                    except:
                        continue
except:
    os.remove('lockfile')



