from fastapi import FastAPI, Depends, HTTPException

from sqlmodel import SQLModel, Field, create_engine, Session, select
from datetime import datetime, timedelta
from typing import Optional

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from fastapi.testclient import TestClient
from main import app


class BookBase(SQLModel):
    title: str = Field(index=True)
    author: str
    year: int


class Book(BookBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    added: datetime = Field(default_factory=datetime.utcnow)
    added_by: Optional[int] = Field(default=None, foreign_key="user.id")


class UserCreate(SQLModel):
    username: str
    password: str


class User(UserCreate, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)


database_url = "sqlite:///library.db"
engine = create_engine(database_url, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


SECRET_KEY = "some-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


app = FastAPI()


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


# אומר לFastAPI מאיפה לקחת את הToken (מה-Authorization header)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.get("/books")
def get_books(session: Session = Depends(get_session)):
    statement = select(Book)
    res = session.exec(statement).all()
    return res


@app.post("/books", response_model=BookBase)
def add_book(book: BookBase, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    new_book = Book(**book.model_dump(), added_by=user.id)
    session.add(new_book)
    session.commit()

    session.refresh(new_book)
    return new_book


@app.delete("/book/{book_id}")
def delete_book(book_id: int, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="user not found")

    if book.added_by != user.id:
        raise HTTPException(status_code=403, detail="user not authorized")

    session.delete(book)
    session.commit()
    return {"deleted": True}


@app.post("/register", status_code=201)
def sign_in(user: UserCreate, session: Session = Depends(get_session)):

    exist = session.exec(select(User).where(User.username == user.username)).first()
    if exist:
        raise HTTPException(status_code=400, detail="user already exist")

    new_user = User(
        username=user.username,
        password=hash_password(user.password)
    )
    session.add(new_user)

    session.commit()
    return {"message": "User created"}


@app.post("/login")
def login(user: UserCreate, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.username == user.username)).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": str(db_user.id)})
    return {"access_token": token, "token_type": "bearer"}


client = TestClient(app)


def test_register():
    response = client.post("/register", json={"username": "ori", "password": "1234"})

    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "User created"


def test_duplicate_register():
    client.post("/register", json={"username": "ori", "password": "1234"})
    response = client.post("/register", json={"username": "ori", "password": "1234"})

    assert response.status_code == 201


def test_login():
    client.post("/register", json={"username": "ori", "password": "1234"})
    response = client.post("/login", json={"username": "ori", "password": "1234"})
    assert response.status_code == 200
    assert "access_token" in response.json()
