# 编码与测试 SOP

## 一、编码前准备清单

在开始编码任何任务前，先完成以下准备：

- [ ] 阅读详细设计伪代码，理解实现目标
- [ ] 在项目中搜索类似实现，找到可参考的样例代码
- [ ] 确认代码分支正确
- [ ] 确认所有依赖已在 pom.xml / package.json 中声明
- [ ] 理解该任务的验收标准

---

## 二、样例代码复用规则

### ✅ 可以复用的场景
- 通用CRUD操作（新增/修改/删除/查询的基本流程结构）
- 通用工具方法（日期处理、字符串处理、业务编号生成）
- 设计模式（Service层结构、Controller层结构、异常处理、日志记录）
- 通用配置（数据源、缓存、安全配置）

### ❌ 禁止照搬的场景
- 业务逻辑（样例的业务规则与当前需求不同时）
- 数据模型（样例的字段与当前表结构不同时）
- 存在技术债务的代码（样例有已知性能问题、安全漏洞时）
- 过度设计（样例包含不必要的复杂抽象时）

> 原则：**参考样例的结构和风格，根据当前需求重写业务逻辑**

---

## 三、Java / Spring Boot 编码规范

### 命名规范（阿里巴巴Java开发规范）

| 类型 | 规范 | 示例 |
|-----|------|-----|
| 类名 | UpperCamelCase | `DictTypeServiceImpl` |
| 方法名/变量名 | lowerCamelCase | `findDictTypeByCode` |
| 常量 | UPPER_CASE_WITH_UNDERSCORES | `MAX_RETRY_COUNT` |
| 包名 | 全部小写 | `com.example.dict` |
| 数据库字段 | snake_case | `create_time` |

### 分层规范

```
Controller  → 只负责：参数接收、@Valid校验、调用Service、返回结果
Service     → 只负责：业务逻辑、事务控制、调用Mapper
Mapper      → 只负责：数据库操作（MyBatis-Plus/SQL）
Entity      → 对应数据库表的POJO，不含业务逻辑
VO/DTO      → 接口请求/响应对象，不含业务逻辑
```

### 必须遵守的编码规则

1. **日志**：使用 `@Slf4j`，不允许使用 `System.out.println`
   ```java
   log.info("删除字典类型，typeCode: {}", typeCode);
   log.error("删除字典类型失败，typeCode: {}，原因: {}", typeCode, e.getMessage(), e);
   ```

2. **异常处理**：不允许空 catch 块
   ```java
   // ❌ 错误
   try { ... } catch (Exception e) {}
   
   // ✅ 正确
   try { ... } catch (Exception e) {
       log.error("操作失败，原因: {}", e.getMessage(), e);
       throw new SystemException("系统异常，请稍后重试");
   }
   ```

3. **事务**：写操作必须加 `@Transactional`，只读操作加 `@Transactional(readOnly = true)`

4. **参数校验**：Service层使用业务判断，Controller层使用 `@Valid` + Bean Validation 注解

5. **MyBatis-Plus 规范**：
   - 实体类必须有 `@TableName`、`@TableId`
   - 逻辑删除字段加 `@TableLogic`
   - 批量插入使用 `saveBatch`，不要循环单条插入
   - 查询指定必要字段，避免 `SELECT *`

---

## 四、单元测试 SOP

### 测试用例命名规范
```
方法名_测试场景_预期结果
例：deleteDictType_whenItemsExist_shouldThrowException
```

### Mock 规范

```java
// 必须Mock的依赖
@Mock private DictTypeMapper dictTypeMapper;
@Mock private DictItemMapper dictItemMapper;
@Mock private RedisTemplate<String, Object> redisTemplate;

// 不需要Mock（直接new）
DictTypeVO dictTypeVO = new DictTypeVO();

// Mock方法设置
when(dictTypeMapper.selectById(1L)).thenReturn(mockDictType);
when(dictTypeMapper.selectById(99L)).thenReturn(null);
```

### 必须覆盖的测试场景

