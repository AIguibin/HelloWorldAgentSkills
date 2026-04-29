# 项目结构说明

## 项目信息

| 项目 | 内容 |
|-----|------|
| 项目名称 | aiguibin-platform-arch |
| 版本 | 1.0.0 |
| 技术栈 | Spring Boot 3.2.5 + Vue 3.4.21 |
| JDK版本 | Java 17 |

## 目录结构

```
aiguibin-platform-arch/
├── src/main/java/com/aiguibin/platform/
│   ├── PlatformApplication.java              # 启动类
│   ├── common/                               # 公共模块
│   │   ├── config/                           # 公共配置
│   │   │   ├── MybatisPlusConfig.java        # MyBatis-Plus配置
│   │   │   ├── RedisConfig.java              # Redis配置
│   │   │   ├── SecurityConfig.java           # 安全配置
│   │   │   ├── SwaggerConfig.java            # API文档配置
│   │   │   └── WebMvcConfig.java             # Web配置
│   │   ├── constant/                         # 常量定义
│   │   │   ├── CommonConstants.java          # 通用常量
│   │   │   └── SecurityConstants.java        # 安全常量
│   │   ├── exception/                        # 异常处理
│   │   │   ├── BusinessException.java        # 业务异常
│   │   │   └── GlobalExceptionHandler.java   # 全局异常处理
│   │   ├── model/                            # 公共模型
│   │   │   ├── Result.java                   # 统一响应
│   │   │   └── PageResult.java               # 分页响应
│   │   ├── util/                             # 工具类
│   │   │   ├── IpUtils.java                  # IP工具
│   │   │   └── SecurityUtils.java            # 安全工具
│   │   └── result/                           # 统一响应
│   ├── core/                                 # 核心模块
│   │   ├── user/                             # 用户管理
│   │   │   ├── controller/UserController.java
│   │   │   ├── service/UserService.java
│   │   │   ├── mapper/UserMapper.java
│   │   │   ├── entity/SysUser.java
│   │   │   └── dto/
│   │   ├── role/                             # 角色管理
│   │   ├── menu/                             # 菜单管理
│   │   ├── org/                              # 机构管理
│   │   ├── dept/                             # 部门管理
│   │   ├── permission/                       # 权限管理
│   │   └── log/                              # 审计日志
│   ├── modules/                              # 功能模块
│   │   └── dbcompare/                        # 数据库比对模块
│   │       ├── controller/
│   │       ├── service/
│   │       ├── mapper/
│   │       ├── model/
│   │       ├── job/
│   │       └── util/
│   └── config/                               # 全局配置
├── src/main/resources/
│   ├── application.yml                       # 主配置
│   ├── application-dev.yml                   # 开发环境
│   └── static/                               # 前端资源
└── pom.xml
```

## 模块说明

### 1. common 公共模块
- **config**: 全局配置类
- **constant**: 系统常量定义
- **exception**: 异常处理体系
- **model**: 公共数据模型
- **util**: 通用工具类

### 2. core 核心模块
- **user**: 用户管理（用户CRUD、密码管理）
- **role**: 角色管理（角色CRUD、权限分配）
- **menu**: 菜单管理（菜单树、权限标识）
- **org**: 机构管理（机构树、多机构支持）
- **dept**: 部门管理（部门树、部门负责人）
- **permission**: 权限管理（权限检查、数据权限）
- **log**: 审计日志（操作日志、登录日志）

### 3. modules 功能模块
- **dbcompare**: 数据库比对模块
  - Excel解析服务
  - SVN集成服务
  - 飞秋通知服务
  - 定时任务调度

## 技术选型

| 层级 | 技术 | 版本 | 说明 |
|-----|------|------|------|
| 后端框架 | Spring Boot | 3.2.5 | 主框架 |
| 安全框架 | Spring Security | 6.x | 认证授权 |
| Token | JWT | - | 无状态认证 |
| ORM | MyBatis-Plus | 3.5.6 | 数据访问 |
| 多数据源 | dynamic-datasource | 4.3.0 | 动态数据源 |
| Excel | EasyExcel | 3.3.4 | Excel处理 |
| SVN | SVNKit | 1.10.11 | SVN客户端 |
| 缓存 | Caffeine | 3.1.8 | 本地缓存 |
| 连接池 | Druid | 1.2.22 | 数据库连接池 |

## 数据库设计

### 核心表
- **sys_user**: 用户表
- **sys_role**: 角色表
- **sys_menu**: 菜单表
- **sys_org**: 机构表
- **sys_dept**: 部门表
- **sys_user_role**: 用户角色关联表
- **sys_role_menu**: 角色菜单关联表
- **sys_user_org**: 用户机构关联表

### 业务表
- **db_datasource_config**: 数据源配置表
- **db_svn_config**: SVN配置表
- **db_feiQ_config**: 飞秋配置表
- **db_schedule_config**: 定时任务配置表
- **db_execute_record**: 执行记录表
- **db_execute_detail**: 执行明细表
- **db_standard_field**: 贯标字段标准表

---

**生成时间**: 2026-02-22
**生成方式**: AI自动生成
