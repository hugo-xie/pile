/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 50621
Source Host           : localhost:3306
Source Database       : charger

Target Server Type    : MYSQL
Target Server Version : 50621
File Encoding         : 65001

Date: 2016-08-06 21:32:17
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for pile
-- ----------------------------
DROP TABLE IF EXISTS `pile`;
CREATE TABLE `pile` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sn` varchar(80) NOT NULL,
  `name` varchar(80) NOT NULL,
  `longitude` decimal(13,10) NOT NULL,
  `latitude` decimal(13,10) NOT NULL,
  `address` varchar(80) DEFAULT NULL,
  `auto_ack` int(11) NOT NULL,
  `electricity` decimal(10,2) NOT NULL,
  `service` decimal(10,2) NOT NULL,
  `appointment` decimal(10,2) NOT NULL,
  `open` time NOT NULL,
  `close` time NOT NULL,
  `auto_ack_start` datetime DEFAULT NULL,
  `auto_ack_end` datetime DEFAULT NULL,
  `man_ack_secs` int(11) DEFAULT NULL,
  `man_ack_times` int(11) DEFAULT NULL,
  `owner_id` int(11) DEFAULT NULL,
  `supported` int(11) DEFAULT '1',
  `locked_by` int(11) DEFAULT NULL,
  `started_by` int(11) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `voltage` decimal(10,2) DEFAULT NULL,
  `temperature` decimal(10,2) DEFAULT NULL,
  `pm` decimal(10,2) DEFAULT NULL,
  `is_charging` tinyint(1) DEFAULT NULL,
  `can_book` tinyint(1) DEFAULT NULL,
  `is_available` tinyint(1) DEFAULT NULL,
  `software_version` varchar(80) DEFAULT NULL,
  `last_maintain_time` datetime DEFAULT NULL,
  `next_maintain_time` datetime DEFAULT NULL,
  `maintain_description` text,
  `is_qualified` tinyint(1) DEFAULT NULL,
  `is_deleted` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `sn` (`sn`),
  UNIQUE KEY `name` (`name`),
  KEY `owner_id` (`owner_id`),
  KEY `locked_by` (`locked_by`) USING BTREE,
  KEY `started_by` (`started_by`) USING BTREE,
  CONSTRAINT `pile_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=975667 DEFAULT CHARSET=utf8;
