import datetime
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Episode:
    name: str
    season: int
    number: int
    airstamp: Optional[datetime.datetime] = None


@dataclass
class ExternalSiteInfo:
    name: str
    value: str
    last_update: Optional[int] = None


@dataclass
class Series:
    id: int
    name: str
    season_count: int
    premiered: Optional[datetime.date] = None
    ended: Optional[datetime.date] = None
    episodes: list[Episode] = field(default_factory=list)
    external_sites: list[ExternalSiteInfo] = field(default_factory=list)
