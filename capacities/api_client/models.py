from enum import Enum
from pydantic import BaseModel


class Origin(str, Enum):
    """The allowed origins when adding content to daily notes."""

    COMMAND_PALETTE = "commandPalette"


class ObjectTypes(Enum):
    """
    Taken from docs:

    https://docs.capacities.io/developer/api#api-reference:~:text=Basic%20structures%20(structures%20provided%20by%20Capacities)%20have%20the%20following%20structureIds%3A
    """

    def __init__(self, structure_name: str, structure_id: str) -> None:
        super().__init__()
        self.structure_name = structure_name
        self.structure_id = structure_id

    SPACE = ("Space", "RootSpace")
    OBJECT_TYPE = ("Object type", "RootStructure")
    COLLECTION = ("Collection", "RootDatabase")
    QUERY = ("Query", "RootQuery")
    PAGE = ("Page", "RootPage")
    IMAGE = ("Image", "MediaImage")
    PDF = ("PDF", "MediaPDF")
    AUDIO = ("Audio", "MediaAudio")
    VIDEO = ("Video", "MediaVideo")
    WEBLINK = ("Weblink", "MediaWebResource")
    FILE = ("File", "MediaFile")
    TWEET = ("Tweet", "MediaTweet")
    AI_CHAT = ("AI Chat", "RootAIChat")
    TABLE = ("Table", "RootSimpleTable")
    DAILY_NOTE = ("Daily Note", "RootDailyNote")
    TAG = ("Tag", "RootTag")


class SpaceIcon(BaseModel):
    type: str
    val: str


class Space(BaseModel):
    id: str
    title: str
    icon: SpaceIcon


class StructurePropertyDefinitions(BaseModel):
    id: str
    name: str
    type: str
    dataType: str


class Collection(BaseModel):
    id: str
    title: str


class Structure(BaseModel):
    id: str
    title: str
    pluralName: str
    propertyDefinitions: list[StructurePropertyDefinitions]
    labelColor: str
    collections: list[Collection]


class SearchResultHighlight(BaseModel):
    context: dict[str, str]
    snippets: list[str]


class SearchResult(BaseModel):
    id: str
    spaceId: str
    structureId: str
    title: str
    highlights: list[SearchResultHighlight]
