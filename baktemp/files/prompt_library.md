# 各阶段标准 Prompt 模板库

## Prompt 编写五大核心原则

每个 Prompt 必须包含以下五个要素，缺一不可：

| 要素 | 作用 | 示例 |
|-----|------|-----|
| **角色（Role）** | 锚定AI身份，激活对应知识 | "你是资深Java后端工程师" |
| **上下文（Context）** | 提供足够背景，避免假设 | "项目技术栈是Spring Boot 3.0+MySQL 8.0" |
| **任务（Task）** | 明确要做什么 | "实现DictTypeService的deleteDictType方法" |
| **输出格式（Format）** | 规定交付物格式和结构 | "输出Markdown格式，包含以下章节..." |
| **负面清单（Negative）** | 明确禁止行为，避免常见错误 | "不要使用魔法数字；不要遗漏异常场景" |

> 💡 在使用Prompt时，将 `{{变量}}` 替换为实际内容。

---

## 阶段1：需求分析 Prompt

### 1.1 需求理解与拆分

```
【角色】
你是一位资深需求分析专家，擅长业务需求分析、需求拆分和需求文档编写，
具备10年以上企业级系统开发经验。

【上下文】
项目名称：{{project_name}}
项目描述：{{project_description}}
技术栈：{{tech_stack}}
用户原始需求：{{raw_requirement}}

【任务】
根据用户原始需求，编写完整的需求规格说明书。

【输出格式】
Markdown格式，必须包含以下章节：
1. 功能概述（项目背景、核心目标、功能模块列表）
2. 业务流程（每个模块的主流程，用有序步骤描述）
3. 功能需求（用户故事形式，格式："作为[角色]，我希望[功能]，以便[价值]"）
   - 每个用户故事必须包含验收标准（Given-When-Then格式）
4. 数据字典（字段名、类型、长度、是否必填、说明）
5. 场景清单（正常场景/异常场景/边界场景/权限场景/状态场景）
6. 非功能需求（性能、安全、可用性、兼容性要求）

【约束】
- 每个用户故事颗粒度：1-3天可完成
- 场景清单必须完整穷举，不能只写"其他异常场景"
- 数据字典必须定义所有实体的所有字段

【负面清单】
- ❌ 不要遗漏异常场景和边界条件
- ❌ 不要出现"后续完善"等模糊描述
- ❌ 不要出现无法量化的性能要求（如"响应快"）
- ❌ 不要遗漏权限相关场景
```

---

## 阶段2：设计 Prompt

### 2.1 数据库设计

```
【角色】
你是一位资深数据库设计专家，精通MySQL设计规范，擅长设计高性能、可扩展的数据库结构。

【上下文】
项目技术栈：{{tech_stack}}
数据库版本：{{db_version}}
编码规范：{{coding_standard}}
已确认的数据字典：{{data_dictionary}}

【任务】
根据数据字典，设计完整的数据库表结构，包含建表SQL。

【输出格式】
1. 数据库设计说明（表清单、表间关系说明）
2. 每张表的设计说明：
   - 字段名、类型、长度、是否为空、默认值、注释
   - 主键设计（推荐bigint自增或雪花ID）
   - 索引设计（普通索引、唯一索引）
3. 完整的建表SQL（带注释）

【约束】
- 每张表必须包含通用字段：id、create_time、update_time、is_deleted、create_by、update_by
- 字段命名使用下划线命名法（snake_case）
- 字符集统一使用 utf8mb4
- 存储引擎使用 InnoDB
- 外键关联字段必须建立索引
- 频繁查询的字段必须建立索引

【负面清单】
- ❌ 不要使用无意义的字段名（如 a、b、c）
- ❌ 不要遗漏索引设计
- ❌ varchar 长度不要无脑设255，根据实际业务设计
- ❌ 不要遗漏表注释和字段注释
```

### 2.2 接口设计

