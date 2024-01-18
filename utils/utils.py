import os
import shutil
from dataclasses import dataclass
from urllib.parse import urlparse
import psutil
from random import choice
from utils.messages import messages
from string import ascii_uppercase, digits
import undetected_chromedriver as uc
from undetected_chromedriver import ChromeOptions
from shutil import rmtree
from os import path
from config import proxies_folder, screenshots_folder, user_data_dir, drivers_dir
from logger import logger
import chromedriver_autoinstaller


def get_random_user_data_dir() -> str:
    """
    Генерирует и возвращает случайное имя директории для пользовательских данных.

    :return: Строка, представляющая случайное имя директории для пользовательских данных.
    """
    random_string = ''.join(choice(ascii_uppercase + digits) for _ in range(7))
    return f'{user_data_dir}/{random_string}'


def proxies(
        scheme: str,
        hostname: str,
        port: str,
        username: str,
        password: str,
        folder_name: str
) -> str:
    """
    Создает расширение для браузера Chrome, настраивающее прокси.

    Аргументы:
    - scheme (str): Протокол прокси (например, "http" или "socks5").
    - hostname (str): Хост прокси.
    - port (str): Порт прокси.
    - username (str): Имя пользователя для аутентификации на прокси (если требуется).
    - password (str): Пароль для аутентификации на прокси (если требуется).
    - folder_name (str): Имя папки, в которую будет сохранено расширение.

    :return:
    - str: Абсолютный путь к созданной папке с расширением.

    Пример использования:
    proxy_folder_path = proxies(
        scheme='http',
        hostname='proxy.example.com',
        port='8080',
        username='myusername',
        password='mypassword',
        folder_name='my_extension'
    )
    print(proxy_folder_path)
    # Вывод: /полный/путь/к/папке/my_extension
    """
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "%s",
                host: "%s",
                port: parseInt(%s)
              },
              bypassList: ["localhost"]
            }
          };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (scheme, hostname, port, username, password)

    proxy_folder = os.path.join('extension_proxies', folder_name)

    os.makedirs(proxy_folder)

    with open(f"{proxy_folder}/manifest.json", "w") as f:
        f.write(manifest_json)

    with open(f"{proxy_folder}/background.js", "w") as f:
        f.write(background_js)

    proxy_folder_path = os.path.abspath(proxy_folder)

    return proxy_folder_path


def get_random_question() -> str:
    """
    Возвращает случайный вопрос из списка доступных вопросов в файле 'questions.py'.

    :return:
    - str: Случайно выбранный вопрос.

    Пример использования:
    random_question = get_random_question()
    print(random_question)
    # Вывод: "Какой ваш любимый цвет?"
    """
    return choice(messages)


@dataclass
class ProxyInfo:
    scheme: str
    hostname: str
    port: str
    username: str
    password: str


def get_proxy_object(proxy_string: str) -> ProxyInfo:
    """
    Возвращает объект ProxyInfo, созданный из строки прокси.

    Аргументы:
        - proxy_string (str): Строка прокси в формате "username:password@host:port".

    :return:
        - ProxyInfo: Объект ProxyInfo, содержащий информацию о прокси.

    Исключения:
        - ValueError: Если строка прокси имеет неверный формат или отсутствуют обязательные компоненты.

    Пример использования:
        proxy_string = 'test_user:test_password@test_hostname:test_port'
        proxy_info = get_proxy_object(proxy_string)
        print(proxy_info)
    #Вывод:
        ProxyInfo(
                scheme='http',
                hostname='test_hostname',
                port='test_port',
                username='test_user',
                password='test_password'
                )
    """
    parsed_proxy = urlparse(f'http://{proxy_string}')

    scheme: str = parsed_proxy.scheme or 'http'
    hostname: str = parsed_proxy.hostname or ''
    port: str = str(parsed_proxy.port) or ''
    username: str = parsed_proxy.username or ''
    password: str = parsed_proxy.password or ''

    if not all([scheme, hostname, port, username, password]):
        raise ValueError('Неверный формат строки прокси')

    return ProxyInfo(scheme=scheme,
                     hostname=hostname,
                     port=port,
                     username=username,
                     password=password)


def get_proxy_extension_folder(proxy_info: ProxyInfo) -> str:
    """
    Создает расширение для браузера Chrome, настраивающее прокси на основе информации из объекта ProxyInfo.

    Аргументы:
    - proxy_info (ProxyInfo): Объект ProxyInfo, содержащий информацию о прокси.

    :return:
    - str: Абсолютный путь к созданной папке с расширением.

    Пример использования:
    proxy_info = ProxyInfo(
        scheme='http',
        hostname='proxy.example.com',
        port='8080',
        username='myusername',
        password='mypassword'
    )
    proxy_folder_path = get_proxy_extension_folder(proxy_info)
    print(proxy_folder_path)
    # Вывод: /полный/путь/к/папке/my_extension
    """
    random_string = ''.join(choice(ascii_uppercase + digits) for _ in range(7))
    proxy_folder_name = proxies(
        scheme=proxy_info.scheme,
        hostname=proxy_info.hostname,
        port=proxy_info.port,
        username=proxy_info.username,
        password=proxy_info.password,
        folder_name=random_string
    )

    return proxy_folder_name


