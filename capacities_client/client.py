import logging
import os
from dotenv import load_dotenv
from requests import Session
from typing import Any, Optional
from uuid import UUID

from capacities_goodreads_automation.models import ObjectTypes, SearchResult, Space, Structure

API_URL = "https://api.capacities.io"
logger = logging.getLogger("capacities.client")


class CapacitiesAPIClient:
    """
    Capacities API Client
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        url: str = API_URL,
    ) -> None:
        load_dotenv()

        if api_key is None:
            api_key = os.getenv("CAPACITIES_API_TOKEN")

        if not api_key:
            raise ValueError("CAPACITIES_API_TOKEN cannot be missing.")

        self._api_key = api_key
        self._url = url.replace(".com/", ".com") + "/"

        self._session = Session()
        self._session.hooks = {
            "response": lambda r, *args, **kwargs: r.raise_for_status()
        }
        self._session.headers["Authorization"] = f"Bearer {self._api_key}"
        self._session.headers["Accept"] = "application/json"

    @staticmethod
    def _encode_params_in_url(endpoint: str, data: dict) -> str:
        params = ""
        get_char = "?"

        for key, value in data.items():
            params += f"{get_char}{key}={value}"
            get_char = "&"

        return endpoint + params

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
    ) -> dict[str, Any]:

        if method == "GET" and data is not None:
            endpoint = self._encode_params_in_url(endpoint, data)
            data = None

        if data is None:
            data = {}

        return self._session.request(
            method=method,
            url=self._url + endpoint,
            data=data
        ).json()

    @staticmethod
    def _validate_uuid(uuid_str: str) -> None:
        try:
            _ = UUID(uuid_str)
        except ValueError:
            raise ValueError(f"{uuid_str} is not a valid uuid string.")

    @property
    def spaces(self) -> list[Space]:
        """Get your spaces."""

        return [
            Space(**sp)
            for sp in self._request("GET", "spaces")["spaces"]
        ]

    def space_info(self, space_id: str) -> list[Structure]:
        """Returns all structures (object types) with property definitions and collections of a space."""

        self._validate_uuid(space_id)
        return [
            Structure(**st)
            for st in self._request("GET", "space-info", {"spaceid": space_id})["structures"]
        ]

    def search(
        self,
        mode: str,
        search_term: str,
        space_ids: list[str],
        filter_structure_ids: list[ObjectTypes]
    ) -> list[SearchResult]:
        """Returns content based on a search term in a set of spaces."""

        logger.warning("This endpoint is not working yet.")

        [self._validate_uuid(space_id) for space_id in space_ids]

        return [
            SearchResult(**st)
            for st in self._request(
                "POST",
                "search",
                {
                    "mode": mode,
                    "searchTerm": search_term,
                    "spaceIds": space_ids,
                    "filterStructureIds": [fs.structure_id for fs in filter_structure_ids],
                }
            )["results"]
        ]


if __name__ == "__main__":
    # TODO: move to tests

    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    space_id = os.getenv("CAPACITIES_SPACE_ID")
    assert space_id is not None

    client = CapacitiesAPIClient()

    print(client.spaces)
    print(client.space_info(space_id))
    print(client.search(
        mode="title",
        search_term="DONE",
        space_ids=[space_id],
        filter_structure_ids=[ObjectTypes.TAG],
    ))