| 场景类型 | 示例 | 测试要点 |
|---------|------|---------|
| 正常场景 | 正常删除字典类型 | 验证删除成功，verify调用了Mapper |
| 不存在场景 | 删除不存在的记录 | 验证抛出BusinessException |
| 业务冲突场景 | 删除时存在子记录 | 验证抛出BusinessException，verify未执行删除 |
| 空值边界 | 传入null参数 | 验证抛出ValidationException |
| 最大值边界 | 字段值达到最大长度 | 验证校验通过/失败 |

### 覆盖率达标策略

```java
// 覆盖分支的关键：每个 if/else 都要有对应的测试用例
@Test
void deleteDictType_success() { /* 正常流程 */ }

@Test
void deleteDictType_notFound() { /* id不存在 */ }

@Test
void deleteDictType_hasItems() { /* 有子记录，应拒绝删除 */ }
```

---

## 五、接口测试 SOP

### curl 测试脚本规范

```bash
#!/bin/bash
# 接口测试脚本 - {{模块名}}
# 生成时间: {{日期}}
# 服务地址
BASE_URL="http://localhost:8080"
TOKEN="Bearer your-token-here"

echo "========================================"
echo "测试：新增字典类型 - 正常场景"
echo "预期：返回 code=0，data中包含新增记录ID"
echo "========================================"
curl -s -X POST "${BASE_URL}/api/dict-types" \
  -H "Content-Type: application/json" \
  -H "Authorization: ${TOKEN}" \
  -d '{
    "typeCode": "GENDER",
    "typeName": "性别",
    "description": "用户性别"
  }' | python3 -m json.tool

echo ""
echo "========================================"
echo "测试：新增字典类型 - 编码重复（异常场景）"
echo "预期：返回 code=40001，提示编码已存在"
echo "========================================"
curl -s -X POST "${BASE_URL}/api/dict-types" \
  -H "Content-Type: application/json" \
  -H "Authorization: ${TOKEN}" \
  -d '{
    "typeCode": "GENDER",
    "typeName": "性别2"
  }' | python3 -m json.tool

echo ""
echo "========================================"
echo "测试：新增字典类型 - 缺少必填参数（异常场景）"
echo "预期：返回 code=400，提示typeCode不能为空"
echo "========================================"
curl -s -X POST "${BASE_URL}/api/dict-types" \
  -H "Content-Type: application/json" \
  -H "Authorization: ${TOKEN}" \
  -d '{"typeName": "性别"}' | python3 -m json.tool
```

---

## 六、PDCA 执行循环详解

每个原子任务严格按照以下循环执行：

```
Plan（计划）
├── 读取 exec_index.yaml 中当前任务的描述和验收标准
├── 阅读相关设计文档（详细设计/接口设计/数据库设计）
├── 确认所有依赖任务已完成（status=DONE）
└── 在项目中搜索类似实现作为参考

Do（执行）
├── 先写类/方法的框架（注释+方法签名）
├── 填充实现逻辑（严格按伪代码实现）
└── 编写单元测试

Check（检查）
├── 切换角色为"代码审查员"
├── 对照 references/review_checklists.md 逐项检查
├── 运行单元测试，确认通过
└── 检查覆盖率是否达标

Act（处理）
├── 发现问题：返回 Do 阶段修正
├── 全部通过：更新 exec_index.yaml 中任务状态为 DONE
├── 记录实际耗时
└── 将交付物路径写入任务记录
```

---

## 七、技术债务记录

当发现需要记录但不阻塞的技术债务时，追加到 `04_logs/tech_debt.md`：

```markdown
| 债务ID | 类型 | 描述 | 严重程度 | 发现时间 | 所在文件 | 建议解决方案 |
|-------|-----|------|---------|---------|---------|------------|
| TD001 | 代码债务 | Service层直接返回PO对象，应增加VO转换 | 中 | 2025-02-01 | UserService.java | 增加BeanUtils.copyProperties转换 |
| TD002 | 测试债务 | 边界场景测试用例不完整 | 低 | 2025-02-01 | DictTypeServiceTest.java | 补充null值和最大长度场景 |
```

**P0级技术债务**（必须立即修复，阻塞后续任务）：
- SQL注入风险
- 未处理的空指针（高概率触发）
- 敏感信息泄露（日志/响应）
- 核心接口无事务保护
