from functools import lru_cache

import fastapi
import gpxpy
from fastapi import APIRouter

from app import auth, config, models, dto, serializers

api = APIRouter()


@lru_cache()
def jwt_helper() -> auth.JWTHelper:
    return auth.JWTHelper(config.get_settings().jwt_key)


async def get_current_user(request: fastapi.Request) -> str:
    jwt_help = jwt_helper()
    try:
        api_token = request.cookies.get('Api-Token') or request.headers.get('X-Api-Token')
        if api_token is None:
            raise ValueError("Empty Api-Token/cookie")
        user_data = jwt_help.decode_token(api_token.encode())
    except Exception as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail=json_error("Could not validate credentials"),
        )

    if not user_data:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail=json_error("Could not validate credentials"),
        )

    user_id = user_data.get('user_id')
    return user_id


def gen_route_token(route_id: str) -> str:
    return jwt_helper().gen_token({'route_id': route_id})


def json_error(error):
    return {'error': error}


def serialize_route(route):
    route_dto = serializers.RouteSerializer.serialize(route)
    route_dto.share_token = gen_route_token(f'{route.id}')
    return route_dto


async def get_route_by_id(route_id) -> models.Route:
    route = await models.Route.get(route_id)
    if not route:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=json_error('Route not found')
        )
    return route


@api.post('/signup')
async def signup_handler(response: fastapi.Response, auth_req: dto.AuthRequest):
    existing = await models.User.find(models.User.username == auth_req.username).first_or_none()
    if existing:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_412_PRECONDITION_FAILED,
            detail=json_error('user already exists')
        )

    user = models.User(username=auth_req.username, password=auth_req.password)
    await user.insert()

    token = jwt_helper().gen_token({'user_id': f'{user.id}'})
    response.set_cookie("Api-Token", token)
    return {'user_id': f'{user.id}', 'api_token': token}


@api.post('/signin')
async def signin_handler(response: fastapi.Response, auth_req: dto.AuthRequest):
    user = await models.User.find(
        models.User.username == auth_req.username and models.User.password == auth_req.password).first_or_none()
    if not user:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=json_error('user not found or invalid password')
        )

    token = jwt_helper().gen_token({'user_id': f'{user.id}'})
    response.set_cookie("Api-Token", token)
    return {'user_id': f'{user.id}', 'api_token': token}


@api.get('/user')
async def get_user(user_id: str = fastapi.Depends(get_current_user)):
    user = await models.User.get(user_id)
    if not user:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=json_error('user not found')
        )
    return serializers.UserSerializer.serialize(user)


@api.post('/logout')
def logout_handler(response: fastapi.Response):
    response.delete_cookie("Api-Token")
    return {'status': 'ok'}


@api.post('/route/create')
async def route_create_handler(create_req: dto.CreateRouteRequest, user_id: str = fastapi.Depends(get_current_user)):
    route = models.Route(title=create_req.title,
                         description=create_req.description, user_id=user_id,
                         track_points=[], waypoints=[])
    await route.insert()

    return serialize_route(route)


@api.get('/route')
async def route_list(user_id: str = fastapi.Depends(get_current_user)):
    routes = await models.Route.find(models.Route.user_id == user_id).to_list()
    return [serialize_route(route) for route in routes]


@api.get('/route/{route_id}')
async def route_get(route_id: str, user_id: str = fastapi.Depends(get_current_user), token: str | None = None):
    route = await get_route_by_id(route_id)

    if token and jwt_helper().decode_token(token.encode()).get('route_id') == route_id:
        return serialize_route(route)

    if route.user_id != user_id:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail=json_error('You are not allowed to view this route')
        )

    return serialize_route(route)


@api.post('/route/{route_id}/update')
async def update_route(route_id: str, update_req: dto.UpdateRouteRequest,
                       user_id: str = fastapi.Depends(get_current_user)):
    route = await get_route_by_id(route_id)
    if route.user_id != user_id:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail=json_error('You are not allowed to modify this route')
        )

    if update_req.title:
        route.title = update_req.title
    if update_req.description:
        route.description = update_req.description
    if update_req.waypoints:
        route.waypoints = [serializers.WaypointSerializer.to_model(waypoint) for waypoint in update_req.waypoints]
    if update_req.track_points:
        route.track_points = [serializers.TrackPointSerializer.to_model(track_point) for track_point in
                              update_req.track_points]

    await route.save()

    return serialize_route(route)


@api.post('/route/{route_id}/upload')
async def route_upload(route_id: str,
                       file: fastapi.UploadFile,
                       user_id: str = fastapi.Depends(get_current_user)):
    route = await get_route_by_id(route_id)
    if route.user_id != user_id:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail=json_error('You are not allowed to modify this route')
        )

    try:
        gpx = gpxpy.parse(file.file)
        waypoints = [
            models.Waypoint(
                lat=f'{waypoint.latitude}',
                lon=f'{waypoint.longitude}',
                ele=f'{waypoint.elevation}' if waypoint.elevation else None,
                name=waypoint.name,
                desc=waypoint.description,
                comment=waypoint.comment,
                sym=waypoint.symbol,
                time=waypoint.time.isoformat() if waypoint.time else None,
            )
            for waypoint in gpx.waypoints
        ]
        track_points = [
            models.TrackPoint(
                lat=f'{point.latitude}',
                lon=f'{point.longitude}',
                ele=f'{point.elevation}' if point.elevation else None,
                time=f'{point.time}',
            )
            for track in gpx.tracks
            for segment in track.segments
            for point in segment.points
        ]
        route.waypoints = waypoints
        route.track_points = track_points
        await route.save()
    except Exception as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=json_error(f'Could not parse GPX file')
        )

    return serialize_route(route)
