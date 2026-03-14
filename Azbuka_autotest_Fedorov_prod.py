# ТЕСТ: Проверка работоспособности всех элементов меню
# САЙТ: http://f.azbukar.beget.tech/
# СТИЛЬ: ООП с использованием функций
# ============================================================

# Блок 1 Импорт библиотек
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime 
import logging
import time

# Блок 2 Инициализация блока логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================
# БЛОК ОБЩИХ ВСПОМОГАТЕЛЬНЫХ ФУНКЦИЙ
# ============================================================

# Блок 3: Функция безопасного клика
def safe_click(driver, by, value, max_attempt=3):
    """Безопасное выполнение клика по элементу с повторными попытками"""
    for attempt in range(max_attempt):
        try:
            element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((by, value)))
            element.click()
            logger.info(f"Успешный клик по элементу: {by}={value}")
            return True
        except Exception as e:
            logger.warning(f"Попытка {attempt + 1}/{max_attempt} не удалась: {e}")
            if attempt < max_attempt - 1:
                time.sleep(0.1)
    logger.error(f"Не удалось кликнуть по элементу после {max_attempt} попыток")
    return False

# Блок 4_1: Функция безопасного возврата на главную
def safe_return_to_main_page(driver):
    """Безопасный возврат на главную страницу"""
    try:
        logger.info("  Попытка возврата на главную страницу")
        
        # Проверяем, не на главной ли мы уже
        if driver.current_url == "http://f.azbukar.beget.tech/":
            logger.info("  Уже на главной странице")
            return True
        
        # Пробуем клик по логотипу
        if safe_click(driver, By.XPATH, "//div[contains(@class, 'descktop_logo')]"):
            time.sleep(0.2)
            if driver.current_url == "http://f.azbukar.beget.tech/":
                logger.info("  ✓ Возврат на главную через логотип успешен")

            else:
                # Если логотип не сработал, пробуем прямой переход
                driver.get("http://f.azbukar.beget.tech/")
                logger.info("  ✓ Возврат на главную через прямую ссылку")
                return True
            
    except Exception as e:
        logger.error(f"  ✗ Ошибка при возврате на главную: {e}")
        # Последняя попытка - прямой переход
        try:
            driver.get("http://f.azbukar.beget.tech/")
            logger.info("  ✓ Возврат на главную через прямую ссылку (аварийный)")
            return True
        except:
            logger.error("  ✌ Критическая ошибка - не удалось вернуться на главную")
            return False
        
# Блок 4_2: Функция принудительного возврата на главную
def force_return_to_main(driver):
    """Принудительный возврат на главную страницу через прямой переход"""
    logger.info("  Принудительный переход на главную страницу")
    # Пробуем клик по логотипу
    if safe_click(driver, By.XPATH, "//div[contains(@class, 'descktop_logo')]"):
        time.sleep(0.3)
        if driver.current_url == "http://f.azbukar.beget.tech/":
            logger.info("  ✓ Возврат на главную через логотип успешен")
        else:
            # Если логотип не сработал, пробуем прямой переход
            driver.get("http://f.azbukar.beget.tech/")
            logger.info("  ✓ Возврат на главную через прямую ссылку")
    time.sleep(0.2)  # Небольшая пауза для стабильности
    return True

# Блок 5: Функция проверки открытия страницы
def verify_page_opened(driver, expected_text, page_type="page"):
    """
    Проверяет, что открылась правильная страница
    page_type: "page" для обычных страниц, "product" для продуктов
    """
    try:
        logger.info(f"Проверка открытия страницы '{expected_text}'")
        
        # Нормализуем ожидаемый текст
        import re
        normalized_expected = re.sub(r'\s+', ' ', expected_text).strip()
        
        # Пробуем найти элемент с нормализованным текстом
        try:
            # Сначала пробуем точное совпадение с normalize-space
            page_element = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((
                    By.XPATH, f"//div[contains(@class, 'page-header') and .//*[normalize-space()='{normalized_expected}']]")))
            
            logger.info(f"✓ Страница '{expected_text}' успешно открыта (точное совпадение)")
            return True
            
        except:
            # Если точное не нашлось, ищем по содержанию и проверяем текст
            page_element = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((
                    By.XPATH, f"//div[contains(@class, 'page-header') and .//*[contains(text(), '{normalized_expected[:20]}')]]")))
            
            page_text = page_element.text
            normalized_page = re.sub(r'\s+', ' ', page_text).strip()
            
            # Проверяем вхождение (игнорируя пробелы)
            if normalized_expected in normalized_page or normalized_page in normalized_expected:
                logger.info(f"✓ Страница '{expected_text}' успешно открыта (по содержанию)")
                return True
            else:
                logger.error(f"Ожидался текст '{expected_text}', получено: '{page_text}'")
                save_screenshot(driver, f"error_{normalized_expected[:30]}")
                return False
        
    except Exception as e:
        logger.error(f"✗ Ошибка при проверке страницы '{expected_text}': {e}")
        save_screenshot(driver, f"exception_{expected_text[:30]}")
        return False

