from os import path
from datetime import datetime
from random import random, choice
from shutil import rmtree
from string import ascii_uppercase, digits
from time import sleep
from multiprocessing import current_process
import undetected_chromedriver as uc
from extension import proxies
import signal
import functools
from urllib.parse import urlparse
from logger import logger
from utils import utils


def delete_temp_folder(temp_folder, current_process_name):
    if path.isdir(f'extension_proxies/{temp_folder}'):
        logger.info(
            f'{current_process_name} - Удаление временной папки с прокси для сайта "{temp_folder}"')
        try:
            rmtree(f'extension_proxies/{temp_folder}')
        except Exception as e:
            logger.exception(e)
            logger.error(
                f'{current_process_name} - Ошибка при удалении папки - extension_proxies/{temp_folder}')


# TODO: need better cleanup
def handle_sigterm(driver, current_process_name, signum, frame):
    logger.warning(f'{current_process_name} - Остановка воркера / {signum} / {frame}')
    driver.quit()
    exit(0)


def get_chrome_options(proxy=None, random_string=''):
    chrome_options = uc.ChromeOptions()

    if proxy is not None:
        proxy_folder = proxies(proxy["user"], proxy["password"], proxy["ip"], proxy["port"], random_string)
        chrome_options.add_argument(f"--load-extension={proxy_folder}")
        chrome_options.add_argument(
            f'--proxy-server={proxy["protocol"]}://{proxy["user"]}:{proxy["password"]}@{proxy["ip"]}:{proxy["port"]}')

    # chrome_options.add_argument('--auto-open-devtools-for-tabs')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--window-size=800,600')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--no-first-run --no-service-autorun --password-store=basic')

    return chrome_options


def run(site_list, proxy_queue, lock):
    while True:
        with lock:
            if proxy_queue.empty():
                lock.release()
                sleep(random())
                lock.acquire()
                continue
            site = choice(site_list)
            proxy = proxy_queue.get()

        current_process_name = current_process().name
        logger.info(f'{current_process_name} - Воркер запущен')
        logger.info(f'{current_process_name} - Сайт и прокси: {site} / {proxy}')

        proxy_object = utils.get_proxy_object(proxy)
        random_string = ''.join(choice(ascii_uppercase + digits) for _ in range(7))

        logger.info(f'{current_process_name} - {site} / {proxy} - Временная папка с прокси для сайта "{random_string}"')
        chrome_options = get_chrome_options(proxy_object, random_string)

        logger.info(f'{current_process_name} - {site} / {proxy} - Запуск Chrome')
        driver = uc.Chrome(
            # version_main='120.0.6099.217',
            options=chrome_options)
        try:
            # Обработчик завершения работы
            sigterm_handler = functools.partial(handle_sigterm, driver, current_process_name)
            signal.signal(signal.SIGTERM, sigterm_handler)

            logger.info(f'{current_process_name} - {site} / {proxy} - Открытие сайта')
            driver.get(site)

            # ВАШ КОД

            # Создание скриншота
            url_netloc = urlparse(site).netloc
            screenshot_file_name = f'{current_process_name}_{url_netloc}_{datetime.now().microsecond}'
            logger.info(
                f'{current_process_name} - Создание скриншота, ' +
                f'имя файла - "{screenshot_file_name}.png"')
            try:
                screenshot_abs_path = path.abspath('screenshots')
                screenshot_path = path.join(screenshot_abs_path, f'{screenshot_file_name}.png')
                driver.save_screenshot(screenshot_path)
                logger.info(
                    f'{current_process_name} - Путь к файлу - {screenshot_path}')
            except Exception as e:
                logger.exception(e)
                logger.error(
                    f'{current_process_name} - Ошибка при создании скриншота')

            logger.success(f"{current_process_name} - {site} / {proxy} - Задача выполнена")
        except Exception as e:
            logger.exception(e)
            logger.error(f'{current_process_name} - {site} / {proxy} - ' +
                         f'Неизвестная ошибка')
        finally:
            logger.info(f'{current_process_name} - {site} / {proxy} - Закрытие Chrome')
            driver.quit()
            # Удаление временной папки
            delete_temp_folder(random_string, current_process_name)

            with lock:
                proxy_queue.put(proxy)
