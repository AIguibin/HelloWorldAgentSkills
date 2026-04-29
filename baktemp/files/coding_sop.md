# 编码与测试 SOP

## 一、编码前准备清单

在开始编码任何任务前，先完成以下准备（不跳过）：

- [ ] 读取 `exec_index.yaml` 中当前任务的描述和验收标准
- [ ] 阅读相关详细设计文档（伪代码）
- [ ] 阅读相关接口设计文档
- [ ] 确认所有前置依赖任务状态为 `DONE`
- [ ] 在项目中搜索类似实现，找到可参考的样例代码
- [ ] 确认代码分支正确
- [ ] 确认所有依赖已在 pom.xml 中声明

> **任务粒度基准**：每个原子任务 **2-8 小时**（单个类/方法/组件），过大则拆分，过小则合并。

---

## 二、样例代码复用规则

> 核心原则：**参考样例的结构和风格，根据当前需求重写业务逻辑，禁止无脑粘贴**

### ✅ 可以复用的场景

| 场景 | 示例 |
|-----|------|
| 通用CRUD流程结构 | 新增/修改/删除/查询的方法骨架 |
| 通用工具方法 | 日期处理、字符串处理、业务编号生成 |
| 通用设计模式 | Service层结构、Controller层结构、异常处理、日志记录模式 |
| 通用配置 | 数据源、Redis、安全配置的写法 |

### ❌ 禁止照搬的场景

| 场景 | 原因 |
|-----|------|
| 业务逻辑（样例业务规则与当前需求不同） | 会引入错误的业务逻辑 |
| 数据模型（样例字段与当前表结构不同） | 会导致数据错乱 |
| 存在已知技术债务的代码 | 延续技术债务 |
| 过度设计（包含不必要的复杂抽象） | 增加维护复杂度 |

---

## 三、Java / Spring Boot 编码规范（核心要点）

### 分层职责严格遵守

```
Controller  只做：参数接收 → @Valid校验 → 调Service → 包装返回
Service     只做：业务逻辑 → @Transactional事务 → 调Mapper
Mapper      只做：数据库操作（MyBatis-Plus/自定义SQL）
Entity      对应数据库表的POJO，不含业务逻辑
VO/DTO      接口请求/响应对象，不含业务逻辑
```

**交叉越界示例（禁止）**：
```java
// ❌ Controller 里写了业务逻辑
@PostMapping("/dict-types")
public Result<?> add(@RequestBody DictTypeAddDTO dto) {
    // 直接在Controller判断编码是否重复，这是Service的职责
    if (dictTypeMapper.countByCode(dto.getTypeCode()) > 0) {
        return Result.fail("编码重复");
    }
    ...
}
```

### 必须遵守的关键规则

**日志**：使用 `@Slf4j`，禁止 `System.out.println`
```java
log.info("删除字典类型成功，id: {}, typeCode: {}", id, dictType.getTypeCode());
log.error("删除字典类型失败，id: {}，原因: {}", id, e.getMessage(), e);
```

**异常处理**：禁止空 catch 块
```java
// ❌ 错误：吞掉异常
try { doSomething(); } catch (Exception e) {}

// ✅ 正确：记录日志并向上抛出
try { doSomething(); } catch (Exception e) {
    log.error("操作失败: {}", e.getMessage(), e);
    throw new SystemException("系统异常，请稍后重试");
}
```

**事务**：写操作必须加 `@Transactional`
```java
@Transactional(rollbackFor = Exception.class)   // 写操作
@Transactional(readOnly = true)                  // 只读操作（可选，提升性能）
```

**MyBatis-Plus 规范**：
```java
// ✅ 实体类注解
@TableName("dict_type")
@TableId(type = IdType.AUTO)
@TableLogic         // 逻辑删除字段
private Integer isDeleted;

// ✅ 批量插入（禁止循环单条insert）
dictTypeService.saveBatch(list);  // 而不是 for(item : list) dictTypeMapper.insert(item)

// ✅ 查询指定字段（禁止SELECT *）
dictTypeMapper.selectList(
    new LambdaQueryWrapper<DictType>()
        .select(DictType::getId, DictType::getTypeCode, DictType::getTypeName)
        .eq(DictType::getIsDeleted, 0)
);
```

---

## 四、单元测试 SOP

### 测试命名规范
```
方法名_场景描述_预期结果

示例：
  deleteDictType_success_shouldCallDeleteById
  deleteDictType_whenTypeNotFound_shouldThrowBusinessException
  deleteDictType_whenItemsExist_shouldNotCallDeleteAndThrow
```

### Mock 规范

```java
@ExtendWith(MockitoExtension.class)
class DictTypeServiceImplTest {

    @InjectMocks
    private DictTypeServiceImpl dictTypeService;  // 被测类，不Mock

    // 必须Mock的外部依赖
    @Mock private DictTypeMapper dictTypeMapper;
    @Mock private DictItemMapper dictItemMapper;
    @Mock private RedisTemplate<String, Object> redisTemplate;

    // 不需要Mock（直接new）
    // DictTypeVO, DictTypeAddDTO 等简单POJO
}
```

### 必须覆盖的测试场景

| 场景类型 | 测试内容 | 核心断言 |
|---------|---------|---------|
| 正常流程 | 完整的正常执行路径 | verify关键方法被调用，结果正确 |
| 记录不存在 | 查询返回null时 | assertThrows(BusinessException.class, ...) |
| 业务规则冲突 | 如删除时有子记录 | assertThrows + verify关键方法未被调用 |
| 空值边界 | 传入null参数 | assertThrows(ValidationException.class, ...) |
| 最大长度边界 | 字段值达到最大允许长度 | 断言通过或失败（视业务规则） |

