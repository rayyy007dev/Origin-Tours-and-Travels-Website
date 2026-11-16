"""FastAPI application for the ORIGIN Tours & Travels website."""

import os
import secrets
from contextlib import asynccontextmanager
from typing import Annotated, Literal

import psycopg
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, field_validator
from psycopg import sql
from psycopg.errors import UniqueViolation

from database import get_db, initialize_database


TourCategory = Literal["domestic", "international", "umrah"]


class ContactForm(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=40)
    subject: str | None = Field(default=None, max_length=160)
    message: str = Field(min_length=5, max_length=5000)

    @field_validator("name", "message")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value


class DestinationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    country: str = Field(min_length=2, max_length=120)
    duration: str = Field(min_length=1, max_length=80)
    price: int = Field(ge=0)
    image: str = Field(default="", max_length=500)
    description: str = Field(min_length=5, max_length=2000)
    link: str = Field(default="", max_length=300)


class DestinationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    country: str | None = Field(default=None, min_length=2, max_length=120)
    duration: str | None = Field(default=None, min_length=1, max_length=80)
    price: int | None = Field(default=None, ge=0)
    image: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, min_length=5, max_length=2000)
    link: str | None = Field(default=None, max_length=300)


class TourCreate(BaseModel):
    slug: str = Field(min_length=2, max_length=120, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    category: TourCategory
    name: str = Field(min_length=2, max_length=120)
    region: str = Field(default="", max_length=120)
    duration: str = Field(default="", max_length=80)
    price: int | None = Field(default=None, ge=0)
    image: str = Field(default="", max_length=500)
    description: str = Field(min_length=5, max_length=2000)
    features: list[str] = Field(default_factory=list)
    cta_label: str = Field(default="Explore Package", max_length=80)
    is_featured: bool = False
    sort_order: int = Field(default=0, ge=0)


class TourUpdate(BaseModel):
    slug: str | None = Field(default=None, min_length=2, max_length=120, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    category: TourCategory | None = None
    name: str | None = Field(default=None, min_length=2, max_length=120)
    region: str | None = Field(default=None, max_length=120)
    duration: str | None = Field(default=None, max_length=80)
    price: int | None = Field(default=None, ge=0)
    image: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, min_length=5, max_length=2000)
    features: list[str] | None = None
    cta_label: str | None = Field(default=None, max_length=80)
    is_featured: bool | None = None
    sort_order: int | None = Field(default=None, ge=0)



def require_admin_key(
    x_admin_key: Annotated[str | None, Header()] = None,
) -> None:
    """Protect private enquiry data and all write endpoints."""
    expected_key = os.getenv("ADMIN_API_KEY")
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin API is disabled. Set ADMIN_API_KEY in the .env file.",
        )

    if not x_admin_key or not secrets.compare_digest(x_admin_key.encode("utf-8"), expected_key.encode("utf-8")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid X-Admin-Key header is required.",
        )


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Database work happens at startup, not when main.py is imported.
    initialize_database()
    yield


app = FastAPI(
    title="ORIGIN Tours & Travels API",
    description="API for tour packages, destinations, and contact enquiries.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-Admin-Key"],
)


@app.get("/", tags=["Health"])
def home():
    return {"message": "ORIGIN backend is running"}


@app.get("/api", tags=["Health"])
def api_home():
    return {"message": "ORIGIN API is running"}


@app.get("/api/health", tags=["Health"])
def database_health(connection: Annotated[psycopg.Connection, Depends(get_db)]):
    connection.execute("SELECT 1")
    return {"status": "ok", "database": "connected"}


# -----------------------------------------------------------------------------
# Public contact form; private enquiry management requires the admin key.
# -----------------------------------------------------------------------------

