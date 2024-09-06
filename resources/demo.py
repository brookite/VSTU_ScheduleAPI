import requests

base_url = "http://localhost:8000"


# Например, получим доступ ко всем занятиям
r = requests.get(f"{base_url}/api/events")
print(r.json())


# Авторизация пока поддерживается в данном API только как session-based
# К сожалению, он требует CSRF токен и использование этого способа авторизации достаточно сложное
# Рекомендуется сделать pull-request с реализацией авторизации для API через JWT, OAuth или токены
# https://www.django-rest-framework.org/api-guide/authentication/


# Данные в Cookies у каждой сессии авторизации будут разные
cookies = {
    "sessionid": "po4hympdjpugoyirzlrwmkjma15s6tdq",
    "csrftoken": "GlvmTdebt45bWYE74OfzmpWeIh4o1TL5",
}

# Например, удалим следующую запись
r = requests.delete(f"{base_url}/api/events/14/", cookies=cookies)
print(r.json())
