CREATE TABLE `drawml`.`user` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `date_created` DATETIME NULL,
  `date_modified` DATETIME NULL,
  `user_id` VARCHAR(45) NOT NULL,
  `pw` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `user_id_name_UNIQUE` (`user_id` ASC));

CREATE TABLE `drawml`.`experiment` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `date_created` DATETIME NULL,
  `date_modified` DATETIME NULL,
  `name` VARCHAR(45) NOT NULL,
  `user_id` INTEGER NOT NULL,
  `xml` BLOB NULL,
  `drawing` BLOB NULL,
  `input` INT NULL,
  PRIMARY KEY (`user_id`, `name`),
  FOREIGN KEY user(user_id) REFERENCES user(id) ON DELETE CASCADE,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `user_id_name_UNIQUE` (`user_id`, `name` ASC));

CREATE TABLE `drawml`.`data` (
  `id` MEDIUMINT NOT NULL AUTO_INCREMENT,
  `date_created` DATETIME NULL,
  `date_modified` DATETIME NULL,
  `name` VARCHAR(45) NOT NULL,
  `path` VARCHAR(45) NOT NULL,
  `user_id` INTEGER NOT NULL,
  PRIMARY KEY (`user_id`, `name`),
  FOREIGN KEY user(user_id) REFERENCES user(id) ON DELETE CASCADE,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `user_id_name_UNIQUE` (`user_id`, `name` ASC));