# Блок 6: Функция сохранения скриншота
def save_screenshot(driver, name_prefix):
    """Сохранение скриншота с временной меткой"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name_prefix}_{timestamp}.png"
    driver.save_screenshot(filename)
    logger.info(f"Скриншот: {filename} сохранен")
    return filename

# Блок 7: Функция навигации к подменю
def navigate_to_submenu(driver, category_name):
    """
    Открывает путь: Услуги -> указанная категория
    Возвращает True если успешно, False если ошибка
    """
    try:
        logger.info(f"  Навигация: Услуги -> {category_name}")
        
        # Всегда начинаем с главной
        safe_return_to_main_page(driver)
        
        # Открываем главное меню "Услуги"
        if not safe_click(driver, By.XPATH,
            "//div[contains(@class, 'desktop_menu_link') and .//*[text()='Услуги']]"):
            logger.error(f"  ✗ Не удалось открыть меню 'Услуги'")
            return False
        time.sleep(0.3)
        
        # Открываем подменю указанной категории
        if not safe_click(driver, By.XPATH,
            f"//div[contains(@class, 'category_button') and .//*[text()='{category_name}']]"):
            logger.error(f"  ✗ Не удалось открыть категорию '{category_name}'")
            save_screenshot(driver, f"exception_{category_name}")
            return False
        time.sleep(0.3)
        
        logger.info(f"  ✓ Навигация к '{category_name}' выполнена успешно")
        return True
        
    except Exception as e:
        logger.error(f"  ✗ Ошибка навигации к '{category_name}': {e}")
        return False

# Блок 8: Функция проверки категории с продуктами
def check_product_category(driver, category_name, products):
    """
    Универсальная функция для проверки категории с несколькими продуктами
    Возвращает количество успешных и неудачных проверок
    """
    print("="*50)
    logger.info(f"📋 ПРОВЕРКА КАТЕГОРИИ С ПРОДУКТАМИ: {category_name}")
    print("="*50)
    
    # Всегда начинаем с главной
    safe_return_to_main_page(driver)
    time.sleep(0.2)

    successful_products = 0
    failed_products = 0
    
    for i, product in enumerate(products):
        logger.info(f"🔄 [{i+1}/{len(products)}] Проверка продукта '{product}'")
        
        # Навигация к категории
        if not navigate_to_submenu(driver, category_name):
            save_screenshot(driver, f"error_product_{product}")
            logger.error(f"  ✗ Пропуск продукта '{product}' из-за ошибки навигации")
            failed_products += 1
            force_return_to_main(driver)
            continue

        # Попытка открыть продукт:
        try:
            logger.info(f"  Попытка открыть продукт '{product}'")

            # Ищем и кликаем по продукту
            if not safe_click(driver, By.XPATH,
                f"//div[contains(@class, 'product_button') and .//*[text()='{product}']]"):

                # Если клик не удался
                save_screenshot(driver, f"error_product_{product}")
                logger.error(f"✗ Не удалось кликнуть по продукту '{product}'")
                force_return_to_main(driver)
                failed_products += 1
                continue

            time.sleep(0.3)

            # Проверка страницы продукта
            if verify_page_opened(driver, product, "product"):
                logger.info(f"  ✓ Продукт '{product}' успешно открыт")
                successful_products += 1
            else:
                logger.error(f"  ✗ Страница продукта '{product}' не открылась")
                failed_products += 1

        except Exception as e:
            logger.error(f"  ✗ Ошибка при открытии продукта '{product}': {e}")
            save_screenshot(driver, f"exception_product_{product}")
            failed_products += 1
            force_return_to_main(driver)
            continue
    
    # Финальная статистика
    print("="*50)
    logger.info(f"📊 ИТОГИ ПРОВЕРКИ КАТЕГОРИИ '{category_name}'")
    logger.info(f"✅ Успешно проверено: {successful_products} из {len(products)}")
    logger.info(f"❌ С ошибками: {failed_products} из {len(products)}")
    print("="*50)
    
    return {"success": successful_products, "failed": failed_products, "total": len(products)}

# Блок 9: Функция проверки категории с прямой ссылкой на продукт
def check_single_page_category(driver, category_name):
    """
    Функция для проверки категории, которая при клике ведет сразу на страницу
    (не содержит подменю с продуктами)
    Возвращает True если успешно, False если ошибка
    """
    print("="*50)
    logger.info(f"📋 ПРОВЕРКА КАТЕГОРИИ (ОДНА СТРАНИЦА): {category_name}")
    print("="*50)
    
    # Всегда начинаем с главной
    safe_return_to_main_page(driver)
    time.sleep(0.2)

    try:
        # Навигация к категории
        logger.info(f"🔄 Открытие категории '{category_name}'")
        
        # Открываем главное меню "Услуги"
        safe_click(driver, By.XPATH,
                  "//div[contains(@class, 'desktop_menu_link') and .//*[text()='Услуги']]")
        time.sleep(0.3)
        
        # Клик по категории (она сразу ведет на страницу)
        safe_click(driver, By.XPATH,
                  f"//div[contains(@class, 'category_button') and .//*[text()='{category_name}']]")
        time.sleep(0.3)
        
        # Проверяем, что открылась правильная страница
        if verify_page_opened(driver, category_name, "page"):
            logger.info(f"✅ Категория '{category_name}' успешно открыта")
            result = True
        else:
            logger.error(f"❌ Ошибка при открытии категории '{category_name}'")
            result = False

        return result
        
    except Exception as e:
        logger.error(f"✗ Ошибка при проверке категории '{category_name}': {e}")
        save_screenshot(driver, f"error_category_{category_name}")
        safe_return_to_main_page(driver)
        return False

# ============================================================
# БЛОК ОСНОВНЫХ ФУНКЦИЙ ТЕСТИРОВАНИЯ
# ============================================================

# Блок 10: Функция инициализации WebDriver
def init_driver():
    """Инициализация и настройка веб-драйвера Chrome"""
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.maximize_window()
        logger.info("WebDriver успешно инициализирован")
        return driver
    except Exception as e:
        logger.error(f"Ошибка при инициализации WebDriver: {e}")
        raise

# Блок 11: Функция открытия страницы сайта
def open_website(driver, url):
    """Открытие страницы браузера"""
    driver.get(url)

# Блок 12: Функция проверки элементов основного меню
def click_to_main_menu(driver):
    """
    Проверка всех пунктов основного меню
    Возвращает количество успешных ипровалившихся проверок
    """
    menu_items = [
        "Портфолио",
        "О компании",
        "Почему мы",
        "Рекламным агентствам",
        "Контакты",
        "Вакансии"
    ]
    
    successful = 0
    failed = 0
    
    # Отдельно обрабатываем "Услуги" (не требует проверки страницы)
    logger.info("🔄 Открытие меню 'Услуги'")
    try:
        safe_click(driver, By.XPATH,
                  "//div[contains(@class, 'desktop_menu_link') and .//*[text()='Услуги']]")
        time.sleep(0.3)
        logger.info("  Меню 'Услуги' открыто (без проверки страницы)")
        successful += 1
    except:
        logger.error("  Ошибка при открытии меню 'Услуги'")
        failed += 1
    
    # Проверка остальных пунктов меню
    for item in menu_items:
        logger.info(f"🔄 Открытие страницы '{item}'")
        
        try:
            safe_click(driver, By.XPATH,
                      f"//div[contains(@class, 'desktop_menu_link') and .//*[text()='{item}']]")
            time.sleep(0.3)
            
            if verify_page_opened(driver, item, "page"):
                successful += 1
            else:
                failed += 1
            time.sleep(0.3)
        except Exception as e:
            logger.error(f"  Ошибка при открытии '{item}': {e}")
            failed += 1
    
    # Финальный возврат на главную
    logger.info("🏠 Финальный возврат на главную страницу")
    safe_return_to_main_page(driver)
    
    logger.info(f"✅ Проверка основного меню завершена. Успешно: {successful}, ошибок: {failed}")
    return {"success": successful, "failed": failed, "total": len(menu_items) + 1}  # +1 за "Услуги"

# Блок 13: Функция проверки подменю 'Вывески из БУКВ'
def checking_to_menu_signboard_of_letters(driver):
    """
    Проверка всех продуктов в подменю 'Вывески из БУКВ'
    """
    products = [
        "Буквы с лицевой подсветкой",
        "Буквы с световым лицом и бортом",
        "Буквы с торцевой подсветкой",
        "Буквы с контражурной подсветкой",
        "Буквы с пиксельной  подсветкой",
        "Буквы с RGB подсветкой",
        "Буквы из нержавеющей стали",
        "Буквы из жидкого акрила",
        "Объемные буквы без подсветки",
        "Псевдообъемные буквы без подсветки",
        "Плоские буквы без подсветки",
        "Буквы из пенопласта"
    ]
    
    return check_product_category(driver, "Вывески из БУКВ", products)

# Блок 14: Функция проверки подменю 'СВЕТОВЫЕ КОРОБА'
def checking_to_menu_light_boxes(driver):
    """
    Проверка всех продуктов в подменю 'СВЕТОВЫЕ КОРОБА'
    """
    products = [
        "Односторонние лайтбоксы",
        "Двухсторонние лайтбоксы",
        "Фигурные световые короба",
        "Световые короба с инкрустацией",
        "Текстильные световые короба",
        "Напольные световые короба",
        "LED табло (Бегущая строка)"
    ]
    
    return check_product_category(driver, "СВЕТОВЫЕ КОРОБА", products)

# Блок 15: Функция проверки подменю 'КРЫШНЫЕ РЕКЛАМНЫЕ КОНСТРУКЦИИ'
def checking_to_menu_roof_advertising_structures(driver):
    """
    Проверка категории 'КРЫШНЫЕ РЕКЛАМНЫЕ КОНСТРУКЦИИ' (ведет сразу на страницу)
    """
    return check_single_page_category(driver, "КРЫШНЫЕ РЕКЛАМНЫЕ КОНСТРУКЦИИ")

# Блок 16: Функция проверки подменю 'РЕКЛАМНЫЕ СТЕЛЫ, ПИЛОНЫ, ПИЛЛАРЫ'
def checking_to_menu_pylons(driver):
    """
    Проверка всех продуктов в подменю 'РЕКЛАМНЫЕ СТЕЛЫ, ПИЛОНЫ, ПИЛЛАРЫ'
    """
    products = [
        "Стелы",
        "Пилоны",
        "Билборды",
        "Пиллары"
    ]
    
    return check_product_category(driver, "РЕКЛАМНЫЕ СТЕЛЫ, ПИЛОНЫ, ПИЛЛАРЫ", products)

# Блок 17: Функция проверки подменю 'БРАНДМАУЭР, СИТИ ФОРМАТ'
def checking_to_menu_firewall_urban_cityformat(driver):
    """
    Проверка всех продуктов в подменю 'БРАНДМАУЭР, СИТИ ФОРМАТ'
    """
    products = [
        "Брандмауэр",
        "СИТИ ФОРМАТ"
    ]
    
    return check_product_category(driver, "БРАНДМАУЭР, СИТИ ФОРМАТ", products)

# Блок 18: Функция проверки подменю 'ПАНЕЛЬ КРОНШТЕЙНЫ'
def checking_to_menu_panel_breackets(driver):
    """
    Проверка всех продуктов в подменю 'ПАНЕЛЬ КРОНШТЕЙНЫ'
    """
    products = [
        "Плоские – с прямыми поверхностями.",
        "Объемные – с выступающими буквами и элементами."
    ]
    
    return check_product_category(driver, "ПАНЕЛЬ КРОНШТЕЙНЫ", products)

# Блок 19: Функция проверки подменю 'СВЕТОВЫЕ ПАНЕЛИ'
def checking_to_menu_light_panels(driver):
    """
    Проверка категории 'СВЕТОВЫЕ ПАНЕЛИ'
    """
    products = [
        "Кристалайт",
        "Фреймлайт",
        "Уличные световые панели",
        "Акрилайт"
    ]

    return check_product_category(driver, "СВЕТОВЫЕ ПАНЕЛИ", products)

# Блок 20: Функция проверки подменю 'НЕОНОВЫЕ ВЫВЕСКИ' (ведет сразу на страницу)
def checking_to_menu_neon_signs(driver):
    """
    Проверка категории 'НЕОНОВЫЕ ВЫВЕСКИ' (ведет сразу на страницу)
    """
    return check_single_page_category(driver, "НЕОНОВЫЕ ВЫВЕСКИ")

# Блок 21: Функция проверки подменю 'ПЕЧАТЬ'
def checking_to_menu_print(driver):
    """
    Проверка категории 'ПЕЧАТЬ'
    """
    products = [
        "Интерьерная печать - пленка, баннер, сетка",
        "Широкоформатная печать - пленка, баннер, сетка",
        "Рулонная УФ печать",
        "Планшетная УФ печать",
        "Печать на ткани Самба"
    ]

    return check_product_category(driver, "ПЕЧАТЬ", products)

# Блок 22: Функция проверки подменю 'БРЕНДИРОВАНИЕ АВТОТРАНСПОРТА'
def checking_to_menu_car_branding(driver):
    """
    Проверка категории 'БРЕНДИРОВАНИЕ АВТОТРАНСПОРТА' (ведет сразу на страницу)
    """
    return check_single_page_category(driver, "БРЕНДИРОВАНИЕ АВТОТРАНСПОРТА")

# Блок 23: Функция проверки подменю 'РЕКЛАМА НА ОКНАХ'
def checking_to_menu_advertisign_on_windows(driver):
    """
    Проверка категории 'РЕКЛАМА НА ОКНАХ' (ведет сразу на страницу)
    """
    return check_single_page_category(driver, "РЕКЛАМА НА ОКНАХ")

# Блок 24: Функция проверки подменю 'POSM'
def checking_to_menu_posm(driver):
    """
    Проверка категории 'POSM'
    """
    products = [
        "ПЭТ карманы",
        "Объемные карманы из ОРГ стекла",
        "Меню-холдер",
        "Визитница",
        "L-образные подставки"
    ]
    return check_product_category(driver, "POSM", products)

# ============================================================
# БЛОК ЗАПУСКА ТЕСТОВ С ОБЩЕЙ СТАТИСТИКОЙ
# ============================================================

# Блок 25: Главная функция
def main():
    """Главная функция программы - точка входа"""
    driver = None
    start_time = datetime.now()
    
    # Общая статистика
    total_tests = 0
    total_success = 0
    total_failed = 0
    failed_categories = []
    
    try:
        # Инициализация и открытие сайта
        driver = init_driver()
        open_website(driver, "http://f.azbukar.beget.tech/")
        
        # Словарь с тестами и их описанием
        tests = [
            {"name": "Основное меню", "function": click_to_main_menu, "type": "menu"},
            {"name": "Вывески из БУКВ", "function": checking_to_menu_signboard_of_letters, "type": "products"},
            {"name": "СВЕТОВЫЕ КОРОБА", "function": checking_to_menu_light_boxes, "type": "products"},
            {"name": "КРЫШНЫЕ РЕКЛАМНЫЕ КОНСТРУКЦИИ", "function": checking_to_menu_roof_advertising_structures, "type": "single"},
            {"name": "РЕКЛАМНЫЕ СТЕЛЫ, ПИЛОНЫ, ПИЛЛАРЫ", "function": checking_to_menu_pylons, "type": "products"},
            {"name": "БРАНДМАУЭР, СИТИ ФОРМАТ", "function": checking_to_menu_firewall_urban_cityformat, "type": "products"},
            {"name": "ПАНЕЛЬ КРОНШТЕЙНЫ", "function": checking_to_menu_panel_breackets, "type": "products"},
            {"name": "СВЕТОВЫЕ ПАНЕЛИ", "function": checking_to_menu_light_panels, "type": "products"},
            {"name": "НЕОНОВЫЕ ВЫВЕСКИ", "function": checking_to_menu_neon_signs, "type": "single"},
            {"name": "ПЕЧАТЬ", "function": checking_to_menu_print, "type": "products"},
            {"name": "БРЕНДИРОВАНИЕ АВТОТРАНСПОРТА", "function": checking_to_menu_car_branding, "type": "single"},
            {"name": "РЕКЛАМА НА ОКНАХ", "function": checking_to_menu_advertisign_on_windows, "type": "single"},
            {"name": "POSM", "function": checking_to_menu_posm, "type": "products"}
        ]
        
        # Запуск всех тестов
        for test in tests:
            print(f"\n{'#'*60}")
            logger.info(f"ЗАПУСК ТЕСТА: {test['name']}")
            print(f"{'#'*60}")
            
            try:
                result = test["function"](driver)
            except Exception as e:
                logger.error(f"Критическая ошибка в тесте {test['name']}: {e}")
                result = {"success": 0, "failed": 1, "total": 1}
            
            # Обработка результатов в зависимости от типа теста
            if test["type"] == "menu":
                total_success += result["success"]
                total_failed += result["failed"]
                total_tests += result["total"]
                if result["failed"] > 0:
                    failed_categories.append(f"{test['name']} ({result['failed']} ошибок)")
            
            elif test["type"] == "products":
                total_success += result["success"]
                total_failed += result["failed"]
                total_tests += result["total"]
                if result["failed"] > 0:
                    failed_categories.append(f"{test['name']} ({result['failed']} ошибок)")
            
            elif test["type"] == "single":
                total_tests += 1
                if result:
                    total_success += 1
                else:
                    total_failed += 1
                    failed_categories.append(test["name"])
            
            time.sleep(1)

        safe_return_to_main_page(driver)
        
        # Время выполнения теста
        end_time = datetime.now()
        duration = end_time - start_time
        
        # ИТОГОВАЯ СТАТИСТИКА
        print("\n" + "="*70)
        print("📊 ИТОГОВАЯ СТАТИСТИКА ТЕСТИРОВАНИЯ")
        print("="*70)
        print(f"🕒 Время выполнения: {duration.total_seconds():.2f} секунд")
        print(f"📋 Всего проверок: {total_tests}")
        print(f"✅ Успешно: {total_success}")
        print(f"❌ С ошибками: {total_failed}")
        if total_tests > 0:
            success_rate = (total_success/total_tests*100)
            print(f"📈 Процент успеха: {success_rate:.1f}%")
        
        if failed_categories:
            print("\n⚠️ Проблемные категории:")
            for cat in failed_categories:
                print(f"   • {cat}")
        
        print("="*70)
        
        # Определение успешности теста
        if total_failed == 0:
            logger.info("🎉 ТЕСТ УСПЕШНО ЗАВЕРШЕН! Все проверки пройдены.")
            print("✨ РЕЗУЛЬТАТ: ТЕСТ ПРОЙДЕН УСПЕШНО")
        else:
            logger.error(f"❌ ТЕСТ ЗАВЕРШЕН С ОШИБКАМИ! Найдено {total_failed} проблем.")
            print(f"⚠️ РЕЗУЛЬТАТ: ТЕСТ НЕ ПРОЙДЕН (ошибок: {total_failed})")
            
        print("="*70)

    except Exception as e:
        logger.error(f"Тест завершился с критической ошибкой: {e}", exc_info=True)
        print("\n" + "="*70)
        print("❌ КРИТИЧЕСКАЯ ОШИБКА ВЫПОЛНЕНИЯ ТЕСТА")
        print("="*70)
    finally:
        if driver:
            time.sleep(3)
            driver.quit()
            logger.info("Браузер закрыт")

if __name__ == "__main__":
    main()