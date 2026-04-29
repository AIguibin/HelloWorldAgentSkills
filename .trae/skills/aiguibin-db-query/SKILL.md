---
name: "aiguibin-db-query"
description: "提供后端代码中数据库查询的工具和最佳实践。用于开发后端应用时需要与数据库交互的场景，包括查询、插入、更新、删除等操作。"
---

# 后端数据库查询技能

## 功能介绍

该技能提供后端代码开发中数据库查询的完整解决方案，包括：

- 支持多种数据库类型（MySQL、PostgreSQL、MongoDB、Redis等）
- 查询构建与优化
- 参数化查询防止SQL注入
- 事务处理
- 连接池管理
- 错误处理
- 性能监控
- 优先使用chat2DB的mcp工具查询数据库表结构和数据

## 使用场景

当你需要开发后端代码并与数据库交互时，该技能可以帮助你：

- 编写高效的数据库查询语句
- 实现安全的数据库操作
- 处理复杂的数据关系
- 优化查询性能
- 实现事务一致性
- 使用chat2DB的mcp工具查询数据库表结构和数据

### 何时使用chat2DB的mcp工具

当你需要以下信息时，**必须优先使用chat2DB的mcp工具**查询数据库：

1. 查看数据库表结构（包括字段名、类型、约束等）
2. 查询表中的实际数据
3. 了解数据库中的表关系
4. 验证SQL语句的执行结果
5. 分析数据库性能问题
6. 任何需要获取真实数据库信息的场景

## 示例代码

### MySQL查询示例

```javascript
// 使用参数化查询防止SQL注入
const mysql = require('mysql2/promise');

async function getUserById(userId) {
  const connection = await mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'password',
    database: 'mydb'
  });
  
  try {
    // 参数化查询
    const [rows] = await connection.execute(
      'SELECT * FROM users WHERE id = ?',
      [userId]
    );
    return rows[0];
  } finally {
    await connection.end();
  }
}
```

### PostgreSQL事务示例

```python
import psycopg2
from psycopg2 import extras

conn = psycopg2.connect(
    host="localhost",
    database="mydb",
    user="postgres",
    password="password"
)

def transfer_funds(from_account, to_account, amount):
    cur = conn.cursor()
    
    try:
        # 开始事务
        conn.autocommit = False
        
        # 检查余额
        cur.execute("SELECT balance FROM accounts WHERE id = %s", (from_account,))
        from_balance = cur.fetchone()[0]
        
        if from_balance < amount:
            raise ValueError("余额不足")
        
        # 扣减转出账户
        cur.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (amount, from_account))
        
        # 增加转入账户
        cur.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s", (amount, to_account))
        
        # 提交事务
        conn.commit()
        return True
    except Exception as e:
        # 回滚事务
        conn.rollback()
        raise e
    finally:
        # 恢复自动提交
        conn.autocommit = True
        cur.close()
```

### MongoDB查询示例

```javascript
const { MongoClient } = require('mongodb');

const uri = 'mongodb://localhost:27017';
const client = new MongoClient(uri);

async function getProducts(category, minPrice) {
  try {
    await client.connect();
    const database = client.db('mydb');
    const products = database.collection('products');
    
    // 查询构建
    const query = {
      category: category,
      price: { $gte: minPrice }
    };
    
    const options = {
      sort: { price: 1 },
      projection: { _id: 1, name: 1, price: 1 }
    };
    
    const cursor = products.find(query, options);
    return await cursor.toArray();
  } finally {
    await client.close();
  }
}
```

## 最佳实践

1. **使用chat2DB的mcp工具**：在需要查看表结构或数据时，优先使用chat2DB的mcp工具查询数据库，获取真实的数据库信息
2. **使用参数化查询**：始终使用参数化查询防止SQL注入攻击
3. **关闭连接**：使用try-finally确保数据库连接正确关闭
4. **使用连接池**：高并发场景下使用连接池管理数据库连接
5. **优化查询**：添加适当的索引，避免SELECT *，使用LIMIT限制返回数据量
6. **事务处理**：关键操作使用事务确保数据一致性
7. **错误处理**：捕获并适当处理数据库错误
8. **监控性能**：记录慢查询，定期优化

## 工具推荐

- **关系型数据库**：Sequelize (Node.js), SQLAlchemy (Python), Hibernate (Java)
- **NoSQL数据库**：Mongoose (MongoDB), Redis OM
- **ORM框架**：Prisma, TypeORM, Drizzle ORM
- **连接池**：HikariCP (Java), pgBouncer (PostgreSQL), ProxySQL (MySQL)

## 常见问题

### Q: 如何防止SQL注入？
A: 使用参数化查询，避免直接拼接SQL字符串。所有ORM框架都提供了参数化查询功能。

### Q: 什么时候使用事务？
A: 当需要执行多个相关操作，要么全部成功，要么全部失败时使用事务。例如转账操作、订单创建等。

### Q: 如何优化慢查询？
A: 1. 分析查询执行计划；2. 添加适当的索引；3. 优化查询结构；4. 限制返回数据量；5. 考虑分表分库。

### Q: 连接池大小如何设置？
A: 根据数据库类型和服务器配置调整，一般建议：
   - CPU核心数 × 2 + 磁盘数量
   - 或根据数据库厂商推荐设置

## 版本历史

- v1.0.0: 初始版本，支持MySQL、PostgreSQL、MongoDB查询
- v1.1.0: 添加Redis支持和事务处理示例
- v1.2.0: 增加最佳实践和性能优化指南