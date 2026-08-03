import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SeachCinemaPage:
    """
    Page Object для страницы поиска Кинопоиска.
    Инкапсулирует локаторы элементов и методы взаимодействия с ними.
    """

    # Локатор кнопки закрытия всплывающего окна.
    # By.CSS_SELECTOR — стратегия поиска; селектор ищет кнопку
    # по атрибуту data-tid="CloseButton".
    CLOSE_BUTTON = (
        By.CSS_SELECTOR,
        'button[data-tid="CloseButton"]'
    )

    # Локатор поисковой строки (базовый).
    # Ищет input с name="text" и ролью combobox.
    SEARCH_BAR = (
        By.CSS_SELECTOR,
        'input[name="text"][role="combobox"]'
    )

    # Локатор кнопки поиска (лупа).
    # Ищет кнопку по aria-label="Найти".
    BUTTON_SEARCH = (
        By.CSS_SELECTOR,
        'button[aria-label="Найти"]'
    )

    # Локатор ссылки «Расширенный поиск».
    # Ищет a по aria-label="Расширенный поиск".
    BUTTON_ADVANCED_SEARCH = (
        By.CSS_SELECTOR,
        'a[aria-label="Расширенный поиск"]'
    )

    # Локатор поля ввода в подсказках поиска.
    # Ищет input по aria-label="Фильмы, сериалы, персоны".
    SEARCH_INPUT = (
        By.CSS_SELECTOR,
        'input[aria-label="Фильмы, сериалы, персоны"]'
    )

    # Локатор карточки фильма в подсказках.
    # Пример жёстко заданного ID (в реальных тестах лучше избегать).
    MOVIE_CARD = (
        By.ID,
        'suggest-item-film-263531'
    )

    # Локатор заголовка (названия) фильма на странице фильма.
    # Ищет span внутри h1[itemprop="name"].
    MOVIE_TITLE = (
        By.CSS_SELECTOR,
        'h1[itemprop="name"] span'
    )

    def __init__(self, driver, base_url):
        """
        Инициализация страницы.

        :param driver: WebDriver — экземпляр браузера для управления.
        :param base_url: str — базовый URL страницы, которую открывает класс.
        """
        self.driver = driver
        self.base_url = base_url
        # WebDriverWait — объект ожидания; 10 — таймаут в секундах.
        self.wait = WebDriverWait(self.driver, 10)

    @allure.step("Открытие страницы Кинопоиска")
    def open(self):
        """Открывает страницу по сохранённому base_url."""
        self.driver.get(self.base_url)

    @allure.step("Закрытие всплывающего окна на странице")
    def close_tab(self):
        """Закрывает всплывающее окно, если оно присутствует."""
        with allure.step(
            "Ожидание кликабельной кнопки закрытия окна"
        ):
            try:
                close_btn = self.wait.until(
                    EC.element_to_be_clickable(self.CLOSE_BUTTON)
                )
                with allure.step("Клик по кнопке закрытия"):
                    close_btn.click()
            except Exception:
                # Окно могло не появиться — это не ошибка.
                pass

    @allure.step("Проверка ввода названия в поисковой строке")
    def search_cinema(self, text: str):
        """
        Вводит текст в поисковую строку.

        :param text: str — текст для ввода в поиск.
        """
        with allure.step(
            f"Ожидание поисковой строки (locator: {self.SEARCH_BAR})"
        ):
            search_input = self.wait.until(
                EC.presence_of_element_located(self.SEARCH_BAR)
            )
        with allure.step(f"Ввод текста '{text}' в строку поиска"):
            search_input.send_keys(text)

    @allure.step("Открытие страницы для поиска случайного фильма")
    def search_random_cinema(self):
        """Нажимает кнопку поиска (лупа) для перехода к случайному фильму."""
        with allure.step("Ожидание кликабельной кнопки поиска"):
            search_button = self.wait.until(
                EC.element_to_be_clickable(self.BUTTON_SEARCH)
            )
        with allure.step("Клик по кнопке поиска"):
            search_button.click()

    @allure.step("Проверка перехода на страницу случайного фильма")
    def assert_on_random_movie_page(self):
        """
        Проверяет, что URL содержит '/chance/' — признак страницы
        случайного фильма.
        """
        url = self.driver.current_url
        with allure.step(
            f"Проверка URL на подстроку '/chance/': {url}"
        ):
            assert "/chance/" in url, (
                f"Ожидался URL с '/chance/', но текущий: {url}"
            )

    @allure.step("Открытие страницы расширенного поиска")
    def get_advanced_search(self):
        """Нажимает кнопку «Расширенный поиск»."""
        with allure.step(
            "Ожидание кликабельной кнопки «Расширенный поиск»"
        ):
            search_button = self.wait.until(
                EC.element_to_be_clickable(self.BUTTON_ADVANCED_SEARCH)
            )
        with allure.step("Клик по кнопке «Расширенный поиск»"):
            search_button.click()

    @allure.step("Проверка перехода на страницу расширенного поиска")
    def assert_on_advanced_search_movie(self):
        """
        Проверяет, что URL содержит '/s/' — признак страницы
        расширенного поиска.
        """
        url = self.driver.current_url
        with allure.step(f"Проверка URL на подстроку '/s/': {url}"):
            assert "/s/" in url, (
                f"Ожидался URL с '/s/', но текущий: {url}"
            )

    @allure.step("Открытие страницы фильма по поиску")
    def get_movie_genre_displays(self, text: str):
        """
        Выполняет поиск фильма по названию и переходит на его страницу.

        :param text: str — название фильма для поиска.
        """
        with allure.step("Очистка поля ввода перед новым поиском"):
            search_input = self.wait.until(
                EC.presence_of_element_located(self.SEARCH_BAR)
            )
            search_input.clear()
        with allure.step(f"Ввод текста '{text}' в поле поиска"):
            search_input.send_keys(text)
        with allure.step(
            "Ожидание кликабельного элемента подсказки"
        ):
            extra_input = self.wait.until(
                EC.element_to_be_clickable(self.SEARCH_INPUT)
            )
            extra_input.click()
        with allure.step("Выбор карточки фильма из подсказок"):
            movie_card = self.wait.until(
                EC.element_to_be_clickable(self.MOVIE_CARD)
            )
            movie_card.click()

    @allure.step("Проверка, что открыта страница корректного фильма")
    def assert_on_correct_movie_page(self, expected_title_substring: str):
        """
        Проверяет, что заголовок фильма содержит ожидаемую подстроку.

        :param expected_title_substring: str — подстрока, которую
                                         ожидаем увидеть в заголовке.
        """
        with allure.step(
            f"Ожидание видимости заголовка фильма "
            f"(locator: {self.MOVIE_TITLE})"
        ):
            title_element = self.wait.until(
                EC.visibility_of_element_located(self.MOVIE_TITLE)
            )
        title_text = title_element.text
        with allure.step(
            f"Сравнение заголовка: ожидалось '{expected_title_substring}', "
            f"найдено '{title_text}'"
        ):
            assert expected_title_substring.lower() in title_text.lower(), (
                f"Ожидалось, что заголовок содержит "
                f"'{expected_title_substring}', но найден: '{title_text}'"
            )
