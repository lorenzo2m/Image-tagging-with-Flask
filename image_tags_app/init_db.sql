-- init_db.sql
CREATE TABLE IF NOT EXISTS pictures (
    id CHAR(36) PRIMARY KEY,
    path VARCHAR(255) NOT NULL,
    date CHAR(36) NOT NULL
);

CREATE TABLE IF NOT EXISTS tags (
    tag VARCHAR(32),
    picture_id CHAR(36),
    confidence INT,
    date CHAR(36) NOT NULL,
    PRIMARY KEY (tag, picture_id),
    FOREIGN KEY (picture_id) REFERENCES pictures(id) ON DELETE CASCADE
);