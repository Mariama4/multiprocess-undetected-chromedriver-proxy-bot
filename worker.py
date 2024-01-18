from time import sleep
from multiprocessing import Process, Queue
import undetected_chromedriver as uc
import utils
from logger import logger


class Worker(Process):
    """
    Класс, представляющий рабочий процесс.

    Аргументы:
        name (str): Имя рабочего процесса.
        site_list (list): Список сайтов для посещения.
        proxy_queue (Queue): Очередь прокси.
        lock (Lock): Объект блокировки.
        daemon (bool, optional): Флаг, указывающий, является ли процесс демоном. По умолчанию True.

    """

    def __init__(self,
                 name: str,
                 site_list: list,
                 proxy_queue: Queue,
                 driver_path: str,
                 *,
                 daemon: bool = True) -> None:
        self.site_list = site_list
        self.proxy_queue = proxy_queue
        self.driver = None
        self.driver_path = driver_path
        self.driver_version = utils.get_chromedriver_version()

        super().__init__(name=name, daemon=daemon)
        self.log = logger.bind(classname=self.name)
        self.log.success('Инициализирован')

    def run(self):
        """
        Запускает выполнение рабочего процесса.

        """
        while True:
            if self.proxy_queue.empty():
                sleep(5)
                continue
            proxy_string = self.proxy_queue.get()
            site_url = next(self.site_list)

            self.log = logger.bind(classname=self.name,
                                   url=site_url)

            proxy_info = utils.get_proxy_object(proxy_string=proxy_string)
            proxy_folder_name = utils.get_proxy_extension_folder(proxy_info=proxy_info)
            try:
                chromedriver_options = utils.get_chromedriver_options(proxy_folder_name=proxy_folder_name)
                self.driver = uc.Chrome(
                    version_main=self.driver_version,
                    options=chromedriver_options,
                    user_data_dir=utils.get_random_user_data_dir(),
                    driver_executable_path=self.driver_path,
                    headless=True,
                    log_level=3
                )
                self.driver.set_window_size(400, 580)
                try:
                    self.log.info('Ожидание загрузки сайта...')
                    self.driver.get(site_url)

                    # Ваш код

                    script = utils.get_script()
                    self.driver.execute_script(script)
                    sleep(10)

                    # Ваш код

                    try:
                        screenshot_path = utils.get_screenshot_path(site_url=site_url)
                        self.driver.save_screenshot(screenshot_path)
                        self.log.success(f'Скриншот сохранен - {screenshot_path}')
                    except:
                        self.log.error('Ошибка создания скриншота')
                except:
                    self.log.error('Неизвестная ошибка')
                finally:
                    self.log.info('Закрытие')
                    self.driver.quit()
            except Exception as e:
                self.log.exception(e)
                self.log.error('Неизвестная ошибка')
            finally:
                utils.delete_proxy_extension_folder(proxy_folder_name)
                self.proxy_queue.put(proxy_string)

    def start(self) -> None:
        """
        Запускает выполнение рабочего процесса.

        """
        self.log.success('Запущен')
        super().start()

    def join(self, timeout=None):
        """
        Блокирует выполнение программы, пока рабочий процесс не завершится или не истечет таймаут.

        Аргументы:
            timeout (float or None, optional): Таймаут ожидания завершения процесса. По умолчанию None.

        """
        self.log.success('Остановка (join)')
        super().join(timeout=timeout)

    def terminate(self):
        """
        Прекращает выполнение рабочего процесса.

        """
        self.log.success('Остановка (terminate)')
        super().terminate()
