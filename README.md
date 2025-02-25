# SkillMatcher

A service that compares a user-submitted skill name against a curated administrator list of skill names using multiple matching methods.

### Usage
- In you terminal run: ``git clone https://github.com/Simonatraj/skill_matcher.git``
- Connect to your local database. Run these queries:

USE skill_matcher;

CREATE TABLE `User` (
  `user_id` INT AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`)
);

CREATE TABLE `Query` (
  `query_id` INT AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `input_string` TEXT NOT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`query_id`),
  FOREIGN KEY (`user_id`) REFERENCES `User`(`user_id`)
);

CREATE TABLE `Skill` (
  `skill_id` INT AUTO_INCREMENT,
  `skill_name` VARCHAR(100) NOT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`skill_id`)
);

CREATE TABLE `MatchResult` (
  `match_id` INT AUTO_INCREMENT,
  `query_id` INT NOT NULL,
  `skill_id` INT NOT NULL,
  `matching_method` VARCHAR(50),
  `matching_score` DECIMAL(5,2),
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`match_id`),
  FOREIGN KEY (`query_id`) REFERENCES `Query`(`query_id`),
  FOREIGN KEY (`skill_id`) REFERENCES `Skill`(`skill_id`)
);

CREATE TABLE `Administrator` (
  `admin_id` INT AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `skill_id` INT,
  PRIMARY KEY (`admin_id`),
  FOREIGN KEY (`skill_id`) REFERENCES `Skill`(`skill_id`)
);

