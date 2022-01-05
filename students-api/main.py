from typing import Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, status
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import and_
from db import engine
from db import students as students_table
from models import PatchStudent, PostStudent, PutStudent, StudentModel
from session import JSONResponse

app = FastAPI()


@app.get('/students')
def get_students(
        department: Optional[str] = None,
        gender: Optional[str] = None) -> JSONResponse:
    with engine.connect() as conn:
        students = conn.execute(select(students_table)).fetchall()
        if gender and department:
            students = conn.execute(select(students_table).where(and_(
                students_table.c.gender == gender,
                students_table.c.department == department))).fetchall()
        if gender and not department:
            students = conn.execute(select(students_table).where(
                students_table.c.gender == gender)) .fetchall()
        if department and not gender:
            students = conn.execute(select(students_table).where(
                students_table.c.department == department)).fetchall()
    if not students:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no students'
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=(StudentModel(**student._asdict()) for student in students)
    )


@app.get('/students/{student_id}')
def get_students_by_id(student_id: UUID) -> JSONResponse:
    with engine.connect() as conn:
        student = conn.execute(students_table.select().where(
            students_table.c.id == student_id)).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Student with id: {student_id} dose not exist'
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={'data': StudentModel(**student._asdict())}
    )


@app.post('/students')
def add_student(student: PostStudent) -> JSONResponse:
    try:
        with engine.begin() as conn:
            new_student = conn.execute(students_table.insert().values(
                **student.dict()).returning(students_table))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Bad data')
    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content=StudentModel(**new_student.fetchone()))


@app.delete("/students/{student_id}")
def delete_student(student_id: UUID) -> JSONResponse:
    try:
        with engine.begin() as conn:
            conn.execute(students_table.delete().where(
                students_table.c.id == student_id
            ))
    except Exception:
        raise HTTPException(
            status_code=404,
            detail=f'Student with id: ({student_id}) dose not exist'
        )
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED,
                        content=f'Student with id: {student_id} deleted')


@app.put("/students/{student_id}")
def update_student_info(student_id: UUID, student: PutStudent) -> JSONResponse:
    try:
        with engine.begin() as conn:
            updated_student = conn.execute(students_table.update()
                                           .where(students_table.c.id
                                                  == student_id)
                                           .values(
                **student.dict()).returning(students_table))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Bad data')
    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content=StudentModel(**updated_student.fetchone()))


@app.patch("/students/{student_id}")
def update_student_sepcifec_info(student_id: UUID,
                                 student: PatchStudent) -> JSONResponse:
    try:
        with engine.begin() as conn:
            updated_student = conn.execute(students_table.update()
                                           .where(students_table.c.id
                                                  == student_id)
                                           .values(
                **student.dict(exclude_none=True)).returning(students_table))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Bad data')
    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content=StudentModel(**updated_student.fetchone()))
