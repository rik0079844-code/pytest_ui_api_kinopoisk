import pytest
import allure
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pages.kinopoisk_page_UI import SeachCinemaPage
from config import BASE_URL, SEARCH_TEXT_RUS, SEARCH_TEXT_ENG


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    yield driver
    driver.quit()


@allure.title("Поиск названия фильма на кириллице")
@allure.description(
    "Тест проверяет возможность введения названия "
    "фильма на кириллице."
)
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("Поиск на Кинопоиске")
@allure.story("Ввод поискового запроса на русском языке")
@pytest.mark.ui
def test_search_cinema_rus(driver):
    page = SeachCinemaPage(driver, BASE_URL)
    page.open()

    with allure.step(
        "Безопасное закрытие всплывающего окна, если оно есть"
    ):
        try:
            page.close_tab()
        except Exception:
            # Окно могло не появиться — это не ошибка теста
            pass

    search_text = SEARCH_TEXT_RUS
    with allure.step(f"Выполнение поиска по запросу '{search_text}'"):
        page.search_cinema(search_text)

    search_input_element = page.wait.until(
        lambda d: d.find_element(*page.SEARCH_BAR)
    )
    with allure.step(
        f"Проверка, что в поле ввода отображается текст '{search_text}'"
    ):
        assert search_input_element.get_attribute("value") == search_text


@allure.title("Поиск названия фильма на латинице")
@allure.description(
    "Тест проверяет возможность введения названия "
    "фильма на латинице."
)
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("Поиск на Кинопоиске")
@allure.story("Ввод поискового запроса на английском языке")
@pytest.mark.ui
def test_search_cinema_eng(driver):
    page = SeachCinemaPage(driver, BASE_URL)
    page.open()

    with allure.step(
        "Безопасное закрытие всплывающего окна, если оно есть"
    ):
        try:
            page.close_tab()
        except Exception:
            pass

    search_text = SEARCH_TEXT_ENG
    with allure.step(f"Выполнение поиска по запросу '{search_text}'"):
        page.search_cinema(search_text)

    search_input_element = page.wait.until(
        lambda d: d.find_element(*page.SEARCH_BAR)
    )
    with allure.step(
        f"Проверка, что в поле ввода отображается текст '{search_text}'"
    ):
        assert search_input_element.get_attribute("value") == search_text


@allure.title("Открытие страницы поиска случайного фильма")
@allure.description(
    "Тест проверяет работоспособность кнопки в виде "
    "лупы для открытия страницы поиска случайного фильма."
)
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("Навигация на Кинопоиске")
@allure.story("Переход на страницу случайного фильма")
@pytest.mark.ui
def test_search_random_page(driver):
    page = SeachCinemaPage(driver, BASE_URL)
    page.open()

    with allure.step(
        "Безопасное закрытие всплывающего окна, если оно есть"
    ):
        try:
            page.close_tab()
        except Exception:
            pass

    with allure.step(
        "Переход на страницу случайного фильма через кнопку поиска"
    ):
        page.search_random_cinema()

    with allure.step(
        "Проверка, что URL соответствует странице случайного фильма"
    ):
        page.assert_on_random_movie_page()


@allure.title("Открытие страницы расширенного поиска")
@allure.description(
    "Тест проверяет работоспособность кнопки "
    "«Расширенный поиск» для открытия страницы "
    "расширенного поиска."
)
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("Навигация на Кинопоиске")
@allure.story("Переход на страницу расширенного поиска")
@pytest.mark.ui
def test_advanced_search_page(driver):
    page = SeachCinemaPage(driver, BASE_URL)
    page.open()

    with allure.step(
        "Безопасное закрытие всплывающего окна, если оно есть"
    ):
        try:
            page.close_tab()
        except Exception:
            pass

    with allure.step("Переход на страницу расширенного поиска"):
        page.get_advanced_search()

    with allure.step(
        "Проверка, что URL соответствует странице "
        "расширенного поиска"
    ):
        page.assert_on_advanced_search_movie()


@allure.title("Открытие страницы фильма по поиску")
@allure.description(
    "Тест проверяет поиск и переход на страницу "
    "фильма по поиску."
)
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("Поиск и переход к карточке фильма")
@allure.story("Поиск фильма и переход на его страницу")
@pytest.mark.ui
def test_movie_genre_displays(driver):
    page = SeachCinemaPage(driver, BASE_URL)
    page.open()

    with allure.step(
        "Безопасное закрытие всплывающего окна, если оно есть"
    ):
        try:
            page.close_tab()
        except Exception:
            pass

    search_text = SEARCH_TEXT_RUS
    with allure.step(
        f"Поиск фильма по запросу '{search_text}' и "
        "переход на карточку"
    ):
        page.get_movie_genre_displays(search_text)

    with allure.step(
        "Проверка, что заголовок страницы соответствует "
        "ожидаемому"
    ):
        page.assert_on_correct_movie_page(search_text)
