import aiohttp


async def make_request(url: str, method: str, settings: dict = {}, **kwargs) -> tuple:
    async with aiohttp.ClientSession(**settings) as session:
        async with session.request(method, url, **kwargs) as response:
            try:
                response.raise_for_status()
                response_json = await response.json()
                return response, response_json
            except aiohttp.ContentTypeError as e:
                print(e)
                raise e


async def make_download_request(
    url: str, method: str, settings: dict, **kwargs
) -> tuple:
    async with aiohttp.ClientSession(**settings) as session:
        async with session.request(method, url, **kwargs) as response:
            try:
                response.raise_for_status()
                response_content = await response.read()
                return response, response_content
            except aiohttp.ClientError as e:
                raise e