```
【角色】
你是一位资深后端架构师，精通RESTful API设计规范，擅长设计清晰、一致的接口契约。

【上下文】
项目技术栈：{{tech_stack}}
已设计的数据库表：{{table_list}}
统一响应格式：{"code": 0, "message": "success", "data": {}}

【任务】
根据功能需求和数据库设计，设计完整的RESTful API接口文档。

【输出格式】
每个接口必须包含：
- 接口路径（使用复数名词，如 /api/dict-types）
- HTTP方法（GET/POST/PUT/DELETE）
- 功能描述
- 请求头（Authorization等）
- 请求参数（Query参数、路径参数、请求体字段，包含类型/是否必填/说明）
- 响应示例（成功+失败）
- 错误码定义

【约束】
- 路径使用复数名词，不包含动词
- 查询用GET，创建用POST，全量更新用PUT，部分更新用PATCH，删除用DELETE
- 分页接口必须返回总数（total）
- 所有接口统一使用 {{统一响应格式}}

【负面清单】
- ❌ 不要在路径中使用动词（如 /getUser、/deleteUser）
- ❌ 不要遗漏请求参数的校验规则
- ❌ 不要遗漏错误码定义
```

### 2.3 详细设计（伪代码）

```
【角色】
你是一位资深系统设计专家，擅长将业务需求转化为清晰的实现伪代码，
为开发工程师提供可直接参考的实现指南。

【上下文】
待设计的方法：{{method_name}}
所在类：{{class_name}}
功能描述：{{feature_description}}
相关数据库表：{{related_tables}}
相关接口设计：{{related_api}}

【任务】
编写 {{method_name}} 的详细设计伪代码，包含完整的逻辑流程和异常处理。

【输出格式】
```
方法名：{{method_name}}
输入参数：{{params with types}}
返回值：{{return type and description}}

伪代码：
1. 参数校验
   - if {{param}} 为空 then 抛出 ValidationException("xxx不能为空")
2. 业务查询
   - 查询数据库获取 {{entity}}
   - if 记录不存在 then 抛出 BusinessException("xxx不存在")
3. 业务规则校验
   - if {{business_rule}} then 抛出 BusinessException("xxx")
4. 执行操作（开启事务）
   - 执行 {{operation1}}
   - 执行 {{operation2}}
5. 返回结果
   - 组装响应VO并返回

异常处理：
- ValidationException → HTTP 400，code: 400
- BusinessException → HTTP 200，code: {{error_code}}
- 系统异常 → HTTP 500，记录错误日志，返回 code: 500
```

【负面清单】
- ❌ 不要写依赖特定语言语法的伪代码
- ❌ 不要遗漏任何业务规则的校验
- ❌ 不要遗漏异常场景处理
```

---

## 阶段4：编码实现 Prompt

### 4.1 Service层实现

```
【角色】
你是一位资深{{language}}开发工程师，精通{{framework}}，
严格遵循{{coding_standard}}，有丰富的企业级系统开发经验。

【上下文】
当前任务ID：{{task_id}}
任务描述：{{task_description}}
涉及的数据库表：{{table_names}}
依赖的已完成任务：{{depends_on_tasks}}
详细设计伪代码：
{{pseudocode}}

参考样例代码（同项目其他Service实现）：
{{sample_code_path}}

【任务】
实现 {{class_name}}.{{method_name}} 方法，满足以下验收标准：
{{acceptance_criteria}}

【输出格式】
1. 完整的Java实现代码（包含必要的JavaDoc注释和行内注释）
2. 对应的JUnit5单元测试（覆盖正常场景+所有异常场景）
3. 如涉及HTTP接口，附上curl测试命令

【约束】
- 严格遵循 {{coding_standard}}
- 所有public方法必须有JavaDoc注释
- 异常处理不允许空catch块
- 不允许使用魔法数字，使用常量或枚举
- 不允许使用System.out.println，使用SLF4J日志框架
- 关键操作必须有日志记录（INFO级别）
- Service层必须使用@Transactional（涉及写操作时）

【单元测试要求】
- 行覆盖率 ≥ {{line_coverage}}%
- 分支覆盖率 ≥ {{branch_coverage}}%
- 所有public方法覆盖率 = 100%
- 外部依赖（Mapper、外部服务）必须使用Mockito Mock
- 测试方法命名：方法名_场景描述_预期结果

【负面清单】
- ❌ 不要在循环内执行数据库查询（N+1问题）
- ❌ 不要忽略参数的null值校验
- ❌ 不要将敏感信息（密码、Token）输出到日志
- ❌ 不要照搬样例代码的业务逻辑，根据当前需求调整
```

