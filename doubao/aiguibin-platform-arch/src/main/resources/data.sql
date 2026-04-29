USE platform_config;

INSERT INTO sys_org (org_code, org_name, org_type, parent_code, parent_codes, level, sort_order, status) VALUES
('ORG001', '总部', 'HEAD', '0', '', 1, 1, 1),
('ORG002', '北京分公司', 'BRANCH', 'ORG001', 'ORG001', 2, 1, 1),
('ORG003', '上海分公司', 'BRANCH', 'ORG001', 'ORG001', 2, 2, 1);

INSERT INTO sys_dept (dept_code, dept_name, org_code, parent_code, parent_codes, sort_order, status) VALUES
('DEPT001', '技术部', 'ORG001', '0', '', 1, 1),
('DEPT002', '产品部', 'ORG001', '0', '', 2, 1),
('DEPT003', '运维部', 'ORG002', '0', '', 1, 1);

INSERT INTO sys_role (role_code, role_name, role_type, data_scope, remark, status) VALUES
('ADMIN', '超级管理员', 'system', 1, '系统超级管理员，拥有所有权限', 1),
('NORMAL', '普通用户', 'custom', 4, '普通用户，仅有基本权限', 1);

INSERT INTO sys_menu (menu_code, menu_name, parent_id, menu_type, icon, path, component, permission, sort_order, status) VALUES
('SYSTEM', '系统管理', 0, 1, 'system', '/system', NULL, NULL, 1, 1),
('SYSTEM_USER', '用户管理', 1, 2, 'user', '/system/user', 'system/user/index', 'system:user:view', 1, 1),
('SYSTEM_USER_ADD', '用户新增', 2, 3, NULL, NULL, NULL, 'system:user:add', 1, 1),
('SYSTEM_USER_EDIT', '用户编辑', 2, 3, NULL, NULL, NULL, 'system:user:edit', 2, 1),
('SYSTEM_USER_DELETE', '用户删除', 2, 3, NULL, NULL, NULL, 'system:user:delete', 3, 1),
('SYSTEM_ROLE', '角色管理', 1, 2, 'role', '/system/role', 'system/role/index', 'system:role:view', 2, 1),
('SYSTEM_ORG', '机构管理', 1, 2, 'org', '/system/org', 'system/org/index', 'system:org:view', 3, 1),
('DB_COMPARE', '数据库比对', 0, 1, 'database', '/db', NULL, NULL, 2, 1),
('DB_COMPARE_CONFIG', '数据源配置', 9, 2, 'config', '/db/config', 'db/config/index', 'db:config:view', 1, 1),
('DB_COMPARE_EXECUTE', '比对执行', 9, 2, 'execute', '/db/execute', 'db/execute/index', 'db:execute:view', 2, 1),
('DB_COMPARE_RECORD', '执行记录', 9, 2, 'record', '/db/record', 'db/record/index', 'db:record:view', 3, 1);

INSERT INTO sys_role_menu (role_id, menu_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (1, 11),
(2, 8), (2, 9), (2, 10), (2, 11);

INSERT INTO sys_user (user_no, username, password, real_name, email, phone, org_code, dept_code, status) VALUES
('EMP001', 'admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '系统管理员', 'admin@aiguibin.com', '13800138000', 'ORG001', 'DEPT001', 1),
('EMP002', 'test', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '测试用户', 'test@aiguibin.com', '13800138001', 'ORG002', 'DEPT003', 1);

INSERT INTO sys_user_org (user_id, org_code, is_default) VALUES
(1, 'ORG001', 1),
(1, 'ORG002', 0),
(2, 'ORG002', 1);

INSERT INTO sys_user_role (user_id, role_id) VALUES
(1, 1),
(2, 2);

INSERT INTO db_standard_field (column_name, column_comment, column_type, data_code, description, enabled) VALUES
('id', '主键ID', 'BIGINT', 'STD001', '主键ID，自增', 1),
('create_time', '创建时间', 'DATETIME', 'STD002', '创建时间', 1),
('update_time', '更新时间', 'DATETIME', 'STD003', '更新时间', 1),
('create_by', '创建人', 'BIGINT', 'STD004', '创建人ID', 1),
('update_by', '更新人', 'BIGINT', 'STD005', '更新人ID', 1),
('deleted', '删除标记', 'TINYINT', 'STD006', '逻辑删除标记', 1),
('status', '状态', 'TINYINT', 'STD007', '状态：0-禁用，1-启用', 1);

INSERT INTO sys_config (config_key, config_value, description) VALUES
('system.name', 'AI Guibin Platform', '系统名称'),
('system.version', '1.0.0', '系统版本'),
('file.upload.maxSize', '52428800', '文件上传最大大小（字节）');
