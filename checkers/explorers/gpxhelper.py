import csv
import datetime
import os.path
import random
from collections import namedtuple
from dataclasses import dataclass

import gpxpy


@dataclass
class WaypointParams:
    name: str
    description: str
    sym: str = 'Flag, Blue'


Point = namedtuple("Point", "lat lon ele time")


class TrackHelper:
    def __init__(self):
        self.gpx_raw_files = []
        with open(os.path.join(os.path.dirname(__file__), 'gpx_ds_small.csv')) as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                self.gpx_raw_files.append(row[0])

    def random_point(self) -> Point:
        lat = random.randint(575700, 660800) / 10000
        lon = random.randint(278400, 1325900) / 10000
        return Point(lat, lon, random.randint(500, 800),
                     datetime.datetime.now() - datetime.timedelta(days=random.randint(-1000, 1000)))

    def random_gpx(self, creator: str, num_points=10, waypoints: list[WaypointParams] = None):
        start = self.random_point()
        out_points = [gpxpy.gpx.GPXTrackPoint(latitude=start.lat, longitude=start.lon, elevation=start.ele,
                                              time=start.time)]
        for i in range(num_points):
            prev_point = out_points[-1]
            latitude, longitude = prev_point.latitude + random.randint(-1,
                                                                       1) / 1000, prev_point.longitude + random.randint(
                -1, 1) / 1000
            elev = prev_point.elevation + random.randint(-10, 10) / 10
            time = prev_point.time + datetime.timedelta(seconds=random.randint(5, 30))
            out_points.append(
                gpxpy.gpx.GPXTrackPoint(latitude=latitude, longitude=longitude, elevation=elev, time=time))
        wp_out = []
        for wp in waypoints or []:
            point = random.choice(out_points)
            wp_out.append(gpxpy.gpx.GPXWaypoint(
                latitude=point.latitude,
                longitude=point.longitude,
                elevation=point.elevation,
                name=wp.name,
                description=wp.description,
                symbol=wp.sym,
                time=point.time
            ))

        return self._generate_gpx(creator, out_points, wp_out)

    def random_gpx_from_ds(self, creator: str, waypoints: list[WaypointParams] = None):
        gpx_file = random.choice(self.gpx_raw_files)
        parsed = gpxpy.parse(gpx_file)
        points = [point
                  for track in parsed.tracks
                  for segment in track.segments
                  for point in segment.points
                  ]
        while len(points) < 1:
            gpx_file = random.choice(self.gpx_raw_files)
            parsed = gpxpy.parse(gpx_file)
            points = [point
                      for track in parsed.tracks
                      for segment in track.segments
                      for point in segment.points
                      ]
        wp_out = []
        for wp in waypoints or []:
            point = random.choice(points)
            wp_out.append(gpxpy.gpx.GPXWaypoint(
                latitude=point.latitude + 0.0001,
                longitude=point.longitude + 0.0001,
                elevation=point.elevation,
                name=wp.name,
                description=wp.description,
                symbol=wp.sym,
                time=point.time
            ))
        return self._generate_gpx(creator, points, wp_out)

    def _generate_gpx(self, creator: str, points: list[gpxpy.gpx.GPXTrackPoint],
                      waypoints: list[gpxpy.gpx.GPXWaypoint]):
        gpx = gpxpy.gpx.GPX()
        gpx.creator = creator

        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

        gpx_segment.points = points
        gpx.waypoints = waypoints

        return gpx.to_xml(prettyprint=True)
