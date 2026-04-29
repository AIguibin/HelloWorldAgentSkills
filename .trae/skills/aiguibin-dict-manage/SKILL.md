---
name: "aiguibin-dict-manage"
description: "提供完整的数据字典管理方案，包含管理流程、SQL操作规范和前端实现标准，确保数据字典的统一管理和规范使用。"
---

# 数据字典管理技能
## 技能描述
该技能提供完整的数据字典管理方案，基于sys_dict_type和sys_dict_item两张表结构，实现数据字典的统一管理、规范使用和动态获取。适用于需要统一管理系统中各类编码、分类、状态等固定值的场景。
## 功能介绍

该技能提供完整的数据字典管理方案，基于sys_dict_type和sys_dict_item两张表结构，实现数据字典的统一管理、规范使用和动态获取。适用于需要统一管理系统中各类编码、分类、状态等固定值的场景。

## 表结构说明

### sys_dict_type（字典类型表）

| 字段名 | 类型 | 描述 | 约束 |
|-------|------|------|------|
| uuid | varchar(32) | UUID，32位随机字符串 | 非空，唯一 |
| id | bigint unsigned | 主键ID | 自增，非空 |
| dict_type_code | varchar(50) | 字典类型编码 | 非空，唯一 |
| dict_type_name | varchar(100) | 字典类型名称 | 非空 |
| description | varchar(255) | 描述 | 可选 |
| sort_order | int | 排序 | 默认100 |
| status | tinyint | 状态：1-启用 0-禁用 | 默认1 |
| created_by | varchar(20) | 创建人用户编号 | 非空 |
| created_time | datetime | 创建时间 | 默认当前时间 |
| updated_by | varchar(20) | 更新人用户编号 | 可选 |
| updated_time | datetime | 更新时间 | 默认当前时间，自动更新 |
| is_deleted | tinyint | 是否删除：0-否，1-是 | 默认0 |

### sys_dict_item（字典项表）

| 字段名 | 类型 | 描述 | 约束 |
|-------|------|------|------|
| uuid | varchar(32) | UUID，32位随机字符串 | 非空，唯一 |
| id | bigint unsigned | 主键ID | 自增，非空 |
| dict_type_code | varchar(50) | 字典类型编码 | 非空 |
| dict_value | varchar(50) | 字典值 | 非空 |
| dict_label | varchar(100) | 字典标签 | 非空 |
| group_code | varchar(50) | 分组编码 | 可选 |
| group_name | varchar(100) | 分组名称 | 可选 |
| sort_order | int | 排序 | 默认100 |
| status | tinyint | 状态：1-启用 0-禁用 | 默认1 |
| created_by | varchar(20) | 创建人用户编号 | 非空 |
| created_time | datetime | 创建时间 | 默认当前时间 |
| updated_by | varchar(20) | 更新人用户编号 | 可选 |
| updated_time | datetime | 更新时间 | 默认当前时间，自动更新 |
| is_deleted | tinyint | 是否删除：0-否，1-是 | 默认0 |

## 数据字典管理流程

### 1. 需求分析

- 收集系统中需要使用数据字典的场景
- 分析数据字典的使用频率和范围
- 确定数据字典的分类和编码规则

### 2. 数据字典梳理

- 识别系统中所有需要统一管理的静态数据
- 对数据进行分类，确定字典类型
- 梳理每个字典类型下的具体字典项
- 确定字典项的分组规则（如有必要）

### 3. 数据字典类型划分

- **基础数据类型**：系统核心数据，如用户状态、性别、民族等
- **业务数据类型**：与业务相关的数据，如订单状态、支付方式、商品分类等
- **配置数据类型**：系统配置相关数据，如日志级别、缓存策略等
- **枚举数据类型**：固定的枚举值，如开关状态、是否选项等

### 4. 码值规划

- **字典类型编码规则**：使用大写字母+下划线，如 `USER_STATUS`、`PAYMENT_METHOD`
- **字典值规则**：使用有意义的编码，如 `ENABLED`、`DISABLED`，或数字编码
- **字典标签规则**：使用中文描述，如 `启用`、`禁用`
- **分组编码规则**：如需分组，使用与字典类型编码类似的规则
- **排序规则**：根据业务需求确定字典项的排序顺序

### 5. 计划文档编写

编写详细的数据字典管理计划文档，包含：
- 数据字典梳理结果
- 类型划分说明
- 码值规划规则
- 实施时间表
- 责任人

### 6. 审核与确认

- 提交计划文档给相关部门审核
- 收集审核意见并修改
- 获得最终确认后执行后续操作

### 7. SQL编写与执行

- 根据确认后的计划编写SQL语句
- 执行SQL语句，初始化数据字典
- 验证数据字典的正确性

### 8. 前端实现

- 确保所有涉及码值选择的界面使用选项类型控件
- 实现数据字典的动态获取

### 9. 维护与更新

- 定期审查数据字典的使用情况
- 根据业务需求更新数据字典
- 记录数据字典的变更历史

## SQL操作规范

