from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from scripts.db import engine

Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    link = Column(String(500), nullable=False, unique=True)
    tag = Column(String(100), nullable=True)
    scraped_at = Column(DateTime, default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "link": self.link,
            "tag": self.tag,
            "scraped_at": self.scraped_at.isoformat()
        }

# Ensure tables are created
Base.metadata.create_all(bind=engine)