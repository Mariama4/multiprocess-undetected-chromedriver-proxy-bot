from faker import Faker
from random import choice
import re
from utils.domains import domains
from utils.messages import messages
from utils.descriptions import descriptions

fake = Faker('ru_RU') # Change if u want


def get_random_email():
    email = fake.email().split('@')
    email[1] = choice(domains)
    email = '@'.join(email)
    return email


def get_random_message():
    return choice(messages)


def get_random_description():
    return choice(descriptions)


def get_random_person():
    name = fake.first_name()
    email = get_random_email()
    phone = fake.phone_number()
    description = get_random_description()
    message = get_random_message()

    person = {
        "name": name,
        "email": email,
        "phone": phone,
        "description": description,
        "message": message
    }

    return person


def get_proxy_object(proxy):
    splited_proxy_string = re.split('[:@]', proxy)
    # Протокол тоже должен устанавливаться в зависимости от прокси / обновить extensions
    proxy_object = {
        'protocol': 'http',
        'ip': splited_proxy_string[2],
        'port': splited_proxy_string[3],
        'user': splited_proxy_string[0],
        'password': splited_proxy_string[1]
    }

    return proxy_object
