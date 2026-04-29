# AI Guibin Platform - 数据库管理平台

## 项目简介

aiguibin-platform-arch 是一个基于微内核 + 插件式架构的数据库管理平台，提供数据库比对、认证授权、系统设置等核心功能。

## 技术栈

- **后端**: Spring Boot 3.2.5 + Java 17
- **ORM**: MyBatis-Plus 3.5.6
- **数据库**: MySQL 8.0
- **连接池**: Druid 1.2.22
- **Excel处理**: EasyExcel 3.3.4
- **动态数据源**: dynamic-datasource-spring-boot-starter 4.3.0
- **本地缓存**: Caffeine 3.1.8
- **接口文档**: Knife4j 4.4.0
- **工具库**: Hutool 5.8.26, Lombok 1.18.32

## 项目结构

```
aiguibin-platform-arch/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/aiguibin/platform/
│   │   │       ├── PlatformApplication.java          # 启动类
│   │   │       ├── common/                            # 公共模块
│   │   │       │   ├── constant/                      # 常量
│   │   │       │   ├── exception/                     # 异常
│   │   │       │   ├── result/                        # 响应结果
│   │   │       │   └── util/                          # 工具类
│   │   │       ├── config/                            # 配置模块
│   │   │       ├── controller/                        # 控制器层
│   │   │       ├── service/                           # 服务层
│   │   │       ├── mapper/                            # 数据访问层
│   │   │       ├── entity/                            # 实体类
│   │   │       ├── dto/                               # 数据传输对象
│   │   │       └── vo/                                # 视图对象
│   │   └── resources/
│   │       ├── application.yml                        # 主配置文件
│   │       ├── application-dev.yml                    # 开发环境配置
│   │       ├── schema.sql                             # 数据库初始化脚本
│   │       ├── data.sql                               # 测试数据脚本
│   │       └── mapper/                                # MyBatis XML映射文件
│   └── test/
└── pom.xml                                             # Maven配置文件
```

## 快速开始

### 1. 环境要求

- JDK 17+
- Maven 3.8+
- MySQL 8.0+

### 2. 数据库初始化

执行 `src/main/resources/schema.sql` 创建数据库和表结构，然后执行 `data.sql` 插入测试数据。

### 3. 修改配置

修改 `application-dev.yml` 中的数据库连接信息：

```yaml
spring:
  datasource:
    dynamic:
      datasource:
        master:
          url: jdbc:mysql://localhost:3306/platform_config?...
          username: root
          password: your_password
```

### 4. 启动项目

```bash
mvn clean install
mvn spring-boot:run
```

### 5. 访问接口文档

启动成功后，访问：http://localhost:8080/api/doc.html

## 默认账号

- 用户名: admin
- 密码: admin123

## 核心模块

1. **认证授权模块**: 两步登录、JWT Token、RBAC权限、数据权限
2. **系统设置模块**: 用户、机构、部门、角色、菜单、审计日志管理
3. **数据库比对模块**: Excel解析、多数据源比对、结果生成

## 开发计划

- M0（Day 1-5）: 项目基础设施 ✅
- M1（Day 6-17）: 认证授权模块
- M2（Day 18-43）: 系统设置模块
- M3（Day 44-83）: 数据库比对模块

## License

Apache 2.0
