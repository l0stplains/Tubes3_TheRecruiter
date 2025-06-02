-- Create database
CREATE DATABASE IF NOT EXISTS ats_system 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE ats_system;

-- Create users
CREATE USER IF NOT EXISTS 'gongyoo'@'%' IDENTIFIED BY 'roulette';
CREATE USER IF NOT EXISTS 'gongyoo'@'localhost' IDENTIFIED BY 'roulette';

GRANT ALL PRIVILEGES ON ats_system.* TO 'gongyoo'@'%';
GRANT ALL PRIVILEGES ON ats_system.* TO 'gongyoo'@'localhost';

FLUSH PRIVILEGES;

-- ApplicantProfile table
CREATE TABLE IF NOT EXISTS ApplicantProfile (
    applicant_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) DEFAULT NULL,
    last_name VARCHAR(50) DEFAULT NULL,
    date_of_birth DATE DEFAULT NULL,
    address VARCHAR(255) DEFAULT NULL,
    phone_number VARCHAR(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ApplicationDetail table  
CREATE TABLE IF NOT EXISTS ApplicationDetail (
    detail_id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id INT NOT NULL,
    application_role VARCHAR(100) DEFAULT NULL,
    cv_path TEXT NOT NULL,
    FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SHOW TABLES;
DESCRIBE ApplicantProfile;
DESCRIBE ApplicationDetail;