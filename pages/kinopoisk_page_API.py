import requests
from typing import Any, Dict, List, Optional
import allure


class KinopoiskApiClient:
    @allure.step("Инициализация клиента API Кинопоиска")
    def __init__(self, base_url: str, token: str) -> None:
        """
        Параметры:
        - base_url: базовый URL API (например,
          "https://kinopoiskapi.unofficial.tech").
          Должен содержать только домен, без версии API и без
          завершающего слэша. rstrip("/") убирает слэш на конце,
          чтобы при склейке с endpoint не было двойного "/".
        - token: секретный API‑ключ (токен) для авторизации.
          Передаётся в заголовок X-API-KEY.
        """
        self.base_url = base_url.rstrip("/")
        self.headers: Dict[str, str] = {
            "X-API-KEY": token,
            "Accept": "application/json"
        }

    @allure.step("Выполнение HTTP-запроса и валидация Content-Type")
    def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Параметры:
        - endpoint: относительный путь к ресурсу API (например,
          "/v1.4/movie/search"). Склеивается с base_url в полный URL.
        - params: словарь параметров запроса (query-параметры).
          Например: {"query": "Матрица", "limit": 5}.
          Если None — запрос идёт без query-параметров.

        Внутри метода:
        - url: формируется как base_url + endpoint.
        - headers: берутся из self.headers (там уже есть токен и Accept).
        - timeout=10: таймаут 10 секунд — чтобы запрос не висел
          бесконечно при проблемах сети.
        - Content-Type: проверяется, что сервер действительно вернул JSON.
          Если нет — выбрасываем ошибку, чтобы не парсить мусор и сразу
          видеть проблему (неверный токен, неверный URL и т. п.).
        """
        url = f"{self.base_url}{endpoint}"
        resp = requests.get(
            url,
            headers=self.headers,
            params=params,
            timeout=10,
        )

        content_type = resp.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            raise RuntimeError(
                f"Ожидался JSON, но сервер вернул '{content_type}'. "
                f"Возможно, неверный URL или проблема с токеном. "
                f"Ответ (первые 300 символов): {resp.text[:300]}"
            )
        return resp

    @allure.step("Поиск фильма по названию через API")
    def search_movie_by_title(self, query: str, limit: int = 5) -> requests.Response:
        """
        Параметры:
        - query: поисковый запрос (название фильма), может быть на
          кириллице или латинице.
        - limit: максимальное число возвращаемых результатов
          (по умолчанию 5).

        Формирует запрос к эндпоинту /v1.4/movie/search с параметрами
        query и limit. Возвращает ответ от API (объект Response).
        """
        endpoint = "/v1.4/movie/search"
        params = {"query": query, "limit": limit}
        return self._request(endpoint, params=params)

    @allure.step("Поиск совпадения названия фильма в списке результатов")
    def find_result_containing_title(
        self,
        results: List[Dict[str, Any]],
        query: str
    ) -> Optional[Dict[str, Any]]:
        """
        Параметры:
        - results: список найденных фильмов (список словарей),
          полученный из API.
        - query: искомое название (подстрока), по которой ищем
          совпадение.

        Логика:
        - Если query пустой — сразу возвращаем None.
        - Приводим query к нижнему регистру для регистронезависимого
          поиска.
        - Для каждого фильма смотрим поле names (список объектов
          с названиями).
        - В каждом объекте names берём text (текст названия).
          Если его нет — пропускаем.
        - Проверяем, содержится ли query_lower в text.lower().
          Если да — возвращаем этот фильм.
        - Если ни одно совпадение не найдено — возвращаем None.
        """
        if not query:
            return None

        query_lower = query.lower()

        for item in results:
            # Получаем список названий, по умолчанию пустой список,
            # чтобы не было ошибок
            names_list = item.get("names") or []

            for name_obj in names_list:
                # Берём текст, если его нет — пропускаем
                text = name_obj.get("text")
                if not text:
                    continue

                # Проверка на совпадение (регистронезависимая)
                if query_lower in text.lower():
                    return item

        for movie in results:
            # Проверяем русское название (если поле существует)
            name_ru = movie.get('nameRu', '') or ''
            # Проверяем английское название (если поле существует)
            name_en = movie.get('nameEn', '') or ''
            # Проверяем основное поле name (если есть)
            name_main = movie.get('name', '') or ''
            
            # Приводим все к нижнему регистру для сравнения
            if (query_lower in name_ru.lower() or 
                query_lower in name_en.lower() or 
                query_lower in name_main.lower()):
                return movie
                
        return None

    @allure.step("Поиск фильмов по жанру через API")
    def search_by_genre(self, genre: str, limit: int = 5) -> requests.Response:
        """
        Параметры:
        - genre: название жанра (например, "драма", "фантастика").
          Передаётся как значение параметра genres.name.
        - limit: максимальное число возвращаемых фильмов
          (по умолчанию 5).

        Запрос идёт на /v1.4/movie с query-параметром genres.name=genre
        и limit. Это фильтрация по жанру на стороне API.
        """
        endpoint = "/v1.4/movie"
        params = {"genres.name": genre, "limit": limit}
        return self._request(endpoint, params=params)

    @allure.step("Парсинг ответа API и извлечение списка результатов")
    def parse_search_response(self, response: requests.Response) -> List[Dict[str, Any]]:
        """
        Параметр:
        - response: объект ответа от API (requests.Response),
          полученный после запроса.

        Логика:
        - Если статус-код не 200 — считаем, что результатов нет,
          возвращаем пустой список.
        - Пытаемся распарсить JSON.
        - API v1.4 возвращает список фильмов в поле docs
          (а не results).
        - Если docs нет или это не список — возвращаем пустой список.
        - Иначе возвращаем содержимое docs.
        """
        if response.status_code != 200:
            return []

        data = response.json()
        results = data.get("docs", [])

        if not isinstance(results, list):
            return []
        return results
    