@app.post("/api/contact", status_code=status.HTTP_201_CREATED, tags=["Contact"])
def submit_contact_message(
    data: ContactForm,
    connection: Annotated[psycopg.Connection, Depends(get_db)],
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO contact_messages (name, email, phone, subject, message)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, name, email, phone, subject, message, created_at
            """,
            (data.name, str(data.email), data.phone, data.subject, data.message),
        )
        saved_message = cursor.fetchone()

    connection.commit()
    return {
        "message": "Your message has been received",
        "contact": saved_message,
    }


@app.get("/api/contact", tags=["Contact"], dependencies=[Depends(require_admin_key)])
def get_contact_messages(
    connection: Annotated[psycopg.Connection, Depends(get_db)],
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name, email, phone, subject, message, is_read, created_at
            FROM contact_messages
            ORDER BY created_at DESC, id DESC
            """
        )
        messages = cursor.fetchall()
    return {"contacts": messages}


@app.delete(
    "/api/contact/{contact_id}",
    tags=["Contact"],
    dependencies=[Depends(require_admin_key)],
)
def delete_contact_message(
    contact_id: int,
    connection: Annotated[psycopg.Connection, Depends(get_db)],
):
    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM contact_messages WHERE id = %s RETURNING id",
            (contact_id,),
        )
        deleted_message = cursor.fetchone()

    if deleted_message is None:
        raise HTTPException(status_code=404, detail="Contact message not found")

    connection.commit()
    return {"message": "Contact message deleted", "id": deleted_message["id"]}


# -----------------------------------------------------------------------------
# Public tour listing + protected tour management.
# -----------------------------------------------------------------------------

@app.get("/api/tours", tags=["Tours"])
def get_tours(
    connection: Annotated[psycopg.Connection, Depends(get_db)],
    category: TourCategory | None = None,
):
    with connection.cursor() as cursor:
        if category is None:
            cursor.execute(
                """
                SELECT id, slug, category, name, region, duration, price,
                       image, description, features, cta_label, is_featured,
                       sort_order
                FROM tours
                ORDER BY category, sort_order, id
                """
            )
        else:
            cursor.execute(
                """
                SELECT id, slug, category, name, region, duration, price,
                       image, description, features, cta_label, is_featured,
                       sort_order
                FROM tours
                WHERE category = %s
                ORDER BY sort_order, id
                """,
                (category,),
            )
        tours = cursor.fetchall()
    return {"tours": tours}


@app.post(
    "/api/tours",
    status_code=status.HTTP_201_CREATED,
    tags=["Tours"],
    dependencies=[Depends(require_admin_key)],
)
def create_tour(
    tour: TourCreate,
    connection: Annotated[psycopg.Connection, Depends(get_db)],
):
    values = tour.model_dump()
    columns = list(values)
    column_sql = sql.SQL(", ").join(sql.Identifier(column) for column in columns)
    placeholders = sql.SQL(", ").join(sql.SQL("%s") for _ in columns)

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("INSERT INTO tours ({}) VALUES ({}) RETURNING *").format(
                    column_sql, placeholders
                ),
                tuple(values[column] for column in columns),
            )
            created_tour = cursor.fetchone()
        connection.commit()
    except UniqueViolation:
        connection.rollback()
        raise HTTPException(status_code=409, detail="A tour with this slug already exists")

    return {"message": "Tour created", "tour": created_tour}


@app.put(
    "/api/tours/{tour_id}",
    tags=["Tours"],
    dependencies=[Depends(require_admin_key)],
)
def update_tour(
    tour_id: int,
    updates: TourUpdate,
    connection: Annotated[psycopg.Connection, Depends(get_db)],
):
    update_values = updates.model_dump(exclude_unset=True, exclude_none=True)
    if not update_values:
        raise HTTPException(status_code=400, detail="No updates were provided")

    assignments = sql.SQL(", ").join(
        sql.SQL("{} = %s").format(sql.Identifier(column))
        for column in update_values
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("UPDATE tours SET {}, updated_at = NOW() WHERE id = %s RETURNING *").format(assignments),
                (*update_values.values(), tour_id),
            )
            updated_tour = cursor.fetchone()
        if updated_tour is None:
            raise HTTPException(status_code=404, detail="Tour not found")
        connection.commit()
    except UniqueViolation:
        connection.rollback()
        raise HTTPException(status_code=409, detail="A tour with this slug already exists")

    return {"message": "Tour updated", "tour": updated_tour}


