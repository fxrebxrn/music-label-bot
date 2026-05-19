from enum import Enum

class UserRole(str, Enum):
    ARTIST = "artist"
    MODERATOR = "moderator"
    ADMIN = "admin"

class ApplicationType(str, Enum):
    RELEASE = "release"
    ACCOUNT_LINK = "account_link"

class ApplicationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ReleaseStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class DistributionType(str, Enum):
    PAID = "paid"
    FREE = "free"

class ArtistType(str, Enum):
    SINGER = "singer"
    PRODUCER = "producer"

class ReleaseFormat(str, Enum):
    ALBUM = "album"
    SINGLE = "single"
    EP = "ep"
