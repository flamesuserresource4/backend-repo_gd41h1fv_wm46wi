"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import date

# Sports club specific schemas

class Team(BaseModel):
    name: str = Field(..., description="Team name")
    sport: str = Field(..., description="Sport type, e.g., Football, Basketball")
    coach: Optional[str] = Field(None, description="Head coach name")
    age_group: Optional[str] = Field(None, description="Age group or division")
    logo_url: Optional[HttpUrl] = Field(None, description="Team logo URL")
    description: Optional[str] = Field(None, description="Team description")
    achievements: Optional[List[str]] = Field(default_factory=list, description="List of notable achievements")

class Player(BaseModel):
    team_id: str = Field(..., description="Reference to team _id as string")
    first_name: str
    last_name: str
    position: Optional[str] = None
    number: Optional[int] = None
    photo_url: Optional[HttpUrl] = None

class ClubInfo(BaseModel):
    title: str = Field(..., description="Information title, e.g., About, Contact, Facilities")
    content: str = Field(..., description="Rich text or markdown content")
    order: int = Field(0, description="Display order")

class Document(BaseModel):
    title: str = Field(..., description="Document title")
    category: Optional[str] = Field(None, description="Category, e.g., Forms, Schedules, Policies")
    file_url: HttpUrl = Field(..., description="Public URL to the document (PDF, DOC, etc.)")
    published_on: Optional[date] = Field(None, description="Publish date")
    description: Optional[str] = Field(None, description="Short description")

# Example generic schemas (kept for reference)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
