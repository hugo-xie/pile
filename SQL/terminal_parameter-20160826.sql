/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 50621
Source Host           : localhost:3306
Source Database       : charger

Target Server Type    : MYSQL
Target Server Version : 50621
File Encoding         : 65001

Date: 2016-08-26 20:20:38
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for terminal_parameter
-- ----------------------------
DROP TABLE IF EXISTS `terminal_parameter`;
CREATE TABLE `terminal_parameter` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(80) COLLATE utf8_unicode_ci DEFAULT NULL,
  `param` text COLLATE utf8_unicode_ci,
  `timestamp` datetime DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `complete_timestamp` datetime DEFAULT NULL,
  `pile_sn` varchar(80) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
