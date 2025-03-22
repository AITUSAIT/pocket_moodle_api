from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, PlainSerializer, PlainValidator, errors
from typing_extensions import Annotated


class UserJSONEncoder:
    # pylint: disable=no-member
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)  # type: ignore

    # pylint: enable=no-member


def hex_bytes_validator(val: Any) -> bytes:
    if isinstance(val, bytes):
        return val
    if isinstance(val, bytearray):
        return bytes(val)
    if isinstance(val, str):
        return bytes.fromhex(val)
    raise errors.BytesError()


HexBytes = Annotated[bytes, PlainValidator(hex_bytes_validator), PlainSerializer(lambda v: v.hex())]


class PydanticBaseModel(BaseModel):
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

    def to_json(self) -> str:
        return self.model_dump_json()

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class User(PydanticBaseModel):
    user_id: int
    api_token: Optional[str]
    register_date: datetime
    mail: Optional[str]
    last_active: Optional[datetime]
    is_admin: bool
    is_manager: bool
    moodle_id: Optional[int]

    def is_newbie(self) -> bool:
        return datetime.now() - self.register_date < timedelta(days=14)

    def is_active_user(self) -> bool:
        return self.last_active is not None and self.last_active > datetime.now() - timedelta(weeks=2)

    def has_api_token(self) -> bool:
        return self.api_token is not None


class MailingModel(PydanticBaseModel):
    id: int
    content: str
    media_type: Optional[str] = None
    media_id: Optional[str] = None


class MailingMessage(PydanticBaseModel):
    id: int
    mailing_id: int
    chat_id: int
    message_id: Optional[int] = None
    sent_date: Optional[datetime] = None
    edit_date: Optional[datetime] = None


class Group(PydanticBaseModel):
    id: int
    tg_id: int
    name: str
    users: List[int]

    class Config:
        frozen = True  # This makes the class hashable


class Grade(PydanticBaseModel):
    grade_id: int
    name: str
    percentage: str

    class Config:
        frozen = True


class Deadline(PydanticBaseModel):
    id: int
    assign_id: int
    name: str
    due: datetime
    graded: bool
    submitted: bool
    status: dict[str, int]

    class Config:
        frozen = True


class Course(PydanticBaseModel):
    course_id: int
    name: str
    teacher_name: str | None
    active: bool


class GroupedCourse(PydanticBaseModel):
    course_id: int
    name: str
    active: bool
    grades: Dict[str, Grade]
    deadlines: Dict[str, Dict[str, Deadline]]


class NotificationStatus(PydanticBaseModel):
    status: bool
    is_newbie_requested: bool
    is_update_requested: bool
    is_end_date: bool
    error_check_token: bool


class SettingBot(PydanticBaseModel):
    status: bool
    notification_grade: bool
    notification_deadline: bool


class SettingApp(PydanticBaseModel):
    status: bool
    notification_grade: bool
    notification_deadline: bool


class Server(PydanticBaseModel):
    token: str
    name: str


class CourseContent(PydanticBaseModel):
    id: int
    name: str
    section: int
    modules: Dict[str, "CourseContentModule"]


class CourseContentModule(PydanticBaseModel):
    id: int
    url: Optional[str]
    name: str
    modplural: str
    modname: str


class CourseContentModuleFile(PydanticBaseModel):
    id: int
    filename: str
    filesize: int
    fileurl: str
    timecreated: int
    timemodified: int
    mimetype: str


class CourseContentModuleUrl(PydanticBaseModel):
    id: int
    name: str
    url: str
