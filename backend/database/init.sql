CREATE DATABASE IF NOT EXISTS medium_db;
USE medium_db;  -- Ensure we're using the correct database

CREATE TABLE IF NOT EXISTS articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    link TEXT NOT NULL,
    tag VARCHAR(100),
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);