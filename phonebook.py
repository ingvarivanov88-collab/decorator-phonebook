import csv
import re
from pprint import pprint


def format_phone(phone):
    """
    Приводит телефон к формату +7(999)999-99-99
    Если есть добавочный номер: +7(999)999-99-99 доб.9999
    """
    if not phone or phone == '':
        return ''

    phone_clean = str(phone).strip()

    # Паттерн для основного номера
    main_pattern = r'(\+7|8)?\s*\(?(\d{3})\)?\s*\-?(\d{3})\-?(\d{2})\-?(\d{2})'

    # Паттерн для добавочного номера
    ext_pattern = r'(доб\.?\s*|ext\.?\s*|д\.?\s*)(\d+)'

    # Ищем добавочный номер
    ext_match = re.search(ext_pattern, phone_clean, re.IGNORECASE)
    ext = ''
    if ext_match:
        ext = f' доб.{ext_match.group(2)}'

    # Ищем основной номер
    main_match = re.search(main_pattern, phone_clean)
    if main_match:
        formatted = f"+7({main_match.group(2)}){main_match.group(3)}-{main_match.group(4)}-{main_match.group(5)}"
        return formatted + ext

    return phone


def normalize_name(contact):
    """
    Нормализует ФИО: распределяет по полям lastname, firstname, surname
    """
    # Получаем первые три поля
    lastname = contact[0] if len(contact) > 0 else ''
    firstname = contact[1] if len(contact) > 1 else ''
    surname = contact[2] if len(contact) > 2 else ''

    # Если в lastname есть пробелы (значит там записано полное имя)
    if ' ' in lastname and not firstname:
        # Разбиваем полное имя на части
        name_parts = lastname.split()
        if len(name_parts) >= 1:
            contact[0] = name_parts[0]  # фамилия
        if len(name_parts) >= 2:
            contact[1] = name_parts[1]  # имя
        if len(name_parts) >= 3:
            contact[2] = name_parts[2]  # отчество

    # Если в firstname есть пробелы (значит там имя+отчество)
    elif ' ' in firstname and not surname:
        name_parts = firstname.split()
        if len(name_parts) >= 1:
            contact[1] = name_parts[0]  # имя
        if len(name_parts) >= 2:
            contact[2] = name_parts[1]  # отчество

    # Если в surname есть данные, но firstname пустое (особый случай)
    elif surname and not firstname:
        # Возможно, имя записано в surname
        contact[1] = contact[2]
        contact[2] = ''

    return contact


def merge_duplicates(contacts):
    """
    Объединяет дублирующиеся записи по фамилии и имени
    """
    merged = {}

    for contact in contacts[1:]:  # пропускаем заголовок
        # Ключ для группировки: фамилия + имя (в нижнем регистре)
        key = (contact[0].lower(), contact[1].lower())

        if key not in merged:
            merged[key] = contact.copy()
        else:
            # Объединяем данные: берем непустые значения из новой записи
            existing = merged[key]
            for i in range(len(contact)):
                if contact[i] and not existing[i]:
                    existing[i] = contact[i]

    # Возвращаем с заголовком
    return [contacts[0]] + list(merged.values())


def print_contacts(contacts, title="Контакты"):
    """
    Красиво выводит контакты
    """
    print(f"\n{title}:")
    print("=" * 100)
    for i, contact in enumerate(contacts):
        if i == 0:
            print(
                f"{'№':<3} {'Фамилия':<15} {'Имя':<15} {'Отчество':<15} {'Организация':<20} {'Должность':<35} {'Телефон':<25} {'Email':<25}")
            print("-" * 100)
        else:
            print(
                f"{i:<3} {contact[0]:<15} {contact[1]:<15} {contact[2]:<15} {contact[3]:<20} {contact[4]:<35} {contact[5]:<25} {contact[6]:<25}")
    print("=" * 100)


def main():
    # Читаем файл с данными
    input_file = "phonebook_raw.csv"

    try:
        with open(input_file, encoding="utf-8") as f:
            rows = csv.reader(f, delimiter=",")
            contacts_list = list(rows)

        print(f"📁 Загружен файл: {input_file}")
        print(f"📊 Всего записей (включая заголовок): {len(contacts_list)}")

        # Показываем исходные данные
        print_contacts(contacts_list, "ИСХОДНЫЕ ДАННЫЕ")

        # Сохраняем заголовок
        header = contacts_list[0]

        # Обрабатываем данные (начиная с 1-й строки)
        processed_contacts = [header]

        print("\n🔄 Обработка данных...")
        for i, contact in enumerate(contacts_list[1:], 2):
            original = contact.copy()

            # Нормализуем ФИО
            contact = normalize_name(contact)

            # Форматируем телефон
            if len(contact) > 5:
                contact[5] = format_phone(contact[5])

            processed_contacts.append(contact)

            # Выводим изменения
            if original != contact:
                print(f"  Строка {i}:")
                print(f"    Было: {original}")
                print(f"    Стало: {contact}")

        # Объединяем дубликаты
        print("\n🔄 Объединение дубликатов...")
        final_contacts = merge_duplicates(processed_contacts)

        # Показываем результат
        print_contacts(final_contacts, "РЕЗУЛЬТАТ ОБРАБОТКИ")

        # Статистика
        duplicates = len(processed_contacts) - len(final_contacts)
        print(f"\n📊 Статистика:")
        print(f"  - Всего записей в исходном файле: {len(contacts_list) - 1}")
        print(f"  - После обработки ФИО и телефонов: {len(processed_contacts) - 1}")
        print(f"  - После объединения дубликатов: {len(final_contacts) - 1}")
        print(f"  - Объединено дубликатов: {duplicates}")

        # Сохраняем результат
        output_file = "phonebook.csv"
        with open(output_file, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(final_contacts)

        print(f"\n✅ Готово! Результат сохранен в файл: {output_file}")

        # Дополнительная проверка для конкретных случаев из ваших данных
        print("\n🔍 Проверка обработки конкретных случаев:")

        # Ищем Мартиняхина (должен объединиться)
        martinyakhin = [c for c in final_contacts[1:] if c[0].lower() == 'мартиняхин']
        if martinyakhin:
            print(f"  ✓ Мартиняхин Виталий Геннадьевич объединен: {martinyakhin[0]}")

        # Ищем Лукину
        lukina = [c for c in final_contacts[1:] if c[0].lower() == 'лукина']
        if lukina:
            print(f"  ✓ Лукина Ольга Владимировна: телефон {lukina[0][5]}")

        # Ищем Лагунцова
        laguntsov = [c for c in final_contacts[1:] if c[0].lower() == 'лагунцов']
        if laguntsov:
            print(f"  ✓ Лагунцов Иван Алексеевич: email {laguntsov[0][6]}")

    except FileNotFoundError:
        print(f"❌ Ошибка: файл {input_file} не найден!")
        print(f"📁 Текущая директория: {os.getcwd()}")
        print("💡 Убедитесь, что файл phonebook_raw.csv находится в папке с программой")
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import os

    main()