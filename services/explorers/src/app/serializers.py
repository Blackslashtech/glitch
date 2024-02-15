from app import models
from app import dto


class UserSerializer:
    @staticmethod
    def serialize(user: models.User) -> dto.User:
        return dto.User(
            id=f'{user.id}',
            username=user.username,
        )


class WaypointSerializer:
    @staticmethod
    def to_model(waypoint: dto.Waypoint) -> models.Waypoint:
        return models.Waypoint(
            lat=waypoint.lat,
            sym=waypoint.sym,
            lon=waypoint.lon,
            ele=waypoint.ele,
            name=waypoint.name,
            desc=waypoint.desc,
            comment=waypoint.comment,
            time=waypoint.time,
        )

    @staticmethod
    def serialize(waypoint: models.Waypoint) -> dto.Waypoint:
        return dto.Waypoint(
            lat=waypoint.lat,
            sym=waypoint.sym,
            lon=waypoint.lon,
            ele=waypoint.ele,
            name=waypoint.name,
            desc=waypoint.desc,
            comment=waypoint.comment,
            time=waypoint.time,
        )


class TrackPointSerializer:
    @staticmethod
    def to_model(track_point: dto.TrackPoint) -> models.TrackPoint:
        return models.TrackPoint(
            lat=track_point.lat,
            lon=track_point.lon,
            ele=track_point.ele,
            time=track_point.time,
        )

    @staticmethod
    def serialize(track_point: models.TrackPoint) -> dto.TrackPoint:
        return dto.TrackPoint(
            lat=track_point.lat,
            lon=track_point.lon,
            ele=track_point.ele,
            time=track_point.time,
        )


class RouteSerializer:

    @staticmethod
    def serialize(route: models.Route):
        return dto.Route(
            id=f'{route.id}',
            title=route.title,
            user_id=route.user_id,
            description=route.description,
            track_points=[TrackPointSerializer.serialize(track_point) for track_point in route.track_points],
            waypoints=[WaypointSerializer.serialize(waypoint) for waypoint in route.waypoints],
            share_token=None,
        )
