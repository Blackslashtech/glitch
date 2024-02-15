import pydantic
from beanie import Document
from typing import Optional


class User(Document):
    username: str
    password: str

    class Settings:
        name = "users"


class TrackPoint(pydantic.BaseModel):
    lat: str
    lon: str
    ele: Optional[str]
    time: Optional[str]


class Waypoint(pydantic.BaseModel):
    lat: str
    lon: str
    ele: Optional[str]
    name: str
    desc: Optional[str]
    comment: Optional[str]
    sym: Optional[str]
    time: Optional[str]


class Route(Document):
    title: str
    user_id: str
    description: str
    track_points: list[TrackPoint]
    waypoints: list[Waypoint]

    class Settings:
        name = "routes"
