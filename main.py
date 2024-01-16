import json
import random
from os import path
from multiprocessing import Lock, Queue, Process, cpu_count
from worker import run
from shutil import rmtree
from logger import logger


def clear_temp_folder():
    if path.isdir('extension_proxies'):
        logger.info(
            f'Очистка временной папки')
        try:
            rmtree(f'extension_proxies')
        except Exception as e:
            logger.exception(e)
            logger.error(
                f'Ошибка при очистки папки - extension_proxies')


def main():
    logger.info('Запуск приложения')
    clear_temp_folder()
    logger.info('Для закрытия нажмите ENTER')

    try:
        sites = json.load(open('data/sites.json'))['sites']
        proxies = json.load(open('data/proxies.json'))['proxies']
    except KeyError:
        logger.error('Проверьте файлы sites.json/proxies.json! ' +
                     'В файле sites.json наличие массива с именем "sites", ' +
                     'в файле proxies.json наличие массива с именем "proxies"!')
        return
    except FileNotFoundError:
        logger.error('Проверьте наличие файлов в папке data: sites.json и proxies.json!')
        return
    except Exception as e:
        logger.exception(e)
        logger.error('Неизвестная ошибка, перезапустите приложение или сообщите разработчику')
        return

    if len(sites) == 0:
        logger.error('0 сайтов.')
        return

    if len(proxies) == 0:
        logger.error('0 прокси.')
        return

    random.shuffle(proxies)

    site_list = []
    proxy_queue = Queue()
    lock = Lock()

    logger.info(f'Количество сайтов - {len(sites)}')
    for site in sites:
        site_list.append(site)

    logger.info(f'Количество прокси - {len(proxies)}')
    for proxy in proxies:
        proxy_queue.put(proxy)

    num_workers = min(cpu_count() - 1, len(proxies))

    logger.info(
        'Максимальное количество воркеров ' +
        f'(Минимальное значение из: все ядра минус 1 или количество прокси; кастомное значение) - {num_workers}')

    try:
        workers = []
        for _ in range(num_workers):
            worker_process = Process(target=run, args=(site_list, proxy_queue, lock))
            logger.info(f'Запуск воркера - {worker_process.name}')
            worker_process.start()
            workers.append(worker_process)
    except Exception as e:
        logger.exception(e)
        logger.error('Произошла ошибка при создании воркера, перезапустите приложение или сообщите разработчику.')
        return

    if len(workers) != 0:
        logger.warning(f'Запущено {len(workers)} воркеров')
        input()
        for worker_process in workers:
            worker_process.terminate()
            worker_process.join()

        clear_temp_folder()
    else:
        logger.warning(f'Запущено 0 воркеров.')

    logger.warning(f'Завершение работы...')
    exit(0)


if __name__ == '__main__':
    main()