### 1. 查询操作

#### 查询所有启用的字典类型

```sql
SELECT * FROM sys_dict_type WHERE status = 1 AND is_deleted = 0 ORDER BY sort_order;
```

#### 查询指定类型的字典项

```sql
SELECT * FROM sys_dict_item 
WHERE dict_type_code = 'USER_STATUS' AND status = 1 AND is_deleted = 0 
ORDER BY sort_order;
```

#### 查询分组的字典项

```sql
SELECT * FROM sys_dict_item 
WHERE dict_type_code = 'PRODUCT_CATEGORY' AND group_code = 'ELECTRONICS' 
AND status = 1 AND is_deleted = 0 
ORDER BY sort_order;
```

### 2. 插入操作

#### 插入字典类型

```sql
INSERT INTO sys_dict_type (
  uuid, dict_type_code, dict_type_name, description, sort_order, status, created_by
) VALUES (
  UUID(), 'USER_STATUS', '用户状态', '系统用户状态管理', 100, 1, 'admin'
);
```

#### 插入字典项

```sql
INSERT INTO sys_dict_item (
  uuid, dict_type_code, dict_value, dict_label, group_code, group_name, sort_order, status, created_by
) VALUES (
  UUID(), 'USER_STATUS', 'ENABLED', '启用', NULL, NULL, 10, 1, 'admin'
), (
  UUID(), 'USER_STATUS', 'DISABLED', '禁用', NULL, NULL, 20, 1, 'admin'
);
```

### 3. 更新操作

#### 更新字典类型

```sql
UPDATE sys_dict_type 
SET dict_type_name = '用户状态管理', description = '系统用户状态的统一管理', 
    sort_order = 50, updated_by = 'admin' 
WHERE dict_type_code = 'USER_STATUS' AND is_deleted = 0;
```

#### 更新字典项

```sql
UPDATE sys_dict_item 
SET dict_label = '已启用', sort_order = 5, updated_by = 'admin' 
WHERE dict_type_code = 'USER_STATUS' AND dict_value = 'ENABLED' AND is_deleted = 0;
```

### 4. 删除操作

#### 逻辑删除字典类型

```sql
UPDATE sys_dict_type 
SET is_deleted = 1, updated_by = 'admin' 
WHERE dict_type_code = 'USER_STATUS';
```

#### 逻辑删除字典项

```sql
UPDATE sys_dict_item 
SET is_deleted = 1, updated_by = 'admin' 
WHERE dict_type_code = 'USER_STATUS' AND dict_value = 'DISABLED';
```

### 5. 批量操作

#### 批量插入字典项

```sql
INSERT INTO sys_dict_item (
  uuid, dict_type_code, dict_value, dict_label, sort_order, status, created_by
) VALUES 
(UUID(), 'PAYMENT_METHOD', 'ALIPAY', '支付宝', 10, 1, 'admin'),
(UUID(), 'PAYMENT_METHOD', 'WECHAT', '微信支付', 20, 1, 'admin'),
(UUID(), 'PAYMENT_METHOD', 'CREDIT_CARD', '信用卡', 30, 1, 'admin');
```

## 前端实现标准

### 1. 控件使用规范

- **禁止使用普通输入框**：所有涉及码值选择的界面元素，必须使用选项类型控件
- **推荐控件类型**：
  - 下拉框（Select）：适用于选项较多的场景
  - 单选按钮组（Radio Group）：适用于选项较少的场景
  - 开关（Switch）：适用于二选一的场景
  - 标签选择器（Tag Select）：适用于多选场景

### 2. 数据获取规范

- **动态获取数据**：所有字典项数据必须通过后端接口动态获取并赋值
- **禁止硬编码**：严禁在前端代码中硬编码写死任何字典数据
- **缓存策略**：合理使用缓存，减少API请求次数
- **实时更新**：当数据字典发生变更时，及时更新前端缓存

### 3. 后端接口设计

#### 获取字典类型列表

```javascript
// GET /api/dict/types
// 响应格式
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "dict_type_code": "USER_STATUS",
      "dict_type_name": "用户状态",
      "description": "系统用户状态管理"
    },
    // 更多字典类型
  ]
}
```

#### 获取指定类型的字典项

```javascript
// GET /api/dict/items/{dictTypeCode}
// 响应格式
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "dict_value": "ENABLED",
      "dict_label": "启用",
      "sort_order": 10
    },
    {
      "dict_value": "DISABLED",
      "dict_label": "禁用",
      "sort_order": 20
    }
  ]
}
```

#### 获取分组的字典项

```javascript
// GET /api/dict/items/{dictTypeCode}/group/{groupCode}
// 响应格式
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "dict_value": "LAPTOP",
      "dict_label": "笔记本电脑",
      "group_code": "ELECTRONICS",
      "group_name": "电子产品",
      "sort_order": 10
    },
    {
      "dict_value": "SMARTPHONE",
      "dict_label": "智能手机",
      "group_code": "ELECTRONICS",
      "group_name": "电子产品",
      "sort_order": 20
    }
  ]
}
```

