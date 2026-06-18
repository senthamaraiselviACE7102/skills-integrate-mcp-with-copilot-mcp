"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

from db import (
    ActivityFullError,
    ActivityNotFoundError,
    AlreadySignedUpError,
    NotSignedUpError,
    fetch_activities,
    initialize_database,
    signup_for_activity as signup_student,
    unregister_from_activity as unregister_student,
)

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return fetch_activities()


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    try:
        signup_student(activity_name, email)
    except ActivityNotFoundError:
        raise HTTPException(status_code=404, detail="Activity not found")
    except AlreadySignedUpError:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )
    except ActivityFullError:
        raise HTTPException(status_code=400, detail="Activity is full")

    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    try:
        unregister_student(activity_name, email)
    except ActivityNotFoundError:
        raise HTTPException(status_code=404, detail="Activity not found")
    except NotSignedUpError:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    return {"message": f"Unregistered {email} from {activity_name}"}
