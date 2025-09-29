/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.8.3-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: mycrm
-- ------------------------------------------------------
-- Server version	11.8.3-MariaDB-0+deb13u1 from Debian

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `account_emailaddress`
--

DROP TABLE IF EXISTS `account_emailaddress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_emailaddress` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(254) NOT NULL,
  `verified` tinyint(1) NOT NULL,
  `primary` tinyint(1) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `account_emailaddress_user_id_email_987c8728_uniq` (`user_id`,`email`),
  KEY `account_emailaddress_email_03be32b2` (`email`),
  CONSTRAINT `account_emailaddress_user_id_2c513194_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_emailaddress`
--

LOCK TABLES `account_emailaddress` WRITE;
/*!40000 ALTER TABLE `account_emailaddress` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `account_emailaddress` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `account_emailconfirmation`
--

DROP TABLE IF EXISTS `account_emailconfirmation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_emailconfirmation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `sent` datetime(6) DEFAULT NULL,
  `key` varchar(64) NOT NULL,
  `email_address_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `key` (`key`),
  KEY `account_emailconfirm_email_address_id_5b7f8c58_fk_account_e` (`email_address_id`),
  CONSTRAINT `account_emailconfirm_email_address_id_5b7f8c58_fk_account_e` FOREIGN KEY (`email_address_id`) REFERENCES `account_emailaddress` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_emailconfirmation`
--

LOCK TABLES `account_emailconfirmation` WRITE;
/*!40000 ALTER TABLE `account_emailconfirmation` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `account_emailconfirmation` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=89 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `auth_permission` VALUES
(1,'Can add log entry',1,'add_logentry'),
(2,'Can change log entry',1,'change_logentry'),
(3,'Can delete log entry',1,'delete_logentry'),
(4,'Can view log entry',1,'view_logentry'),
(5,'Can add permission',2,'add_permission'),
(6,'Can change permission',2,'change_permission'),
(7,'Can delete permission',2,'delete_permission'),
(8,'Can view permission',2,'view_permission'),
(9,'Can add group',3,'add_group'),
(10,'Can change group',3,'change_group'),
(11,'Can delete group',3,'delete_group'),
(12,'Can view group',3,'view_group'),
(13,'Can add user',4,'add_user'),
(14,'Can change user',4,'change_user'),
(15,'Can delete user',4,'delete_user'),
(16,'Can view user',4,'view_user'),
(17,'Can add content type',5,'add_contenttype'),
(18,'Can change content type',5,'change_contenttype'),
(19,'Can delete content type',5,'delete_contenttype'),
(20,'Can view content type',5,'view_contenttype'),
(21,'Can add session',6,'add_session'),
(22,'Can change session',6,'change_session'),
(23,'Can delete session',6,'delete_session'),
(24,'Can view session',6,'view_session'),
(25,'Can add company',7,'add_company'),
(26,'Can change company',7,'change_company'),
(27,'Can delete company',7,'delete_company'),
(28,'Can view company',7,'view_company'),
(29,'Can add contact',8,'add_contact'),
(30,'Can change contact',8,'change_contact'),
(31,'Can delete contact',8,'delete_contact'),
(32,'Can view contact',8,'view_contact'),
(33,'Can add document link',9,'add_documentlink'),
(34,'Can change document link',9,'change_documentlink'),
(35,'Can delete document link',9,'delete_documentlink'),
(36,'Can view document link',9,'view_documentlink'),
(37,'Can add email log',10,'add_emaillog'),
(38,'Can change email log',10,'change_emaillog'),
(39,'Can delete email log',10,'delete_emaillog'),
(40,'Can view email log',10,'view_emaillog'),
(41,'Can add file asset',11,'add_fileasset'),
(42,'Can change file asset',11,'change_fileasset'),
(43,'Can delete file asset',11,'delete_fileasset'),
(44,'Can view file asset',11,'view_fileasset'),
(45,'Can add call log',12,'add_calllog'),
(46,'Can change call log',12,'change_calllog'),
(47,'Can delete call log',12,'delete_calllog'),
(48,'Can view call log',12,'view_calllog'),
(49,'Can add project',13,'add_project'),
(50,'Can change project',13,'change_project'),
(51,'Can delete project',13,'delete_project'),
(52,'Can view project',13,'view_project'),
(53,'Can add time entry',14,'add_timeentry'),
(54,'Can change time entry',14,'change_timeentry'),
(55,'Can delete time entry',14,'delete_timeentry'),
(56,'Can view time entry',14,'view_timeentry'),
(57,'Can add site',15,'add_site'),
(58,'Can change site',15,'change_site'),
(59,'Can delete site',15,'delete_site'),
(60,'Can view site',15,'view_site'),
(61,'Can add email address',16,'add_emailaddress'),
(62,'Can change email address',16,'change_emailaddress'),
(63,'Can delete email address',16,'delete_emailaddress'),
(64,'Can view email address',16,'view_emailaddress'),
(65,'Can add email confirmation',17,'add_emailconfirmation'),
(66,'Can change email confirmation',17,'change_emailconfirmation'),
(67,'Can delete email confirmation',17,'delete_emailconfirmation'),
(68,'Can view email confirmation',17,'view_emailconfirmation'),
(69,'Can add social account',18,'add_socialaccount'),
(70,'Can change social account',18,'change_socialaccount'),
(71,'Can delete social account',18,'delete_socialaccount'),
(72,'Can view social account',18,'view_socialaccount'),
(73,'Can add social application',19,'add_socialapp'),
(74,'Can change social application',19,'change_socialapp'),
(75,'Can delete social application',19,'delete_socialapp'),
(76,'Can view social application',19,'view_socialapp'),
(77,'Can add social application token',20,'add_socialtoken'),
(78,'Can change social application token',20,'change_socialtoken'),
(79,'Can delete social application token',20,'delete_socialtoken'),
(80,'Can view social application token',20,'view_socialtoken'),
(81,'Can add expense draft',21,'add_expensedraft'),
(82,'Can change expense draft',21,'change_expensedraft'),
(83,'Can delete expense draft',21,'delete_expensedraft'),
(84,'Can view expense draft',21,'view_expensedraft'),
(85,'Can add invoice draft',22,'add_invoicedraft'),
(86,'Can change invoice draft',22,'change_invoicedraft'),
(87,'Can delete invoice draft',22,'delete_invoicedraft'),
(88,'Can view invoice draft',22,'view_invoicedraft');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `auth_user` VALUES
(3,'pbkdf2_sha256$1000000$DJlkLYn8x0pr0v5U1fpvlP$NpKKDBGRSDBo1i3EmuZ2FKZ9F/e/TDSDDbEtWON3dBA=','2025-09-28 07:58:37.130757',1,'admin','','','admin@mycrm.local',1,1,'2025-08-22 11:23:33.453807');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `crm_core_calllog`
--

DROP TABLE IF EXISTS `crm_core_calllog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `crm_core_calllog` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `number` varchar(64) NOT NULL,
  `direction` varchar(10) NOT NULL,
  `status` varchar(12) NOT NULL,
  `source` varchar(12) NOT NULL,
  `started_at` datetime(6) NOT NULL,
  `duration_s` int(10) unsigned DEFAULT NULL CHECK (`duration_s` >= 0),
  `note` longtext NOT NULL,
  `raw` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`raw`)),
  `created_at` datetime(6) NOT NULL,
  `company_id` bigint(20) DEFAULT NULL,
  `contact_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `crm_core_calllog_company_id_5707582c_fk_crm_core_company_id` (`company_id`),
  KEY `crm_core_calllog_contact_id_0378495d_fk_crm_core_contact_id` (`contact_id`),
  KEY `crm_core_calllog_number_a57c6759` (`number`),
  CONSTRAINT `crm_core_calllog_company_id_5707582c_fk_crm_core_company_id` FOREIGN KEY (`company_id`) REFERENCES `crm_core_company` (`id`),
  CONSTRAINT `crm_core_calllog_contact_id_0378495d_fk_crm_core_contact_id` FOREIGN KEY (`contact_id`) REFERENCES `crm_core_contact` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `crm_core_calllog`
--

LOCK TABLES `crm_core_calllog` WRITE;
/*!40000 ALTER TABLE `crm_core_calllog` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `crm_core_calllog` VALUES
(1,'+4368181752646','out','failed','sipgate','2025-09-03 07:10:48.671632',NULL,'','{\"status_code\": 200, \"body\": \"{\\\"sessionId\\\":\\\"52546B150B0C0D3A5D0618050605780B08020F48525B515F7851545B5054595740424D541F57005E5E5F40745A54415B71517C53510B5D585E59424F5D4156017446185E\\\"}\", \"payload\": {\"deviceId\": \"e0\", \"caller\": \"+498414544240\", \"callee\": \"+4368181752646\"}}','2025-09-03 07:10:48.671774',NULL,NULL);
/*!40000 ALTER TABLE `crm_core_calllog` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `crm_core_company`
--

DROP TABLE IF EXISTS `crm_core_company`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `crm_core_company` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `address` longtext NOT NULL,
  `phone` varchar(50) NOT NULL,
  `website` varchar(200) NOT NULL,
  `description` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `crm_core_company`
--

LOCK TABLES `crm_core_company` WRITE;
/*!40000 ALTER TABLE `crm_core_company` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `crm_core_company` VALUES
(1,'division one Interim Management GmbH','Friedrichstrasse 6  |  D‑70174 Stuttgart','','','','2025-08-27 13:05:24.934878','2025-08-27 13:05:24.934948'),
(4,'Synsero','Synsero Experts GmbH\r\nGabelsbergerstraße 4\r\n80333 München\r\nDeutschland','','','','2025-09-10 16:32:38.118715','2025-09-10 16:32:38.118875'),
(5,'Krongaard GmbH','|  FUHLENTWIETE 10  |  20355 HAMBURG','','','','2025-09-18 17:36:47.960855','2025-09-18 17:36:47.960922');
/*!40000 ALTER TABLE `crm_core_company` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `crm_core_contact`
--

DROP TABLE IF EXISTS `crm_core_contact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `crm_core_contact` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `phone` varchar(64) NOT NULL,
  `phone_normalized` varchar(32) NOT NULL,
  `company_id` bigint(20) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `email` varchar(254) DEFAULT NULL,
  `first_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  `position` varchar(100) DEFAULT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `crm_core_contact_phone_normalized_b286c4da` (`phone_normalized`),
  KEY `crm_core_contact_company_id_030420c0_fk_crm_core_company_id` (`company_id`),
  CONSTRAINT `crm_core_contact_company_id_030420c0_fk_crm_core_company_id` FOREIGN KEY (`company_id`) REFERENCES `crm_core_company` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `crm_core_contact`
--

LOCK TABLES `crm_core_contact` WRITE;
/*!40000 ALTER TABLE `crm_core_contact` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `crm_core_contact` VALUES
(1,'','+49223856612',NULL,'2025-08-23 06:24:28.130046','lothar.wacker@reisewacker.de','Lothar','Wacker',NULL,'2025-08-23 06:26:00.127812'),
(2,'+497112031058426','+497112031058426',1,'2025-08-27 12:59:43.045581','oezdemir@division-one.com','Özdemir,','Aylin','Recruiter','2025-08-27 13:06:09.545188'),
(3,'+4907112031058459','+4907112031058459',1,'2025-08-27 13:02:45.467369','schulten@division-one.com','Schulten,','Benjamin','Partner','2025-08-27 13:06:20.291716'),
(4,'','',NULL,'2025-09-06 18:42:13.175735','manisha.singhi@mbade.com','Manisha','Singhi',NULL,'2025-09-06 18:42:13.175836'),
(5,'+4989248891220','+4989248891220',4,'2025-09-10 16:28:16.816343','lange@synsero.de','Florian','Lange','Recruiter','2025-09-10 16:33:16.808240'),
(6,'','',NULL,'2025-09-17 21:02:11.241120','pwisz@amadeus-fire.de','Wisz,','Paulina',NULL,'2025-09-17 21:02:11.241183'),
(7,'+49(0)40 30 38 44 125','+49040303844125',5,'2025-09-18 17:34:40.482341','Pauline.Gross@krongaard.de','Pauline','Gross','Recruiter','2025-09-18 17:37:00.530840');
/*!40000 ALTER TABLE `crm_core_contact` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `crm_core_documentlink`
--

DROP TABLE IF EXISTS `crm_core_documentlink`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `crm_core_documentlink` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `url` varchar(200) NOT NULL,
  `company_id` bigint(20) DEFAULT NULL,
  `contact_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `crm_core_documentlink_company_id_4e368890_fk_crm_core_company_id` (`company_id`),
  KEY `crm_core_documentlink_contact_id_bc6ea9a9_fk_crm_core_contact_id` (`contact_id`),
  CONSTRAINT `crm_core_documentlink_company_id_4e368890_fk_crm_core_company_id` FOREIGN KEY (`company_id`) REFERENCES `crm_core_company` (`id`),
  CONSTRAINT `crm_core_documentlink_contact_id_bc6ea9a9_fk_crm_core_contact_id` FOREIGN KEY (`contact_id`) REFERENCES `crm_core_contact` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `crm_core_documentlink`
--

LOCK TABLES `crm_core_documentlink` WRITE;
/*!40000 ALTER TABLE `crm_core_documentlink` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `crm_core_documentlink` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `crm_core_emaillog`
--

DROP TABLE IF EXISTS `crm_core_emaillog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `crm_core_emaillog` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `subject` varchar(255) NOT NULL,
  `message` longtext NOT NULL,
  `timestamp` datetime(6) NOT NULL,
  `contact_id` bigint(20) DEFAULT NULL,
  `recipient` varchar(254) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `crm_core_emaillog_contact_id_8a3709bd_fk_crm_core_contact_id` (`contact_id`),
  CONSTRAINT `crm_core_emaillog_contact_id_8a3709bd_fk_crm_core_contact_id` FOREIGN KEY (`contact_id`) REFERENCES `crm_core_contact` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `crm_core_emaillog`
--

LOCK TABLES `crm_core_emaillog` WRITE;
/*!40000 ALTER TABLE `crm_core_emaillog` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `crm_core_emaillog` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `crm_core_expensedraft`
--

DROP TABLE IF EXISTS `crm_core_expensedraft`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `crm_core_expensedraft` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `amount` decimal(10,2) DEFAULT NULL,
  `description` longtext NOT NULL,
  `supplier` varchar(255) NOT NULL,
  `category` varchar(100) NOT NULL,
  `message_id` varchar(255) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `crm_core_expensedraft`
--

LOCK TABLES `crm_core_expensedraft` WRITE;
/*!40000 ALTER TABLE `crm_core_expensedraft` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `crm_core_expensedraft` VALUES
(3,'2025-09-04',NULL,'Updates to your Mollie User Agreement','','','AAMkAGY2NThhZDJlLTdiYjYtNDNmMi04NDVkLTRmYTUzNDAzNzcyNQBGAAAAAADqXhEuhCRLS59fL0nSfO1GBwB3_k8U9iJjTp7ilr_z1JTwAAAAAAEMAAB3_k8U9iJjTp7ilr_z1JTwAANiXlg5AAA=','2025-09-04 17:14:34.597574'),
(4,'2025-09-04',NULL,'spusu - Ihre Rechnung KdNr 4096380','','','AAMkAGY2NThhZDJlLTdiYjYtNDNmMi04NDVkLTRmYTUzNDAzNzcyNQBGAAAAAADqXhEuhCRLS59fL0nSfO1GBwB3_k8U9iJjTp7ilr_z1JTwAAAAAAEMAAB3_k8U9iJjTp7ilr_z1JTwAANiXlfRAAA=','2025-09-04 17:21:48.309390'),
(5,'2025-09-04',NULL,'Deine Bestellung - Finanz.at','','','AAMkAGY2NThhZDJlLTdiYjYtNDNmMi04NDVkLTRmYTUzNDAzNzcyNQBGAAAAAADqXhEuhCRLS59fL0nSfO1GBwB3_k8U9iJjTp7ilr_z1JTwAAAAAAEMAAB3_k8U9iJjTp7ilr_z1JTwAANiXlgUAAA=','2025-09-04 17:24:23.135487'),
(6,'2025-09-04',NULL,'Deine Bestellung - Finanz.at','','','AAMkAGY2NThhZDJlLTdiYjYtNDNmMi04NDVkLTRmYTUzNDAzNzcyNQBGAAAAAADqXhEuhCRLS59fL0nSfO1GBwB3_k8U9iJjTp7ilr_z1JTwAAAAAAEMAAB3_k8U9iJjTp7ilr_z1JTwAANiXlgUAAA=','2025-09-04 18:28:43.874863'),
(7,'2025-09-04',NULL,'Deine Bestellung - Finanz.at','','','AAMkAGY2NThhZDJlLTdiYjYtNDNmMi04NDVkLTRmYTUzNDAzNzcyNQBGAAAAAADqXhEuhCRLS59fL0nSfO1GBwB3_k8U9iJjTp7ilr_z1JTwAAAAAAEMAAB3_k8U9iJjTp7ilr_z1JTwAANiXlgUAAA=','2025-09-04 18:41:31.264963'),
(8,'2025-09-04',NULL,'Deine Bestellung - Finanz.at','','','AAMkAGY2NThhZDJlLTdiYjYtNDNmMi04NDVkLTRmYTUzNDAzNzcyNQBGAAAAAADqXhEuhCRLS59fL0nSfO1GBwB3_k8U9iJjTp7ilr_z1JTwAAAAAAEMAAB3_k8U9iJjTp7ilr_z1JTwAANiXlgUAAA=','2025-09-04 19:53:34.811984'),
(9,'2025-09-04',NULL,'Deine Bestellung - Finanz.at','','','AAMkAGY2NThhZDJlLTdiYjYtNDNmMi04NDVkLTRmYTUzNDAzNzcyNQBGAAAAAADqXhEuhCRLS59fL0nSfO1GBwB3_k8U9iJjTp7ilr_z1JTwAAAAAAEMAAB3_k8U9iJjTp7ilr_z1JTwAANiXlgUAAA=','2025-09-04 21:04:53.927798'),
(10,'2025-09-15',NULL,'DeepL Test','','','','2025-09-15 10:23:23.285321'),
(11,'2025-09-15',NULL,'DeepL Test','','','','2025-09-15 10:50:30.758727'),
(12,'2025-09-15',NULL,'DeepL Test','','','','2025-09-15 11:29:47.611480'),
(13,'2025-09-15',NULL,'DeepL Test','','','','2025-09-15 11:35:54.312734'),
(14,'2025-09-15',NULL,'DeepL Test','','','','2025-09-15 11:49:27.647360'),
(15,'2025-09-15',NULL,'TestPDF','Dummy PDF file','','','2025-09-15 12:01:06.864366'),
(16,'2025-09-15',NULL,'TestPDF','Dummy PDF file','','','2025-09-15 12:02:33.663792'),
(17,'2025-09-15',NULL,'TestPDF','Dummy PDF file','','','2025-09-15 12:02:41.259947'),
(18,'2025-09-15',NULL,'TestPDF','','','','2025-09-15 12:03:16.707612'),
(19,'2025-09-11',8.99,'DeepL Test','S DeepL','','','2025-09-15 12:06:36.866074'),
(20,'2025-09-11',8.99,'DeepL Test','S DeepL','','','2025-09-15 12:10:54.128838'),
(21,'2025-09-11',8.99,'DeepL Test','S DeepL','','','2025-09-15 15:12:11.336266'),
(22,'2025-09-11',8.99,'DeepL Test','S DeepL','','','2025-09-15 15:12:29.425955'),
(23,'2025-09-11',8.99,'DeepL Test','S DeepL','','','2025-09-15 15:25:46.148987'),
(24,'2025-09-11',8.99,'DeepL Test','S DeepL','','','2025-09-15 15:40:54.966427'),
(25,'2025-09-11',8.99,'DeepL Test','S DeepL','','','2025-09-15 15:52:51.430437'),
(26,'2025-09-11',8.99,'DeepL Test','S DeepL','','','2025-09-15 15:53:09.918624'),
(27,'2025-09-18',19.16,'OCR-Erkennung – united-domains GmbH – 19.16 EUR','united-domains GmbH','','AAMkAGY2NThhZDJlLTdiYjYtNDNmMi04NDVkLTRmYTUzNDAzNzcyNQBGAAAAAADqXhEuhCRLS59fL0nSfO1GBwB3_k8U9iJjTp7ilr_z1JTwAAAAAAEMAAB3_k8U9iJjTp7ilr_z1JTwAANrlG8-AAA=','2025-09-18 18:26:55.995026'),
(28,'2025-09-18',19.16,'OCR-Erkennung – united-domains GmbH – 19.16 EUR','united-domains GmbH','','AAMkAGY2NThhZDJlLTdiYjYtNDNmMi04NDVkLTRmYTUzNDAzNzcyNQBGAAAAAADqXhEuhCRLS59fL0nSfO1GBwB3_k8U9iJjTp7ilr_z1JTwAAAAAAEMAAB3_k8U9iJjTp7ilr_z1JTwAANrlG8-AAA=','2025-09-18 18:27:36.764030');
/*!40000 ALTER TABLE `crm_core_expensedraft` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `crm_core_fileasset`
--

DROP TABLE IF EXISTS `crm_core_fileasset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `crm_core_fileasset` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `file` varchar(100) NOT NULL,
  `original_name` varchar(255) NOT NULL,
  `size` bigint(20) NOT NULL,
  `notes` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `company_id` bigint(20) DEFAULT NULL,
  `contact_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `crm_core_fileasset_company_id_51d67174_fk_crm_core_company_id` (`company_id`),
  KEY `crm_core_fileasset_contact_id_8b0ea3ea_fk_crm_core_contact_id` (`contact_id`),
  KEY `crm_core_fi_created_96231c_idx` (`created_at`,`original_name`),
  CONSTRAINT `crm_core_fileasset_company_id_51d67174_fk_crm_core_company_id` FOREIGN KEY (`company_id`) REFERENCES `crm_core_company` (`id`),
  CONSTRAINT `crm_core_fileasset_contact_id_8b0ea3ea_fk_crm_core_contact_id` FOREIGN KEY (`contact_id`) REFERENCES `crm_core_contact` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `crm_core_fileasset`
--

LOCK TABLES `crm_core_fileasset` WRITE;
/*!40000 ALTER TABLE `crm_core_fileasset` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `crm_core_fileasset` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `crm_core_invoicedraft`
--

DROP TABLE IF EXISTS `crm_core_invoicedraft`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `crm_core_invoicedraft` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `source` varchar(20) NOT NULL,
  `source_message_id` varchar(255) NOT NULL,
  `source_attachment_id` varchar(255) NOT NULL,
  `attachment_sha256` varchar(64) NOT NULL,
  `pdf` varchar(100) NOT NULL,
  `issuer` varchar(255) NOT NULL,
  `invoice_number` varchar(128) NOT NULL,
  `invoice_date` date DEFAULT NULL,
  `currency` varchar(8) NOT NULL,
  `net_amount` decimal(12,2) DEFAULT NULL,
  `vat_rate` decimal(5,2) DEFAULT NULL,
  `vat_amount` decimal(12,2) DEFAULT NULL,
  `gross_amount` decimal(12,2) DEFAULT NULL,
  `raw_text` longtext NOT NULL,
  `raw_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`raw_json`)),
  `status` varchar(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `crm_core_invoicedraft_created_by_id_2ed07834_fk_auth_user_id` (`created_by_id`),
  KEY `crm_core_in_source__d371c7_idx` (`source_message_id`,`source_attachment_id`),
  KEY `crm_core_in_attachm_4a8c15_idx` (`attachment_sha256`),
  CONSTRAINT `crm_core_invoicedraft_created_by_id_2ed07834_fk_auth_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `crm_core_invoicedraft`
--

LOCK TABLES `crm_core_invoicedraft` WRITE;
/*!40000 ALTER TABLE `crm_core_invoicedraft` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `crm_core_invoicedraft` VALUES
(1,'mail','','','3df79d34abbca99308e79cb94461c1893582604d68329a41fd4bec1885e6adb4','invoices/source/2025/09/invoice_3df79d34abbc.pdf','Dummy PDF file','',NULL,'EUR',NULL,NULL,NULL,NULL,'Dummy PDF file',NULL,'draft','2025-09-14 09:47:48.558174',3),
(2,'mail','','','','invoices/source/2025/09/dummy.pdf','Dummy PDF file','',NULL,'EUR',NULL,NULL,NULL,NULL,'Dummy PDF file',NULL,'draft','2025-09-14 09:58:29.959049',NULL),
(3,'mail','','','','invoices/source/2025/09/RE_Deepl.pdf','S DeepL','','2025-09-11','EUR',-349242037.51,20.00,349242045.00,7.49,'S DeepL\n\nDeepL SE, Maarweg 165, 50825 Köln\nUSt.-Nr. : DE349242045\n\nRECHNUNGSANSCHRIFT\n\nAlfred Hagn\n\nAlfred Hagn\nUnternehmensberatung\nRudolf-Waisenhorngasse 138/4\nWien, 1230\n\nOsterreich\n\nBESCHREIBUNG\n\nDeepL Pro Starter\n\nUST.-DETAILS\nGesamtsumme (zzgl. USt.) - € 7,49\n\nUST. BEI 20 % = € 1,50\n\nZAHLUNGEN\n\nRECHNUNG\n\nRechnung # DI-20250911-886\n\nRechnungsdatum 11.09.2025 00:00\nUTC\n\nRechnungsbetrag € 8,99 (EUR)\nKunden-ID 991933\n\nZahlungsbedingungen Fällig mit\nErhalt\n\nBEZAHLT\n\nABONNEMENT\nID 951527\n\nRechnungszeitraum 11.09.2025 00:00 UTC\n\nbis 11.10.2025 00:00 UTC\n\nMENGE STÜCKPREIS B\n(inkl. UST.)\n1.000000 € 8,99\nGesamtsumme\nZahlungen\n\nFälliger Betrag (EUR)\n\n€ 8,99 (EUR) wurden am 11.09.2025 00:11 UTC bezahlt per MasterCard, endend auf 0605.\n\nHINWEISE\n\nETRAG (EUR)\n(inkl. UST.)\n\n€ 8,99\n\n€ 8,99\n-€ 8,99\n\n€ 0,00\n\nVisit: www.deepl.com - Email: info@deepl.com - Management Board: Dr. Jaroslaw Kutylowski (CEO) - Chairman of the\nSupervisory Board: Florian Schweitzer - Register Court Cologne, HRB 10461 7- VAT ID DE349242045\n',NULL,'draft','2025-09-14 10:45:33.518915',NULL),
(4,'mail','','','','invoices/source/2025/09/RE_Deepl_xxYTKBz.pdf','S DeepL','','2025-09-11','EUR',7.49,20.03,1.50,8.99,'S DeepL\n\nDeepL SE, Maarweg 165, 50825 Köln\nUSt.-Nr. : DE349242045\n\nRECHNUNGSANSCHRIFT\n\nAlfred Hagn\n\nAlfred Hagn\nUnternehmensberatung\nRudolf-Waisenhorngasse 138/4\nWien, 1230\n\nOsterreich\n\nBESCHREIBUNG\n\nDeepL Pro Starter\n\nUST.-DETAILS\nGesamtsumme (zzgl. USt.) - € 7,49\n\nUST. BEI 20 % = € 1,50\n\nZAHLUNGEN\n\nRECHNUNG\n\nRechnung # DI-20250911-886\n\nRechnungsdatum 11.09.2025 00:00\nUTC\n\nRechnungsbetrag € 8,99 (EUR)\nKunden-ID 991933\n\nZahlungsbedingungen Fällig mit\nErhalt\n\nBEZAHLT\n\nABONNEMENT\nID 951527\n\nRechnungszeitraum 11.09.2025 00:00 UTC\n\nbis 11.10.2025 00:00 UTC\n\nMENGE STÜCKPREIS B\n(inkl. UST.)\n1.000000 € 8,99\nGesamtsumme\nZahlungen\n\nFälliger Betrag (EUR)\n\n€ 8,99 (EUR) wurden am 11.09.2025 00:11 UTC bezahlt per MasterCard, endend auf 0605.\n\nHINWEISE\n\nETRAG (EUR)\n(inkl. UST.)\n\n€ 8,99\n\n€ 8,99\n-€ 8,99\n\n€ 0,00\n\nVisit: www.deepl.com - Email: info@deepl.com - Management Board: Dr. Jaroslaw Kutylowski (CEO) - Chairman of the\nSupervisory Board: Florian Schweitzer - Register Court Cologne, HRB 10461 7- VAT ID DE349242045\n',NULL,'draft','2025-09-14 10:52:11.398601',NULL),
(5,'mail','AAMkAGY2NThhZDJlLTdiYjYtNDNmMi04NDVkLTRmYTUzNDAzNzcyNQBGAAAAAADqXhEuhCRLS59fL0nSfO1GBwB3_k8U9iJjTp7ilr_z1JTwAAAAAAEMAAB3_k8U9iJjTp7ilr_z1JTwAANrlG8-AAA=','AAMkAGY2NThhZDJlLTdiYjYtNDNmMi04NDVkLTRmYTUzNDAzNzcyNQBGAAAAAADqXhEuhCRLS59fL0nSfO1GBwB3_k8U9iJjTp7ilr_z1JTwAAAAAAEMAAB3_k8U9iJjTp7ilr_z1JTwAANrlG8-AAABEgAQAB7NNxBRHixAjBd1hZBre4A=','','','united-domains GmbH','','2025-09-17','EUR',15.97,NULL,3.19,19.16,'united-domains GmbH\nGautinger Str. 10\n82319 Starnberg\nSupport: +49 (0) 8151 / 36867 - 0\nE-Mail: support@united-domains.de\nBitte halten Sie bei Anrufen Ihre PIN bereit.\nSie können diese in Ihrem Portfolio festlegen.\nunited-domains GmbH · Gautinger Str. 10 · 82319 Starnberg\nAlfred Hagn\nRudolf-Waisenhorng.138-4\n1230 Wien\nÖSTERREICH\nRechnung: AR20250917A0089492\nRechnungsdatum: 17.09.2025 Fälligkeitsdatum: 18.09.2025\nKundennummer: 89492 Mandats-ID: AT0089492XX0002\nGläubiger-ID: DE30ZZZ00000004764\nDatum Artikel Preis (EUR)\n17.09.2025Registrierung interimhagn.de\n17.09.2025-16.09.2026\n19,16\n Gesamt Netto 15,97\nIm Gesamtbetrag enthaltene MwSt. 20,00 % 3,19\n Gesamt Brutto 19,16\nDas Datum der Registrierung entspricht dem Leistungszeitpunkt.\nWir ziehen den Rechnungsbetrag per SEPA-Lastschrift von ihrem Konto (IBAN:\nATXXXXXXXXXXXXXXXX2200 / BIC: BKAUATWW) zum Fälligkeitsdatum ein.\nIst das Fälligkeitsdatum ein Wochenend-/Feiertag, erfolgt die Abbuchung am nächsten Werktag.\nSie sind berechtigt, begründete Einwendungen gegen einzelne in der Rechnung gestellte Forderungen\nzu erheben. Bitte wenden Sie sich gerne an uns.\nAlle Rechnungen finden Sie online zum Download in Ihrem Domain-Portfolio unter dem Menüpunkt\n\"Konto/Rechnungen\": https://www.united-domains.de\nVielen Dank für Ihren Auftrag!\nIhre united-domains GmbH\nGeschäftsführung: Schweiz MwSt: CHE-274.284.535 MWST Sitz Starnberg\nSaad Daoud Türkei MwSt: 8920484983 HRB 29 43 48, Amtsgericht München\nMichael Klemund UK MwSt: 377 8696 18\nUSt-IdNr.: DE203066334\nSt.Nr.: 117/116/71090','{\"attachment\": {\"id\": \"AAMkAGY2NThhZDJlLTdiYjYtNDNmMi04NDVkLTRmYTUzNDAzNzcyNQBGAAAAAADqXhEuhCRLS59fL0nSfO1GBwB3_k8U9iJjTp7ilr_z1JTwAAAAAAEMAAB3_k8U9iJjTp7ilr_z1JTwAANrlG8-AAABEgAQAB7NNxBRHixAjBd1hZBre4A=\", \"name\": \"rechnung_AR20250917A0089492.pdf\", \"contentType\": \"application/pdf\", \"size\": 25818}, \"amounts\": {\"net\": \"15.97\", \"vat\": \"3.19\", \"gross\": \"19.16\", \"vat_rate\": \"20\"}}','draft','2025-09-18 18:20:48.402575',NULL),
(6,'mail','AAMkAGY2NThhZDJlLTdiYjYtNDNmMi04NDVkLTRmYTUzNDAzNzcyNQBGAAAAAADqXhEuhCRLS59fL0nSfO1GBwB3_k8U9iJjTp7ilr_z1JTwAAAAAAEMAAB3_k8U9iJjTp7ilr_z1JTwAANrlG8-AAA=','AAMkAGY2NThhZDJlLTdiYjYtNDNmMi04NDVkLTRmYTUzNDAzNzcyNQBGAAAAAADqXhEuhCRLS59fL0nSfO1GBwB3_k8U9iJjTp7ilr_z1JTwAAAAAAEMAAB3_k8U9iJjTp7ilr_z1JTwAANrlG8-AAABEgAQAB7NNxBRHixAjBd1hZBre4A=','','','united-domains GmbH','','2025-09-17','EUR',15.97,NULL,3.19,19.16,'united-domains GmbH\nGautinger Str. 10\n82319 Starnberg\nSupport: +49 (0) 8151 / 36867 - 0\nE-Mail: support@united-domains.de\nBitte halten Sie bei Anrufen Ihre PIN bereit.\nSie können diese in Ihrem Portfolio festlegen.\nunited-domains GmbH · Gautinger Str. 10 · 82319 Starnberg\nAlfred Hagn\nRudolf-Waisenhorng.138-4\n1230 Wien\nÖSTERREICH\nRechnung: AR20250917A0089492\nRechnungsdatum: 17.09.2025 Fälligkeitsdatum: 18.09.2025\nKundennummer: 89492 Mandats-ID: AT0089492XX0002\nGläubiger-ID: DE30ZZZ00000004764\nDatum Artikel Preis (EUR)\n17.09.2025Registrierung interimhagn.de\n17.09.2025-16.09.2026\n19,16\n Gesamt Netto 15,97\nIm Gesamtbetrag enthaltene MwSt. 20,00 % 3,19\n Gesamt Brutto 19,16\nDas Datum der Registrierung entspricht dem Leistungszeitpunkt.\nWir ziehen den Rechnungsbetrag per SEPA-Lastschrift von ihrem Konto (IBAN:\nATXXXXXXXXXXXXXXXX2200 / BIC: BKAUATWW) zum Fälligkeitsdatum ein.\nIst das Fälligkeitsdatum ein Wochenend-/Feiertag, erfolgt die Abbuchung am nächsten Werktag.\nSie sind berechtigt, begründete Einwendungen gegen einzelne in der Rechnung gestellte Forderungen\nzu erheben. Bitte wenden Sie sich gerne an uns.\nAlle Rechnungen finden Sie online zum Download in Ihrem Domain-Portfolio unter dem Menüpunkt\n\"Konto/Rechnungen\": https://www.united-domains.de\nVielen Dank für Ihren Auftrag!\nIhre united-domains GmbH\nGeschäftsführung: Schweiz MwSt: CHE-274.284.535 MWST Sitz Starnberg\nSaad Daoud Türkei MwSt: 8920484983 HRB 29 43 48, Amtsgericht München\nMichael Klemund UK MwSt: 377 8696 18\nUSt-IdNr.: DE203066334\nSt.Nr.: 117/116/71090','{\"attachment\": {\"id\": \"AAMkAGY2NThhZDJlLTdiYjYtNDNmMi04NDVkLTRmYTUzNDAzNzcyNQBGAAAAAADqXhEuhCRLS59fL0nSfO1GBwB3_k8U9iJjTp7ilr_z1JTwAAAAAAEMAAB3_k8U9iJjTp7ilr_z1JTwAANrlG8-AAABEgAQAB7NNxBRHixAjBd1hZBre4A=\", \"name\": \"rechnung_AR20250917A0089492.pdf\", \"contentType\": \"application/pdf\", \"size\": 25818}, \"amounts\": {\"net\": \"15.97\", \"vat\": \"3.19\", \"gross\": \"19.16\", \"vat_rate\": \"20\"}}','draft','2025-09-18 18:21:09.739005',NULL),
(7,'mail','AAMkAGY2NThhZDJlLTdiYjYtNDNmMi04NDVkLTRmYTUzNDAzNzcyNQBGAAAAAADqXhEuhCRLS59fL0nSfO1GBwB3_k8U9iJjTp7ilr_z1JTwAAAAAAEMAAB3_k8U9iJjTp7ilr_z1JTwAANrlG8-AAA=','AAMkAGY2NThhZDJlLTdiYjYtNDNmMi04NDVkLTRmYTUzNDAzNzcyNQBGAAAAAADqXhEuhCRLS59fL0nSfO1GBwB3_k8U9iJjTp7ilr_z1JTwAAAAAAEMAAB3_k8U9iJjTp7ilr_z1JTwAANrlG8-AAABEgAQAB7NNxBRHixAjBd1hZBre4A=','','','united-domains GmbH','','2025-09-17','EUR',15.97,NULL,3.19,19.16,'united-domains GmbH\nGautinger Str. 10\n82319 Starnberg\nSupport: +49 (0) 8151 / 36867 - 0\nE-Mail: support@united-domains.de\nBitte halten Sie bei Anrufen Ihre PIN bereit.\nSie können diese in Ihrem Portfolio festlegen.\nunited-domains GmbH · Gautinger Str. 10 · 82319 Starnberg\nAlfred Hagn\nRudolf-Waisenhorng.138-4\n1230 Wien\nÖSTERREICH\nRechnung: AR20250917A0089492\nRechnungsdatum: 17.09.2025 Fälligkeitsdatum: 18.09.2025\nKundennummer: 89492 Mandats-ID: AT0089492XX0002\nGläubiger-ID: DE30ZZZ00000004764\nDatum Artikel Preis (EUR)\n17.09.2025Registrierung interimhagn.de\n17.09.2025-16.09.2026\n19,16\n Gesamt Netto 15,97\nIm Gesamtbetrag enthaltene MwSt. 20,00 % 3,19\n Gesamt Brutto 19,16\nDas Datum der Registrierung entspricht dem Leistungszeitpunkt.\nWir ziehen den Rechnungsbetrag per SEPA-Lastschrift von ihrem Konto (IBAN:\nATXXXXXXXXXXXXXXXX2200 / BIC: BKAUATWW) zum Fälligkeitsdatum ein.\nIst das Fälligkeitsdatum ein Wochenend-/Feiertag, erfolgt die Abbuchung am nächsten Werktag.\nSie sind berechtigt, begründete Einwendungen gegen einzelne in der Rechnung gestellte Forderungen\nzu erheben. Bitte wenden Sie sich gerne an uns.\nAlle Rechnungen finden Sie online zum Download in Ihrem Domain-Portfolio unter dem Menüpunkt\n\"Konto/Rechnungen\": https://www.united-domains.de\nVielen Dank für Ihren Auftrag!\nIhre united-domains GmbH\nGeschäftsführung: Schweiz MwSt: CHE-274.284.535 MWST Sitz Starnberg\nSaad Daoud Türkei MwSt: 8920484983 HRB 29 43 48, Amtsgericht München\nMichael Klemund UK MwSt: 377 8696 18\nUSt-IdNr.: DE203066334\nSt.Nr.: 117/116/71090','{\"attachment\": {\"id\": \"AAMkAGY2NThhZDJlLTdiYjYtNDNmMi04NDVkLTRmYTUzNDAzNzcyNQBGAAAAAADqXhEuhCRLS59fL0nSfO1GBwB3_k8U9iJjTp7ilr_z1JTwAAAAAAEMAAB3_k8U9iJjTp7ilr_z1JTwAANrlG8-AAABEgAQAB7NNxBRHixAjBd1hZBre4A=\", \"name\": \"rechnung_AR20250917A0089492.pdf\", \"contentType\": \"application/pdf\", \"size\": 25818}, \"amounts\": {\"net\": \"15.97\", \"vat\": \"3.19\", \"gross\": \"19.16\", \"vat_rate\": \"20\"}}','draft','2025-09-18 18:26:55.977314',3),
(8,'mail','AAMkAGY2NThhZDJlLTdiYjYtNDNmMi04NDVkLTRmYTUzNDAzNzcyNQBGAAAAAADqXhEuhCRLS59fL0nSfO1GBwB3_k8U9iJjTp7ilr_z1JTwAAAAAAEMAAB3_k8U9iJjTp7ilr_z1JTwAANrlG8-AAA=','AAMkAGY2NThhZDJlLTdiYjYtNDNmMi04NDVkLTRmYTUzNDAzNzcyNQBGAAAAAADqXhEuhCRLS59fL0nSfO1GBwB3_k8U9iJjTp7ilr_z1JTwAAAAAAEMAAB3_k8U9iJjTp7ilr_z1JTwAANrlG8-AAABEgAQAB7NNxBRHixAjBd1hZBre4A=','','','united-domains GmbH','','2025-09-17','EUR',15.97,NULL,3.19,19.16,'united-domains GmbH\nGautinger Str. 10\n82319 Starnberg\nSupport: +49 (0) 8151 / 36867 - 0\nE-Mail: support@united-domains.de\nBitte halten Sie bei Anrufen Ihre PIN bereit.\nSie können diese in Ihrem Portfolio festlegen.\nunited-domains GmbH · Gautinger Str. 10 · 82319 Starnberg\nAlfred Hagn\nRudolf-Waisenhorng.138-4\n1230 Wien\nÖSTERREICH\nRechnung: AR20250917A0089492\nRechnungsdatum: 17.09.2025 Fälligkeitsdatum: 18.09.2025\nKundennummer: 89492 Mandats-ID: AT0089492XX0002\nGläubiger-ID: DE30ZZZ00000004764\nDatum Artikel Preis (EUR)\n17.09.2025Registrierung interimhagn.de\n17.09.2025-16.09.2026\n19,16\n Gesamt Netto 15,97\nIm Gesamtbetrag enthaltene MwSt. 20,00 % 3,19\n Gesamt Brutto 19,16\nDas Datum der Registrierung entspricht dem Leistungszeitpunkt.\nWir ziehen den Rechnungsbetrag per SEPA-Lastschrift von ihrem Konto (IBAN:\nATXXXXXXXXXXXXXXXX2200 / BIC: BKAUATWW) zum Fälligkeitsdatum ein.\nIst das Fälligkeitsdatum ein Wochenend-/Feiertag, erfolgt die Abbuchung am nächsten Werktag.\nSie sind berechtigt, begründete Einwendungen gegen einzelne in der Rechnung gestellte Forderungen\nzu erheben. Bitte wenden Sie sich gerne an uns.\nAlle Rechnungen finden Sie online zum Download in Ihrem Domain-Portfolio unter dem Menüpunkt\n\"Konto/Rechnungen\": https://www.united-domains.de\nVielen Dank für Ihren Auftrag!\nIhre united-domains GmbH\nGeschäftsführung: Schweiz MwSt: CHE-274.284.535 MWST Sitz Starnberg\nSaad Daoud Türkei MwSt: 8920484983 HRB 29 43 48, Amtsgericht München\nMichael Klemund UK MwSt: 377 8696 18\nUSt-IdNr.: DE203066334\nSt.Nr.: 117/116/71090','{\"attachment\": {\"id\": \"AAMkAGY2NThhZDJlLTdiYjYtNDNmMi04NDVkLTRmYTUzNDAzNzcyNQBGAAAAAADqXhEuhCRLS59fL0nSfO1GBwB3_k8U9iJjTp7ilr_z1JTwAAAAAAEMAAB3_k8U9iJjTp7ilr_z1JTwAANrlG8-AAABEgAQAB7NNxBRHixAjBd1hZBre4A=\", \"name\": \"rechnung_AR20250917A0089492.pdf\", \"contentType\": \"application/pdf\", \"size\": 25818}, \"amounts\": {\"net\": \"15.97\", \"vat\": \"3.19\", \"gross\": \"19.16\", \"vat_rate\": \"20\"}}','draft','2025-09-18 18:27:36.757769',3);
/*!40000 ALTER TABLE `crm_core_invoicedraft` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `django_admin_log` VALUES
(3,'2025-08-22 15:03:24.165085','4','localadmin',3,'',4,3),
(4,'2025-08-22 15:03:24.165180','2','alfred.hagn@hagninterim.de_old_2',3,'',4,3),
(5,'2025-08-22 15:03:43.198202','3','admin',2,'[{\"changed\": {\"fields\": [\"password\"]}}]',4,3),
(6,'2025-09-04 16:13:40.438107','2','[2025-09-04] 9.99 €  – Finanz',1,'[{\"added\": {}}]',21,3),
(7,'2025-09-04 16:15:23.686416','2','[2025-09-04] 9.99 €  – Finanz',3,'',21,3),
(8,'2025-09-04 16:15:23.686752','1','[2025-09-04] —  – Deine Bestellung - Finanz.at',3,'',21,3),
(9,'2025-09-04 16:16:41.147741','7','admin – Allgemein – 2025-09-02 12:19',3,'',14,3),
(10,'2025-09-04 16:16:41.147929','6','admin – Allgemein – 2025-09-02 08:15',3,'',14,3),
(11,'2025-09-04 16:16:41.148020','5','admin – Allgemein – 2025-09-01 15:25',3,'',14,3),
(12,'2025-09-04 16:16:41.148085','4','admin – Allgemein – 2025-09-01 15:19',3,'',14,3),
(13,'2025-09-04 16:16:41.148142','3','admin – Allgemein – 2025-09-01 11:05',3,'',14,3),
(14,'2025-09-04 16:16:41.148195','1','admin – Allgemein – 2025-09-01 10:51',3,'',14,3),
(15,'2025-09-04 16:16:41.148243','2','admin – Allgemein – 2025-09-01 10:00',3,'',14,3);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `django_content_type` VALUES
(16,'account','emailaddress'),
(17,'account','emailconfirmation'),
(1,'admin','logentry'),
(3,'auth','group'),
(2,'auth','permission'),
(4,'auth','user'),
(5,'contenttypes','contenttype'),
(12,'crm_core','calllog'),
(7,'crm_core','company'),
(8,'crm_core','contact'),
(9,'crm_core','documentlink'),
(10,'crm_core','emaillog'),
(21,'crm_core','expensedraft'),
(11,'crm_core','fileasset'),
(22,'crm_core','invoicedraft'),
(6,'sessions','session'),
(15,'sites','site'),
(18,'socialaccount','socialaccount'),
(19,'socialaccount','socialapp'),
(20,'socialaccount','socialtoken'),
(13,'timeclock','project'),
(14,'timeclock','timeentry');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `django_migrations` VALUES
(1,'contenttypes','0001_initial','2025-08-21 16:59:40.450137'),
(2,'auth','0001_initial','2025-08-21 16:59:41.462545'),
(3,'account','0001_initial','2025-08-21 16:59:41.765966'),
(4,'account','0002_email_max_length','2025-08-21 16:59:41.829233'),
(5,'account','0003_alter_emailaddress_create_unique_verified_email','2025-08-21 16:59:41.922626'),
(6,'account','0004_alter_emailaddress_drop_unique_email','2025-08-21 16:59:42.008057'),
(7,'account','0005_emailaddress_idx_upper_email','2025-08-21 16:59:42.033957'),
(8,'account','0006_emailaddress_lower','2025-08-21 16:59:42.058480'),
(9,'account','0007_emailaddress_idx_email','2025-08-21 16:59:42.150433'),
(10,'account','0008_emailaddress_unique_primary_email_fixup','2025-08-21 16:59:42.181708'),
(11,'account','0009_emailaddress_unique_primary_email','2025-08-21 16:59:42.208964'),
(12,'admin','0001_initial','2025-08-21 16:59:42.430735'),
(13,'admin','0002_logentry_remove_auto_add','2025-08-21 16:59:42.454219'),
(14,'admin','0003_logentry_add_action_flag_choices','2025-08-21 16:59:42.487937'),
(15,'contenttypes','0002_remove_content_type_name','2025-08-21 16:59:42.686344'),
(16,'auth','0002_alter_permission_name_max_length','2025-08-21 16:59:42.791553'),
(17,'auth','0003_alter_user_email_max_length','2025-08-21 16:59:42.859553'),
(18,'auth','0004_alter_user_username_opts','2025-08-21 16:59:42.883809'),
(19,'auth','0005_alter_user_last_login_null','2025-08-21 16:59:42.984115'),
(20,'auth','0006_require_contenttypes_0002','2025-08-21 16:59:42.988586'),
(21,'auth','0007_alter_validators_add_error_messages','2025-08-21 16:59:43.009836'),
(22,'auth','0008_alter_user_username_max_length','2025-08-21 16:59:43.093712'),
(23,'auth','0009_alter_user_last_name_max_length','2025-08-21 16:59:43.158405'),
(24,'auth','0010_alter_group_name_max_length','2025-08-21 16:59:43.229030'),
(25,'auth','0011_update_proxy_permissions','2025-08-21 16:59:43.250732'),
(26,'auth','0012_alter_user_first_name_max_length','2025-08-21 16:59:43.314443'),
(27,'crm_core','0001_initial','2025-08-21 16:59:43.779924'),
(28,'crm_core','0002_emaillog_recipient','2025-08-21 16:59:43.900875'),
(29,'crm_core','0003_rename_sent_at_emaillog_timestamp_and_more','2025-08-21 16:59:44.032352'),
(30,'crm_core','0004_fileasset','2025-08-21 16:59:44.288663'),
(31,'crm_core','0005_remove_contact_company_remove_contact_created_at_and_more','2025-08-21 16:59:44.933693'),
(32,'crm_core','0006_contact_company_contact_created_at_contact_email_and_more','2025-08-21 16:59:45.466350'),
(33,'crm_core','0007_calllog','2025-08-21 16:59:45.746308'),
(34,'sessions','0001_initial','2025-08-21 16:59:45.838811'),
(35,'sites','0001_initial','2025-08-21 16:59:45.874004'),
(36,'sites','0002_alter_domain_unique','2025-08-21 16:59:45.942451'),
(37,'socialaccount','0001_initial','2025-08-21 16:59:46.736224'),
(38,'socialaccount','0002_token_max_lengths','2025-08-21 16:59:46.926142'),
(39,'socialaccount','0003_extra_data_default_dict','2025-08-21 16:59:46.951540'),
(40,'socialaccount','0004_app_provider_id_settings','2025-08-21 16:59:47.204130'),
(41,'socialaccount','0005_socialtoken_nullable_app','2025-08-21 16:59:47.456721'),
(42,'socialaccount','0006_alter_socialaccount_extra_data','2025-08-21 16:59:47.574722'),
(43,'timeclock','0001_initial','2025-08-21 16:59:47.915415'),
(44,'timeclock','0002_timeentry_is_remote','2025-08-21 16:59:48.035642'),
(45,'timeclock','0003_alter_timeentry_options_alter_project_name_and_more','2025-09-01 10:49:28.023752'),
(46,'crm_core','0008_expensedraft','2025-09-04 16:12:03.697138'),
(47,'crm_core','0009_invoicedraft','2025-09-13 20:10:38.053833');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `django_session` VALUES
('2kd4m0alb97fo8ekp1f717509574x0nj','.eJyNVtmSozoS_Zd67upgMWX7vtlmMdiIYpEEmpioAGEXi7ApG2ygo_99BK7e4t6ZmAcCSGWmMo9OZurb0_VM85jFlJ7bU_N2beLmcH3669v3L08_ZHHbZIdTk9O4yc-nt-rQZOeU6_zr29Pj--mvP708cdvm6S9xriwFQZAl6askyuJclr481ZfzLU8PF25S5fRyvp6Po3qbj07oTBKWsRQ_Swdp8TybK_R5QdPZs7KMl_O5JAjiIX76_u8vT1NIb-31cHmbDOWnP2RJTMvDaVyIGRvFXz8D-zrpfC5fv67-SGz9afWHqyy-ZtzPPJ3LaSqJL8JMmR9ihYpSHMv0GB_TWFkejvNUiBfiQUiUlyNNFseD_DJTXhZUWcqH5VxJuNP3S1xnb82Z78EdHnpLOISr3MmtHRLdfL-x2kRSCuKbLyZDAobEirBVJdKySUKrA-L7gE66b2tpDbAyw4ayjTBBhyobfAl5NCQNkhajnywx6OjXh4Mpgty8mqd3Md1wv2UW2AXIgeDdgOgVEYIdrJa2v03vfqj1QCeE9Fy_amryf-tby688mSzFLt_UvNvq6vH0wvTeB9N_Ew38vRF-rT-eMeCayvYY8Dndenc6nG97GQi0V-QYK2Uip8O-Uli6WRbRgJhjeLmdizlRzX4feIU9vDdOYCvEF5kTrBlQUWXzN1HhzczveYx1wSzOHRig8tjT7EawoyrKnUKTQVA-Yik0njiaUZ64HVDR4XGDYDU4m3seYVCMANqP7577y21_BEov6InHzq45VbU89Md1dhvXXVR7LtZujl6vXaiv3dK7oBJ9uOWio0OGgEByKFkghdchNmaiW3VbDFNmQ0v2NP3in7IdHEAN1PQlPUX3QwF6qqEC6OwDBgi7MnF8A7mOAWJ7cLudGHU7udbcKl0HUDej8iq5ZTNQPdNcZm0Q85zYAD02RCMp3y8uvl9iGPWpuM4CpF8jRvqkAid0WkmJqG8iVPfoZJGUeU2s14ON2IZo50ug0nsM4T3hGTiovPuliHAAjATR-05EkS16OaqWMpKzyO6XIt6yKC1TYzyLCIscuzoxT2uZE4zjJ1aRb6Ujael2fSQGG6jRZQesZAmGIycKWolHurVucYXGMxgxv1ODlSPG0UAVR6UCP_8GDCkDvSCQCpX7oFQizgu7KCV70Do7gPxdylMM4foeYy-L-B_nazfKSKU3Me6UUPq5rxnhtJ3WJCYRrBwTrjMVZ6lfyclij_hZmW7ZfYwlDQGj-SS7R9gr-feLWWiK3c8GsJlJjj_jHJz43nIc2MQR3FWUx2tqWUak2bh2i6c6sgqgmncHa33kCz0JzNk-cGWA7Yafdwk2gsjXFDDQnnO3I1gbbe-JoXNWjfva03-KHzjZYw0OY23qGoB276imAMb4T9b5wWVljQJvTaVFR8Ja9Qf26oUMJid0CUSr8uCig1B88PjxyL99c24v137BXl2oTZhRCUyYuBLHitdwFFrDnlkswu7732VeSCsmEH_NEqzXyWatI9FuXV5zJASDGwJEJdTvOe58zeDnxHhv8AnWy3-SIdmqUwO-exW7ktBuYYUyoqd9HHrsf-i3LueFVy2vxEC9qTHgotV_iwHwGr_-yCeYYv6Mh4Ezz4tz43edn_n9g0wJYkPvyS8_wYiNqYlZjO8tlFBLNr90EpljxDlnbtd9IpE64XlCQYTwh53uZVRqfmKNDH2I5U8MfvPzh_wTmz9t_x4fmvj9yNPU0UBCs_k995844u764MAn99TVjKhpRtSysSU48BkgRxUc58IQBVFDVJaTYp1HBanAwG1GWxnlk-2JlBSRNpCyyt9mWlwuQapqSjD6EdgRVESGquXG0hLirV54GzH0DX0Gx9588jhWepvqSx5_WvPheuS8vFFjqm8dPXQeg64CBcBwRgw-U7BV2oXZAMPmvV9Q7IGxPeazw4ACwFFnG6gEky1q41AXCVr-rOfos5731VjPyopjd-Ln1aacUzEWWsL35nUpUmM2xsAHNRmxbSe9cn0eew6feQIJrTrxlZI89hHise8UmRpvQQzF2jhA1Ni-qMXD-hYF6xOvu9GvxM9k6mn7YuozfH56w9Rvi4j3ED7nhlLYB5FCCtjw_jLwfqnYXM7PorPHWThoPEfY2WNvKLQOqLAjanTfY72IRkxUxKJczIDkSrwfDURdV7bKLwLY7uzp4mDKDib8PD3egwEjRcltopnjCzOb6-8DKkW8JwIDzkAA786j98-SEBzJyZv4glgtc1rVyUDlUIhmGNYYSODI5xpGUIehQCzHFzHFnUnCdQj0eh8KaUkFq7Al74rLFKeIKTZuCrvQX0Y-HQxxCDkf-dlcxz2czar7Ked3DY7R3DwBMRp7Z1l7GIOrs60lIjNvj7ssReBygIqINLvzWF0ejEWDN6LD-4uAKmL45ezOu0R-9H_49Aqydcf7hQRUW3RUPoOKkp9l1lBxKRDDmu4QHoL50f1q1ccXu9bQQXtV4MoJFV12Xk1i6V6AhN3SnRfnMpkNciBsXXL7KK4X_51E6nNpCLdteaph1QZK1kb6VpG22xN9bt6qlzdR3K2a5LUtXy07l3J53hOjq-avrUWO-511q58lWGQ9Zgeywxox36GrxUnWepK4epHC7U5rZ41ZbtOzpa8t1rJ7xlopu5ThbsjTjrKPbK_WyaVss4GQ3az-2IgLDDrtGO-8Dz7xl4VCs4Xbn_SdUt3A_NzKB_OjrjLPlFwsCbfr-lLMBSOHGFIjX8j723n7-nzcysV2_bZsha0WacGbKT6v1NesFNVKbfy1EpZv93f51m2PZ2txZPd6Y65utoQiCt61pvc_Dv6wcE7vT9__AzfxXbs:1v2aLe:wzwkeGBXYcOduhxBREc08wAaIiEn7_QfnidSGzwrlWQ','2025-10-11 19:12:46.330338'),
('2zctjk3ogjuspuy3u5fud0fwoev5xfkr','.eJw1y7EOgjAQANB_uZlYEaGWmcVRR40hzXGYxtKSXmtImv67LM4vLwN7NNpqRJ9cHDnqSAx9hgtbla52CMtjuDX3DfpnhjV4JN4drH8bBxVMOmroXbK2gvWDNKKfaPxSMLOh8BdHW9yTwLAI2lZyTCymoOfIAkpVy1bW7bHr5OGkGqnO6lXKD79ENJM:1uup9n:64EMtLH3siJ_QIx_i4FCoA0yW0w0ckmxSa4SF9ZxBDM','2025-09-20 09:24:27.299704'),
('3lu9fpknprybol2adzd89ckgd6e6q345','.eJxVj8FuhDAMRP_FZ0BJSEiyt-1vVBUyjiOisqQi0Mtq_70L5cLNmpk3Gj8BifI2rz1u68jzmgjXlOf-weuYQ4Hb5xP-b7hByZRwOgmoAFe4SWuc7pQUtvHSSCt9BT9L_k2BlzfySLTkkuMe39JeQloJjwprxcrV2hqqHQVdG4_eWiWEZITXVwXHpH4rvPQH2MJFG5C-ed4NnKZdbs5hzZE57dLcL499nNSlasQyvntssG0ISnZCG8toSCrEliLGgMZztEGgkywG00UaXOS206ZzZHzL3poBXn_EXW0s:1v0KK4:DmRlphrxCz3B22XE0nIS3NR80pQkpw0tG4Lp1YcT_0k','2025-10-05 13:41:48.041783'),
('3u0qdd9nqxpge4qbhymz363suwrkdj5t','.eJxVj8FuhiAQhN-FsxpAEPDWvkbTmHVZoqm_NIK9GN-9au3B22Z2vsnMxlLEESZAjOucu5QhU2LtthfsX4M1DzTnESGPce5elIfoD8_Hxv5u1j5T2MFm1gqjG2uNcLaykgsldcG-l_gzeloO5DXiElMMp30dzxBUkjuQUEqStlRGY2nRq1I7cMZIzgUB2z8LdlXq1kRLd4E1e2g94BfN5wOm6ZSru1h1ee53qt4ew95v6hE1QBqOHONN7b0UDVfaEGgUEqDGAMGDdhSM52AF8V43AXsbqG7UMR61q8kZ3bP9F2rNdzE:1uticI:gyn_yPgHoxVr9O3RtCseBJ6HpJ68IlsMqLPat7Oqh-I','2025-09-17 08:13:18.848609'),
('4876spp7rnwqhh5ma71wue798ijj0xxs','.eJwlyUEKwyAQAMC_7FlKAk2jfqDk0kOuoch2XYtEYlBTSsW_t9C5ToUcyWNAonhsxeSChTPoCp_rOs3opoe7Wf-eJeilwp4icf49hPj0GwiwWBD0doQgYF-JDUXL5sXJO8_pP0304zDIUSmpTueuV93l3toXrXQp_A:1upUaz:B0SnL3-wAu7EWaijbCQHOVpNHBsunNb_WyaYnSQQ4_E','2025-09-05 16:26:29.410445'),
('4aks86z3bt6xtfmfv94ak8xbr8hfpqd8','.eJwlydEKwiAUANB_uc8SbrKt_IboQXoIRsjl7jYk0aGuCPHfCzqvp0KO5NAjUdxDsblg4Qy6ggmX2_A253RV60ehAT1X2FIkzr8HH1cXQMCCBUGH3XsB25PYUlzYvji5h-P0nya6aRjlsetVf5CTVCd1b-0LkGQpkA:1uqKwq:55LKFUJ02ikh70UBvmVlUAHa4CGaa_DVxAVVG_XhDMo','2025-09-08 00:20:32.076833'),
('7zvpjlei15zkyg3w9a5vdrstt4y4ipo7','eyJzb2NpYWxhY2NvdW50X3N0YXRlcyI6e319:1upCtZ:dA9dlz5LeDaKp6PTIR_wRwvZ5DLM4LFPBkZaQ03uGhM','2025-09-04 21:32:29.982841'),
('85cyb1ti06g5dybxc339skk9tsxi2jmm','.eJyNVtmSo7gS_Zd67u5gLZt-M2YxNIhik0A3blSAwMUisNvGNjAx_z4C1ywddx7uAwFIqczU0TmZ-u3leiJ1RjNCTrd-eL8O2VBeX77_9vuXlz_HsttQlf1Qk2yoT_17Vw7VqWA2__nt5fn98v1XLy9s7fDynd_I8nbL8Zz4TVK4rSB9eTlfTve6KC9sRVeTy-l6Oi7Wt3rxQSSBUzIh-yqUwvartJHJ1y0ppK-ykimbjcBxfJm9_P7fLy9rRu-3a3l5XxeKL7-M5Rlpy36ZyChdhr995vVttfmcvn7b_bIv9XPVL66q7FoxP5tiIxaFwL9ykrwpM5nwQpaJ5Jgdi0xWyuOm4LItX3K5_Hok-fZYiq-S_LolsiKWykbOmdOPS3au3ocTi8EclpPNlcmu9mr7B-T92tnbt1yQGxxar1YTS6gtEDapCQ01zLpBwFz10-eK1m3UrmxHJ2xtFEc0Jnxlkbi65DFNilZf_FS5SRa_YTxbPKitq9V_8MWe-W3PONONhvkEiCou0rDud-Mb5HUxNKVH1ME0CJl9N5zx_21vK9_YZqoC-Syo9XC13fOZuPXtROv_kM7svef-nn8-S8JnIrpLwqfiEDzIfLo7IuDIJIsZkttcLGank2mxV5p0htQzg9qt-Rpr1uREQePOH4MXuTIOeepFKgUa7Fz2xlp8t-pHnSGDs5rTCOaY9zQie9puXsBOu7T2Gl0EUSyBuZVczWUbhxJhG3cjwoPoQ2K-2T4edYpAswDo7tfvifmr3RUooyE9y51ea6LpdRIu8_S-zPvwHPhIv3vGWfVjQ81a-PDpSSSNraLEHcEBaxiCzkO-ECTBBXK0gzq4lDDY-7MuF_p5-jEbemGeQUDBq4fOckQpcmNJCgUopLM-wt7uYaRGkXF-ywRrjpJUKM2zAdqCz5D1KFp6LdvAL-ZqDA8FjTTs5iyHqKtwbNg-afkx2F_lPEllnwvSSCRjSnEQHSANDTyUaGwLvfBdoeVIQsaoGyns4zGPCgElQYMo3GcHYKEouBa9DX2O_-lyAc1bjnd1uY96_Z5yhuPOQFzOIkU8w-6cW70qMoIx_PguDe1iIS05qEdG-JmYY1UiucpRvHCiIR1_JAf7nnVwOYMF8wcxabtgnM7LeRKOnf8A5oKCieNwB1snauWU8cJtWsFlOLlRzN7tM4dEfWQoqFL2x_g6LmO4M4YMjXIi_BXXSlFxW-cEKmAkH3Nms4qzNa64t-kzf9oWB_pYcikSQEm9jj1SFLTsmwlZl91JmsFeErxQYhxc-X5jONCVI2jsCMvX0qsKC9Iyd89WHdkN0KyHh_QpDbkJR5bkRL4IkDt4JmjBnuPZnAxmMjENjRitwn_kpsHhNa67_hfoiZO7aHBetGnoIHYnT7M4sOTf26cnl2UVRoFKhO2Ik7MWzvQtSGic9_AS8XYXxNsxjvmVx5-P-I9v1W8VNWzomx_rK2ZEACsmvsCwYhpOE3t2qE1T5H_871iQkI5yOFRpjoxzvlftKDZ8pzWaVIAz4YwZrtjKam4-PqLVRg4xMhhufJWhxy3uYIX3cpSZxoRZjH_aQNE-F2b8b2O3WKiqJ_6ffgR4w3sVMA1fHQpo3vl_25jKg-XNCqP6IJ3SMb5QywAAGrs_18VpAi6sbv0S9zP3Z74GnHFiDf-WC-PC9Ynd55lpOxFrrA5p7ZA2lLL6xmpdOjNuj2njM24HLRD8Oe3iOY10_nNtn3f0lrD6mSYBXbXWDQMR2rU2ERHWq-8etwTiWyRUXXio9KxVQKHpciTEs8vRI-iwGGu2nwlKjA5GE-z5JDQNKV5qXs_03Rm3wlAY1sWZNa0jO-87MVfdGPBp82wgHWgAiiVsslqNbNa8rAGY7uztOdmdKXVQLLtmzAGUjq4JW7CuhbcsMXgMlb90kn7qxOkWncg7ds7rPgsTThnibpjFZnzniSktObAGiBce3Fa7Vj0tWma9hMOJfc5DucXPOFy26LmHRsbjMaLVEQvXgSRBCjiF85Dyyvi8-BXYma21wmlW_bK-FMwrto0-Ai0esZY-HMT4uuxPgzSt-YqdjcA0O2NN7VxNn5h2R3dicZuU6bllemw5J0pl3MRsjTWz2iW7bJz1y9Fd-tKsM1zi0V3rjCV6CNeYnbkTAYqblq1JJS_kJJfFcCIipKzWAJP1sih-eM-aKuUJOOI-WPlERGAHGoCxFryFSXBDvcp6jT0WsxrhdrjhbnC8A-PijB3PMIZCkN2ysTGMbdZCsZw2YJ-b_gT7c-vPxiWdrbFcLxfVQHjljA82zfdr7XlY2orbGp-IrJ7117-4F1IDp8JDKnvcl1AfWM3iY2GQox7GzK-JukDKJz51YpmSOUC4xT-iZieCva386bNgNXDtx1HKuXPMMNAnj_G7NPk5EYM27a1PLrLLiYGOBX8RPy52YPRUjPv88G7uJpNdx3x5580m9_q2R0oO92LDIWz3clRtt8f0p9YKIYU8OsxBTpVhJ1Jjox1_XEJofn2ocq52b3ETco2BKWwhKopWm7p883bC5uiG13pzd1A-JKEOyiAAG7sRGmUUquv49mq4wJ_U7H1b3eam4HHYF3d9ilulnuIiDfuBD85JrZ8-KJzfot3BdS3r5AyZOUOZ4eQdemWT-H437-_TRyAEYxLk9-q9aVUxo-LrJcT1tm8ixO4uZaXrlmGAn493Y8Odis3B8OppUpU539tqALf9K3_duMoHGJzdj-tbSn5ctv3-MQWvgwKr5sPbnrWf3ml_Ef3Tz_pNjzXz63n38vsfzWIkFg:1upUcs:atfP2GOTr7hPSOf5XzT7aTAckrQqdXLSy_kC-ePr0Tw','2025-09-05 16:28:26.210703'),
('8kmsxrtfepn7nliu1jlfy99w3ot6zqrr','.eJwlycEKAiEQANB_mbNEG6uL3opg6VA_ECHDOBuW6KJuF_HfC3rX16Ak8hiQKG2x2lKxcgHT4Fzmi4u35Tpn_ZpORzD3BmtOxOX3ENLTRxDgsCKYuIUgYH0TW0qO7YezXzzn_3QxTFJqqZQ67Eal1X4YH71_AaXnKZo:1upoXe:SG4tp8xfNcMA2lhYBMVbPVjPwD7_QrFkDVJevG_GJO0','2025-09-06 13:44:22.475126'),
('bzld8a5tmv8sqieubwdfjiy0iph49ol5','.eJwlyUsOwiAQANC7zJqYYlsRTuCqi26NIWQYDZFAw8doCXfXxLd9DXJEZ7xBjDUUnYsplEE1sHK97Is4pfXz3ksVoK4NthSR8u_Bx4cLwMCaYkCF6j2D7YmkMVrSL0ru7ij9pzMu5llOZy6mw8jlcBzGW-9f0mIqGA:1upmKk:giu7JAL_pScZBhfDq5AQ8B6q3-m5HjsGAUwQjnaknEs','2025-09-06 11:22:54.323588'),
('dcvx4y68el1x0wfpmeg5ehb0chvab023','.eJyNVtuSozgS_Zd6nupAYHyZN2MDhjaiEUKANjYqQFDmIrDbxjYwMf--wq7q6Y6Z3dgHApAyU5knT2bqj5eEseO17d6Sa1fkbVeypCuP7VuTd8Uxu7z8_q8_Xp7fL7-_XI6sTPiHxstvL0n38jtYqCtpNlfA4guQZSAD5beX0_l4K7P8LFSakp2Pl-P7JH4tJyNsJkurRE5e5Vxevs4WKntdsmz2qq6S1WIhSxLIk5c___3by8Olt-slP789FJWXX9bShNV5O20knE_LXz4c-_KQ-di-fFn_Epj2ofWLqSK5FMLOIlsoWSaDuTRTF3miMiAnicLek_csUVf5-yKTkiXIpVSdv7N0-Z4r85k6XzJ1peSrhZoKo4dzcireuqM4QxjMB1vKo3XplvZXArxyv7GvqaxW1LfmVsNm2Fh2gVLc8Bb2Qc23RMpOkNsFVbIzIac4b4s6MPnZGaFLTHhjuiOHRJ_sFKnJJrt-MFoAltbFag8g2wi7dYGdCpZQQjcIUBWToA-alePvsrsf6QM0KKWDkG-6E_2_5e3VFxFMkYWeONS6O9v18xmkx3uPH_9dPIr3Rvpr__lMDp-Y4kwOH7MdurPxeNsrUGKDqiShWqdKNu4blWebVRWPhLsmKp0SlHRrDXuMKmc8dC52VOoD7mKNwy1pHPGm2-BmlfcyCQ3Jqo49HAPV2Xqys9XlCey4iUu30hWI6zvcxncHxyJwMmMicAcz4OI1cHAwg_69jENYTQA6m8f3IOyVjj8BZVSsFb7zS8m2ehk9ZPlt2vfICXmhfnONk-YFhpaEPUIt0X1sjCT0RmpQm7S0Q9Fp5wyd4RLjioJecUODJyGbxQA1qS4NuZ65aEv3zi5roXEqMlM9-zXfhJgWnmJbDBjHPOj7sCl2-c6IwqoGTmuAbJdd6A4hrzmAVCIBluoZGx01loor4yeCK-jjbREwgR0BxY5IzjkBzgzXKEEKwrDOcBDCCG0uI9nZBtONIKl7mHO0dQNiJqOlxJieEq45dIRWGtkAYaKIuEoX21sS9leP2ySteQEDcJlyEYdAYHdKrVZTBMEEfqCJfTubSMt22js1-cjMvshDtUjDYOJExRrwznb2LWnIlIMJ8zszeT1hHI9MdbdMEvnv4JhxOEgSbUi9x7UaC144VS07o96LPIp3rTx8iLR7EqIiFn-Cr_20RhujE_lRI_nHuVYcZtfHnsxlGqrvqZB5FGdtXGhr86f_vM52_D75kkWQs_Kxdo9DVIvvuVU5yr5iYF_po7uZjc6juH6coaUmHWjoHXzTaNOH7upZeI0jOdVajbFd7LHNnerQwS0D8SDNYtmT9jgQe7UCx6neDB5PXGy1Sxyh5sHN4fEPkmdN9qLORmHv7gQe8EZr5lSeNMXGmsNjf18bBOrGmI4Gz2u4d4OVkRN0zcLuW9BQA48GwoLD3ucTZX99B8YGS8ZXoaN5_myq5zFWHo1tG4c9TxtUiBq5Bg0p6Eb7-5qRDUmEuGWSTtTOxdJJFAyqFssCTwVqDJCRRtbVC3uxR0-pScY9t3kcev-whiLWcIn6minyyUUP8Wlo1ESxT5kZ_A95VRP8M1O5r8VZBz8AWrD5bz6AIgnvn_HAyedPfwK5KJjg3y8yn_H9w9qew2McTVz6tAMFNt4Bh8Yp3ahY8K7-SebGTHIVOT1M9UAbfhFxYkyQ96lHTGNMlB9YB3EEz58Y_GTnl_UPbH7V_bt_hMlk-IjzQB5cBz_F_heOqXl_cCD5MQ9o7WJaub40ODKs9mEsUWx17lbv3Q3g8RgP7rYeYRMMLj586GYiTvWdKUj0u-DRXxMZjMmzV4xZ-KjdIWtQTxr1W2JSK9fRdywBycH8G8XO6JOlTNvMc7h2TgGKWQj1PcmsOCrQxP1MYBmHqhQpIj6Z31K-GmN5dX_WOCFPmY8-IzuA4qKOK6uLG29wSkmKR2cm-szohkFHxQyh2AO00u-insFDN1RPLCL8p55SfNT7NZnqvdaO8TNOiUb2KfXVmj7qmNzTqXc0n31Gfch5ZlFQWT2lLeIC627fCE5N50ToNPmY7KgG-coLd9wnPpCy2j6GAnOPa6IuJ7uUP3uSfnWm3tVmJ7p7zi5Y2WJ2rkcXex2seAN9SfQf0btw3Yv1TszMQcxExZlixPp9OtfBugSxUcNKzPYQlhMmMCTlPtQVuo1Fv4K1Y05z1QLxqI-P3lsxlTZ2A02vc2TSCE5IsDqoe3zo4Xbq4VTYrQU_DgDitWpxSfhZdAysmsyc-GS3qELYD-sBmSLWYGVi4s1Ebos80uy0QuIOdxQzqEho3ZmpQiRa3yVqIug1zkjNPkGAgjCq-0R2Bic6TnybpRF8FzNB5Ob-7Jfl-jEXchOMkbiLiJm1sFoI4gm_-oTCEF7c3UmmCkf7sC8yAs95oAKiOz3ipzo3l124AS6NHIk01PTr2R2OXvnuf9pEFd150_1DFnGDqRbErPqMVfhrP-4YiATlu_fF39-zXdOCZnfxaYmS7DUGHfda8n1d0LW19ZS2VjY4Gr92nU-RyGwLeKqfD_OFT_NiWQx2dONcYZh9L5PrmKh507QCOow2ejugYT7O5tIG-iiAvVJ1h2VG5m97bVG0l90rdhIp2Rwbq9GU8_Vy3qmrQQ7gWNJB2e0qLU9x6F1MvlxnZeatD6_R5mjpvEzn23X1VubfLvu3DZ6Lyh6a64Cj9X19rK1TuCx63_L45bhutZVpsEVZbtbQ_pp4W6kF1x6eKbVfD939pN3P8-LgL4bdmsUOr2690q_yYJ6cYRYGW_R18_Y99bav5ne_SZaL70F6rQYahEHQ-B3zbtECVfuZ-xa-LsejqlthvnFX3suf_wGCQGSU:1v2mIq:RsRO23n7UICmMHH95ydLP6ILVa8-m_EkS1HtryuPB-k','2025-10-12 07:58:40.260538'),
('dheqq2tb1gr011z7b4km2irkp9zew6ck','.eJyNVltzqzgS_i95nnOKi4nteYttIHBABBAS0taWCwQ2F4FJjI1hav77Cic5c1Izu7UPFNDqbvXl-1r64-F8YmXCE8ZOl7bfn_ukz88Pv__x528Pn7Lk0hd525cs6ctTu2_yvjhlQudffzy8fz_8_tXLg7DtH36Xl9pqsVoqqvxdWWsr8f3bQ_d2upZZ_iZMmpK9nc6nw6x-KWcnbKFI60RJvim5svq2WGrs24pli2_aOlkvl4okyXny8Oe_f3u4h7S_nPO3_d1QffgiSxNW5-28kHA-i79_BPb9rvOxfP7-9CWxzYfVF1dFci6En2W2VLNMkR-lhbbME43JSpKo7JAcskRb54dlJiUrOZdS7fHA0tUhVx8X2uOKaWs1Xy-1VDg9viVdse9PYg_hMB9tKY-fSq-0fyDZL52tfUkVraKh9Whxo_ZRPWb49poaqGUIJezZDiIziDI549QIIhcano-RHSh2Hatd5MRMjuR69lOkJpv9htFkyaC0zlZ7lLOt8FsX0K1ACaTgCuSgIii6Rc3aDZ-zIYz1ERiU0lHoN31H_299e_1dJFNk2BebWoO7e3p_Run-duD9vyeTeG-lv9bfnzngjqnuHPApew4GNp2ujgokNmpqgrU6VbPJaTSebdcVmRD3zKB0S7mkO2t0YFC507H3oKvRUOYe3HCwQ40r3nQXXa1yKBNsSFZ1uoEpWoDdURG6w1xs0pDSq3QVwKPk7YjmTk8icbRgInEXMtnb-ZpbWbIrfBAMqrmA7vb-PQp_pRvOhTIq1orY-blkO72Mw3mdX-d1H3WBj_WrZ3QbPzI2wY5jCrMYRn2fclsPjcxxd0VMJ_ctMPttohpO1GQQmrSiuhGlE7Xd2IY55CHY8S2ue5BK0Q2h4xuI_IFhexHoa86Q_Qh0V8N6n4Rx9urLaPRgYaaY3xzVIGncja7IO1Iy7OkaxhAoSdRzxiOFKR2HuEggIkMid0WmEiVRj5PISQujdZFVXKVxrSYoQ5FSVInBAW3pLRPAw2UfRMaThuvOYXVmhbuA4ga14UQvKWQKhrREU8Hd-iSTpjOtex1lUbsutdqNKgAm6ic3JLSzGbTseXOgJp-YeStyrBUpjmZMVKyRDwL816RBcw_mmg_M5PVcYzIxzdsxSfS0B1PGwShJtEG1A2uNCFy4Va24k35zYSTetXqPId4MCQ4KIv4EXm-zjDZGn-CbFis_97UIzi73NYUrFGuHVOjcyVkbZ9ra_D1-XmfPfJhjyWLAWXmXDQQHtfh-tCpXdSomO5U-edvF5N7J9XOPTWrSkWL_GJpGm95t1-_Ea1zJrZ40Au3CgTZ3q2MPdkwmo7Qgii85MBJrtQqmmW8GJzMW282ZxEFzx-Z4_5eTd07eBM8m4W9wI1_2J2vhVr4058aa433dqQ0EdGNKJ4PnNXC8aG3kKLhkuH-JGmrAyQigwLD_-cTZX9-RsYWS8UPYbPxwMfN5Iup9sO0IvvG0CQqBp0vUoIJuN3-XGdmYxAG3TNQL7pwtHcXRqG2IIuqpgg2T0URj6-Ljm1ijXWqiyeE2J9j_B1kQs4ZLNNyYop9czJCQYqNGqt1lZvQ_9LWNwJ-ZKrda7HUMI3kTbf9bDHKR4OEzHzDH_BmP4EjBBP6-6Hzm9w8yh4MTiWcsffoBojb-EWKjS7caFLirf9G5MhNdRE-PMx9ow88iTwhR4H_aIdOYEvVnrSMSg7fPGvzi54v8ozZfbf8eH2IKGj_yPKI71uVfcv-rjqk53DGQ_DwPisqDT6oXSgtX0WUHosaDgps7siClXHti3hHo30AVjaTS77YZvnNzzJrghhrtJTGplevBK5RkyYX8hUJ3CtFKoW3mu3zzlsoBYRjoDsosEhfBjO1M1IpgTYpVEb_CrylfT0RZD-8cRuhd52OOKK5MYVGTyupJ449uKUlkchdijkwejnoK64FCX6aVPgi-yndbrHUsRvyXmVF88PmSzHyuN6d5hogzTKKx3aWhVtM7T9GQzrOh-Zwj2l3PN4uCKlqXtgEXteydRmBm3icOujnGFNrEEfwlrS0hBADbkQE3XHdbJHg3-6X8feboF3eeTW3W0ef3s8mFugSgUYNKnMMYlHN-AKPSwbpKd0TMFlC7JhlcaMlk0qd5X1DZ4jx9mjzo96DiDQglMZPEPIP1TchF__RRnJOqO9cF6sN9tlZMo43dANPvXUX0WdiA6qg58HgDu3lGUxFLLVF4lAF80iwuiTiLnsnrJjNnvNhmKM4XJPAQIOrjSB4A7nykDENudl2A5Vs0bTjeHaVkorKrcsp2GwoNO_B5R1DLS1eyz6SRtBwHz1QNklDXJKKyGVeLNAYHMftFj4b32b-zfsqZKvZvxTmuonKud8gNSpRhkbe0zZHep6YhR0qvwRZF_mSYuAkW6SiLnmicTQGmNf0BqycVbO31p8_MBPX93gCJ5Ir7h-jD6Ik7Qm7KU6wGNWlnnNsGCsUlagu6b5aJnw8ItHqzfYVwWex3vgLgtzMCq2tQ7deVV6wSNLZv2Y9pGT1GOXLloorkl5fwVRmbx2jx9rb9Ifqfbk6rPGn66xlc4Cs8BY732IVsvGbT6anbui9b2aozw08rbZtJ-tnz15dnrCVj7ZxlZb1HzZW0r447OnbhHb0tv-B4GUr7RtWiE2KSH65V_eK9JitrY-9r9TYhe9EmaNvi5_XqFW3fHg9lI4bGWn0OyqC4nsdw3fQjMdcGu0Vvr3D3Avs4kQ77ffZSXtS8Ube5u55sgmRe1vQlaG0ISnGtNi4ufL4qT0m7PZnL7uXg9MWO0CKMns6vXeYp6WY7rPbWvv5WP4_jZZchC1qwyhk_t8PDn_8BBS9kFA:1v0QrW:5wU1VBMaFFbARpEN6LLtcpncx_eW_fG_fILDyGSq43o','2025-10-05 20:40:46.245300'),
('fwrcs34y9ovhln3o1n7u3hjzxq1j2gnx','.eJxVj0tuhjAMhO-SNaA8ScKuvUZVIeMYgcpPKhK6Qdy9QOmCnTUz32i8sRRxhAkQ4zrnNmXIlFiz7QX712DNA815RMhjnNsX5SGGI_Oxsb-bNc8WdrCZNcIa62suNa-Edk4oU7DvJf6MgZYDeY24xBT7M76OZwlqyT1IKCVJV2prsHQYdGk8eGsl54KA7Z8Fuya1a6KlvUDFHloH-EXzacA0nXJ1D6uuzG2n6u3x2PtNPaoGSMPRY4NVIUhRc20sgUEhART20AcwnnobODhBvDN1j53rSdXa1A6NV-St6dj-C19cdyY:1uyDlQ:tI4KI8R3EBg4yvA7qOYUsPF2yS_uw8E1UWJbFbXIOhE','2025-09-29 18:17:20.309598'),
('h86p3ygiue4z3xit27jbw7veorcvxhkt','.eJy1009z4iAYBvDvwjkTQwgg3urabG3V6vZ_dzoOA8RlgyENpLo6fvfi9LD13PTIvMP8nmd42QNnheaGC2Hbyi-d5145MNiDbJswukkgeyDqNX96BIPfe1A3VigX5sDYla5ABCT3HAyq1pgI1KVQS2GlWr6pRhdaNR-TQwQppjhlCOM4QylEjLxE4AJNZvetWGTbad7mln9BiECltj5c6olm3Su0Ua4H_rMExgSHOv2g3ozKHF5S6XdyasVu3pnq9VqdoCiGjCSYBhSe38p02uY_yomejS8fOkPVtlaVC21lwwvvjmfb-JMYWUwRIQiFGLPx2bhfr-_Hj7pd0JJ28qaExRhBSuGx6NnwepX_NavJfGXcxc2fbyv6qSFN44T1EWQ4BJhfDTfCVD9HxaRIFu6qswC14VXPW8n_ndgoRhlL0pQFu90Vz_LJ-9Gvc0bvSt3xQre1sVye6Fn4TrBPMH45HN4B_HU5pw:1uwPfy:KvsZB67UdtMFoj3WbFgqjUbFYosqrmZo0r38q1SeuHU','2025-09-24 18:36:14.435535'),
('j4bxdcsptdcyw71c12n900i9rcgoj975','eyJzb2NpYWxhY2NvdW50X3N0YXRlcyI6eyJaRkxnT2tDN0loNnFIcUdYIjpbeyJwcm9jZXNzIjoibG9naW4iLCJkYXRhIjpudWxsLCJwa2NlX2NvZGVfdmVyaWZpZXIiOm51bGx9LDE3NTU4NjA3MjQuNDA3NTk2XX19:1upPaG:Wc-tfLGOOxtkQKpnFsceFeZKXkoSFFCwEbTapGmaytI','2025-09-05 11:05:24.415928'),
('jk0da31y2hwpq4f8yc9j974bzukoh4x6','.eJxVjMsOwiAQRf-FtSFQOjxcuvcbyMAMUjU0Ke3K-O_apAvd3nPOfYmI21rj1nmJE4mzMOL0uyXMD247oDu22yzz3NZlSnJX5EG7vM7Ez8vh_h1U7PVbO3KGaNBWjeAYIesB0eSChRACF0cKvWaVwJacfGFjR7A-QzAcHCTx_gABNTie:1uy4t3:Tk7EV1StFn1fDd2PwVECORA2jgHtwJ50KtN48MP6rQQ','2025-09-29 08:48:37.064206'),
('jx98pp6qxfyszcg0u7grv3j5xrenyigc','.eJxVj0FuhTAMRO-SNaCQYJKwa69RVcg4RqDySUVCN4i7FyhdsLNm5o3Gm4iBRpyQKKxzamPCxFE0256Jfw3XNPCcRsI0hrl9cRqCPzIfm_i7RfNsEQebRFMasAYkGFtU1pUaMvG9hJ_R83IQr5GWEEN_ptfx7KBKSYcKc8XK5pUByi35KgeHzhglZcko9s9MXIvaNfLSXqAWD61D-uL5NHCaTrm4dxVX5rZj8fb46_2mHlUDxuHoMd5o71VZywoMI1CpEDX12HsEx73xEm3JsoO6p872rOsKakvgNDsDndh_ARZxdwI:1v1XMo:rVRJQp0WK7XBoADDU0i5FAlUnoVaX0HEHTyrTDhv6qA','2025-10-08 21:49:38.535328'),
('l34tf7hbd5p5r2zh0tybhqu2ni2yvtvg','.eJxVj8FuhDAMRP_FZ0AhIXGyt-1vVBUyTiKisqSC0Mtq_70L5cLNmpk3Gj-BmPM2l562Moa5JKaS8tw_QhmzX-H2-YT_G26wZk40nQRUQAVuLWqL1ji0jRNWOYMV_Cz5N_mwvJFH4iWvOe7xLe0l3EnhSFItg7R1h5pry76rtSOHKIVoA8Hrq4JjUr-tYekPUMFFG4i_w7wbNE273JzDmiNz2mtzvzz2cVKXqpHW8d2DHpX3sjWi0xhIcyuJFEeKnrQLEb0g2wYxaBN5sDEo02ljWTsVHOoBXn_m7W1O:1v1gpu:72EK8VMfyEiGq81PCIQx25pegAkggkmw2DwlD3fFaxo','2025-10-09 07:56:18.930285'),
('meawj927mszvi2qv11cuttushlzc309f','.eJyVVtmyozgS_Zf73FXBYmzTb8YshjLigpEEmpi4AQibRdiUjY2ho_99BL7V1RU9DzMPBFoyU5knT6b0x9vtkpUJS7Lscj93H7cu6fLb2-9__Pnb24-15N4V-bkrs6QrL-ePJu-KC-Uy__rj7TV--_1XK29ct3v7XVwpS0lVFUn9ulqK6-Va-u2tvV4eJc2vXKUps-vldjlO4vdyMpItJEFNpOSLlEvrL4uVkn1ZZ3TxRVETdbWSBEHMk7c___3b2-zSx_2WXz9mRfntl7U0yer8PG0kjE3LXz8d-zrLfG7fvm5-CUz71PrFVJHcCm5nRVcypZK4FBbKKk-UTJSSRM6OyZEmipofV1RI1mIupMrymKXrYy4vF8pynSmqnKsrJeVGT9ekLT66Cz-DG8wHR8ijTemVzjck-uV-69xTSanIwV7addsg7PQpdEyCgEWMwg70ICQyendrs_Al8ZkJNArrYASCoSDY7qDV97l1m-wUqZVNdg9wtEVQ2jf7fBLpdrZLEsOskKkBzFQX68Twm-c7Eg35YC36sEFxcODyTdeS_1neUb_yYAqKfX6o3bv65vUNwvzfh_O8i0f-3wo_91_f5HCbye7k8IXugj4bL4-9DIRsUOQEK3Uq03HfKIxu1SoeEfOsoHRLsSS6PezDoHLHU-eFrkIOIvNCjQEdNS7_Ex0-7LIvE2wKdnV5ghFKblUrbmUrE9hxE5deZcggjAcvrAe-xwNHi4wH7oaZCCq3d8da8Q59GWNQTQC623k8cHulOwNlVtmZ-85uZaYbZTTLsse076M28LHx8MxW86GpYUSGoAYNMS4iREVE66D2DIRpLbaZbsa4uQhpvRAz6yl4utHDutgBST34UibHEmh9SCOA2y7BzIJiYe5F805rYgWGouSV5kBMLkF5GyCD1xSKgBgOpqPWHgyqp7oJUIN2ABaXQAY1OKNzHgUNrDsrhYGTNfQR7Ezuk3oDiF6p0En0rFWpTGraPBeBwPRMUpy0oTFplC1pgI4bsYdMawP8FAE2HWQG7gGqW8SHZHRlCmM53WnFoXk-gU6qKRcxFjl2bWqfNZkTjOMnNvHBoRNps512JBYbefxFjpUixXDiRJU14jHbOY-kQVMOJsz7zGL1hHE8ZoqnZwLPfwdGysAgCKRB9T6slZjzgudUckfj6YY892Mtzz5EWp_goIj5jPP1Oa2RxuS4PpVI-utcO8b0Pu9JTCJYOaZc5lWc5o2cHfbyn9V0x_rJF54dlpXzWh_joObjpV0ZijssRrBdSN5hwTk48_3OcWAzR_Czybi_tlEURFpMe49kriOnArrde9gY4oMwkNBe7ENfBtjtPIvnbyuIfE8BYzbwGnoSbEy6fWqZApnPdec5xS-c3KkGx6k2TQNAd_B0WwCT_2fn8uKyoqEw0DJp_SRRqx9G9h5EDKZndA1Fpwng-gmhOPP485P_Ntb8WtUOFXv3oTFjlklgxsSXOFa8huPIGffMYTH2T_9cC6KsYQI5aCzFZptuNSeEpr-vzSqW0JgJ5ohmbBUttfpTOMsoB4JNjptYJLi_wwYVZKuEiWUOhJ_xdxkkOy214H9bu0OpKF74f9qR0J1sNcBr-LZngKWN_1PGUnvuN2-MWp81asP5wmwTAGRufujBOAJX3rdevplBkUndj7h_2vll_a_Yf9H9h38mGklkf8apoUxCwx7-LXaTDkkUMI7ZLZ3zCl4NvNr0QHIXMYbKPnT7ePQ7UkGee5EBHPPeDGXOC9GzDDlufJmUn7qS0qZMHenEJ855PDjXNAKtzYRpX4xnjjkS2Zk4rdULqYtFYLXvYeQ_PagydwRONJKGipsBWt0DmcUzFvwOCUWRmzNXBTLV-Dk48vjOCVbvkQx4v9HmuggQnGV-1ML_2fcnXTFt2JNi9LNumx91q1ym2vatqeZ4nOeA8Rx0-yZgE3dppN3n3vJZm_tmlttwbp25zTu10JBg4U6s1znUqicfl3mEPCiJxA-p6ctGRyNTJ7pzznl9zHYb9HlvLPp5LrE6GyZsbd6ffNHFvuRuxSKWpvh8kWC7i0Nag1IQXMnvSbV5uhWq3HCqbVtyG6i4uqvwXiB5OBa5zuCOGceE95zpng1t3m8y3nsR4_U_-VqCkTX83hPIVhgJjjknfMnT647fNwK_r2XQ2E8vDJinQ9HV6_k-yy1xjCQivPgE-khoz0CmQSJq31JDdYEFkvzMRtfcyPzBciAmKNwze4ARGfzVQA78JoAQbTErcI7tkT8gyjRkCjHomZqtHZ6Dig4T74ouE9WW7ByWzmcZp1ePmtfH6f7l74yRYnt-NEHEqlQvlrShCjyItzhCYSIzj6JAdyFJyK547NGp44-UEZikCerWc_ldYZ-FHzaFWApeb4PKH0F44nmY3wYLzvUj5Xybe3iNENf5GmiErE7n27Wl7yO6inc2xsfodEFEBv4Hyuu9kyXK3Vo3Q5yl_X5v7J1Ttivqj4trJa20Wiffe2ER3iLntgufh20qiEf6fs2dSHg_2stTqHzRVmq_f1zlEuKqE4fu_v2kVwUDlnRM7yZERy_fCKf6skqJfh8oYrZxq2rx4nzbR_L3PBENslucAL5XbpuZy7QsvA2A_vOLpA-eJZ7Ao0LScnnSlivne50j5-E-WXvRvt08NexUhTfC7ZfyGymqm4mbUAHqxwdcr7SH-e3edr4PmzX6PjrqUY9rQrPd5iyfd7a4XuOPW4MdLN3D7QmPy2XiteXR9De8PvWL9f0dP8psM95O99qCKzXXpGOTJlWnnt7-_A_1DzwA:1urFjt:2YUVAhYhAEO9jFxLoYcDflgof7gBFU1etiaN3moIaYw','2025-09-10 12:58:57.633321'),
('mwj6pomx7zvkyd5a1rly28p2jwji51q7','.eJyNVtuSozgS_Zd6nupAYHyZN2MDBiNR3CSkjY0Kbi4uwnaXsbHpmH9fgatnpnfnYR8wspRKnUydk8mPl8spqxKeZNnpeuzeL13SFZeX33_88dvLz7nk2pXFsauypKtOx_e26MpTLmz-9ePlOX75_VcvL2Jv9_I7WKjqaraU5fm3FZCU5XLx28v583Sr8uJTbGmr7PN0OR1G82s1OslmsrRK5ORVLuTl62yhZq_LLJ-9qqtktVjIkgSK5OWPf__2MkF6v16Kz_dpo_Lyy1yaZE1xHBcSzsfpb1_Avk02X8uXb-tfAtO-dv3iqkwupfCzyBdKnstgLs3URZGoGZCTRMkOySFP1FVxWORSsgSFlKrzQ5YuD4Uyn6nzZaaulGK1UFPh9OMzOZfv3UmcIRwWD1sq4nXlVvYeA69yNvY1ldWaBdbcqn2WGljGJqNsa_j5Bth-XPo06o6-CTwSlxcn5hLU_SEAmgdjrkFz1RJyGf2UqZmNfoNosACqrIt1_AD5RvhtzizRjRobGiJ8BcmW6V57f8NAVwJz1octpn4g7NvuzP5ve3v1TQRT5sQTh1o93K6fz0Oa3k44_e_oIN4b6a_15zMCPmcKHAGf8p3fZ8Pp5ihIyh6qkhC1SZV8cFqV55tVTQfMXdOvYAUqtrUeTujXcPjo3BCqLADcDTWOtriF4s220c2q-iohhmTVpzsaIuCGnuKGljwmm7a0cmtdQWGkom2mwpqKwPEsE4HDMAMobAAcIgUJH5Sgekwg3Ezjh_BXwSlRRp0dBXZ-qbKtXsXBuM5v47qHz75H9JtrnDUvMjSm-E5gGHYaUTlqceViX09a1c-2vo5jY_CI0bPjWYeRvYcgl5mEyr3c4UxhG9YCA5MVSTEdUu67QduJC1evYe1HrqHt0m0mFUc8D1q12YPchgQRJPtuaPogb9E8lcpZGkVyfsyrSGFz2oDKV5AbyQwjmYd4dyaFvvwMDHHuQG9JK6mp4hNHRldWNwOT73XQYC6yEgRDXmaPLonaFY1aTsLG1iLzvBM4gywCJJBPqtd2AW3QDEWGQqP7W9TamjXlEYjcnVPrqImoxvyBlgZ2PpI222kHZvIhM-9lQdQyJdHIiTprwSHb2QITHu9gzHmfmbwZc0yHTHVF7OL-OzTkHD0kibW4ccJGpYIXsG5kOOh3GEbi3SgThljrE-KXVPwTfL2Pc6w1uoTc1Vj-81yLkvw6rclcZkQ9pMJmEmdjXNjR5k_8vMl3vB-x5DHiWTXN9ZT4jRgLIdsl3OpzFGYS3J7uI-fd2hN41oJjuILhaYBbrXFro4atPme10cDJx584tNRkD0a8j8A0jum0tnqKs4USrNcqDe3SCW0O649O8BjQhzSjsic5gtc0bBQ0jJo0OB35etQuNPbbib9TYdBA8tTtiG0Q_noYecAbrBmsPWmMP2s_pnWnMTDSjSEdDF40yHGjlVFg_5qTTtwvM8LB8EPBc-_nE-d_jSNjE0rGXuzRvGA2an6gylT8tpTcedr6pdDRVeiiZBvtf-eM_JHEPrdM3Al9XSydIw-vr57QJYvR4MUIZzJ-CIyXdKOh0cbhNqcibyExzulGDRgxGoejE43Hu_u7jR9nLZdY8E9zapiYxpT_Lz-h4EJj6aBMSH-NZHxlm79sUkUTuAU3d9ojldk5NaOPSAJR9HOfIWKSu-G_zn1i_8KLJx6Bf8IiuNBPuUv-rLV54xII3EB6sNaTHSK4tc06GvqcVpKEQta6W0_wBA7QnJrMkJOJ94-89e-4Vd8Sk1mF7n8PJSDBkL-xEA4BXsrsmHuQa58p8GlGkO7g3KKiCY2cyE18pUSVYkXkUua3lK8GKq_6pz4wftp8aVSGgIVlQ2uro633gAIXHeBMaHRwSdSxsOlZ6AFW673IIZj2EvWcxZj_TY_llw6uyaiDRjuN-hT9QWKxfU4DtWETv3Gfjrprf2pUnew8syyZrJ7To89FLjunFVwaz4n984gxPZZKis8Yt-In5gGTzn6wQydGbMHX0S_jTz3rVzjq_pif2e5Z92GoizwbDapFjyOoGuNDBFcO0RW2pUKTqIEm7WFoATrow3guqm3Rq9aD6EcdqnmLAmm8I0Xk5C7mO1EzHqIHKXDMS6j3U92qM5W1dotMr4MybsWdS6j-UJ3w4462Y_1jAksjsfBD9K61anFJ4Cy7DKza3Bz5YndO1KvRVgsCs5Ow0kiE5IToqCp2fpAdbd2LoCLqiMDBd7jm35MoUvM2xx4_U3zkFZTsCxW9oSD-TvSzJNBViSrZyKtZGqODqKvijvpnXd0-cRcmGGLRz0XdX1hHBGg1fVj4hKCLuzvLTOG-Q-5ljtFnEakA6_Du83NTmMuObIDLYijhlplBM-uF0qtD8NOnX7OdN_ZwWcQP3K2o83XzM2aJmfbUp30cVQfvW7t08et2k3S66R1Stu9CwSmov3nK7LMLC7JNt0bfBel3Ul8KubXeu451-tvyPHxflu4uK4N6GF677WlB9uhSvVZZdZXfl7t66BZ4WK_7U-M64BJSnZ21O9TgHO-X3ZW-ov21Pl4u3DbvMmydm7ro7M33hV0fedO7r3YG9j5b4WydX9aHR4JeZ_vPk10nJ2e5SdaPx-GuD8ja1Qcwg_3DvTeWV6au9Tiufel-K1ahSW-7ddvnlw8zlZb7eKm1SIPdu74iS9Xdf642-sJOLjfN6Rot6iVd2mlv-8DmSpPc5g20wgze0mg_uwX7aPXeZWGuNEB83SWft3r9IUff49rwPq1KB9YevCJqOIAuq1zbEu_lj_8AqF8jCA:1upmLv:DipLLKVWB-Yff1G2eH8_wAyM1qqiFZI69MSDTEcwX_c','2025-09-06 11:24:07.464516'),
('o4jxgiyu3qefcj2xa38nclwe3ecyhqnj','.eJw1i7EKgzAUAP_lzaFGxVrciuDg0qlTKSE8X0toTCR5iiXk3-vS7bjjEkSPRluN6FfHKrJmitAl6IdGf-9jv9-u2zjx4R4JluCR4sFg_ds4EDBp1tC51VoBywdJoZ9IbRTMy1D4F0c7H1OBYS7YzFRAFmXbtHUtz_XlJGVVSVk-c_4BZBYwAA:1uvZyY:O9x8hWb0-kasj-sgt6iJzsVQvIwqDfIjV8HZkhXXd3g','2025-09-22 11:23:58.008361'),
('ofzt8azbu6zerg7ly1sa7dtqmmsj0d0j','eyJzb2NpYWxhY2NvdW50X3N0YXRlcyI6eyJhRWJVWW44TFFrd0RkUmo0IjpbeyJwcm9jZXNzIjoibG9naW4iLCJkYXRhIjpudWxsLCJwa2NlX2NvZGVfdmVyaWZpZXIiOm51bGx9LDE3NTU4NjMxNjguODk2MDQyM119fQ:1upQDg:I4cz20DFIDo3-6ypRc459sE1PjQ4vONEZk3L3ZHCV1g','2025-09-05 11:46:08.900943'),
('p9f9dejd4sz4khx63t6qw0l4f50f6ww6','.eJxVj8FuhiAQhN-FsxpAEPDWvkbTmHVZoqm_NIK9GN-9au3B22Z2vsnMxlLEESZAjOucu5QhU2LtthfsX4M1DzTnESGPce5elIfoD8_Hxv5u1j5T2MFm1gqjG6u0FbIyWjmhCva9xJ_R03IQrxGXmGI43et4ZqCS3IGEUpK0pTIaS4teldqBM0ZyLgjY_lmwq1G3Jlq6C6zZQ-sBv2g-HzBNp1zdvarLc79T9fbY9X5Tj6gB0nDkGG9q76VouNKGQKOQADUGCB60o2A8ByuI97oJ2NtAdaOO7ahdTc7onu2_EGV2_A:1utXqm:y2o-ge7i-1PIG4Y1bpFhyj_W06-JrlogX2bKoZLNqk8','2025-09-16 20:43:32.799357'),
('qaubr53tdq4brc3jsr07ihav3ao1kfnq','eyJzb2NpYWxhY2NvdW50X3N0YXRlcyI6eyJaY0dtSjMyeFM1VmdVZU1HIjpbeyJwcm9jZXNzIjoibG9naW4iLCJkYXRhIjpudWxsLCJwa2NlX2NvZGVfdmVyaWZpZXIiOm51bGx9LDE3NTY5Nzg1NDYuNjQ5NjAwM119fQ:1uu6Ne:vJMdf1-TJsejq5_eCdRMmPedFZ83BZ1dwTPNXnyP3nw','2025-09-18 09:35:46.655002'),
('r8534ivov9g73zcoboop2ohk4knqg7yb','.eJy10l1vgjAYBeD_0muCLW1p6900TI1sYU7ddFkMQmWEzxUE1PjfV7OLxevp9cmbJ2_OOYGqCGI_9YOg2Of1pqr9WlagfwLt60Oy9B6jxD2O3RdnBvofJ1CqIpCVzkFaRHEODBD6tQ_6-T5NDVAmgdwERSg3jVTxLpbqNzkbiFFmC0IoNSHhkPJPA0w6VVnh08LJ2qEaHsJ_AAbIZVfro16gsh748zg1MeUQIu1ZzqCNamfVpdvpscyeb-bt4lRWVyozCcICXdTRImv80aRtphGfN1_wxuq-TAs_vMKFSWyLI4i1_ua6ylaH1aKKXUvMb1OiFihk2LIuLZbIe9kOoxlN1thqVuzu_wlkUhsLRojWl-Fo6Xn1oPPojOdrfo8NCWzakCG928uIbCbLnM7HSdy959_ofiMS1LQpgVj3eD7_AOtnLJc:1ux6dD:Lp_dTqDTQK-nKb6xf3NsSegPAq303_F9nfbH4u683UA','2025-09-26 16:28:15.660261'),
('s2jtnszyubj4hm6o0kdjqxdwtu674m9x','.eJw1y7EKwjAQgOF3uTmYVomtHUUcXAUXkRKu1xJMk5C7SqH03a2D48_HvwBHdNZbxDgFaVmsEEOzwNXfbwMWlwcb585phOa5QMoRiTcHHwcXQEFnxUITJu8VpDdSi7Gj9kPZ9Y7yXwLNsk0a86hpThSYWHfZ9sK_jlk0rKqsTHWs6vpQ7_amKE15eq3rF05DN1I:1ux2Yg:-0NVBCSDfzYSyRsh35HjQRYxfksz9xIBhOf3-rlwYpU','2025-09-26 12:07:18.264177'),
('tqssb4t9d31z3iw16cj09tge8q4hap5x','eyJzb2NpYWxhY2NvdW50X3N0YXRlcyI6eyJVV1NDUnZoNGpRcVlPVlpnIjpbeyJwcm9jZXNzIjoibG9naW4iLCJkYXRhIjpudWxsLCJwa2NlX2NvZGVfdmVyaWZpZXIiOm51bGx9LDE3NTU5NTE0MDguNjI5NTYzXX19:1upnAu:lgWTSckYj9CIJk7B7jG3D5IChv0wwCRQGLu9COe6fvQ','2025-09-06 12:16:48.635263'),
('uq8qzsqsppvuw2fywaro2xpx2ppbfr9p','.eJwlycEKAiEQANB_mbNEW7mK3xC0XToUIe7sFLLiLOoWIf57Qe_6KmRG74JD5DUWm4srlMFUeM9ndTp-Bj3zJVzHEcytwpIYKf8eAj99BAGTKw5MXEMQsMxIFnki-6LkH57Sf5rolJRa9l1_2Mit1Pudurf2BdYiKiY:1upOOi:NqgpQS8HqvC0wx_r7rCRnmp-OqTyabcxrZhJCbxEvgQ','2025-09-05 09:49:24.510598'),
('x3z4ktjkdlrr3h3jlzbcfxcitxww63m5','.eJwlyVEKAiEQANC7zLcE7ZZuHqELLGyEDKOFJM6iYxDi3Qt6v69DZYqYkIhbFlcFJVSwHWrbPhmvwp5W1KuAvXXYC1Oov4fEz5hBgUdBsLmlpGB_UXDEPrh3KPERQ_nPUEdz1pfZLMYc9DLPp2m6j_EFA6Qqpw:1utvnh:u8q0hOGPHif7xsPYI3vTpSz3nH-pejiMOceEu7a2Wb4','2025-09-17 22:17:57.689246'),
('yxx9cbspibrn3402xl98oi55w2k7k659','.eJwlycEKAiEQANB_mbNE1pqL39Ah6Bgh0-xsSOYs6hYh_ntB7_oaFKGAEYlkTdWXipULuAbm9Jm3tzCOdM5Her7BXRosWYjL7yHKPSRQMGFFcGmNUcHyIPYkE_sX5zAHzv_pSltzsHpn9npjh8Fqc-39C5eRKbQ:1uszB5:EazHI76d0iMY6V21HsMYsZkjJ5576ILg13sPQokB3G0','2025-09-15 07:42:11.750549'),
('zuw7mha494rabjsxpsurkrk2nady0lsl','eyJzb2NpYWxhY2NvdW50X3N0YXRlcyI6eyJZUjlNU1ZHNUxvbEZmdlBUIjpbeyJwcm9jZXNzIjoibG9naW4iLCJkYXRhIjpudWxsLCJwa2NlX2NvZGVfdmVyaWZpZXIiOm51bGx9LDE3NTU4NjMxMTQuODY1MDYwOF19fQ:1upQCo:PR3-ZO7VzeDJAGvGqqzu2LJJYkNTDMC9FrFtsKTIYio','2025-09-05 11:45:14.871353');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `django_site`
--

DROP TABLE IF EXISTS `django_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_site_domain_a2e37b91_uniq` (`domain`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_site`
--

LOCK TABLES `django_site` WRITE;
/*!40000 ALTER TABLE `django_site` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `django_site` VALUES
(1,'mycrm.interimhagn.de','MyCRM');
/*!40000 ALTER TABLE `django_site` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `socialaccount_socialaccount`
--

DROP TABLE IF EXISTS `socialaccount_socialaccount`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `socialaccount_socialaccount` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `provider` varchar(200) NOT NULL,
  `uid` varchar(191) NOT NULL,
  `last_login` datetime(6) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `extra_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`extra_data`)),
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `socialaccount_socialaccount_provider_uid_fc810c6e_uniq` (`provider`,`uid`),
  KEY `socialaccount_socialaccount_user_id_8146e70c_fk_auth_user_id` (`user_id`),
  CONSTRAINT `socialaccount_socialaccount_user_id_8146e70c_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `socialaccount_socialaccount`
--

LOCK TABLES `socialaccount_socialaccount` WRITE;
/*!40000 ALTER TABLE `socialaccount_socialaccount` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `socialaccount_socialaccount` VALUES
(3,'microsoft','c4209a2a-2e28-475c-8cd4-59a9772001ea','2025-09-28 07:58:37.082344','2025-08-22 16:27:07.001228','{\"@odata.context\": \"https://graph.microsoft.com/v1.0/$metadata#users(businessPhones,displayName,givenName,id,jobTitle,mail,mobilePhone,officeLocation,preferredLanguage,surname,userPrincipalName,mailNickname,companyName)/$entity\", \"businessPhones\": [\"+4368181752646\"], \"displayName\": \"Alfred Hagn\", \"givenName\": \"Alfred\", \"id\": \"c4209a2a-2e28-475c-8cd4-59a9772001ea\", \"jobTitle\": \"Gesch\\u00e4ftsf\\u00fchrer\", \"mail\": \"alfred.hagn@hagninterim.de\", \"mobilePhone\": \"+4368181752646\", \"officeLocation\": null, \"preferredLanguage\": \"de-DE\", \"surname\": \"Hagn\", \"userPrincipalName\": \"alfred.hagn@hagninterim.de\", \"mailNickname\": \"alfred.hagn\", \"companyName\": \"Hagn Interim\"}',3);
/*!40000 ALTER TABLE `socialaccount_socialaccount` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `socialaccount_socialapp`
--

DROP TABLE IF EXISTS `socialaccount_socialapp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `socialaccount_socialapp` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `provider` varchar(30) NOT NULL,
  `name` varchar(40) NOT NULL,
  `client_id` varchar(191) NOT NULL,
  `secret` varchar(191) NOT NULL,
  `key` varchar(191) NOT NULL,
  `provider_id` varchar(200) NOT NULL,
  `settings` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`settings`)),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `socialaccount_socialapp`
--

LOCK TABLES `socialaccount_socialapp` WRITE;
/*!40000 ALTER TABLE `socialaccount_socialapp` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `socialaccount_socialapp` VALUES
(4,'microsoft','Microsoft','c7987493-77e7-4fed-99c8-296311156397','1SV8Q~.mcGSseDl9~U2FjP4SEQ_wvvq4i3Lf_cWc','','','{}');
/*!40000 ALTER TABLE `socialaccount_socialapp` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `socialaccount_socialapp_sites`
--

DROP TABLE IF EXISTS `socialaccount_socialapp_sites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `socialaccount_socialapp_sites` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `socialapp_id` int(11) NOT NULL,
  `site_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `socialaccount_socialapp_sites_socialapp_id_site_id_71a9a768_uniq` (`socialapp_id`,`site_id`),
  KEY `socialaccount_socialapp_sites_site_id_2579dee5_fk_django_site_id` (`site_id`),
  CONSTRAINT `socialaccount_social_socialapp_id_97fb6e7d_fk_socialacc` FOREIGN KEY (`socialapp_id`) REFERENCES `socialaccount_socialapp` (`id`),
  CONSTRAINT `socialaccount_socialapp_sites_site_id_2579dee5_fk_django_site_id` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `socialaccount_socialapp_sites`
--

LOCK TABLES `socialaccount_socialapp_sites` WRITE;
/*!40000 ALTER TABLE `socialaccount_socialapp_sites` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `socialaccount_socialapp_sites` VALUES
(4,4,1);
/*!40000 ALTER TABLE `socialaccount_socialapp_sites` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `socialaccount_socialtoken`
--

DROP TABLE IF EXISTS `socialaccount_socialtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `socialaccount_socialtoken` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `token` longtext NOT NULL,
  `token_secret` longtext NOT NULL,
  `expires_at` datetime(6) DEFAULT NULL,
  `account_id` int(11) NOT NULL,
  `app_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `socialaccount_socialtoken_app_id_account_id_fca4e0ac_uniq` (`app_id`,`account_id`),
  KEY `socialaccount_social_account_id_951f210e_fk_socialacc` (`account_id`),
  CONSTRAINT `socialaccount_social_account_id_951f210e_fk_socialacc` FOREIGN KEY (`account_id`) REFERENCES `socialaccount_socialaccount` (`id`),
  CONSTRAINT `socialaccount_social_app_id_636a42d7_fk_socialacc` FOREIGN KEY (`app_id`) REFERENCES `socialaccount_socialapp` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `socialaccount_socialtoken`
--

LOCK TABLES `socialaccount_socialtoken` WRITE;
/*!40000 ALTER TABLE `socialaccount_socialtoken` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `socialaccount_socialtoken` VALUES
(3,'eyJ0eXAiOiJKV1QiLCJub25jZSI6Imc4TF8tU3hvTDNxUklDV0dpNlJhZ3drVVpYenhkUGlrMzNOVGNvcEM2WVEiLCJhbGciOiJSUzI1NiIsIng1dCI6IkhTMjNiN0RvN1RjYVUxUm9MSHdwSXEyNFZZZyIsImtpZCI6IkhTMjNiN0RvN1RjYVUxUm9MSHdwSXEyNFZZZyJ9.eyJhdWQiOiIwMDAwMDAwMy0wMDAwLTAwMDAtYzAwMC0wMDAwMDAwMDAwMDAiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9jYzVlOGRiMi1iZDIyLTRjMzgtOTM5ZS1lOTBlNDVmMTBlZDUvIiwiaWF0IjoxNzU5MDQ2MDE2LCJuYmYiOjE3NTkwNDYwMTYsImV4cCI6MTc1OTA1MTU4NSwiYWNjdCI6MCwiYWNyIjoiMSIsImFjcnMiOlsicDEiXSwiYWlvIjoiQVpRQWEvOFpBQUFBaWxRRnVESTFzVWQzZFZJVnZtRXpHMytFOVFuRUx3OWFlaWc4Y1RmbE0yeEdORDZLMHdnNFphdG5rSklCWTZhQ3JIc1FoeUxxWmhHeHFXWjk1MnF1dHdsZHRRQmg1b0VUT0k4czM5Y0huclpVTjNSTDhUcTM5V1hHV0Mra1M4TkRaR3RTNkdTUWNXRCszVHJFcEFUakxNelRDOUVGazI3YTZpalBMZzNIbXJ1RTV3ZFZiOTJDVWxuQlJVbklhNU1sIiwiYW1yIjpbInB3ZCIsIm1mYSJdLCJhcHBfZGlzcGxheW5hbWUiOiJjcm1fcHJvamVjdCIsImFwcGlkIjoiYzc5ODc0OTMtNzdlNy00ZmVkLTk5YzgtMjk2MzExMTU2Mzk3IiwiYXBwaWRhY3IiOiIxIiwiZmFtaWx5X25hbWUiOiJIYWduIiwiZ2l2ZW5fbmFtZSI6IkFsZnJlZCIsImlkdHlwIjoidXNlciIsImlwYWRkciI6IjM3Ljc1LjEzOC4zMyIsIm5hbWUiOiJBbGZyZWQgSGFnbiIsIm9pZCI6ImM0MjA5YTJhLTJlMjgtNDc1Yy04Y2Q0LTU5YTk3NzIwMDFlYSIsInBsYXRmIjoiMyIsInB1aWQiOiIxMDAzMjAwMUQ1QzI4MjQ0IiwicmgiOiIxLkFVNEFzbzFlekNLOU9FeVRudWtPUmZFTzFRTUFBQUFBQUFBQXdBQUFBQUFBQUFCT0FKOU9BQS4iLCJzY3AiOiJDYWxlbmRhcnMuUmVhZCBDYWxlbmRhcnMuUmVhZFdyaXRlIGVtYWlsIEVXUy5BY2Nlc3NBc1VzZXIuQWxsIEZpbGVzLlJlYWQuQWxsIEZpbGVzLlJlYWRXcml0ZSBGaWxlcy5SZWFkV3JpdGUuQWxsIEZpbGVzLlJlYWRXcml0ZS5BcHBGb2xkZXIgSU1BUC5BY2Nlc3NBc1VzZXIuQWxsIE1haWwuUmVhZCBNYWlsLlJlYWQuU2hhcmVkIE1haWwuUmVhZFdyaXRlIE1haWwuUmVhZFdyaXRlLlNoYXJlZCBNYWlsLlNlbmQgTWFpbC5TZW5kLlNoYXJlZCBvcGVuaWQgcHJvZmlsZSBTTVRQLlNlbmQgVGFza3MuUmVhZCBUYXNrcy5SZWFkLlNoYXJlZCBUYXNrcy5SZWFkV3JpdGUgVGFza3MuUmVhZFdyaXRlLlNoYXJlZCBVc2VyLlJlYWQgVXNlci1NYWlsLlJlYWRXcml0ZS5BbGwiLCJzaWQiOiIwMDZkOTZjOS0yM2NjLWY0ZTItODExOC1lYzYyODkzNmUyOTgiLCJzaWduaW5fc3RhdGUiOlsia21zaSJdLCJzdWIiOiIydmRxVm5PaGZIeERqT010MTlPZTMzSV82ZndQMlBrb1RYcWNELVdIYXhRIiwidGVuYW50X3JlZ2lvbl9zY29wZSI6IkVVIiwidGlkIjoiY2M1ZThkYjItYmQyMi00YzM4LTkzOWUtZTkwZTQ1ZjEwZWQ1IiwidW5pcXVlX25hbWUiOiJhbGZyZWQuaGFnbkBoYWduaW50ZXJpbS5kZSIsInVwbiI6ImFsZnJlZC5oYWduQGhhZ25pbnRlcmltLmRlIiwidXRpIjoiaHZBNl9QWHlSVS10dkJoWS0yQlBBQSIsInZlciI6IjEuMCIsIndpZHMiOlsiNjJlOTAzOTQtNjlmNS00MjM3LTkxOTAtMDEyMTc3MTQ1ZTEwIiwiMTE0NTFkNjAtYWNiMi00NWViLWE3ZDYtNDNkMGYwMTI1YzEzIiwiYjc5ZmJmNGQtM2VmOS00Njg5LTgxNDMtNzZiMTk0ZTg1NTA5Il0sInhtc19mdGQiOiJnRjRTSWkyRG9QWU9GTVQ4cWNheXBJbjRacko3ZFhaZktGb3V0Zkw0ZGRNQmMzZGxaR1Z1WXkxa2MyMXoiLCJ4bXNfaWRyZWwiOiIxMiAxIiwieG1zX3N0Ijp7InN1YiI6IkpRWWNsOHp2Z3lRLWxhdVNreU51VEMxRlpkeG8tWC1OZXM0VmZGSk4wNzQifSwieG1zX3RjZHQiOjE2NDM1ODExMjksInhtc190ZGJyIjoiRVUifQ.SLwdHmn1mHsSZiRad-Y1tlQnVqAhZAIDQ3nk3CTXzKttSZRIndn1lbErg67SZeh8hyJXvll3cTcqiauza5emmn9GTTRCEnyRy6z460CNSRUNx3jtg8dV6_LB7hnsH-TMa0aComImB3rusrH59y2UNziZy3HHjBebTWQsGl8AdidQAg-XCoIElib6DAj_iePsL_CT6giLymuyTXAwAokIpW8hxSIQlsoAnB9GFc7iiCANJKaQD0n1uxNrZZJ-gtwpBwr6hgS7yHAcYMljvx3x9eU6arNdWUDRKC_qbQD-GqSma87qUbujyZUWUUmStcQvX7RjL4O_W-8zo5EIWeCO9Q','1.AU4Aso1ezCK9OEyTnukORfEO1ZN0mMfnd-1PmcgpYxEVY5dOAJ9OAA.AgABAwEAAABVrSpeuWamRam2jAF1XRQEAwDs_wUA9P_-h9c-XNWe-AyaTehCbiANJ6fm-5tTlMTjcRnnwgQZs809JaDla99bfbam8ZDx60uH_QFfh9s8avVCb-e6XsUU54SR_OaAq_zPPHFc7nAH8GBioNVRtIUTlhrV03hlwaLnWQqkBkTrPMA-imGq7bL-uLtqQSJEj2ZAGEHwT8pP5OfSL-xCTPL0h2PifrAP5QgPEwWwzfOqCGO6j5aA0j1okQp1S3P18eDjEUvz40OvXJlmXi7SI9JVw7Hwm1Jz_HL_x3VP4B-65UrzjNaBuwEe9_9f9eNp7Kunl46MdbrMvjaLzhcmG3Qwa2PmGeKyIDJnMkiNr9SEWNfvCWq_GdiPvyQ6qsv33gmxhhRLAqDlNgvVtHquDfaV139_oIfJyHuILJT1jEsDr-iVywKfKEXZBfw19aFMxFw_SDxmdJUGA5gwbgqR0yN8D97hnyo69Q9pAmbCVgcMYVkZ8GpCZ9Ohww3V-ZHcdZ67CUObUCHE-OG3HuPOuONSjwQhqDe0uDrJAzrSzzP-dDjTOfmkzXJAInbZZXrSqhUtAY_JH50jwuSNKLfELMXJz6fKZ965VKISieWVDCKvgtvpmkmQm2HKu-ARcdlSKxEObSnlH6zLGmZ-dNA2m43VpWUXaeNvfDXGRQyWZSwMHpw0WEo3GGuXzSeCx9Faln8AarMMQBHg-gzLklandTj2YCBDrirj08LVVwOglImFIiV7ZfN6WXyJzciVUTTUw7ZGoed_ttxSQDVhIFJIuiTc2uQSNG8AhzxcfgbW45_c94GnXGbE-r2EJBWtRaxYsoAhAnv4u29FwBg_WWKnVvOE44TBgyZQh_aSoaatZG4ptXIuyF4nZ6_4PkucupNRC6cOgGeSe8TjEkzGH80tcQI-Yac','2025-09-28 09:26:24.761272',3,4);
/*!40000 ALTER TABLE `socialaccount_socialtoken` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `timeclock_project`
--

DROP TABLE IF EXISTS `timeclock_project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `timeclock_project` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `timeclock_project_name_69393a28_uniq` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `timeclock_project`
--

LOCK TABLES `timeclock_project` WRITE;
/*!40000 ALTER TABLE `timeclock_project` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `timeclock_project` VALUES
(1,'Allgemein',1),
(2,'Test',1);
/*!40000 ALTER TABLE `timeclock_project` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `timeclock_timeentry`
--

DROP TABLE IF EXISTS `timeclock_timeentry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `timeclock_timeentry` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `start_at` datetime(6) NOT NULL,
  `end_at` datetime(6) DEFAULT NULL,
  `duration_s` int(11) DEFAULT NULL,
  `note` varchar(200) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `project_id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `is_remote` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `timeclock_timeentry_project_id_4d1be9cb_fk_timeclock_project_id` (`project_id`),
  KEY `timeclock_timeentry_user_id_b459e196_fk_auth_user_id` (`user_id`),
  CONSTRAINT `timeclock_timeentry_project_id_4d1be9cb_fk_timeclock_project_id` FOREIGN KEY (`project_id`) REFERENCES `timeclock_project` (`id`),
  CONSTRAINT `timeclock_timeentry_user_id_b459e196_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `timeclock_timeentry`
--

LOCK TABLES `timeclock_timeentry` WRITE;
/*!40000 ALTER TABLE `timeclock_timeentry` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `timeclock_timeentry` VALUES
(8,'2025-09-15 20:18:04.850428','2025-09-15 20:18:12.954656',8,'','2025-09-15 20:18:04.851690',1,3,1),
(9,'2025-09-15 20:18:35.865109','2025-09-15 20:18:43.896555',8,'Meeting','2025-09-15 20:18:35.867509',1,3,1);
/*!40000 ALTER TABLE `timeclock_timeentry` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Dumping events for database 'mycrm'
--

--
-- Dumping routines for database 'mycrm'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2025-09-29  2:30:02
