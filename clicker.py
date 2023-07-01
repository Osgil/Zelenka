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
import json
import requests
from log_n_pass import password, login, bot_token, chat_id



if os.path.exists('lockfile'):
    # Файл блокировки уже существует - выходим
    print("Script is already running, exiting...")
    exit(1)

# Создаем файл блокировки
open('lockfile', "w").close() # создаем и закрываем локфайл

options = ChromeOptions()
options.add_argument("--headless=new") # добавляем опции, чтобы браузер работал незаметно для пользователей
options.add_argument("--disable-gpu=chrome=new") # это единственное рабочее сочетание параметров для UC, которое я нашёл
options.add_argument("--disable-popup-blocking=new")
contest_error = [i for i in range(100)] # формируем список для нумерации ошибок, когда не удалось зайти на страницу с розыгрышем
participate_error = [i for i in range(100)] # то же самое для ошибок при нажатии на кнопку участия 
part_delay = [i for i in range(5, 11)]
time_delay = [i for i in range(10, 16)]

# Данные для аутентификации импортируются из другого файла, свои вставьте напрямую
login = login
password =  password
bot_token = bot_token
params = {
            'chat_id': chat_id,
            'text': ''}
    
basic_tg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage?"

params['text'] = 'Участие принято'
requests.get(basic_tg_url, params=params)
params['text'] = 'Руслан залупа'
requests.get(basic_tg_url, params=params)



try: 
    with uc.Chrome(options=options) as browser: # запускаем с помощью контекстного менеджера, чтобы не закрывать вручную
            # аутентификация
        browser.get('https://zelenka.guru/login/') # переходим на страницу логина
        code = browser.execute_script(
        "var xhr = new XMLHttpRequest(); xhr.open('GET', arguments[0], false); xhr.send(null); return xhr.status;"
        ) # код ответа сервера # код ответа сервера 
        if code == 429: # проверяем, не говорит ли нам сервер, что нужно притормозить с запросами
            now = datetime.now() # определяем текущую дату 
            current_time = now.strftime("%D %H:%M:%S") # и форматируем её
            print(f'Время: {current_time} - Слишком много запросов, ждем минуту')
            time.sleep(60) # ждем 60 секунд, если сервер ругается
            browser.refresh() # обновляем страницу
        try:
            captcha_frame = (
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='loginForm--captcha captchaBlock']/div/iframe")))
            ) # ждем пока появится капча 
            browser.switch_to.frame(captcha_frame) # переключаемся на нее
            WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.XPATH, "//span[@id='success-text']"))) # ожидаем, пока она пройдется
            browser.switch_to.default_content() # переключаемся на стандартную область
            browser.find_element(By.ID, 'ctrl_pageLogin_login').send_keys(login) # вставляем СВОЙ(!) логин
            browser.find_element(By.ID, 'ctrl_pageLogin_password').send_keys(password) # и пароль
            intro = browser.find_element(By.XPATH, '//div[@class="loginForm--bottomBar"]/input[@value="Вход"]') # ищем кнопку сабмита
            browser.execute_script("return arguments[0].scrollIntoView(true);", intro) # скроллим до нее
            time.sleep(2) 
            intro.submit() # логинимся
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print(f'{current_time}: Залогинились')
        except TimeoutException: # если долго грузится страница, не появилась капча, или она была не пройдена - выходим, удаляя lockfile
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
            browser.get('https://zelenka.guru/forums/contests/') # переходим на страницу с розыгрышами
            last_page =int([page.text for page in browser.find_elements(By.XPATH, "//div[@class='PageNav']/nav/a")][-1]) # выявляем количество страниц, берем последнюю
            pages = [
                f'https://zelenka.guru/forums/contests/page-{page}?enabled=1&createTabButton=1' for page in range(1, last_page + 1)
                ] # генерируем ссылки на страницы с розыгрышами
        except:
            pages = [f'https://zelenka.guru/forums/contests/page-{page}?enabled=1&createTabButton=1' for page in range(1, 8)] 
        

        while True: # запускаем вечный цикл
            for page in pages: # итерируемся по страницам
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
                except: # обрабатываем ошибки, делаем скриншоты
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
                for link in links: # итерируемся по розыгрышам
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
                            ) # ищем капчу
                        browser.switch_to.frame(captcha_frame) # переключаемся на ее фрейм
                        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.XPATH, "//span[@id='success-text']"))) # ждем прохождения
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
                        button = browser.find_element(By.XPATH, "//div[@class='contestThreadBlock']/a") # ищем кнопку участия
                        browser.execute_script("return arguments[0].scrollIntoView(true);", button) # листаем до нее
                        browser.execute_script("window.scrollBy(0, -150);") # иногда окно прокручивается слишком сильно
                        time.sleep(choice(part_delay)) 
                        now = datetime.now()
                        current_time = now.strftime("%D %H:%M:%S")
                        button.click() # тогда кнопка участия не нажимается
                        print(f'{current_time} Участие принято')
                        time.sleep(2)
                    except:
                        continue
except:
    os.remove('lockfile')