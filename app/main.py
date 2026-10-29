from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app import models
from app.schemas import StudentCreate, StudentResponse, StudentUpdate

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Management System",
    description="A REST API for managing student records",
    version='1.0.0'
)

@app.get('/')
def home():
    return {
        'message':'Welcome to Student Management API'
    }

@app.get('/health')
def health_check():
    return {
        'status':'healthy'
    }

@app.post(
    '/students/',
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED
)
def studentCreate(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    # Check whether the email already exists
    existing_student = (
        db.query(models.Student)
        .filter(models.Student.email == student.email)
        .first()
    )

    if existing_student:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this email already exists"
        )

    # Convert validated input into a database model
    new_student = models.Student(
        name=student.name,
        email=student.email,
        age=student.age,
        course=student.course
    )

    # Add the student to the session
    db.add(new_student)

    try:
        # Save the record to the database
        db.commit()

        # Load the generated ID and other database values
        db.refresh(new_student)

    except IntegrityError:
        # Roll back a failed transaction
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this email already exists"
        )
    
    # Return the created student
    return new_student

@app.get(
    '/students/',
    response_model=list[StudentResponse]
)
def get_all_students(
    db: Session = Depends(get_db)
):
    
    students = db.query(models.Student).all()

    return students

@app.get(
    '/students/{stud_id}',
    response_model=StudentResponse
)
def get_student(
    stud_id:int,
    db:Session = Depends(get_db)
):
    student = (
        db.query(models.Student)
        .filter(models.Student.id == stud_id)
        .first()
    )

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Student with ID {stud_id} not found'
        )

    return student


@app.put(
    '/students/{stud_id}',
    response_model=StudentResponse
)
def student_update(
    stud_id:int,
    student_data:StudentUpdate,
    db:Session = Depends(get_db)
):
    student = (
        db.query(models.Student)
        .filter(models.Student.id == stud_id)
        .first()
    )

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Student with ID {stud_id} not found'
        )

    student_exist = (
        db.query(models.Student)
        .filter(
            models.Student.email == student_data.email,
            models.Student.id != stud_id
        ).first()
    )

    if student_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='A student with this email already exists'
        )

    # Update all editable fields
    student.name = student_data.name
    student.email = student_data.email
    student.age = student_data.age
    student.course = student_data.course

    try:
        db.commit()
        db.refresh(student)

    except IntegrityError:
        db.rollback
        
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Unable to update student due to a data conflict'
        )

    return student