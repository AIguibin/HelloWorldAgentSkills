CREATE DATABASE IF NOT EXISTS platform_config DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE platform_config;

CREATE TABLE IF NOT EXISTS sys_user (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    user_no VARCHAR(50) NOT NULL COMMENT '用户编号',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    password VARCHAR(100) NOT NULL COMMENT '密码',
    real_name VARCHAR(50) COMMENT '真实姓名',
    email VARCHAR(100) COMMENT '邮箱',
    phone VARCHAR(20) COMMENT '手机号',
    avatar VARCHAR(200) COMMENT '头像URL',
    org_code VARCHAR(50) COMMENT '默认机构编码',
    dept_code VARCHAR(50) COMMENT '默认部门编码',
    is_locked TINYINT NOT NULL DEFAULT 0 COMMENT '锁定状态',
    lock_reason VARCHAR(200) COMMENT '锁定原因',
    last_login_time DATETIME COMMENT '最后登录时间',
    last_login_ip VARCHAR(50) COMMENT '最后登录IP',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '状态',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    create_by BIGINT COMMENT '创建人',
    update_by BIGINT COMMENT '更新人',
    deleted TINYINT NOT NULL DEFAULT 0 COMMENT '删除标记',
    UNIQUE KEY uk_user_no (user_no),
    UNIQUE KEY uk_username (username),
    INDEX idx_org_code (org_code),
    INDEX idx_dept_code (dept_code),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

CREATE TABLE IF NOT EXISTS sys_user_org (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    org_code VARCHAR(50) NOT NULL COMMENT '机构编码',
    is_default TINYINT NOT NULL DEFAULT 0 COMMENT '是否默认机构',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY uk_user_org (user_id, org_code),
    INDEX idx_user_id (user_id),
    INDEX idx_org_code (org_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户机构关联表';

CREATE TABLE IF NOT EXISTS sys_org (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    org_code VARCHAR(50) NOT NULL COMMENT '机构编码',
    org_name VARCHAR(100) NOT NULL COMMENT '机构名称',
    org_type VARCHAR(20) COMMENT '机构类型',
    parent_code VARCHAR(50) NOT NULL DEFAULT '0' COMMENT '父机构编码',
    parent_codes VARCHAR(500) COMMENT '所有父机构编码',
    level INT NOT NULL DEFAULT 1 COMMENT '层级',
    sort_order INT NOT NULL DEFAULT 0 COMMENT '排序',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '状态',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    create_by BIGINT COMMENT '创建人',
    update_by BIGINT COMMENT '更新人',
    deleted TINYINT NOT NULL DEFAULT 0 COMMENT '删除标记',
    UNIQUE KEY uk_org_code (org_code),
    INDEX idx_parent_code (parent_code),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='机构表';

CREATE TABLE IF NOT EXISTS sys_dept (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    dept_code VARCHAR(50) NOT NULL COMMENT '部门编码',
    dept_name VARCHAR(100) NOT NULL COMMENT '部门名称',
    org_code VARCHAR(50) NOT NULL COMMENT '所属机构编码',
    parent_code VARCHAR(50) NOT NULL DEFAULT '0' COMMENT '父部门编码',
    parent_codes VARCHAR(500) COMMENT '所有父部门编码',
    manager_id BIGINT COMMENT '部门负责人ID',
    sort_order INT NOT NULL DEFAULT 0 COMMENT '排序',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '状态',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    create_by BIGINT COMMENT '创建人',
    update_by BIGINT COMMENT '更新人',
    deleted TINYINT NOT NULL DEFAULT 0 COMMENT '删除标记',
    UNIQUE KEY uk_dept_code (dept_code),
    INDEX idx_org_code (org_code),
    INDEX idx_parent_code (parent_code),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='部门表';

CREATE TABLE IF NOT EXISTS sys_role (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    role_code VARCHAR(50) NOT NULL COMMENT '角色编码',
    role_name VARCHAR(100) NOT NULL COMMENT '角色名称',
    role_type VARCHAR(20) NOT NULL DEFAULT 'custom' COMMENT '角色类型',
    data_scope TINYINT NOT NULL DEFAULT 1 COMMENT '数据范围',
    remark VARCHAR(200) COMMENT '备注',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '状态',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    create_by BIGINT COMMENT '创建人',
    update_by BIGINT COMMENT '更新人',
    deleted TINYINT NOT NULL DEFAULT 0 COMMENT '删除标记',
    UNIQUE KEY uk_role_code (role_code),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表';

CREATE TABLE IF NOT EXISTS sys_user_role (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    role_id BIGINT NOT NULL COMMENT '角色ID',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY uk_user_role (user_id, role_id),
    INDEX idx_role_id (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色关联表';

CREATE TABLE IF NOT EXISTS sys_menu (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    menu_code VARCHAR(50) NOT NULL COMMENT '菜单编码',
    menu_name VARCHAR(100) NOT NULL COMMENT '菜单名称',
    parent_id BIGINT NOT NULL DEFAULT 0 COMMENT '父菜单ID',
    menu_type TINYINT COMMENT '菜单类型',
    icon VARCHAR(50) COMMENT '图标',
    path VARCHAR(200) COMMENT '路由路径',
    component VARCHAR(200) COMMENT '组件路径',
    permission VARCHAR(100) COMMENT '权限标识',
    sort_order INT NOT NULL DEFAULT 0 COMMENT '排序',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '状态',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    create_by BIGINT COMMENT '创建人',
    update_by BIGINT COMMENT '更新人',
    deleted TINYINT NOT NULL DEFAULT 0 COMMENT '删除标记',
    UNIQUE KEY uk_menu_code (menu_code),
    INDEX idx_parent_id (parent_id),
    INDEX idx_menu_type (menu_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='菜单表';

CREATE TABLE IF NOT EXISTS sys_role_menu (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    role_id BIGINT NOT NULL COMMENT '角色ID',
    menu_id BIGINT NOT NULL COMMENT '菜单ID',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY uk_role_menu (role_id, menu_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色菜单关联表';

CREATE TABLE IF NOT EXISTS sys_oper_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    oper_type VARCHAR(50) COMMENT '操作类型',
    title VARCHAR(100) COMMENT '操作模块',
    method VARCHAR(200) COMMENT '请求方法',
    request_url VARCHAR(500) COMMENT '请求URL',
    request_method VARCHAR(10) COMMENT '请求方式',
    request_params TEXT COMMENT '请求参数',
    response_data TEXT COMMENT '响应数据',
    user_id BIGINT COMMENT '操作用户ID',
    username VARCHAR(50) COMMENT '操作用户名',
    org_code VARCHAR(50) COMMENT '操作机构',
    oper_ip VARCHAR(50) COMMENT '操作IP',
    oper_location VARCHAR(100) COMMENT '操作地点',
    status TINYINT COMMENT '操作状态',
    error_msg TEXT COMMENT '错误信息',
    oper_time DATETIME COMMENT '操作时间',
    cost_time BIGINT COMMENT '耗时(毫秒)',
    INDEX idx_user_id (user_id),
    INDEX idx_oper_time (oper_time),
    INDEX idx_oper_type (oper_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';

CREATE TABLE IF NOT EXISTS sys_login_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    user_id BIGINT COMMENT '用户ID',
    username VARCHAR(50) COMMENT '用户名',
    login_type VARCHAR(20) COMMENT '登录类型',
    login_ip VARCHAR(50) COMMENT '登录IP',
    login_location VARCHAR(100) COMMENT '登录地点',
    user_agent VARCHAR(500) COMMENT '浏览器UA',
    login_status TINYINT COMMENT '登录状态',
    fail_reason VARCHAR(200) COMMENT '失败原因',
    login_time DATETIME COMMENT '登录时间',
    INDEX idx_user_id (user_id),
    INDEX idx_login_time (login_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='登录日志表';

CREATE TABLE IF NOT EXISTS db_datasource_config (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    env VARCHAR(10) NOT NULL COMMENT '环境',
    ds_key VARCHAR(50) NOT NULL COMMENT '数据源标识',
    ds_name VARCHAR(100) NOT NULL COMMENT '数据源名称',
    db_name VARCHAR(100) NOT NULL COMMENT '数据库名',
    db_type VARCHAR(20) NOT NULL DEFAULT 'mysql' COMMENT '数据库类型',
    host VARCHAR(100) NOT NULL COMMENT '主机',
    port INT NOT NULL DEFAULT 3306 COMMENT '端口',
    username VARCHAR(100) NOT NULL COMMENT '用户名',
    password VARCHAR(200) NOT NULL COMMENT '密码',
    connection_params VARCHAR(500) COMMENT '连接参数',
    enabled TINYINT NOT NULL DEFAULT 1 COMMENT '是否启用',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_ds_key (ds_key),
    INDEX idx_env (env)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据源配置表';

CREATE TABLE IF NOT EXISTS db_svn_config (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    config_name VARCHAR(50) NOT NULL DEFAULT 'default' COMMENT '配置名称',
    svn_url VARCHAR(500) NOT NULL COMMENT 'SVN仓库地址',
    username VARCHAR(100) NOT NULL COMMENT '用户名',
    password VARCHAR(200) NOT NULL COMMENT '密码',
    work_copy_path VARCHAR(500) NOT NULL COMMENT '工作副本路径',
    doc_relative_path VARCHAR(200) NOT NULL DEFAULT 'docs' COMMENT '文档相对路径',
    result_relative_path VARCHAR(200) NOT NULL DEFAULT 'results' COMMENT '结果相对路径',
    enabled TINYINT NOT NULL DEFAULT 1 COMMENT '是否启用',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='SVN配置表';

CREATE TABLE IF NOT EXISTS db_feiQ_config (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    config_name VARCHAR(50) NOT NULL DEFAULT 'default' COMMENT '配置名称',
    server_url VARCHAR(200) NOT NULL COMMENT '服务器地址',
    server_port INT NOT NULL DEFAULT 8080 COMMENT '服务器端口',
    receivers VARCHAR(500) NOT NULL COMMENT '接收人列表',
    enabled TINYINT NOT NULL DEFAULT 1 COMMENT '是否启用',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='飞秋配置表';

CREATE TABLE IF NOT EXISTS db_schedule_config (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    env VARCHAR(10) NOT NULL COMMENT '环境',
    job_name VARCHAR(50) NOT NULL COMMENT '任务名称',
    job_description VARCHAR(200) COMMENT '任务描述',
    cron_expression VARCHAR(50) NOT NULL COMMENT 'Cron表达式',
    enabled TINYINT NOT NULL DEFAULT 1 COMMENT '是否启用',
    last_run_time DATETIME COMMENT '上次执行时间',
    next_run_time DATETIME COMMENT '下次执行时间',
    run_count INT NOT NULL DEFAULT 0 COMMENT '执行次数',
    success_count INT NOT NULL DEFAULT 0 COMMENT '成功次数',
    fail_count INT NOT NULL DEFAULT 0 COMMENT '失败次数',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_env (env)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='定时任务配置表';

CREATE TABLE IF NOT EXISTS db_execute_record (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    record_no VARCHAR(32) NOT NULL COMMENT '记录编号',
    env VARCHAR(10) NOT NULL COMMENT '环境',
    ds_key VARCHAR(50) NOT NULL COMMENT '数据源标识',
    db_name VARCHAR(100) NOT NULL COMMENT '数据库名',
    trigger_type VARCHAR(20) NOT NULL COMMENT '触发类型',
    trigger_by BIGINT COMMENT '触发人ID',
    start_time DATETIME NOT NULL COMMENT '开始时间',
    end_time DATETIME COMMENT '结束时间',
    duration_ms BIGINT COMMENT '执行时长(毫秒)',
    status VARCHAR(20) NOT NULL COMMENT '状态',
    table_diff_count INT NOT NULL DEFAULT 0 COMMENT '表差异数',
    column_diff_count INT NOT NULL DEFAULT 0 COMMENT '字段差异数',
    index_diff_count INT NOT NULL DEFAULT 0 COMMENT '索引差异数',
    standard_violation_count INT NOT NULL DEFAULT 0 COMMENT '贯标异常数',
    result_file_path VARCHAR(500) COMMENT '结果文件路径',
    svn_revision VARCHAR(20) COMMENT 'SVN版本号',
    error_msg TEXT COMMENT '错误信息',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_env (env),
    INDEX idx_status (status),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='执行记录表';

CREATE TABLE IF NOT EXISTS db_execute_detail (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    record_id BIGINT NOT NULL COMMENT '执行记录ID',
    diff_type VARCHAR(50) NOT NULL COMMENT '差异类型',
    sub_type VARCHAR(50) NOT NULL COMMENT '子类型',
    table_name VARCHAR(100) COMMENT '表名',
    table_comment VARCHAR(200) COMMENT '表中文名',
    column_name VARCHAR(100) COMMENT '字段名',
    column_comment VARCHAR(200) COMMENT '字段中文名',
    doc_value VARCHAR(500) COMMENT '文档值',
    db_value VARCHAR(500) COMMENT '数据库值',
    diff_description VARCHAR(500) COMMENT '差异描述',
    process_sql TEXT COMMENT '处理SQL',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_record_id (record_id),
    INDEX idx_diff_type (diff_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='执行明细表';

CREATE TABLE IF NOT EXISTS db_standard_field (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    column_name VARCHAR(100) NOT NULL COMMENT '字段英文名',
    column_comment VARCHAR(200) NOT NULL COMMENT '字段中文名',
    column_type VARCHAR(50) NOT NULL COMMENT '标准字段类型',
    data_code VARCHAR(50) COMMENT '数据标准码',
    description VARCHAR(500) COMMENT '说明',
    enabled TINYINT NOT NULL DEFAULT 1 COMMENT '是否启用',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_column_name (column_name),
    UNIQUE KEY uk_column_comment (column_comment)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='贯标字段标准表';

CREATE TABLE IF NOT EXISTS sys_config (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    config_key VARCHAR(100) NOT NULL COMMENT '配置键',
    config_value VARCHAR(500) COMMENT '配置值',
    description VARCHAR(200) COMMENT '配置说明',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_config_key (config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';
