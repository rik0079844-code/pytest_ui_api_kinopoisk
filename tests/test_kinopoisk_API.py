import pytest
import allure
from pages.kinopoisk_page_API import KinopoiskApiClient
from config import (
    BASE_URL_API,
    API_TOKEN,
    SEARCH_TEXT_RUS,
    SEARCH_TEXT_ENG,
    FAKEMOVIE,
    GENRE_TEXT,
)


@pytest.fixture
def kinopoisk_client():
    return KinopoiskApiClient(
        base_url=BASE_URL_API,
        token=API_TOKEN,
    )


@allure.title("Поиск фильма по кириллическому названию")
@allure.description(
    "Проверка поиска фильма по запросу на кириллице и валидация "
    "структуры ответа API"
)
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("API: поиск фильмов")
@allure.story("Поиск по названию (кириллица)")
@pytest.mark.api
def test_search_movie_cyrillic_rus(kinopoisk_client):
    query = SEARCH_TEXT_RUS

    with allure.step(
        f"Выполняем поиск фильма по запросу '{query}' (limit=10)"
    ):
        response = kinopoisk_client.search_movie_by_title(
            query,
            limit=10,
        )

    with allure.step("Проверяем статус-код ответа"):
        assert response.status_code == 200

    with allure.step("Парсим JSON и проверяем наличие поля 'docs'"):
        data = response.json()
        assert "docs" in data and isinstance(data["docs"], list)

    with allure.step("Получаем список результатов через парсер"):
        results = kinopoisk_client.parse_search_response(response)

    with allure.step("Проверяем, что поиск вернул хотя бы один результат"):
        assert len(results) > 0, "Поиск вернул пустой список"

    with allure.step("Проверяем наличие ID у каждого найденного фильма"):
        for movie in results:
            assert "id" in movie, f"У фильма отсутствует ID: {movie}"

    with allure.step("Пытаемся найти точное совпадение по названию"):
        found = kinopoisk_client.find_result_containing_title(
            results,
            query,
        )
        if found is None:
            titles = [
                str(
                    m.get("nameRu")
                    or m.get("nameEn")
                    or m.get("title")
                    or "Unknown"
                )
                for m in results
            ]
            print(
                f"Не удалось найти точное совпадение для '{query}'. "
                f"Выдача: {titles}"
            )


@allure.title("Поиск фильма по латинскому названию")
@allure.description(
    "Проверка поиска фильма по запросу на латинице и валидация "
    "структуры ответа API"
)
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("API: поиск фильмов")
@allure.story("Поиск по названию (латиница)")
@pytest.mark.api
def test_search_movie_cyrillic_eng(kinopoisk_client):
    query = SEARCH_TEXT_ENG

    with allure.step(
        f"Выполняем поиск фильма по запросу '{query}' (limit=10)"
    ):
        response = kinopoisk_client.search_movie_by_title(
            query,
            limit=10,
        )

    with allure.step("Проверяем статус-код ответа"):
        assert response.status_code == 200

    with allure.step("Парсим JSON и проверяем наличие поля 'docs'"):
        data = response.json()
        assert "docs" in data and isinstance(data["docs"], list)

    with allure.step("Получаем список результатов через парсер"):
        results = kinopoisk_client.parse_search_response(response)

    with allure.step("Проверяем, что поиск вернул хотя бы один результат"):
        assert len(results) > 0, "Поиск вернул пустой список"

    with allure.step("Проверяем наличие ID у каждого найденного фильма"):
        for movie in results:
            assert "id" in movie, f"У фильма отсутствует ID: {movie}"

    with allure.step("Пытаемся найти точное совпадение по названию"):
        found = kinopoisk_client.find_result_containing_title(
            results,
            query,
        )
        if found is None:
            titles = [
                str(
                    m.get("nameRu")
                    or m.get("nameEn")
                    or m.get("title")
                    or "Unknown"
                )
                for m in results
            ]
            print(
                f"Не удалось найти точное совпадение для '{query}'. "
                f"Выдача: {titles}"
            )


@allure.title("Поиск фильмов по жанру (кириллический запрос)")
@allure.description(
    "Проверка поиска по жанру и валидация структуры ответа API"
)
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("API: поиск по жанру")
@allure.story("Поиск по жанру (кириллица)")
@pytest.mark.api
def test_search_by_genre_cyrillic(kinopoisk_client):
    genre_query = GENRE_TEXT
    limit = 5

    with allure.step(
        f"Выполняем поиск по жанру '{genre_query}' (limit={limit})"
    ):
        response = kinopoisk_client.search_by_genre(
            genre=genre_query,
            limit=limit,
        )

    with allure.step("Проверяем статус-код и содержимое ответа"):
        assert (
            response.status_code == 200
        ), (
            f"Ожидался 200, получен {response.status_code}. "
            f"Ответ: {response.text}"
        )

        data = response.json()
        assert (
            "docs" in data
        ), (
            f"В ответе отсутствует ожидаемое поле 'docs'. "
            f"Получены ключи: {list(data.keys())}"
        )
        assert isinstance(
            data["docs"],
            list,
        ), (
            f"Поле 'docs' должно быть списком, "
            f"получено: {type(data['docs'])}"
        )


@allure.title("Поиск по пустому жанру (граничный случай)")
@allure.description(
    "Проверка поведения API при пустом значении жанра и валидация "
    "структуры ответа"
)
@allure.severity(allure.severity_level.NORMAL)
@allure.feature("API: поиск по жанру")
@allure.story("Граничные значения: пустой жанр")
@pytest.mark.api
def test_search_by_genre_cyrillic_no_network_none(kinopoisk_client):
    genre_query = ""
    limit = 5

    with allure.step(
        f"Выполняем поиск по пустому жанру (limit={limit})"
    ):
        response = kinopoisk_client.search_by_genre(
            genre=genre_query,
            limit=limit,
        )

    with allure.step("Проверяем статус-код и содержимое ответа"):
        assert (
            response.status_code == 200
        ), (
            f"Ожидался 200, получен {response.status_code}. "
            f"Ответ: {response.text}"
        )

        data = response.json()
        assert (
            "docs" in data
        ), (
            f"В ответе отсутствует ожидаемое поле 'docs'. "
            f"Получены ключи: {list(data.keys())}"
        )
        assert isinstance(
            data["docs"],
            list,
        ), (
            f"Поле 'docs' должно быть списком, "
            f"получено: {type(data['docs'])}"
        )


@allure.title("Проверка обработки несуществующего фильма")
@allure.description(
    "Проверка, что при поиске несуществующего названия API "
    "возвращает пустой список"
)
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("API: поиск фильмов")
@allure.story("Граничный случай: несуществующее название")
@pytest.mark.api
def test_search_nonexistent_movie(kinopoisk_client):
    query = FAKEMOVIE

    with allure.step(
        f"Выполняем поиск несуществующего фильма '{query}'"
    ):
        response = kinopoisk_client.search_movie_by_title(
            query,
            limit=5,
        )

    with allure.step("Проверяем статус-код"):
        assert (
            response.status_code == 200
        ), (
            f"Ожидался 200, получен {response.status_code}. "
            f"Ответ: {response.text}"
        )

    with allure.step("Получаем и проверяем список результатов"):
        results = kinopoisk_client.parse_search_response(response)
        assert results == [], (
            f"Ожидался пустой список результатов, получено: {results}"
        )
