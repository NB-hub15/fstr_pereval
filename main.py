from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from database import Database
from datetime import datetime

app = FastAPI(title="ФСТР - Перевалы API")


# Модели данных для валидации JSON
class UserData(BaseModel):
    email: str
    fam: str
    name: str
    otc: Optional[str] = ""
    phone: str


class CoordsData(BaseModel):
    latitude: str
    longitude: str
    height: str


class LevelData(BaseModel):
    winter: Optional[str] = ""
    summer: Optional[str] = ""
    autumn: Optional[str] = ""
    spring: Optional[str] = ""


class ImageData(BaseModel):
    data: str
    title: str


class PerevalData(BaseModel):
    beauty_title: Optional[str] = ""
    title: str
    other_titles: Optional[str] = ""
    connect: Optional[str] = ""
    add_time: Optional[str] = None
    user: UserData
    coords: CoordsData
    level: Optional[LevelData] = None
    images: List[ImageData] = []


@app.post("/submitData")
async def submit_data(pereval: PerevalData):
    db = None
    try:
        db = Database()

        # Добавляем пользователя
        user_id = db.add_user(
            email=pereval.user.email,
            fam=pereval.user.fam,
            name=pereval.user.name,
            otc=pereval.user.otc,
            phone=pereval.user.phone
        )

        # Добавляем координаты
        coords_id = db.add_coords(
            latitude=pereval.coords.latitude,
            longitude=pereval.coords.longitude,
            height=pereval.coords.height
        )

        # Добавляем перевал
        add_time = None
        if pereval.add_time:
            try:
                add_time = datetime.strptime(pereval.add_time, "%Y-%m-%d %H:%M:%S")
            except:
                add_time = datetime.now()

        pereval_id = db.add_pereval(
            beauty_title=pereval.beauty_title,
            title=pereval.title,
            other_titles=pereval.other_titles,
            connect=pereval.connect,
            user_id=user_id,
            coords_id=coords_id,
            add_time=add_time
        )

        # Добавляем фотографии
        for img in pereval.images:
            db.add_image(pereval_id, img.data, img.title)

        db.commit()

        return {
            "status": 200,
            "message": None,
            "id": pereval_id
        }

    except Exception as e:
        return {
            "status": 500,
            "message": str(e),
            "id": None
        }
    finally:
        if db:
            db.close()