### 4.2 Controller层实现

```
【角色】
你是一位资深{{language}}开发工程师，精通Spring MVC，
严格遵循{{coding_standard}}。

【上下文】
对应的接口设计：{{api_design}}
对应的Service：{{service_class}}
统一响应格式：{{response_format}}
参数校验规范：使用 @Valid + Bean Validation 注解

【任务】
实现 {{controller_class}} 中的 {{method_name}} 接口处理方法。

【约束】
- Controller层只做：参数接收、参数校验、调用Service、返回结果
- 不在Controller层写任何业务逻辑
- 所有接口必须有 @Operation 注解（Swagger文档）
- 参数校验失败统一抛出 MethodArgumentNotValidException
- 路径参数使用 @PathVariable，查询参数使用 @RequestParam，请求体使用 @RequestBody

【负面清单】
- ❌ 不要在Controller层写业务逻辑
- ❌ 不要在Controller层直接操作数据库
- ❌ 不要遗漏 @Valid 注解
```

---

## 阶段5：测试 Prompt

### 5.1 接口测试脚本生成

```
【角色】
你是一位资深测试工程师，擅长接口测试，精通curl命令编写。

【上下文】
接口文档：{{api_documentation}}
服务地址：{{base_url}}（默认 http://localhost:8080）
认证Token：{{auth_token}}（默认留空，需要时替换）

【任务】
为以下接口生成完整的curl测试脚本，覆盖正常场景和异常场景：
{{api_list}}

【输出格式】
Shell脚本，每个测试用例包含：
1. 注释说明（测试场景、预期结果）
2. curl命令（完整的headers、body）
3. 预期响应码和响应体关键字段

【测试用例覆盖要求】
- 每个接口至少：1个正常场景 + 3个异常场景（缺少必填参数、参数格式错误、业务规则冲突）
- 边界值测试（空值、最大值、最小值）
- 权限测试（有权限访问、无权限访问）

【负面清单】
- ❌ 不要只测试正常场景（happy path）
- ❌ 不要遗漏必填参数缺少的场景
- ❌ 不要使用真实的生产环境数据
```

---

## Prompt质量校验标准（Section 3.3）

每次 AI 生成内容后，对照以下4个维度自我评估输出质量，不合格则重新生成：

| 校验维度 | 检查内容 | 不合格则... |
|---------|---------|-----------|
| **完整性** | 输出是否包含所有要求的章节/字段/场景 | 补充缺失内容 |
| **准确性** | 输出是否符合需求/设计/规范，无偏离 | 修正不准确的部分 |
| **一致性** | 输出内部前后是否一致，术语使用是否统一 | 修正矛盾点 |
| **可读性** | 输出是否清晰易懂，格式是否规范，有适当注释 | 重新排版和表达 |

**质量评级**：
- A：4个维度全部通过 → 直接进入下一步
- B：1个维度有小问题 → 修正后继续
- C：2+个维度有问题 → 完整重新生成

---

## Prompt版本化管理（Section 3.4）

在使用自定义Prompt时，按以下格式在 Prompt 头部注明版本：

```yaml
---
prompt_id: stage1-req-01
prompt_name: 需求分析阶段Prompt
version: 1.0.0
last_updated: 2025-02
---
```

**版本号升级规则**：
- 主版本号：Prompt结构重大调整（增减必填模块）
- 次版本号：新增约束或示例
- 修订号：优化描述、修复不清晰的问题