### 覆盖率保障策略

```java
// 确保覆盖所有分支：deleteDictType 有3个分支
// 分支1：id==null（参数校验）
@Test
void deleteDictType_nullId_shouldThrow() { ... }

// 分支2：dictType==null（不存在）
@Test
void deleteDictType_notFound_shouldThrow() { ... }

// 分支3：有子记录（业务规则）
@Test
void deleteDictType_hasItems_shouldThrow() { ... }

// 主流程（到达 deleteById 的路径）
@Test
void deleteDictType_success() { ... }
```

---

## 五、接口测试 SOP（curl 脚本规范）

```bash
#!/bin/bash
# ============================================
# 接口测试脚本 - 字典类型管理
# 生成时间: $(date +%Y-%m-%d)
# ============================================

BASE_URL="http://localhost:8080"
TOKEN="Bearer your-token-here"

run_test() {
    local desc="$1"
    local expected="$2"
    local cmd="$3"
    echo "========================================"
    echo "测试：$desc"
    echo "预期：$expected"
    echo "========================================"
    eval $cmd | python3 -m json.tool
    echo ""
}

# ──── 正常场景 ────
run_test \
    "新增字典类型 - 正常" \
    "返回 code=0，data中包含新增ID" \
    'curl -s -X POST "$BASE_URL/api/dict-types" \
      -H "Content-Type: application/json" \
      -H "Authorization: $TOKEN" \
      -d '"'"'{"typeCode":"GENDER","typeName":"性别","description":"用户性别"}'"'"''

# ──── 异常场景 ────
run_test \
    "新增字典类型 - 编码重复" \
    "返回 code=40001" \
    'curl -s -X POST "$BASE_URL/api/dict-types" \
      -H "Content-Type: application/json" \
      -H "Authorization: $TOKEN" \
      -d '"'"'{"typeCode":"GENDER","typeName":"性别2"}'"'"''

run_test \
    "新增字典类型 - 缺少必填参数 typeCode" \
    "返回 code=400，提示typeCode不能为空" \
    'curl -s -X POST "$BASE_URL/api/dict-types" \
      -H "Content-Type: application/json" \
      -H "Authorization: $TOKEN" \
      -d '"'"'{"typeName":"性别"}'"'"''

# ──── 边界场景 ────
run_test \
    "新增字典类型 - typeCode达到最大长度50" \
    "返回 code=0，新增成功" \
    'curl -s -X POST "$BASE_URL/api/dict-types" \
      -H "Content-Type: application/json" \
      -H "Authorization: $TOKEN" \
      -d '"'"'{"typeCode":"AAAAAAAAAABBBBBBBBBBCCCCCCCCCCDDDDDDDDDDEEEEEEEEEE","typeName":"边界测试"}'"'"''

# ──── 权限场景 ────
run_test \
    "无Token访问 - 未授权" \
    "返回 code=401" \
    'curl -s -X POST "$BASE_URL/api/dict-types" \
      -H "Content-Type: application/json" \
      -d '"'"'{"typeCode":"TEST","typeName":"测试"}'"'"''
```

---

## 六、PDCA 执行循环详解

```
Plan（每个任务开始前，5-10分钟）
├── 读取 exec_index.yaml 中当前任务ID、描述、验收标准
├── 读取任务对应的设计文档（伪代码/接口设计/数据库设计）
├── 确认前置依赖任务已完成（status=DONE）
└── 在项目中搜索类似实现作为参考样例

Do（主要执行时间，2-7小时）
├── 先写类/方法的框架（注释 + 方法签名）
├── 填充实现逻辑（严格按伪代码，不擅自修改设计）
└── 编写单元测试（与实现代码同步编写，不留到最后）

Check（审查，30-60分钟）
├── 切换角色为"代码审查员"
├── 对照 references/review_checklists.md 审查清单4 逐项检查
├── 运行单元测试，确认全部通过
└── 检查覆盖率：行≥80%，分支≥70%，方法=100%

Act（处理，视问题数量而定）
├── 发现P0问题 → 立即修复，返回 Do 阶段重新审查
├── 发现P1/P2问题 → 修复后继续，或记录到 tech_debt.md
└── 全部通过 → 标记任务完成并记录交付物：
    python scripts/exec_index_manager.py \
      --done T5001 \
      --deliverable "src/main/java/.../DictTypeServiceImpl.java" \
      --coverage "行:85%, 分支:75%, 方法:100%"
```

---

## 七、技术债务记录规范

当发现需记录但暂不修复的技术债务时，追加到 `04_logs/tech_debt.md`：

```markdown
| 债务ID | 类型 | 严重程度 | 描述 | 影响 | 所在文件 | 发现时间 | 状态 | 建议方案 |
|-------|-----|---------|------|------|---------|---------|------|---------|
| TD001 | 代码债务 | P1 | Service层直接返回Entity，未转换为VO | 暴露数据库结构 | DictTypeServiceImpl.java | 2025-02-01 | 待处理 | 增加VO转换层 |
| TD002 | 测试债务 | P2 | 边界场景测试用例不完整 | 潜在遗漏边界bug | DictTypeServiceTest.java | 2025-02-01 | 待处理 | 补充null值和最大长度测试 |
```

**P0债务**（必须立即修复，阻塞后续任务）：
- SQL注入风险
- 高概率NPE（如直接使用可能为null的返回值）
- 敏感信息泄露（日志/响应）
- 核心接口无事务保护
- 测试覆盖率低于配置要求
