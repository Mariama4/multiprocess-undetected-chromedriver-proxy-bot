import json
import random
import sys
import time
from multiprocessing import Queue, cpu_count, freeze_support
import utils
from config import data_folder, sites_filename, proxies_filename
from worker import Worker
from logger import logger


def main():
    log = logger.bind(
        classname=__name__
    )

    log.info('Запуск приложения')
    log.info('Для остановки приложения нажмите ENTER')

    utils.delete_drivers_folder()
    utils.delete_proxy_folder()
    utils.create_screenshots_folder()

    try:
        sites: list = json.load(open(f'{data_folder}/{sites_filename}.json'))['sites']
        proxies: list = json.load(open(f'{data_folder}/{proxies_filename}.json'))['proxies']
    except KeyError as e:
        log.error('Проверьте файлы sites.json/proxies.json! ' +
                     'В файле sites.json наличие массива с именем "sites", ' +
                     'в файле proxies.json наличие массива с именем "proxies"!')
        return
    except FileNotFoundError as e:
        log.error('Проверьте наличие файлов в папке data: sites.json и proxies.json!')
        return
    except Exception as e:
        log.error('Неизвестная ошибка, перезапустите приложение или сообщите разработчику')
        return

    if len(sites) == 0:
        log.error('0 сайтов')
        return

    if len(proxies) == 0:
        log.error('0 прокси')
        return

    log.info(f'Количество сайтов - {len(sites)}')
    log.info(f'Количество проксей - {len(proxies)}')

    random.shuffle(proxies)

    site_list = []
    proxy_queue = Queue()

    for site in sites:
        site_list.append(site)

    for proxy in proxies:
        proxy_queue.put(proxy)

    max_num_workers = min(cpu_count() - 1, len(proxies))

    while True:
        time.sleep(0.1)
        user_num_workers = input(
            f'Введите количество процессов (max - {max_num_workers}):'
        )
        try:
            user_num_workers = int(user_num_workers)
        except:
            log.warning('Некорректное значение!')
            continue
        if user_num_workers > max_num_workers:
            log.warning('Введенное количество больше доступного!')
            continue
        break

    log.warning(f'Количество воркеров: {user_num_workers}')

    drivers_path_list = utils.create_chromedrivers_for_workers(count=user_num_workers)

    if user_num_workers == 0:
        return

    workers = [Worker(name=f'worker-{idx}',
                      site_list=site_list,
                      proxy_queue=proxy_queue,
                      driver_path=driver_path
                      ) for idx, driver_path in enumerate(drivers_path_list)]

    try:
        for w in workers:
            w.start()
        log.warning(f'Запущено {len(workers)} воркеров')
        input()
    except Exception as e:
        log.error('Неизвестная ошибка')
    finally:
        log.warning(f'Завершение работы...')
        utils.terminate_all_process(workers)
        utils.delete_drivers_folder()
        utils.delete_proxy_folder()
        exit(0)


if __name__ == '__main__':

    if sys.platform.startswith('win32'):
        from console_patch_windows import disable_quick_edit_mode
        disable_quick_edit_mode()
        freeze_support()

    main()
