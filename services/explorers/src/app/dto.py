from typing import Optional

from pydantic import BaseModel, Field


class AuthRequest(BaseModel):
    username: str
    password: str


class User(BaseModel):
    id: str
    username: str


class CreateRouteRequest(BaseModel):
    title: str
    description: str


class TrackPoint(BaseModel):
    lat: str
    lon: str
    ele: Optional[str]
    time: Optional[str]


class Waypoint(BaseModel):
    lat: str
    lon: str
    ele: Optional[str]
    name: str
    desc: Optional[str]
    comment: Optional[str]
    sym: Optional[str]
    time: Optional[str]


class Route(BaseModel):
    id: str
    title: str
    user_id: str
    description: str
    track_points: list[TrackPoint]
    waypoints: list[Waypoint]
    share_token: Optional[str]


class UpdateRouteRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    track_points: list[TrackPoint]
    waypoints: list[Waypoint]
