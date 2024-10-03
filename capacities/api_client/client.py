import logging
import os
from dotenv import load_dotenv
from requests import Response, Session
from typing import Optional
from uuid import UUID

from capacities.api_client.models import ObjectTypes, Origin, SearchResult, Space, Structure


logger = logging.getLogger("capacities.api_client")
API_URL = "https://api.capacities.io"


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

        if (
            (preferred_space_id := os.getenv("CAPACITIES_PREFERRED_SPACE_ID"))
            and self._validate_uuid(preferred_space_id)
        ):
            preferred_space_id = preferred_space_id
        else:
            preferred_space_id = None

        self._preferred_space_id: Optional[str] = preferred_space_id

        self._session = Session()
        self._session.hooks = {
            "response": lambda r, *args, **kwargs: r.raise_for_status()
        }
        self._session.headers["Authorization"] = f"Bearer {self._api_key}"

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
    ) -> Response:

        if method == "GET" and data is not None:
            endpoint = self._encode_params_in_url(endpoint, data)
            data = None

        if data is None:
            data = {}

        return self._session.request(
            method=method,
            url=self._url + endpoint,
            json=data
        )

    @staticmethod
    def _validate_uuid(uuid_str: Optional[str] = None) -> bool:
        try:
            _ = UUID(uuid_str)
        except ValueError:
            raise ValueError(f"{uuid_str} is not a valid uuid string.")
        return True

    @property
    def spaces(self) -> list[Space]:
        """Get your spaces."""

        return [
            Space(**sp)
            for sp in self._request("GET", "spaces").json()["spaces"]
        ]

    def space_info(self, space_id: Optional[str] = None) -> list[Structure]:
        """Returns all structures (object types) with property definitions and collections of a space."""

        space_id = space_id or self._preferred_space_id
        self._validate_uuid(space_id)

        return [
            Structure(**st)
            for st in self._request(
                "GET",
                "space-info",
                {"spaceid": space_id}
            ).json()["structures"]
        ]

    def search(
        self,
        mode: str,
        search_term: str,
        filter_structure_ids: list[ObjectTypes],
        space_ids: Optional[list[Optional[str]]] = None,
    ) -> Optional[list[SearchResult]]:
        """Returns content based on a search term in a set of spaces."""

        if not space_ids:
            space_ids = [self._preferred_space_id]

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
            ).json()["results"]
        ]
    
    def save_to_daily_note(
        self,
        md_text: str,
        origin: str = Origin.COMMAND_PALETTE,
        space_id: Optional[str] = None,
        no_time_stamp: bool = True,
    ) -> None:
        """
        Saves a text to today's daily note in a space.
        The text can be formatted in markdown.
        Do not use this to import large amounts of content as this could break the daily note.
        Use the import system of Capacities instead.
        """

        space_id = space_id or self._preferred_space_id
        self._validate_uuid(space_id)

        self._request(
            "POST",
            "save-to-daily-note",
            {
                "spaceId": space_id,
                "mdText": md_text,
                "origin": origin,
                "noTimeStamp": no_time_stamp
            }
        )
