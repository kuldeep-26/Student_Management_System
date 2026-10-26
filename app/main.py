from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app import models
from app.schemas import StudentCreate, StudentResponse

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
        db.refresh()

    except IntegrityError:
        # Roll back a failed transaction
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this email already exists"
        )
    
    # Return the created student
    return new_student