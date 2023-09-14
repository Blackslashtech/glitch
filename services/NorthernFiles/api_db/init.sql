CREATE TABLE IF NOT EXISTS `files` (
    `id` VARCHAR(36) NOT NULL,
    `name` TEXT NOT NULL,
    `owner` VARCHAR(36) NOT NULL,
    `mime_type` TEXT NOT NULL,
    `uploaded` BOOLEAN NOT NULL DEFAULT(FALSE),
    `metadata` BLOB,
    `creation_time` DATETIME NOT NULL,
    PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `file_keys` (
    `id` INT AUTO_INCREMENT NOT NULL,
    `user` VARCHAR(36) NOT NULL,
    `file` VARCHAR(36) NOT NULL,
    `key` BLOB NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`file`) REFERENCES `files`(`id`) ON DELETE CASCADE
);