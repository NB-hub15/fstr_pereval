from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import Database

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


# Отдельная модель для PATCH (все поля необязательные, user убран)
class PerevalUpdateData(BaseModel):
    beauty_title: Optional[str] = None
    title: Optional[str] = None
    other_titles: Optional[str] = None
    connect: Optional[str] = None
    level: Optional[LevelData] = None
    coords: Optional[CoordsData] = None


@app.post("/submitData")
async def submit_data(pereval: PerevalData):
    """Добавление нового перевала"""
    db = None
    try:
        db = Database()

        # Добавляем или находим пользователя по email
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

        # Обрабатываем время добавления
        add_time = None
        if pereval.add_time:
            try:
                add_time = datetime.strptime(pereval.add_time, "%Y-%m-%d %H:%M:%S")
            except:
                add_time = datetime.now()
        else:
            add_time = datetime.now()

        # Добавляем перевал со статусом "new"
        pereval_id = db.add_pereval(
            beauty_title=pereval.beauty_title,
            title=pereval.title,
            other_titles=pereval.other_titles,
            connect=pereval.connect,
            user_id=user_id,
            coords_id=coords_id,
            add_time=add_time,
            level_winter=pereval.level.winter if pereval.level else None,
            level_summer=pereval.level.summer if pereval.level else None,
            level_autumn=pereval.level.autumn if pereval.level else None,
            level_spring=pereval.level.spring if pereval.level else None
        )

        # Добавляем фотографии
        for img in pereval.images:
            db.add_image(pereval_id, img.data, img.title)

        db.commit()
        return {"status": 200, "message": None, "id": pereval_id}

    except Exception as e:
        return {"status": 500, "message": str(e), "id": None}
    finally:
        if db:
            db.close()


@app.get("/submitData/")
async def get_perevals_by_user(user_email: str):
    """Получить список всех перевалов пользователя по email"""
    db = Database()

    try:
        # JOIN трёх таблиц для получения всех данных
        query = """
            SELECT 
                p.id, p.status, p.beauty_title, p.title, p.other_titles, p.connect,
                p.add_time, p.level_winter, p.level_summer, p.level_autumn, p.level_spring,
                c.latitude, c.longitude, c.height,
                u.email, u.phone, u.fam, u.name, u.otc
            FROM pereval p
            JOIN coords c ON p.coords_id = c.id
            JOIN users u ON p.user_id = u.id
            WHERE u.email = %s
            ORDER BY p.add_time DESC
        """
        result = db.execute_query(query, (user_email,))

        if not result:
            return {"status": 0, "message": f"Перевалы для {user_email} не найдены", "data": []}

        # Формируем список перевалов
        perevals = []
        for row in result:
            perevals.append({
                "id": row[0],
                "status": row[1],
                "beauty_title": row[2],
                "title": row[3],
                "other_titles": row[4],
                "connect": row[5],
                "add_time": row[6].isoformat() if row[6] else None,
                "level": {
                    "winter": row[7],
                    "summer": row[8],
                    "autumn": row[9],
                    "spring": row[10]
                },
                "coords": {
                    "latitude": row[11],
                    "longitude": row[12],
                    "height": row[13]
                },
                "user": {
                    "email": row[14],
                    "phone": row[15],
                    "fam": row[16],
                    "name": row[17],
                    "otc": row[18]
                }
            })

        return {"status": 1, "message": f"Найдено {len(perevals)} перевалов", "data": perevals}

    except Exception as e:
        return {"status": 500, "message": str(e), "data": []}
    finally:
        db.close()


