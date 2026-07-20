
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cretests` (
  `creep_id` int NOT NULL AUTO_INCREMENT,
  `material_id` int NOT NULL,
  `process_id` int NOT NULL,
  `creep_temp` float DEFAULT NULL,
  `creep_time` float DEFAULT NULL,
  `initial_stress` float DEFAULT NULL,
  `creep_rate` float DEFAULT NULL,
  `creep_limit` float DEFAULT NULL,
  `creep_rupture_strength` float DEFAULT NULL,
  `rupture_time` float DEFAULT NULL,
  `rupture_strength_limit` float DEFAULT NULL,
  `percentage_elongation` float DEFAULT NULL,
  `entry_time` datetime DEFAULT NULL,
  `modify_time` datetime DEFAULT NULL,
  PRIMARY KEY (`creep_id`),
  KEY `material_id` (`material_id`),
  KEY `process_id` (`process_id`),
  CONSTRAINT `cretests_ibfk_1` FOREIGN KEY (`material_id`) REFERENCES `materials` (`material_id`),
  CONSTRAINT `cretests_ibfk_2` FOREIGN KEY (`process_id`) REFERENCES `processes` (`process_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_users_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `documents` (
  `document_id` int NOT NULL AUTO_INCREMENT,
  `doc_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `doc_doi` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `doc_url` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `entry_time` datetime DEFAULT NULL,
  `modify_time` datetime DEFAULT NULL,
  PRIMARY KEY (`document_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `embrittlements` (
  `embrittlement_id` int NOT NULL AUTO_INCREMENT COMMENT '辐照脆化ID',
  `material_id` int NOT NULL COMMENT '材料ID',
  `process_id` int NOT NULL COMMENT '工艺ID',
  `irradiat_id` int NOT NULL COMMENT '辐照ID',
  `dbtt` float DEFAULT NULL COMMENT '韧脆转变温度',
  `dbtt_difference` float DEFAULT NULL COMMENT '辐照前后差值',
  `entry_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '录入时间',
  `modify_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`embrittlement_id`),
  KEY `fk_embrittlements_material_id` (`material_id`),
  KEY `fk_embrittlements_process_id` (`process_id`),
  KEY `fk_embrittlements_irradiat_id` (`irradiat_id`),
  CONSTRAINT `fk_embrittlements_irradiat_id` FOREIGN KEY (`irradiat_id`) REFERENCES `irrconditions` (`irradiat_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_embrittlements_material_id` FOREIGN KEY (`material_id`) REFERENCES `materials` (`material_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_embrittlements_process_id` FOREIGN KEY (`process_id`) REFERENCES `processes` (`process_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='辐照脆化表';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fattests` (
  `fatigue_id` int NOT NULL AUTO_INCREMENT,
  `material_id` int NOT NULL,
  `process_id` int NOT NULL,
  `fatigue_method` varchar(100) DEFAULT NULL,
  `stress_ratio` float DEFAULT NULL,
  `stress_range` float DEFAULT NULL,
  `mean_stress` float DEFAULT NULL,
  `loading_frequency` float DEFAULT NULL,
  `environment_temp` float DEFAULT NULL,
  `fatigue_life` float DEFAULT NULL,
  `fatigue_limit` float DEFAULT NULL,
  `entry_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `modify_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`fatigue_id`),
  KEY `material_id` (`material_id`),
  KEY `process_id` (`process_id`),
  CONSTRAINT `fattests_ibfk_1` FOREIGN KEY (`material_id`) REFERENCES `materials` (`material_id`),
  CONSTRAINT `fattests_ibfk_2` FOREIGN KEY (`process_id`) REFERENCES `processes` (`process_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hardenings` (
  `hardening_id` int NOT NULL AUTO_INCREMENT COMMENT '辐照硬化ID',
  `material_id` int NOT NULL COMMENT '材料ID',
  `process_id` int NOT NULL COMMENT '工艺ID',
  `irradiat_id` int NOT NULL COMMENT '辐照ID',
  `document_id` int NOT NULL COMMENT '文献ID',
  `phase_structure` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '相结构',
  `pre_hv` float DEFAULT NULL COMMENT '未辐照硬度，单位HV',
  `post_hv` float DEFAULT NULL COMMENT '辐照后硬度，单位HV',
  `delta_hv` float DEFAULT NULL COMMENT '硬度变化，单位HV',
  `entry_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '录入时间',
  `modify_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`hardening_id`),
  KEY `idx_hardening_material` (`material_id`),
  KEY `idx_hardening_process` (`process_id`),
  KEY `idx_hardening_irradiat` (`irradiat_id`),
  KEY `idx_hardening_document` (`document_id`),
  CONSTRAINT `fk_hardening_document` FOREIGN KEY (`document_id`) REFERENCES `documents` (`document_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_hardening_irradiat` FOREIGN KEY (`irradiat_id`) REFERENCES `irrconditions` (`irradiat_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_hardening_material` FOREIGN KEY (`material_id`) REFERENCES `materials` (`material_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_hardening_process` FOREIGN KEY (`process_id`) REFERENCES `processes` (`process_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='辐照硬化数据表';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `htproperties` (
  `htproperty_id` int NOT NULL AUTO_INCREMENT,
  `material_id` int NOT NULL,
  `process_id` int NOT NULL,
  `test_type` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `htproperty_temp` float DEFAULT NULL,
  `yield_strength` float DEFAULT NULL,
  `ultimate_strength` float DEFAULT NULL,
  `fracture_strain` float DEFAULT NULL,
  `entry_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `modify_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`htproperty_id`),
  KEY `material_id` (`material_id`),
  KEY `process_id` (`process_id`),
  CONSTRAINT `htproperties_ibfk_1` FOREIGN KEY (`material_id`) REFERENCES `materials` (`material_id`) ON DELETE CASCADE,
  CONSTRAINT `htproperties_ibfk_2` FOREIGN KEY (`process_id`) REFERENCES `processes` (`process_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `imptests` (
  `impact_id` int NOT NULL AUTO_INCREMENT,
  `material_id` int NOT NULL,
  `process_id` int NOT NULL,
  `impact_temp` float DEFAULT NULL,
  `impact_type` varchar(100) DEFAULT NULL,
  `impact_energy` float DEFAULT NULL,
  `absorbed_energy` float DEFAULT NULL,
  `impact_tough_value` float DEFAULT NULL,
  `fracture_type` varchar(100) DEFAULT NULL,
  `entry_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `modify_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`impact_id`),
  KEY `material_id` (`material_id`),
  KEY `process_id` (`process_id`),
  CONSTRAINT `imptests_ibfk_1` FOREIGN KEY (`material_id`) REFERENCES `materials` (`material_id`),
  CONSTRAINT `imptests_ibfk_2` FOREIGN KEY (`process_id`) REFERENCES `processes` (`process_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `irrconditions` (
  `irradiat_id` int NOT NULL AUTO_INCREMENT COMMENT '辐照ID',
  `irradiat_type` varchar(100) DEFAULT NULL COMMENT '辐照类型',
  `irradiat_energy` float DEFAULT NULL COMMENT '粒子能量',
  `irradiat_temp` float DEFAULT NULL COMMENT '辐照温度',
  `irradiat_dose` float DEFAULT NULL COMMENT '辐照剂量',
  `irradiat_fluence` varchar(100) DEFAULT NULL,
  `displac_damage` float DEFAULT NULL COMMENT '离位损伤',
  `entry_time` datetime DEFAULT NULL COMMENT '录入时间',
  `modify_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`irradiat_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='辐照条件表';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `irrcreeps` (
  `ircreep_id` int NOT NULL AUTO_INCREMENT COMMENT '辐照蠕变ID',
  `material_id` int NOT NULL COMMENT '材料ID',
  `process_id` int NOT NULL COMMENT '工艺ID',
  `irradiat_id` int NOT NULL COMMENT '辐照ID',
  `ircreep_temp` float DEFAULT NULL COMMENT '实验温度',
  `ircreep_time` float DEFAULT NULL COMMENT '实验时间',
  `irinitial_stress` float DEFAULT NULL COMMENT '初始应力',
  `ircreep_rate` float DEFAULT NULL COMMENT '稳态蠕变速率',
  `ircreep_limit` float DEFAULT NULL COMMENT '蠕变极限',
  `ircreep_rupture_strength` float DEFAULT NULL COMMENT '蠕变持久强度',
  `irrupture_time` float DEFAULT NULL COMMENT '断裂时间',
  `irrupture_strength_limit` float DEFAULT NULL COMMENT '持久强度极限',
  `irpercentage_elongation` float DEFAULT NULL COMMENT '断后伸长率',
  `entry_time` datetime DEFAULT NULL COMMENT '录入时间',
  `modify_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`ircreep_id`),
  KEY `idx_irrcreeps_material_id` (`material_id`),
  KEY `idx_irrcreeps_process_id` (`process_id`),
  KEY `idx_irrcreeps_irradiat_id` (`irradiat_id`),
  CONSTRAINT `fk_irrcreeps_irradiat_id` FOREIGN KEY (`irradiat_id`) REFERENCES `irrconditions` (`irradiat_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_irrcreeps_material_id` FOREIGN KEY (`material_id`) REFERENCES `materials` (`material_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_irrcreeps_process_id` FOREIGN KEY (`process_id`) REFERENCES `processes` (`process_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='辐照蠕变表';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `material_properties` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` double NOT NULL,
  `unit` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `material_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `material_properties_material_id_eca54722_fk_materials` (`material_id`),
  CONSTRAINT `material_properties_material_id_eca54722_fk_materials` FOREIGN KEY (`material_id`) REFERENCES `materials` (`material_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `materials` (
  `material_id` int NOT NULL AUTO_INCREMENT,
  `material_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `composition_al` double NOT NULL,
  `composition_c` double NOT NULL,
  `composition_co` double NOT NULL,
  `composition_cr` double NOT NULL,
  `composition_cu` double NOT NULL,
  `composition_fe` double NOT NULL,
  `composition_hf` double NOT NULL,
  `composition_mg` double NOT NULL,
  `composition_mn` double NOT NULL,
  `composition_mo` double NOT NULL,
  `composition_n` double NOT NULL,
  `composition_nb` double NOT NULL,
  `composition_ni` double NOT NULL,
  `composition_sc` double NOT NULL,
  `composition_si` double NOT NULL,
  `composition_sn` double NOT NULL,
  `composition_ta` double NOT NULL,
  `composition_ti` double NOT NULL,
  `composition_v` double NOT NULL,
  `composition_w` double NOT NULL,
  `composition_y` double NOT NULL,
  `composition_zn` double NOT NULL,
  `composition_zr` double NOT NULL,
  `entry_time` datetime(6) NOT NULL,
  `modify_time` datetime(6) NOT NULL,
  PRIMARY KEY (`material_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `microstructures` (
  `microstructure_id` int NOT NULL AUTO_INCREMENT,
  `material_id` int NOT NULL,
  `process_id` int NOT NULL,
  `irradiat_id` int NOT NULL,
  `he_bubble_diam` float DEFAULT NULL,
  `he_bubble_dens` float DEFAULT NULL,
  `swelling_rate` float DEFAULT NULL,
  `irradiat_hard` float DEFAULT NULL,
  `entry_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `modify_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`microstructure_id`),
  KEY `material_id` (`material_id`),
  KEY `process_id` (`process_id`),
  KEY `irradiat_id` (`irradiat_id`),
  CONSTRAINT `microstructures_ibfk_1` FOREIGN KEY (`material_id`) REFERENCES `materials` (`material_id`),
  CONSTRAINT `microstructures_ibfk_2` FOREIGN KEY (`process_id`) REFERENCES `processes` (`process_id`),
  CONSTRAINT `microstructures_ibfk_3` FOREIGN KEY (`irradiat_id`) REFERENCES `irrconditions` (`irradiat_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prediction_records` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `prediction_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'hv',
  `input_data` json NOT NULL,
  `output_data` json NOT NULL,
  `created_by_id` int NOT NULL,
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (`id`),
  KEY `idx_prediction_records_created_by_id` (`created_by_id`),
  KEY `idx_prediction_records_created_at` (`created_at`),
  CONSTRAINT `fk_prediction_records_user` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `processes` (
  `process_id` int NOT NULL AUTO_INCREMENT,
  `fabrication` varchar(100) NOT NULL COMMENT '制备工艺',
  `homogenization` tinyint(1) DEFAULT '0' COMMENT '均匀化处理',
  `homogenize_temp` float DEFAULT NULL COMMENT '均匀化温度',
  `homogenize_time` float DEFAULT NULL COMMENT '均匀化时间',
  `normalization` tinyint(1) DEFAULT '0' COMMENT '正火处理',
  `normalize_temp` float DEFAULT NULL COMMENT '正火温度',
  `normalize_time` float DEFAULT NULL COMMENT '正火时间',
  `annealing` tinyint(1) DEFAULT '0' COMMENT '退火处理',
  `annealing_temp` float DEFAULT NULL COMMENT '退火温度',
  `annealing_time` float DEFAULT NULL COMMENT '退火时间',
  `tempering` tinyint(1) DEFAULT '0' COMMENT '回火处理',
  `tempering_temp` float DEFAULT NULL COMMENT '回火温度',
  `tempering_time` float DEFAULT NULL COMMENT '回火时间',
  `quenching` tinyint(1) DEFAULT '0' COMMENT '淬火处理',
  `quenching_type` varchar(100) DEFAULT NULL COMMENT '淬火类型',
  `quenching_temp` float DEFAULT NULL COMMENT '淬火温度',
  `rolling` tinyint(1) DEFAULT '0' COMMENT '轧制处理',
  `rolling_temp` float DEFAULT NULL COMMENT '轧制温度',
  `reduction` float DEFAULT NULL COMMENT '压下量',
  `entry_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '录入时间',
  `modify_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`process_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='工艺表';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rtproperties` (
  `rtproperty_id` int NOT NULL AUTO_INCREMENT,
  `material_id` int NOT NULL,
  `process_id` int NOT NULL,
  `phase_structure` varchar(100) DEFAULT NULL,
  `hardness_value` float DEFAULT NULL,
  `yield_strength_c` float DEFAULT NULL,
  `yield_strength_t` float DEFAULT NULL,
  `ultimate_strength_c` float DEFAULT NULL,
  `ultimate_strength_t` float DEFAULT NULL,
  `fracture_strain_c` float DEFAULT NULL,
  `fracture_strain_t` float DEFAULT NULL,
  `entry_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `modify_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`rtproperty_id`),
  KEY `material_id` (`material_id`),
  KEY `process_id` (`process_id`),
  CONSTRAINT `rtproperties_ibfk_1` FOREIGN KEY (`material_id`) REFERENCES `materials` (`material_id`) ON DELETE CASCADE,
  CONSTRAINT `rtproperties_ibfk_2` FOREIGN KEY (`process_id`) REFERENCES `processes` (`process_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `register_time` datetime(6) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_groups_user_id_group_id_fc7788e8_uniq` (`user_id`,`group_id`),
  KEY `users_groups_group_id_2f3517aa_fk_auth_group_id` (`group_id`),
  CONSTRAINT `users_groups_group_id_2f3517aa_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `users_groups_user_id_f500bee5_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_user_permissions_user_id_permission_id_3b86cbdf_uniq` (`user_id`,`permission_id`),
  KEY `users_user_permissio_permission_id_6d08dcd2_fk_auth_perm` (`permission_id`),
  CONSTRAINT `users_user_permissio_permission_id_6d08dcd2_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `users_user_permissions_user_id_92473840_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

