from app.config import load_dotenv
from fastapi import FastAPI, HTTPException, Response,Depends
from app.database import get_connection, init_db
from app.schemas import StudentCreate, StudentUpdate
from app.auth import router as auth_router, get_current_user, require_admin
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse

from fastapi import FastAPI





app = FastAPI(
    title="Student API",
    description=(
        "A REST API for managing student records, "
        "with JWT authentication and role-based authorization."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://client-server-course.onrender.com",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


@app.exception_handler(Exception)
async def unexpected_error_handler(
    request: Request,
    exc: Exception,
):
    logger.error(
        "Unhandled error on %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "ok"}


@app.get("/")
def home():
    return {"message": "Welcome to the Student Management API!"}

@app.get("/students",
         summary="List all students",
         description="Returns all student records. Login is required.",
         response_description="A list of students",)
def get_students(user:dict= Depends(get_current_user)):
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM students").fetchall()
        return [dict(r) for r in row]
    finally:
        conn.close()

@app.get("/students/{student_id}")
def get_student(student_id:int,user:dict= Depends(get_current_user)):
    conn = get_connection()
    try:
        row = conn.execute("""
        SELECT * FROM students WHERE id = ?""", (student_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Student not found")
        return dict(row)
    finally:
        conn.close()


@app.post("/students",status_code=201,
          summary="Create a student",
          description="Create a new student record.",)
def create_student(student: StudentCreate,user:dict= Depends(get_current_user)):
    conn = get_connection()
    try:
        cursor = conn.execute("""
        INSERT INTO students (name, email) VALUES (?, ?)""",
          (student.name.strip(), student.email.strip()),
        )
        conn.commit()
        row = conn.execute(
            """
            SELECT id, name, email
            FROM students
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

        return dict(row)

    except Exception as exc:
        conn.rollback()

        import sqlite3

        if isinstance(exc, sqlite3.IntegrityError):
            raise HTTPException(
                status_code=409,
                detail="Email already exists or data violates a database rule",
            ) from exc

        raise
    finally:
        conn.close()

@app.put("/students/{student_id}")
def update_student(student_id: int, student: StudentCreate,user:dict= Depends(get_current_user)):
    conn = get_connection()

    try:
        cursor = conn.execute(
            """
            UPDATE students
            SET name = ?, email = ?
            WHERE id = ?
            """,
            (student.name.strip(), student.email.strip(), student_id),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Student not found",
            )

        conn.commit()

        row = conn.execute(
            """
            SELECT id, name, email
            FROM students
            WHERE id = ?
            """,
            (student_id,),
        ).fetchone()

        return dict(row)

    except Exception as exc:
        conn.rollback()

        import sqlite3

        if isinstance(exc, sqlite3.IntegrityError):
            raise HTTPException(
                status_code=409,
                detail="Email already exists or data violates a database rule",
            ) from exc

        raise
    finally:
        conn.close()



@app.patch("/students/{student_id}")
def patch_student(student_id: int, student: StudentUpdate,user:dict= Depends(get_current_user)):
    changes = student.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field to update",
        )

    if any(value is None for value in changes.values()):
        raise HTTPException(
            status_code=400,
            detail="Fields cannot be null",
        )

    if "name" in changes:
        changes["name"] = changes["name"].strip()

        if len(changes["name"]) < 2:
            raise HTTPException(
                status_code=400,
                detail="Name must contain at least 2 non-space characters",
            )

    if "email" in changes:
        changes["email"] = changes["email"].strip()

    conn = get_connection()

    try:
        existing = conn.execute(
            "SELECT id FROM students WHERE id = ?",
            (student_id,),
        ).fetchone()

        if existing is None:
            raise HTTPException(
                status_code=404,
                detail="Student not found",
            )

        # The field names come only from the fixed Pydantic schema.
        assignments = ", ".join(
            f"{field} = ?" for field in changes
        )
        values = list(changes.values()) + [student_id]

        conn.execute(
            f"UPDATE students SET {assignments} WHERE id = ?",
            values,
        )

        conn.commit()

        row = conn.execute(
            """
            SELECT id, name, email
            FROM students
            WHERE id = ?
            """,
            (student_id,),
        ).fetchone()

        return dict(row)

    except Exception as exc:
        conn.rollback()

        import sqlite3

        if isinstance(exc, sqlite3.IntegrityError):
            raise HTTPException(
                status_code=409,
                detail="Email already exists or data violates a database rule",
            ) from exc

        raise
    finally:
        conn.close()



@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int,user:dict= Depends(require_admin),):
    conn = get_connection()

    try:
        cursor = conn.execute(
            "DELETE FROM students WHERE id = ?",
            (student_id,),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Student not found",
            )

        conn.commit()
        return Response(status_code=204)
    finally:
        conn.close()