@app.patch("/submitData/{pereval_id}")
async def update_pereval(pereval_id: int, pereval: PerevalUpdateData):
    """
    Частичное редактирование перевала.
    Только для статуса 'new'. Нельзя редактировать ФИО, email, телефон.
    """
    db = Database()

    try:
        # Проверяем, существует ли перевал и какой у него статус
        result = db.execute_query("SELECT status FROM pereval WHERE id = %s", (pereval_id,))
        if not result:
            return {"state": 0, "message": f"Перевал с id={pereval_id} не найден"}

        # Только new можно редактировать
        if result[0][0] != "new":
            return {"state": 0, "message": f"Редактирование невозможно. Статус: '{result[0][0]}'. Только 'new'"}

        # Собираем только те поля, которые переданы в запросе
        updates = []
        params = []

        if pereval.title is not None:
            updates.append("title = %s")
            params.append(pereval.title)
        if pereval.beauty_title is not None:
            updates.append("beauty_title = %s")
            params.append(pereval.beauty_title)
        if pereval.other_titles is not None:
            updates.append("other_titles = %s")
            params.append(pereval.other_titles)
        if pereval.connect is not None:
            updates.append("connect = %s")
            params.append(pereval.connect)

        # Обновляем уровни сложности
        if pereval.level:
            if pereval.level.winter is not None:
                updates.append("level_winter = %s")
                params.append(pereval.level.winter)
            if pereval.level.summer is not None:
                updates.append("level_summer = %s")
                params.append(pereval.level.summer)
            if pereval.level.autumn is not None:
                updates.append("level_autumn = %s")
                params.append(pereval.level.autumn)
            if pereval.level.spring is not None:
                updates.append("level_spring = %s")
                params.append(pereval.level.spring)

        # Обновляем координаты (отдельная таблица coords)
        if pereval.coords:
            coord_updates = []
            coord_params = []
            if pereval.coords.latitude is not None:
                coord_updates.append("latitude = %s")
                coord_params.append(pereval.coords.latitude)
            if pereval.coords.longitude is not None:
                coord_updates.append("longitude = %s")
                coord_params.append(pereval.coords.longitude)
            if pereval.coords.height is not None:
                coord_updates.append("height = %s")
                coord_params.append(pereval.coords.height)

            if coord_updates:
                coords_result = db.execute_query("SELECT coords_id FROM pereval WHERE id = %s", (pereval_id,))
                if coords_result:
                    coords_id = coords_result[0][0]
                    coord_query = f"UPDATE coords SET {', '.join(coord_updates)} WHERE id = %s"
                    db.cursor.execute(coord_query, coord_params + [coords_id])

        # Если нет полей для обновления
        if not updates:
            return {"state": 0, "message": "Нет полей для обновления"}

        # Выполняем обновление
        query = f"UPDATE pereval SET {', '.join(updates)} WHERE id = %s"
        db.cursor.execute(query, params + [pereval_id])
        db.commit()

        return {"state": 1, "message": "Запись успешно отредактирована"}

    except Exception as e:
        return {"state": 0, "message": str(e)}
    finally:
        db.close()


@app.get("/submitData/{pereval_id}")
async def get_pereval(pereval_id: int):
    """Получение данных перевала по ID вместе со статусом модерации"""
    db = Database()

    try:
        # JOIN трёх таблиц для получения всех данных
        query = """
            SELECT 
                p.id, p.status, p.beauty_title, p.title, p.other_titles, p.connect,
                p.add_time, p.level_winter, p.level_summer, p.level_autumn, p.level_spring,
                c.latitude, c.longitude, c.height,
                u.email, u.phone, u.fam, u.name, u.otc
            FROM pereval p
            JOIN coords c ON p.coords_id = c.id
            JOIN users u ON p.user_id = u.id
            WHERE p.id = %s
        """
        result = db.execute_query(query, (pereval_id,))

        if not result:
            return {"status": 0, "message": f"Перевал с id={pereval_id} не найден"}

        row = result[0]

        # Формируем ответ
        return {
            "id": row[0],
            "status": row[1],
            "beauty_title": row[2],
            "title": row[3],
            "other_titles": row[4],
            "connect": row[5],
            "add_time": row[6].isoformat() if row[6] else None,
            "level": {
                "winter": row[7],
                "summer": row[8],
                "autumn": row[9],
                "spring": row[10]
            },
            "coords": {
                "latitude": row[11],
                "longitude": row[12],
                "height": row[13]
            },
            "user": {
                "email": row[14],
                "phone": row[15],
                "fam": row[16],
                "name": row[17],
                "otc": row[18]
            }
        }

    except Exception as e:
        return {"status": 500, "message": str(e)}
    finally:
        db.close()