def get_chromedriver_options(proxy_folder_name: str) -> ChromeOptions:
    """
    Возвращает настройки ChromeDriver с указанным расширением прокси.

    Аргументы:
        proxy_folder_name (str): Имя папки с расширением прокси.

    :return:
        ChromeOptions: Настройки ChromeDriver с указанным расширением прокси.

    """
    chromedriver_options = uc.ChromeOptions()
    chromedriver_options.add_argument(f"--load-extension={proxy_folder_name}")
    chromedriver_options.add_argument("--dns-prefetch-disable")
    chromedriver_options.add_argument("--disable-gpu")
    chromedriver_options.add_argument("--disable-crash-reporter")
    chromedriver_options.add_argument("--disable-in-process-stack-traces")
    chromedriver_options.add_argument("--disable-logging")
    chromedriver_options.add_argument("--disable-dev-shm-usage")
    chromedriver_options.add_argument("--log-level=3")
    chromedriver_options.add_argument("--mute-audio")

    return chromedriver_options


def delete_proxy_extension_folder(proxy_folder_name: str) -> None:
    """
    Удаляет папку с расширением прокси, если она существует.

    Аргументы:
    - proxy_folder_name (str): Имя папки с расширением прокси.

    :return:
    - None

    Пример использования:
    delete_proxy_extension_folder('my_extension')
    """
    if path.isdir(f'{proxies_folder}/{proxy_folder_name}'):
        try:
            rmtree(f'{proxies_folder}/{proxy_folder_name}')
        except Exception as e:
            logger.error(f'Ошибка при удалении папки')


def get_screenshot_path(site_url: str) -> str:
    """
    Возвращает путь для сохранения скриншота в формате PNG для указанного URL-адреса.

    Аргументы:
    - site_url (str): URL-адрес сайта.

    :return:
    - str: Абсолютный путь для сохранения скриншота.

    Пример использования:
    screenshot_path = get_screenshot_path('https://example.com')
    print(screenshot_path)
    # Вывод: /полный/путь/к/папке/сохранения/скриншота/example.com_A3CD1FG.png
    """
    url_netloc = urlparse(site_url).netloc
    random_string = ''.join(choice(ascii_uppercase + digits) for _ in range(7))
    screenshot_file_name = f'{url_netloc}_{random_string}'
    screenshot_abs_path = path.abspath(screenshots_folder)
    screenshot_path = path.join(screenshot_abs_path, f'{screenshot_file_name}.png')
    return screenshot_path


def get_script() -> str:
    """
    Возвращает строку с JavaScript-скриптом.

    :return:
    - str: JavaScript-скрипт.

    Пример использования:
    script = get_script()
    print(script)
    # Вывод: "console.log("Привет!");"
    """
    script = 'console.log("Привет!");'
    return script


def delete_proxy_folder() -> None:
    """
    Удаляет временную папку (обозначена в config.py -> proxies_folder), если она существует.

    :return:
    - None

    Пример использования:
    delete_proxy_folder()
    """
    if path.isdir(proxies_folder):
        try:
            rmtree(proxies_folder)
        except Exception as e:
            logger.error(f'Ошибка при удалении папки')


def delete_drivers_folder() -> None:
    """
    Удаляет временную папку (обозначена в config.py -> user_data_dir), если она существует.

    :return:
    - None

    Пример использования:
    clear_temp_folder()
    """
    if path.isdir(user_data_dir):
        try:
            rmtree(user_data_dir)
        except Exception as e:
            logger.error(f'Ошибка при удалении папки')


def get_all_children(proc: psutil.Process) -> list:
    """
    Рекурсивно получает все дочерние процессы для заданного процесса.

    Аргументы:
        proc (psutil.Process): Процесс, для которого нужно получить дочерние процессы.

    :return:
        list: Список всех дочерних процессов.

    """
    try:
        if len(proc.children()) == 0:
            return []
        else:
            returned_list = []
            for item in proc.children():
                returned_list.append(item)
                returned_list.extend(get_all_children(item))
            return returned_list
    except psutil.NoSuchProcess:
        return []


def terminate_all_process(list_processes: list) -> None:
    """
    Завершает список процессов и их дочерние процессы.

    Аргументы:
        list_processes (list): Список объектов psutil.Process, представляющих процессы для завершения.

    :return:
        None

    """
    for process in list_processes:
        children = get_all_children(psutil.Process(pid=process.pid))
        process.terminate()
        for child in children:
            try:
                child.terminate()
            except psutil.NoSuchProcess:
                logger.error(f'Ошибка при удалении процесса')


def get_chromedriver_version() -> int:
    """
    Получает версию установленного ChromeDriver.

    Returns:
        int: Версия установленного ChromeDriver.
    """
    return int(chromedriver_autoinstaller.get_chrome_version().split('.')[0])


def create_chromedrivers_for_workers(count: int = 0) -> list[str]:
    """
    Создает несколько экземпляров ChromeDriver для рабочих.

    Args:
        count (int, optional): Количество экземпляров ChromeDriver для создания. По умолчанию 0.

    Returns:
        list[str]: Список путей к созданным экземплярам ChromeDriver.
    """

    is_exist = os.path.exists(drivers_dir)
    if not is_exist:
        os.makedirs(drivers_dir)

    chromedriver_path = chromedriver_autoinstaller.install(path=drivers_dir)
    extension = os.path.splitext(chromedriver_path)[1]
    drivers_path_list = []
    for i in range(count):
        driver_path = f'{drivers_dir}/worker-{i}{extension}'
        shutil.copy2(chromedriver_path, driver_path)
        drivers_path_list.append(driver_path)

    return drivers_path_list


def create_screenshots_folder() -> None:
    """
    Создает папку для скриншотов, если она еще не существует.
    """
    is_exist = os.path.exists(screenshots_folder)
    if not is_exist:
        os.makedirs(screenshots_folder)
