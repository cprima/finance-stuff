/* 
*  DB Script Tool
*  MySQL - 2018-08-02 18:58:22
*  
*  cprior 2018-08-02 19:45
*/ 
CREATE DATABASE IF NOT EXISTS `otmr`
    DEFAULT CHARACTER SET utf8
    DEFAULT COLLATE utf8_general_ci;

USE `otmr`;



/* 
*  currencies
*  
*/ 
DROP TABLE IF EXISTS `currencies`;
CREATE TABLE IF NOT EXISTS `currencies` (
    `currency_id` INT NOT NULL AUTO_INCREMENT,
    `isocode` VARCHAR(3) COLLATE utf8_general_ci NOT NULL,
    `name_en` VARCHAR(32) COLLATE utf8_general_ci,
    `is_active` TINYINT(1) DEFAULT 1,
    `valid_since` DATE DEFAULT '01.01.2000',
    `created_at` timestamp NOT NULL DEFAULT current_timestamp,
PRIMARY KEY (`currency_id`),
INDEX (`currency_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci AUTO_INCREMENT=1 ;

CREATE UNIQUE INDEX `idx_currencies_isocode` ON `currencies` (`isocode`);



/* 
*  exchanges
*  
*/ 
DROP TABLE IF EXISTS `exchanges`;
CREATE TABLE IF NOT EXISTS `exchanges` (
    `exchange_id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(32) COLLATE utf8_general_ci,
    `created_at` timestamp NOT NULL DEFAULT current_timestamp,
PRIMARY KEY (`exchange_id`),
INDEX (`exchange_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci AUTO_INCREMENT=1 ;



/* 
*  quotes
*  
*/ 
DROP TABLE IF EXISTS `quotes`;
CREATE TABLE IF NOT EXISTS `quotes` (
    `quote_id` INT NOT NULL AUTO_INCREMENT,
    `symbol` CHAR(6) COLLATE utf8_general_ci,
    `isin` VARCHAR(12) COLLATE utf8_general_ci,
    `exchange_id` INT,
    `currency_id` INT,
    `date` DATE,
    `time` TIME,
    `resolution` VARCHAR(16) COLLATE utf8_general_ci DEFAULT 'daily' NOT NULL,
    `open` DECIMAL(18,4),
    `high` DECIMAL(18,4),
    `low` DECIMAL(18,4),
    `close` DECIMAL(18,4),
    `volume` INTEGER(10) DEFAULT '0',
    `openinterest` INTEGER(10),
    `created_at` timestamp NOT NULL DEFAULT current_timestamp,
PRIMARY KEY (`quote_id`),
INDEX (`quote_id`),
INDEX (`exchange_id`),
INDEX (`currency_id`),
CONSTRAINT FOREIGN KEY (`exchange_id`) REFERENCES `exchanges` (`exchange_id`) ON DELETE CASCADE ON UPDATE CASCADE,
CONSTRAINT FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`currency_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci AUTO_INCREMENT=1 ;



/* 
*  currencyrates
*  
*/ 
DROP TABLE IF EXISTS `currencyrates`;
CREATE TABLE IF NOT EXISTS `currencyrates` (
    `currencyrate_id` INT NOT NULL AUTO_INCREMENT,
    `currency_id` INT,
    `date` DATE NOT NULL,
    `rate` NUMERIC(10,0) NOT NULL,
    `source_name` VARCHAR(64) COLLATE utf8_general_ci,
    `created_at` timestamp NOT NULL DEFAULT current_timestamp,
PRIMARY KEY (`currencyrate_id`),
INDEX (`currency_id`),
CONSTRAINT FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`currency_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci AUTO_INCREMENT=1 ;



/* 
*  traders
*  
*/ 
DROP TABLE IF EXISTS `traders`;
CREATE TABLE IF NOT EXISTS `traders` (
    `trader_id` INT NOT NULL AUTO_INCREMENT,
    `first_name` VARCHAR(32) COLLATE utf8_general_ci,
    `last_name` VARCHAR(32) COLLATE utf8_general_ci,
    `username` VARCHAR(16) COLLATE utf8_general_ci,
    `password_hash` VARCHAR(255) COLLATE utf8_general_ci,
    `salt` VARCHAR(255) COLLATE utf8_general_ci,
    `created_at` timestamp NOT NULL DEFAULT current_timestamp,
PRIMARY KEY (`trader_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci AUTO_INCREMENT=1 ;



/* 
*  accounts
*  
*/ 
DROP TABLE IF EXISTS `accounts`;
CREATE TABLE IF NOT EXISTS `accounts` (
    `account_id` INT NOT NULL AUTO_INCREMENT,
    `trader_id` INT,
    `is_active` TINYINT(1) DEFAULT 1,
    `created_at` timestamp NOT NULL DEFAULT current_timestamp,
PRIMARY KEY (`account_id`),
INDEX (`account_id`),
CONSTRAINT FOREIGN KEY (`trader_id`) REFERENCES `traders` (`trader_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci AUTO_INCREMENT=1 ;



/* 
*  countries
*  
*/ 
DROP TABLE IF EXISTS `countries`;
CREATE TABLE IF NOT EXISTS `countries` (
    `country_id` INT NOT NULL AUTO_INCREMENT,
    `name_en` VARCHAR(32) COLLATE utf8_general_ci,
    `name_de` VARCHAR(32) COLLATE utf8_general_ci,
    `created_at` timestamp NOT NULL DEFAULT current_timestamp,
PRIMARY KEY (`country_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci AUTO_INCREMENT=1 ;



/* 
*  logs
*  
*/ 
DROP TABLE IF EXISTS `logs`;
CREATE TABLE IF NOT EXISTS `logs` (
    `logs_id` INT NOT NULL AUTO_INCREMENT,
    `msg` VARCHAR(32) COLLATE utf8_general_ci,
    `created_at` timestamp NOT NULL DEFAULT current_timestamp,
PRIMARY KEY (`logs_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci AUTO_INCREMENT=1 ;



