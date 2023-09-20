drop schema if exists `fitness_club_mgmt_sys`;
CREATE DATABASE `fitness_club_mgmt_sys`;
USE `fitness_club_mgmt_sys`;

CREATE TABLE `user` (
	user_pk int AUTO_INCREMENT PRIMARY KEY NOT NULL,
	`first_name` char(255) NOT NULL,
	`last_name` char(255) NOT NULL,
	`password` char(255) NOT NULL,
	`email` char(255) NOT NULL,
    `user_role` int NOT NULL # 0: admin, 2: trainer, 1: member
);

CREATE TABLE `member` (
    # Member and Trainer table does no need to have primary key as the foreign key user_id would be sufficient.
    # SQ: Having their own pk's will make it easier to read
    member_pk int AUTO_INCREMENT PRIMARY KEY NOT NULL,
	`fitness_goals` char(255),
	`subscription_expire_date` date DEFAULT NULL,
	`subscription_amount` float DEFAULT NULL,
	`auto_pay` int DEFAULT NULL,
	`card_num` char(255) DEFAULT NULL,
	`card_exp` date DEFAULT NULL,
	`card_cvc` char(255) DEFAULT NULL,
    `active` int,
    `reminder` int NULL, # 0: no reminder, 1: reminder is clicked
	user_fk int NOT NULL,
    FOREIGN KEY(user_fk) REFERENCES user(user_pk)
);

CREATE TABLE `trainer` (
    trainer_pk int AUTO_INCREMENT PRIMARY KEY NOT NULL,
	`description` char(255),
	user_fk int NOT NULL,
    FOREIGN KEY(user_fk) REFERENCES user(user_pk)
);

CREATE TABLE `news` (
	news_pk int AUTO_INCREMENT PRIMARY KEY NOT NULL,
	user_fk int NOT NULL,
	`create_date` DATE NOT NULL,
	`title` char(255),
    `content` char(255),
    FOREIGN KEY(user_fk) REFERENCES user(user_pk)
);


CREATE TABLE `newsaudience` (
`news_fk` int NOT NULL,
	`member_fk` int NOT NULL,
   FOREIGN KEY(news_fk) REFERENCES news(news_pk),
   FOREIGN KEY(member_fk) REFERENCES member(member_pk));
   

CREATE TABLE `specialisedclass` (
	`specialised_class_pk` int AUTO_INCREMENT PRIMARY KEY NOT NULL,
	`trainer_fk` int NOT NULL,
	`class_rate` decimal NOT NULL,
	`time` TIME NOT NULL,
	`date` DATE NOT NULL,
    FOREIGN KEY(trainer_fk) REFERENCES trainer(trainer_pk)
);

CREATE TABLE `exerciseclass` (
	exercise_class_pk int AUTO_INCREMENT PRIMARY KEY NOT NULL,
	trainer_fk int NOT NULL,
	`name` char(255) NOT NULL,
	`description` char(255) NOT NULL,
	`room` int NOT NULL,
	`time` TIME NOT NULL,
	`date` DATE NOT NULL,
    FOREIGN KEY(trainer_fk) REFERENCES trainer(trainer_pk)
);

CREATE TABLE `booking` (
   booking_pk int AUTO_INCREMENT PRIMARY KEY NOT NULL,
   member_fk int NOT NULL,
   `specialised_class_fk` int,
   `exercise_class_fk` int,
   FOREIGN KEY(member_fk) REFERENCES member(member_pk),
   FOREIGN KEY(specialised_class_fk) REFERENCES specialisedclass(specialised_class_pk),
   FOREIGN KEY(exercise_class_fk) REFERENCES exerciseclass(exercise_class_pk)
);

CREATE TABLE `payment` (
   payment_pk int AUTO_INCREMENT PRIMARY KEY NOT NULL,
   member_fk int DEFAULT NULL,
   `booking_fk` int DEFAULT NULL,
   `amount` decimal NOT NULL,
   `date` date NOT NULL,
   `status` int,
   FOREIGN KEY(member_fk) REFERENCES member(member_pk),
   FOREIGN KEY(booking_fk) REFERENCES booking(booking_pk)
);


CREATE TABLE `attendance` (
    `attendance_pk` int AUTO_INCREMENT PRIMARY KEY NOT NULL,
    `member_fk` int NOT NULL,
    `attendance_type` ENUM('Gym', 'Exercise Class','Specialised Training') NOT NULL,
    `date` DATE NOT NULL,
    `start_time` time not null,
    `end_time` time not null,
    FOREIGN KEY(member_fk) REFERENCES member(member_pk)
);

