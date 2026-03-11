-- =====================================================
-- 教培管理系统 MySQL 数据库初始化脚本
-- 数据库: rachel
-- 字符集: utf8mb4
-- =====================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS `rachel` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `rachel`;

-- 临时禁用外键检查（避免删除表时报错）
SET FOREIGN_KEY_CHECKS = 0;

-- =====================================================
-- 第一部分：系统基础表
-- =====================================================

-- ---------------------------------------------------
-- 1. 用户表 (user)
-- ---------------------------------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `username` VARCHAR(20) NOT NULL COMMENT '用户名',
    `alias` VARCHAR(30) DEFAULT NULL COMMENT '姓名',
    `email` VARCHAR(255) NOT NULL COMMENT '邮箱',
    `phone` VARCHAR(20) DEFAULT NULL COMMENT '电话',
    `password` VARCHAR(128) DEFAULT NULL COMMENT '密码',
    `is_active` TINYINT(1) DEFAULT 1 COMMENT '是否激活: 0-否, 1-是',
    `is_superuser` TINYINT(1) DEFAULT 0 COMMENT '是否超级管理员: 0-否, 1-是',
    `last_login` DATETIME DEFAULT NULL COMMENT '最后登录时间',
    `dept_id` BIGINT DEFAULT NULL COMMENT '部门ID',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    UNIQUE KEY `uk_email` (`email`),
    KEY `idx_alias` (`alias`),
    KEY `idx_phone` (`phone`),
    KEY `idx_is_active` (`is_active`),
    KEY `idx_is_superuser` (`is_superuser`),
    KEY `idx_last_login` (`last_login`),
    KEY `idx_dept_id` (`dept_id`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ---------------------------------------------------
-- 2. 角色表 (role)
-- ---------------------------------------------------
DROP TABLE IF EXISTS `role`;
CREATE TABLE `role` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `name` VARCHAR(20) NOT NULL COMMENT '角色名称',
    `desc` VARCHAR(500) DEFAULT NULL COMMENT '角色描述',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_name` (`name`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表';

-- ---------------------------------------------------
-- 3. API表 (api)
-- ---------------------------------------------------
DROP TABLE IF EXISTS `api`;
CREATE TABLE `api` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `path` VARCHAR(100) NOT NULL COMMENT 'API路径',
    `method` VARCHAR(10) NOT NULL COMMENT '请求方法: GET/POST/PUT/DELETE/PATCH',
    `summary` VARCHAR(500) DEFAULT NULL COMMENT 'API简介',
    `tags` VARCHAR(100) DEFAULT NULL COMMENT 'API标签/模块',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_path` (`path`),
    KEY `idx_method` (`method`),
    KEY `idx_summary` (`summary`(100)),
    KEY `idx_tags` (`tags`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='API表';

-- ---------------------------------------------------
-- 4. 菜单表 (menu)
-- ---------------------------------------------------
DROP TABLE IF EXISTS `menu`;
CREATE TABLE `menu` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `name` VARCHAR(20) NOT NULL COMMENT '菜单名称',
    `menu_type` VARCHAR(20) DEFAULT NULL COMMENT '菜单类型: catalog-目录, menu-菜单',
    `icon` VARCHAR(100) DEFAULT NULL COMMENT '菜单图标',
    `path` VARCHAR(100) NOT NULL COMMENT '菜单路径',
    `order` INT DEFAULT 0 COMMENT '排序',
    `parent_id` BIGINT DEFAULT 0 COMMENT '父菜单ID, 0表示顶级菜单',
    `is_hidden` TINYINT(1) DEFAULT 0 COMMENT '是否隐藏: 0-否, 1-是',
    `component` VARCHAR(100) DEFAULT NULL COMMENT '组件路径',
    `keepalive` TINYINT(1) DEFAULT 1 COMMENT '是否缓存: 0-否, 1-是',
    `redirect` VARCHAR(100) DEFAULT NULL COMMENT '重定向路径',
    `remark` JSON DEFAULT NULL COMMENT '保留字段(JSON)',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_name` (`name`),
    KEY `idx_path` (`path`),
    KEY `idx_order` (`order`),
    KEY `idx_parent_id` (`parent_id`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='菜单表';

-- ---------------------------------------------------
-- 5. 部门表 (dept)
-- ---------------------------------------------------
DROP TABLE IF EXISTS `dept`;
CREATE TABLE `dept` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `name` VARCHAR(20) NOT NULL COMMENT '部门名称',
    `desc` VARCHAR(500) DEFAULT NULL COMMENT '部门描述',
    `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '是否删除: 0-否, 1-是',
    `order` INT DEFAULT 0 COMMENT '排序',
    `parent_id` BIGINT DEFAULT 0 COMMENT '父部门ID, 0表示顶级部门',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_name` (`name`),
    KEY `idx_is_deleted` (`is_deleted`),
    KEY `idx_order` (`order`),
    KEY `idx_parent_id` (`parent_id`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='部门表';

-- ---------------------------------------------------
-- 6. 部门闭包表 (dept_closure)
-- ---------------------------------------------------
DROP TABLE IF EXISTS `dept_closure`;
CREATE TABLE `dept_closure` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `ancestor` BIGINT NOT NULL COMMENT '祖先节点ID',
    `descendant` BIGINT NOT NULL COMMENT '后代节点ID',
    `level` INT DEFAULT 0 COMMENT '层级深度',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_ancestor` (`ancestor`),
    KEY `idx_descendant` (`descendant`),
    KEY `idx_level` (`level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='部门闭包表';

-- ---------------------------------------------------
-- 7. 审计日志表 (audit_log)
-- ---------------------------------------------------
DROP TABLE IF EXISTS `audit_log`;
CREATE TABLE `audit_log` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `username` VARCHAR(64) DEFAULT '' COMMENT '用户名',
    `module` VARCHAR(64) DEFAULT '' COMMENT '功能模块',
    `summary` VARCHAR(128) DEFAULT '' COMMENT '操作描述',
    `method` VARCHAR(10) DEFAULT '' COMMENT '请求方法',
    `path` VARCHAR(255) DEFAULT '' COMMENT '请求路径',
    `status` INT DEFAULT -1 COMMENT 'HTTP状态码',
    `response_time` INT DEFAULT 0 COMMENT '响应时间(毫秒)',
    `request_args` JSON DEFAULT NULL COMMENT '请求参数',
    `response_body` JSON DEFAULT NULL COMMENT '响应内容',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_username` (`username`),
    KEY `idx_module` (`module`),
    KEY `idx_summary` (`summary`),
    KEY `idx_method` (`method`),
    KEY `idx_path` (`path`),
    KEY `idx_status` (`status`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审计日志表';

-- ---------------------------------------------------
-- 8. 用户角色关联表 (user_role)
-- ---------------------------------------------------
DROP TABLE IF EXISTS `user_role`;
CREATE TABLE `user_role` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `role_id` BIGINT NOT NULL COMMENT '角色ID',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_role` (`user_id`, `role_id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_role_id` (`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户角色关联表';

-- ---------------------------------------------------
-- 9. 角色菜单关联表 (role_menu)
-- ---------------------------------------------------
DROP TABLE IF EXISTS `role_menu`;
CREATE TABLE `role_menu` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `role_id` BIGINT NOT NULL COMMENT '角色ID',
    `menu_id` BIGINT NOT NULL COMMENT '菜单ID',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_role_menu` (`role_id`, `menu_id`),
    KEY `idx_role_id` (`role_id`),
    KEY `idx_menu_id` (`menu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色菜单关联表';

-- ---------------------------------------------------
-- 10. 角色API关联表 (role_api)
-- ---------------------------------------------------
DROP TABLE IF EXISTS `role_api`;
CREATE TABLE `role_api` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `role_id` BIGINT NOT NULL COMMENT '角色ID',
    `api_id` BIGINT NOT NULL COMMENT 'API ID',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_role_api` (`role_id`, `api_id`),
    KEY `idx_role_id` (`role_id`),
    KEY `idx_api_id` (`api_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色API关联表';


-- =====================================================
-- 第二部分：教培业务表
-- =====================================================

-- ---------------------------------------------------
-- 11. 学生表 (student)
-- ---------------------------------------------------
DROP TABLE IF EXISTS `student`;
CREATE TABLE `student` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `name` VARCHAR(50) NOT NULL COMMENT '学生姓名',
    `gender` VARCHAR(10) DEFAULT NULL COMMENT '性别: 男/女',
    `birthday` DATE DEFAULT NULL COMMENT '出生日期',
    `phone` VARCHAR(20) DEFAULT NULL COMMENT '联系电话',
    `guardian` VARCHAR(50) DEFAULT NULL COMMENT '监护人姓名',
    `guardian_phone` VARCHAR(20) DEFAULT NULL COMMENT '监护人电话',
    `address` VARCHAR(200) DEFAULT NULL COMMENT '家庭住址',
    `remark` TEXT DEFAULT NULL COMMENT '备注',
    `is_active` TINYINT(1) DEFAULT 1 COMMENT '是否在读: 0-否, 1-是',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_name` (`name`),
    KEY `idx_phone` (`phone`),
    KEY `idx_guardian` (`guardian`),
    KEY `idx_is_active` (`is_active`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学生表';

-- ---------------------------------------------------
-- 12. 课程表 (course)
-- ---------------------------------------------------
DROP TABLE IF EXISTS `course`;
CREATE TABLE `course` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `name` VARCHAR(100) NOT NULL COMMENT '课程名称',
    `unit_price` DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '课时单价(元)',
    `teacher` VARCHAR(50) DEFAULT NULL COMMENT '授课老师',
    `description` TEXT DEFAULT NULL COMMENT '课程描述',
    `status` VARCHAR(20) DEFAULT 'active' COMMENT '状态: active-启用, inactive-停用',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_name` (`name`),
    KEY `idx_unit_price` (`unit_price`),
    KEY `idx_teacher` (`teacher`),
    KEY `idx_status` (`status`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程表';

-- ---------------------------------------------------
-- 13. 课程学生关联表 (course_student)
-- ---------------------------------------------------
DROP TABLE IF EXISTS `course_student`;
CREATE TABLE `course_student` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `course_id` BIGINT NOT NULL COMMENT '课程ID',
    `student_id` BIGINT NOT NULL COMMENT '学生ID',
    `enroll_date` DATE DEFAULT NULL COMMENT '报名日期',
    `discount` DECIMAL(10,2) DEFAULT 0.00 COMMENT '优惠金额',
    `status` VARCHAR(20) DEFAULT 'active' COMMENT '状态: active-在读, inactive-退课',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_course_student` (`course_id`, `student_id`),
    KEY `idx_course_id` (`course_id`),
    KEY `idx_student_id` (`student_id`),
    KEY `idx_status` (`status`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程学生关联表';

-- ---------------------------------------------------
-- 14. 上课记录表 (class_record)
-- ---------------------------------------------------
DROP TABLE IF EXISTS `class_record`;
CREATE TABLE `class_record` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `course_id` BIGINT NOT NULL COMMENT '课程ID',
    `teacher` VARCHAR(50) DEFAULT NULL COMMENT '授课老师',
    `class_date` DATE NOT NULL COMMENT '上课日期',
    `start_time` TIME DEFAULT NULL COMMENT '开始时间',
    `end_time` TIME DEFAULT NULL COMMENT '结束时间',
    `class_hours` DECIMAL(5,1) NOT NULL DEFAULT 0.0 COMMENT '课时数',
    `content` TEXT DEFAULT NULL COMMENT '上课内容',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_course_id` (`course_id`),
    KEY `idx_teacher` (`teacher`),
    KEY `idx_class_date` (`class_date`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='上课记录表';

-- ---------------------------------------------------
-- 15. 课堂考勤表 (class_attendance)
-- ---------------------------------------------------
DROP TABLE IF EXISTS `class_attendance`;
CREATE TABLE `class_attendance` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `class_record_id` BIGINT NOT NULL COMMENT '上课记录ID',
    `student_id` BIGINT NOT NULL COMMENT '学生ID',
    `actual_hours` DECIMAL(5,1) NOT NULL DEFAULT 0.0 COMMENT '实际课时',
    `leave_hours` DECIMAL(5,1) DEFAULT 0.0 COMMENT '请假课时',
    `leave_reason` VARCHAR(200) DEFAULT NULL COMMENT '请假原因',
    `fee` DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '产生费用',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_class_record_id` (`class_record_id`),
    KEY `idx_student_id` (`student_id`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课堂考勤表';

-- ---------------------------------------------------
-- 16. 费用记录表 (fee_record)
-- ---------------------------------------------------
DROP TABLE IF EXISTS `fee_record`;
CREATE TABLE `fee_record` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `student_id` BIGINT NOT NULL COMMENT '学生ID',
    `course_id` BIGINT DEFAULT NULL COMMENT '课程ID',
    `fee_type` VARCHAR(20) NOT NULL COMMENT '费用类型: class_fee-课时费, payment-缴费',
    `amount` DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '金额(正数应收,负数缴费)',
    `ref_type` VARCHAR(20) DEFAULT NULL COMMENT '关联类型: class_attendance, payment',
    `ref_id` BIGINT DEFAULT NULL COMMENT '关联记录ID',
    `remark` VARCHAR(200) DEFAULT NULL COMMENT '备注',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_student_id` (`student_id`),
    KEY `idx_course_id` (`course_id`),
    KEY `idx_fee_type` (`fee_type`),
    KEY `idx_ref_type` (`ref_type`),
    KEY `idx_ref_id` (`ref_id`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='费用记录表';

-- ---------------------------------------------------
-- 17. 缴费记录表 (payment)
-- ---------------------------------------------------
DROP TABLE IF EXISTS `payment`;
CREATE TABLE `payment` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `student_id` BIGINT NOT NULL COMMENT '学生ID',
    `amount` DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '缴费金额',
    `payment_method` VARCHAR(20) DEFAULT 'cash' COMMENT '支付方式: cash-现金, wechat-微信, alipay-支付宝, bank-银行转账',
    `payment_time` DATETIME NOT NULL COMMENT '缴费时间',
    `remark` VARCHAR(200) DEFAULT NULL COMMENT '备注',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_student_id` (`student_id`),
    KEY `idx_payment_method` (`payment_method`),
    KEY `idx_payment_time` (`payment_time`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='缴费记录表';


-- =====================================================
-- 第三部分：初始化数据
-- =====================================================

-- ---------------------------------------------------
-- 初始化管理员用户 (密码: 123456)
-- ---------------------------------------------------
INSERT INTO `user` (`username`, `alias`, `email`, `password`, `is_active`, `is_superuser`) VALUES
('admin', '管理员', 'admin@admin.com', '$argon2id$v=19$m=65536,t=3,p=4$ixFCKIVw7n0vRSjFGONcSw$lneeFgdvO/Tv2pQ6dk8snGDhHq3TsZQxn/+6TP4kUVg', 1, 1);

-- ---------------------------------------------------
-- 初始化角色
-- ---------------------------------------------------
INSERT INTO `role` (`name`, `desc`) VALUES
('管理员', '系统管理员角色'),
('普通用户', '普通用户角色');

-- ---------------------------------------------------
-- 初始化菜单
-- ---------------------------------------------------
-- 系统管理(目录)
INSERT INTO `menu` (`name`, `menu_type`, `icon`, `path`, `order`, `parent_id`, `is_hidden`, `component`, `keepalive`, `redirect`) VALUES
('系统管理', 'catalog', 'carbon:gui-management', '/system', 1, 0, 0, 'Layout', 0, '/system/user');

-- 系统管理子菜单
SET @system_parent_id = LAST_INSERT_ID();
INSERT INTO `menu` (`name`, `menu_type`, `icon`, `path`, `order`, `parent_id`, `is_hidden`, `component`, `keepalive`) VALUES
('用户管理', 'menu', 'material-symbols:person-outline-rounded', 'user', 1, @system_parent_id, 0, '/system/user', 0),
('角色管理', 'menu', 'carbon:user-role', 'role', 2, @system_parent_id, 0, '/system/role', 0),
('菜单管理', 'menu', 'material-symbols:list-alt-outline', 'menu', 3, @system_parent_id, 0, '/system/menu', 0),
('API管理', 'menu', 'ant-design:api-outlined', 'api', 4, @system_parent_id, 0, '/system/api', 0),
('部门管理', 'menu', 'mingcute:department-line', 'dept', 5, @system_parent_id, 0, '/system/dept', 0),
('审计日志', 'menu', 'ph:clipboard-text-bold', 'auditlog', 6, @system_parent_id, 0, '/system/auditlog', 0);

-- 教培管理(目录)
INSERT INTO `menu` (`name`, `menu_type`, `icon`, `path`, `order`, `parent_id`, `is_hidden`, `component`, `keepalive`, `redirect`) VALUES
('教培管理', 'catalog', 'carbon:education', '/education', 2, 0, 0, 'Layout', 0, '/education/student');

-- 教培管理子菜单
SET @education_parent_id = LAST_INSERT_ID();
INSERT INTO `menu` (`name`, `menu_type`, `icon`, `path`, `order`, `parent_id`, `is_hidden`, `component`, `keepalive`) VALUES
('学生管理', 'menu', 'carbon:user-multiple', 'student', 1, @education_parent_id, 0, '/education/student', 0),
('课程管理', 'menu', 'carbon:book', 'course', 2, @education_parent_id, 0, '/education/course', 0),
('上课记录', 'menu', 'carbon:calendar', 'class-record', 3, @education_parent_id, 0, '/education/class-record', 0),
('费用管理', 'menu', 'carbon:currency', 'fee', 4, @education_parent_id, 0, '/education/fee', 0),
('缴费记录', 'menu', 'carbon:wallet', 'payment', 5, @education_parent_id, 0, '/education/payment', 0),
('统计报表', 'menu', 'carbon:chart-bar', 'report', 6, @education_parent_id, 0, '/education/report', 0);

-- ---------------------------------------------------
-- 初始化部门
-- ---------------------------------------------------
INSERT INTO `dept` (`name`, `desc`, `order`, `parent_id`) VALUES
('总公司', '公司总部', 1, 0);

-- =====================================================
-- 完成
-- =====================================================

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;

