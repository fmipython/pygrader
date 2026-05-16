class CoveConfig:
    def __init__(self, base_url: str, api_key: str, project_name: str):
        self.__base_url = base_url
        self.__api_key = api_key
        self.__project_name = project_name

    @property
    def base_url(self) -> str:
        return self.__base_url

    @property
    def api_key(self) -> str:
        return self.__api_key

    @property
    def project_name(self) -> str:
        return self.__project_name