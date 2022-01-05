from typing import Optional
from uuid import UUID

from db import engine
from db import students
from fastapi import FastAPI, HTTPException, status
from models import PatchStudent, PostStudent, PutStudent, StudentModel
from session import JSONResponse

app = FastAPI()


@app.get('/students', response_model=StudentModel)
def get_students(
        department: Optional[str] = None,
        gender: Optional[str] = None) -> JSONResponse:
    sel = None
    if gender and department:
        sel = students.select().where(students.c.gender == gender)\
            .where(students.c.department == department)
    elif gender and not department:
        sel = students.select().where(students.c.gender == gender)
    elif department and not gender:
        sel = students.select().where(students.c.department == department)
    else:
        sel = students.select()

    with engine.connect() as conn:
        students_data = conn.execute(sel).fetchall()

    if not students_data:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={'data': []}

        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={'data': (StudentModel(**student._asdict())
                 for student in students_data)}
    )


@app.get('/students/{student_id}', response_model=StudentModel)
def get_students_by_id(student_id: UUID) -> JSONResponse:
    with engine.connect() as conn:
        student_data = conn.execute(students.select().where(
            students.c.id == student_id)).first()

    if not student_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Student with id: {student_id} dose not exist'
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={'data': StudentModel(**student_data._asdict())}
    )


@app.post('/students', response_model=StudentModel)
def add_student(student: PostStudent) -> JSONResponse:
    try:
        with engine.begin() as conn:
            new_student = conn.execute(students.insert().values(
                **student.dict()).returning(students))

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Bad data')

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={'data': StudentModel(**new_student.fetchone())}
    )


@app.delete("/students/{student_id}")
def delete_student(student_id: UUID) -> JSONResponse:
    with engine.begin() as conn:
        deleted_student = conn.execute(students.delete().where(
            students.c.id == student_id
        )).rowcount
    if not deleted_student:
        raise HTTPException(
            status_code=404,
            detail=f'Student with id: ({student_id}) dose not exist'
        )
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED,
                        content=f'Student with id: {student_id} deleted')


@app.put("/students/{student_id}", response_model=StudentModel)
def update_student_info(student_id: UUID, student: PutStudent) -> JSONResponse:
    # delete the origen
    with engine.begin() as conn:
        deleted_student = conn.execute(students.delete().where(
            students.c.id == student_id
        )).rowcount

        new_student = conn.execute(
            students.insert().values(id=student_id,
                                     ** student.dict()).returning(students))

        if deleted_student:
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content={'data': StudentModel(**new_student.first())})


@app.patch("/students/{student_id}", response_model=StudentModel)
def patch_student(student_id: UUID,
                  student: PatchStudent) -> JSONResponse:

    with engine.begin() as conn:
        updated_student = conn.execute(
            students.update()
            .where(students.c.id == student_id).values(
                **student.dict(exclude_none=True))
            .returning(students))

        if not updated_student.rowcount:
            raise HTTPException(
                status_code=404,
                detail=f'Student with id: ({student_id}) dose not exist'
            )

    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content=StudentModel(**updated_student.fetchone()))
