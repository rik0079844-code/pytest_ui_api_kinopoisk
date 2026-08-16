import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Tuple


class SearchCinemaPage:
    """
    Page Object для страницы поиска Кинопоиска.
    Инкапсулирует локаторы элементов и методы взаимодействия с ними.
    """

    CLOSE_BUTTON: Tuple[By, str] = (
        By.CSS_SELECTOR,
        'button[data-tid="CloseButton"]'
    )

    SEARCH_BAR: Tuple[By, str] = (
        By.CSS_SELECTOR,
        'input[name="text"][role="combobox"]'
    )

    BUTTON_SEARCH: Tuple[By, str] = (
        By.CSS_SELECTOR,
        'button[aria-label="Найти"]'
    )

    BUTTON_ADVANCED_SEARCH: Tuple[By, str] = (
        By.CSS_SELECTOR,
        'a[aria-label="Расширенный поиск"]'
    )

    SEARCH_INPUT: Tuple[By, str] = (
        By.CSS_SELECTOR,
        'input[aria-label="Фильмы, сериалы, персоны"]'
    )

    MOVIE_CARD: Tuple[By, str] = (
        By.ID,
        'suggest-item-film-263531'
    )

    MOVIE_TITLE: Tuple[By, str] = (
        By.CSS_SELECTOR,
        'h1[itemprop="name"] span'
    )

    def __init__(self, driver: WebDriver, base_url: str) -> None:
        """
        Инициализация страницы.

        :param driver: WebDriver — экземпляр браузера для управления.
        :param base_url: str — базовый URL страницы, которую открывает класс.
        """
        self.driver = driver
        self.base_url = base_url
        self.wait: WebDriverWait = WebDriverWait(self.driver, 15)

    @allure.step("Открытие страницы Кинопоиска")
    def open(self) -> None:
        """Открывает страницу по сохранённому base_url."""
        self.driver.get(self.base_url)

    @allure.step("Закрытие всплывающего окна на странице")
    def close_tab(self) -> None:
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
                pass

    @allure.step("Проверка ввода названия в поисковой строке")
    def search_cinema(self, text: str) -> None:
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
    def search_random_cinema(self) -> None:
        """Нажимает кнопку поиска (лупа) для перехода к случайному фильму."""
        with allure.step("Ожидание кликабельной кнопки поиска"):
            search_button = self.wait.until(
                EC.element_to_be_clickable(self.BUTTON_SEARCH)
            )
        with allure.step("Клик по кнопке поиска"):
            search_button.click()

    @allure.step("Проверка перехода на страницу случайного фильма")
    def assert_on_random_movie_page(self) -> None:
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
    def get_advanced_search(self) -> None:
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
    def assert_on_advanced_search_movie(self) -> None:
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
    def get_movie_genre_displays(self, text: str) -> None:
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

        movie_card_locator = (
            By.XPATH,
            f"//*[contains(text(), '{text}')]"
        )

        with allure.step(
            f"Ожидание появления карточки фильма с названием '{text}'"
        ):
            movie_card = self.wait.until(
                EC.element_to_be_clickable(movie_card_locator)
            )
            movie_card.click()

        try:
            with allure.step(
                f"Проверка наличия поля ввода в подсказках (SEARCH_INPUT)"
            ):
                self.wait.until(
                    EC.presence_of_element_located(self.SEARCH_INPUT)
                )
        except Exception:
            pass

    @allure.step("Проверка, что открыта страница корректного фильма")
    def assert_on_correct_movie_page(
        self,
        expected_title_substring: str
    ) -> None:
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

    @allure.step("Проверка, работоспособности поисковой строки")    
    def get_search_value(self) -> str:
        search_input = self.wait.until(
            EC.visibility_of_element_located(self.SEARCH_BAR)
        )
        return search_input.get_attribute("value")