@app.delete(
    "/api/tours/{tour_id}",
    tags=["Tours"],
    dependencies=[Depends(require_admin_key)],
)
def delete_tour(
    tour_id: int,
    connection: Annotated[psycopg.Connection, Depends(get_db)],
):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM tours WHERE id = %s RETURNING id, name", (tour_id,))
        deleted_tour = cursor.fetchone()
    if deleted_tour is None:
        raise HTTPException(status_code=404, detail="Tour not found")
    connection.commit()
    return {"message": "Tour deleted", "tour": deleted_tour}


# -----------------------------------------------------------------------------
# Public destination listing + protected destination management.
# -----------------------------------------------------------------------------

@app.get("/api/destinations", tags=["Destinations"])
def get_destinations(
    connection: Annotated[psycopg.Connection, Depends(get_db)],
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name, country, duration, price, image, description, link
            FROM destinations
            ORDER BY id
            """
        )
        destinations = cursor.fetchall()
    return {"destinations": destinations}


@app.post(
    "/api/destinations",
    status_code=status.HTTP_201_CREATED,
    tags=["Destinations"],
    dependencies=[Depends(require_admin_key)],
)
def create_destination(
    destination: DestinationCreate,
    connection: Annotated[psycopg.Connection, Depends(get_db)],
):
    values = destination.model_dump()
    columns = list(values)
    column_sql = sql.SQL(", ").join(sql.Identifier(column) for column in columns)
    placeholders = sql.SQL(", ").join(sql.SQL("%s") for _ in columns)

    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL("INSERT INTO destinations ({}) VALUES ({}) RETURNING *").format(
                column_sql, placeholders
            ),
            tuple(values[column] for column in columns),
        )
        created_destination = cursor.fetchone()
    connection.commit()
    return {"message": "Destination created", "destination": created_destination}


@app.put(
    "/api/destinations/{destination_id}",
    tags=["Destinations"],
    dependencies=[Depends(require_admin_key)],
)
def update_destination(
    destination_id: int,
    updates: DestinationUpdate,
    connection: Annotated[psycopg.Connection, Depends(get_db)],
):
    update_values = updates.model_dump(exclude_unset=True, exclude_none=True)
    if not update_values:
        raise HTTPException(status_code=400, detail="No valid updates were provided")

    assignments = sql.SQL(", ").join(
        sql.SQL("{} = %s").format(sql.Identifier(column))
        for column in update_values
    )

    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL(
                "UPDATE destinations SET {}, updated_at = NOW() "
                "WHERE id = %s RETURNING *"
            ).format(assignments),
            (*update_values.values(), destination_id),
        )
        updated_destination = cursor.fetchone()

    if updated_destination is None:
        raise HTTPException(status_code=404, detail="Destination not found")

    connection.commit()
    return {"message": "Destination updated", "destination": updated_destination}


@app.delete(
    "/api/destinations/{destination_id}",
    tags=["Destinations"],
    dependencies=[Depends(require_admin_key)],
)
def delete_destination(
    destination_id: int,
    connection: Annotated[psycopg.Connection, Depends(get_db)],
):
    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM destinations WHERE id = %s RETURNING id, name",
            (destination_id,),
        )
        deleted_destination = cursor.fetchone()

    if deleted_destination is None:
        raise HTTPException(status_code=404, detail="Destination not found")

    connection.commit()
    return {"message": "Destination deleted", "destination": deleted_destination}


@app.get("/api/services", tags=["Services"])
def get_services():
    return {
        "services": [
            "Flight booking",
            "Hotel reservations",
            "Airport transfers",
            "Tour planning",
        ]
    }
