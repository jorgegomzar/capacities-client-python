import logging
from dotenv import load_dotenv

from capacities.api_client import CapacitiesAPIClient, ObjectTypes


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # this is to load env variables from a .env file
    load_dotenv()

    client = CapacitiesAPIClient()

    print(client.spaces)
    print(client.space_info())
    print(client.search(
        mode="title",
        search_term="DONE",
        filter_structure_ids=[ObjectTypes.TAG],
    ))
    print(client.save_to_daily_note(
        "[] Test new endpoint",
        no_time_stamp=False
    ))
