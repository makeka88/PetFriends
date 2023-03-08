from settings import valid_email, valid_password
from api import PetFriends
import os

pf = PetFriends()

def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """
    Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key
    """

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем статус и результат
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
        Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
        запрашиваем список всех питомцев и проверяем что список не пустой.
        Доступное значение параметра filter - 'my_pets' либо ''
    """
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Бамблби', animal_type='кот',
                                     age='5', pet_photo='images/chubaka.jpg'):
    """
    Проверяем что можно добавить питомца с корректными данными
    """
    # Получаем полный путь к файлу с изображением питомца
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем статус и результат
    assert status == 200
    assert result['name'] == name


def test_successful_update_self_pet_info(name='Тыковка', animal_type='кошка', age=3):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception('Список питомцев пуст')


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, 'Кексик', 'кот', '2', 'images/red.jpg')
        _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


# 10 тестов
def test_add_new_pet_without_foto(name='Лаки', animal_type='кот', age='0'):

    """ Проверяем простой метод добавления питомца без фото  """

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем статус и результат
    assert status == 200
    assert result['name'] == name


def test_add_pets_correct_photo(pet_photo='images/1.jpg'):
    """
    Проверяем добавление корректного изображения питомцу
    """
    # Получаем полный путь к файлу с изображением питомца
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем добавить фото
    if len(my_pets['pets']) > 0:
        status, result = pf.add_pets_photo(auth_key, pet_photo, my_pets['pets'][0]['id'])

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['pet_photo'] != ''
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception('Список питомцев пуст')


def test_get_api_key_for_invalid_user(email='noname@mail.com', password='bbeeeee'):
    """
    Проверяем что запрос api ключа недоступен незарегистрированным пользователям
    """
    status, result = pf.get_api_key(email, password)
    assert status == 403


def test_get_all_pets_with_invalid_key(filter=''):
    """ Проверяем что запрос всех питомцев с некорректным api ключом недоступен
    """
    auth_key = {
        'key': 'very-invalid-api-key'
    }
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 403


def test_add_new_pet_without_photo_negative_age(name='Мрмяу', animal_type='котёнок', age='-5'):
    """
    Проверяем возможность добавления питомца с отрицательным возрастом. Ожидается код 400
    """

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем статус
    assert status == 400


def test_unsuccessful_update_another_user_pet_info(name='Ниндзя', animal_type='НЛО', age=999):
    """Проверяем возможность обновления информации о питомце другого пользователя. Ожидается отказ доступа"""

    # Получаем ключ auth_key и список питомцев на сайте
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа не равно 200 и имя питомца не заменилось
        assert status != 200

    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception('Список питомцев пуст')


def test_unsuccessful_update_self_pet_info_with_empty_type(name='Грязь', animal_type=' ', age=3):
    """Обновление данных питомца: новая порода пустая строка. Ожидается ответ 400"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 400
        assert status == 400

    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception('Список питомцев пуст')


def test_unsuccessful_delete_another_user_pet():
    """Проверяем возможность удаления питомца другого пользователя. Ожидается отказ доступа"""

    # Получаем ключ auth_key и запрашиваем список всех питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, all_pets = pf.get_list_of_pets(auth_key, '')

    # Берём id первого питомца из общего списка и отправляем запрос на удаление
    pet_id = all_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список всех питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа не равен 200
    assert status != 200


def test_add_new_pet_without_photo_empty_name(name='', animal_type='', age=''):
    """
    Простое добавление питомца (без фото) с пустым именем
    """

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем статус
    assert status != 200


#
def test_add_new_pet_without_photo_long_animal_type(name='Длиннопородный', age='1'):
    """
    Простое добавление питомца (без фото): порода - текст более 255 символов
    """

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца с длинным текстом в породе
    animal_type = 'Очееееееееенннььььь ' \
                  'длииииииииииииииииииииииииииннааааааааааааааааааааааааааяяяяяяяяяяяяяяяяяяяяяяяяяяяяяяяяяяяяяяя ' \
                  'поооооооооооооооооооооооооооорооооооооооооооооооооооооооооооодааааааааааааааааааа'

    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем статус
    assert status != 200