### 4. 前端代码示例

#### React 下拉框示例

```javascript
import React, { useState, useEffect } from 'react';
import { Select } from 'antd';
import apiClient from '../utils/apiClient';

const { Option } = Select;

const UserStatusSelect = ({ value, onChange }) => {
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchOptions = async () => {
      try {
        setLoading(true);
        // 动态获取字典项
        const data = await apiClient.get('/api/dict/items/USER_STATUS');
        setOptions(data);
      } catch (error) {
        console.error('Failed to fetch user status options:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchOptions();
  }, []);

  return (
    <Select
      value={value}
      onChange={onChange}
      loading={loading}
      placeholder="请选择用户状态"
      style={{ width: 200 }}
    >
      {options.map(option => (
        <Option key={option.dict_value} value={option.dict_value}>
          {option.dict_label}
        </Option>
      ))}
    </Select>
  );
};

export default UserStatusSelect;
```

#### Vue 单选按钮组示例

```vue
<template>
  <div>
    <label>用户状态：</label>
    <el-radio-group v-model="userStatus" @change="handleChange">
      <el-radio
        v-for="option in options"
        :key="option.dict_value"
        :label="option.dict_value"
      >
        {{ option.dict_label }}
      </el-radio>
    </el-radio-group>
  </div>
</template>

<script>
export default {
  name: 'UserStatusRadio',
  props: {
    value: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      userStatus: this.value,
      options: [],
      loading: false
    };
  },
  watch: {
    value(newValue) {
      this.userStatus = newValue;
    }
  },
  mounted() {
    this.fetchOptions();
  },
  methods: {
    async fetchOptions() {
      try {
        this.loading = true;
        // 动态获取字典项
        const response = await this.$axios.get('/api/dict/items/USER_STATUS');
        this.options = response.data;
      } catch (error) {
        console.error('Failed to fetch user status options:', error);
      } finally {
        this.loading = false;
      }
    },
    handleChange(value) {
      this.$emit('input', value);
      this.$emit('change', value);
    }
  }
};
</script>
```

### 5. 数据字典管理界面

#### 功能需求

- 字典类型的增删改查
- 字典项的增删改查
- 字典项的分组管理
- 字典项的排序管理
- 字典的启用/禁用功能
- 字典的导入/导出功能
- 字典变更历史记录

#### 设计要点

- 清晰的分类展示
- 便捷的搜索功能
- 直观的排序操作
- 友好的编辑界面
- 完善的权限控制
- 详细的操作日志

## 最佳实践

### 1. 命名规范

- 使用有意义的字典类型编码和字典值
- 保持命名的一致性和可读性
- 避免使用过于复杂或过长的编码

### 2. 性能优化

- 合理使用缓存，减少数据库查询次数
- 对频繁使用的数据字典进行预热
- 优化SQL查询，添加适当的索引
- 分页加载大量字典数据

### 3. 安全性

- 对数据字典的操作进行权限控制
- 记录数据字典的变更历史
- 实现数据字典的版本管理
- 定期备份数据字典

### 4. 可维护性

- 编写详细的数据字典文档
- 建立数据字典的变更流程
- 定期审查数据字典的使用情况
- 及时清理不再使用的数据字典

### 5. 扩展性

- 设计灵活的数据字典结构，支持未来扩展
- 预留分组功能，支持复杂的数据字典场景
- 支持多种数据字典的导入/导出格式
- 提供API接口，支持外部系统调用

## 常见问题

### Q: 如何确定哪些数据需要使用数据字典？
A: 以下情况建议使用数据字典：
   - 系统中频繁使用的静态数据
   - 需要统一管理的编码和分类
   - 可能会发生变化的数据
   - 多个模块共享的数据
   - 需要进行统计和分析的数据

### Q: 数据字典和枚举类的区别是什么？
A: 数据字典存储在数据库中，可以动态修改，不需要重新部署系统；枚举类硬编码在代码中，修改后需要重新编译和部署。对于经常变化的数据，建议使用数据字典；对于固定不变的数据，可以使用枚举类。

### Q: 如何处理数据字典的历史数据？
A: 建议使用逻辑删除，保留历史数据的完整性；同时记录数据字典的变更历史，便于追溯和审计。

### Q: 数据字典的性能问题如何解决？
A: 可以通过以下方式优化性能：
   - 合理使用缓存
   - 对频繁使用的数据字典进行预热
   - 优化SQL查询
   - 分页加载大量字典数据

### Q: 如何确保数据字典的一致性？
A: 可以通过以下方式确保一致性：
   - 建立严格的数据字典管理流程
   - 对数据字典的操作进行审核
   - 实现数据字典的版本管理
   - 定期审查数据字典的使用情况

## 版本历史

- v1.0.0: 初始版本，定义了数据字典管理流程、SQL操作规范和前端实现标准
- v1.1.0: 完善了表结构说明和最佳实践
- v1.2.0: 增加了前端代码示例和常见问题解答
- v1.3.0: 优化了数据字典管理流程和SQL操作规范