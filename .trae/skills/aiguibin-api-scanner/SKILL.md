---
name: aiguibin-api-scanner
description: |
  从大型前端/全栈项目中全面识别前后端接口并整理输出为Excel文档。使用此技能当用户需要：扫描项目中的API接口定义、提取接口URL、生成接口清单文档、处理URL格式规范化问题、进行接口去重和统计。触发场景包括：用户提到"接口清单"、"API文档"、"接口扫描"、"提取接口"、"接口统计"、"URL规范化"等关键词，或需要从代码中提取所有HTTP请求端点。该技能特别擅长处理大型项目，支持分批处理和长时间稳定运行。
---

# API接口扫描与文档生成技能

## 概述

本技能用于从大型前端/全栈项目中全面识别前后端接口，自动提取接口定义，规范化URL格式，并生成结构化的Excel接口清单文档。

## 核心功能

1. **全面扫描**: 递归扫描项目目录，识别所有包含接口定义的文件
2. **模式识别**: 支持多种接口定义模式（url: '', url: "", url: ``）
3. **URL规范化**: 自动检测并修复缺少开头"/"的URL
4. **去重处理**: 确保接口数据唯一性
5. **Excel输出**: 生成包含完整字段的结构化Excel文档
6. **质量保障**: 全量检查确保无遗漏

## 执行流程

### 第一步：项目结构分析

首先分析项目目录结构，确定源代码位置：

```
项目根目录/
├── src/           # 源代码目录（优先扫描）
├── app/           # 应用目录
├── api/           # API定义目录
└── views/         # 视图组件目录
```

使用LS工具探索目录结构，识别关键目录。

### 第二步：接口模式扫描

使用Grep工具扫描所有相关文件，识别以下模式：

```javascript
// 模式1: 单引号
url: '/api/path'

// 模式2: 双引号
url: "/api/path"

// 模式3: 模板字符串
url: `/api/path/${id}`

// 模式4: 缺少开头/（需要规范化）
url: 'api/path'
```

扫描命令示例：
```bash
grep -rn "url:\s*['\"\`]" src/
```

### 第三步：URL规范化处理

对于识别到的URL进行规范化处理：

```javascript
function normalizeUrl(url) {
    // 1. 去除空白
    url = url.trim();
    
    // 2. 检查是否需要添加前缀
    if (!url.startsWith('/') && !url.startsWith('http') && !url.startsWith('${')) {
        url = '/' + url;
    }
    
    // 3. 处理模板变量
    url = url.replace(/\$\{[^}]+\}/g, '');
    
    // 4. 清理多余斜杠
    url = url.replace(/\/+/g, '/').replace(/\/$/, '');
    
    return url;
}
```

### 第四步：数据去重与整理

```javascript
// 使用Set进行去重
const uniqueUrls = [...new Set(allUrls)];

// 构建接口详情
const apiList = uniqueUrls.map(url => ({
    url: url,
    desc: getDescription(url),
    method: getMethod(url),
    params: '',
    module: getModule(url),
    isNormalized: wasNormalized(url)
}));
```

### 第五步：Excel文档生成

使用xlsx库生成Excel文档：

```javascript
const XLSX = require('xlsx');

const wb = XLSX.utils.book_new();
const headers = ['序号', '接口地址', '接口描述', '请求方式', '接口参数', '所属模块', '是否规范化URL'];
const data = [headers];

apiList.forEach((api, index) => {
    data.push([
        index + 1,
        api.url,
        api.desc,
        api.method,
        api.params,
        api.module,
        api.isNormalized ? '是(已添加/前缀)' : '否'
    ]);
});

const ws = XLSX.utils.aoa_to_sheet(data);
ws['!cols'] = [
    { wch: 8 },   // 序号
    { wch: 80 },  // 接口地址
    { wch: 40 },  // 接口描述
    { wch: 12 },  // 请求方式
    { wch: 30 },  // 接口参数
    { wch: 20 },  // 所属模块
    { wch: 20 }   // 是否规范化
];

XLSX.utils.book_append_sheet(wb, ws, '接口清单');
XLSX.writeFile(wb, outputPath);
```

### 第六步：全量检查验证

生成验证报告，确保数据完整性：

```javascript
console.log('========================================');
console.log('Excel文件验证报告');
console.log('========================================');
console.log(`总接口数量: ${data.length}`);
console.log(`规范化URL数量: ${normalizedCount}`);
console.log('\n模块分布统计:');
// 输出各模块接口数量
```

## 输入参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| projectPath | string | 是 | 项目根目录路径 |
| outputPath | string | 否 | Excel输出路径，默认为项目目录下 |
| fileExtensions | array | 否 | 扫描的文件扩展名，默认['.js', '.vue', '.ts'] |
| excludeDirs | array | 否 | 排除的目录，默认['node_modules', 'dist'] |

## 输出格式

### Excel文档结构

| 列名 | 宽度 | 说明 |
|------|------|------|
| 序号 | 8 | 接口序号 |
| 接口地址 | 80 | 完整的接口URL |
| 接口描述 | 40 | 接口功能描述 |
| 请求方式 | 12 | GET/POST/PUT/DELETE |
| 接口参数 | 30 | 接口参数说明 |
| 所属模块 | 20 | 接口所属业务模块 |
| 是否规范化URL | 20 | 是否添加了/前缀 |

### 验证报告格式

```
========================================
Excel文件验证报告
========================================
文件路径: [输出路径]
工作表名称: 接口清单
总接口数量: [数量]
规范化URL数量: [数量]

模块分布统计:
  [模块名]: [数量]个接口
  ...

前10条记录:
  1. [URL] - [描述] [[请求方式]]
  ...

========================================
验证完成
========================================
```

## 模块识别规则

根据URL路径自动识别所属模块：

```javascript
function getModule(url) {
    if (url.includes('/homeCalenderRemind')) return '日历模块';
    if (url.includes('/homeCardManage')) return '卡片管理';
    if (url.includes('/qa/')) return '智能客服';
    if (url.includes('/workflow')) return '工作流';
    if (url.includes('/ucmp-manage-base')) return '基础管理';
    if (url.includes('/ucmp-business-corporate')) return '对公业务';
    if (url.includes('/ucmp-business-retail')) return '零售业务';
    if (url.includes('/ucmp-collateral-manage')) return '押品管理';
    if (url.includes('/ucmp-cust-manage')) return '客户管理';
    if (url.includes('/tansun-tcp-system-boot')) return '系统启动';
    if (url.includes('/tansun-tcp-common')) return '公共服务';
    if (url.includes('/tansun-tcp-workflow')) return '工作流服务';
    // ... 更多模块映射
    return '其他模块';
}
```

## 请求方式推断规则

根据URL路径关键词推断请求方式：

```javascript
function getMethod(url) {
    const getKeywords = ['get', 'query', 'list', 'page', 'tree', 'find', 'select'];
    const lastPart = url.split('/').pop().toLowerCase();
    
    for (const keyword of getKeywords) {
        if (lastPart.includes(keyword)) {
            return 'GET';
        }
    }
    return 'POST'; // 默认POST
}
```

## 错误处理

### 1. 文件读取错误

```javascript
try {
    const content = fs.readFileSync(fullPath, 'utf-8');
    extractUrlsFromFile(fullPath, content);
} catch (err) {
    console.log(`无法读取文件: ${fullPath}`);
    // 继续处理其他文件
}
```

### 2. Excel写入错误

```javascript
try {
    XLSX.writeFile(wb, outputPath);
} catch (err) {
    console.error('写入Excel文件失败:', err.message);
    // 尝试备用路径
    const backupPath = outputPath.replace('.xlsx', `_${Date.now()}.xlsx`);
    XLSX.writeFile(wb, backupPath);
}
```

### 3. 内存溢出处理

对于超大项目，采用分批处理：

```javascript
const BATCH_SIZE = 1000;
for (let i = 0; i < allFiles.length; i += BATCH_SIZE) {
    const batch = allFiles.slice(i, i + BATCH_SIZE);
    processBatch(batch);
    // 定期清理内存
    if (i % 5000 === 0) {
        global.gc && global.gc();
    }
}
```

## 使用示例

### 示例1：基本使用

```
用户：扫描 d:\project\app 目录下的所有接口，生成接口清单Excel
```

执行步骤：
1. 扫描项目目录结构
2. 识别所有包含 url: 的文件
3. 提取并规范化URL
4. 生成Excel文档

### 示例2：指定输出路径

```
用户：从项目中提取所有API接口，输出到 d:\output\接口清单.xlsx
```

### 示例3：处理特定文件类型

```
用户：只扫描 .vue 文件中的接口定义，生成接口文档
```

## 接口识别范围

### 文件类型覆盖

必须对项目中所有相关文件进行彻底检查，确保不遗漏任何接口定义。扫描范围包括但不限于：

| 文件类型 | 说明 | 优先级 |
|----------|------|--------|
| `.js` | JavaScript源文件 | 高 |
| `.vue` | Vue组件文件 | 高 |
| `.ts` | TypeScript源文件 | 高 |
| `.jsx` | React JSX文件 | 中 |
| `.tsx` | React TSX文件 | 中 |
| `.json` | 配置文件（如API配置） | 中 |

### 目录扫描策略

```
优先扫描目录:
├── src/api/          # API定义目录（最高优先级）
├── src/views/        # 视图组件目录
├── src/common/       # 公共模块目录
├── src/utils/        # 工具函数目录
└── src/components/   # 组件目录

排除目录:
├── node_modules/     # 依赖包
├── dist/             # 构建输出
├── build/            # 构建临时文件
└── .git/             # 版本控制
```

### 接口模式识别

必须识别以下所有接口定义模式：

```javascript
// 模式1: 单引号
url: '/api/path'
url: 'api/path'  // 缺少开头/

// 模式2: 双引号
url: "/api/path"
url: "api/path"  // 缺少开头/

// 模式3: 模板字符串
url: `/api/path/${id}`
url: `api/path/${id}`  // 缺少开头/

// 模式4: 变量拼接
url: baseUrl + '/api/path'
url: `${baseUrl}/api/path`

// 模式5: 注释中的接口（需标记）
// url: '/api/old-path'
```

## Excel文档内容要求

### 必需字段

| 字段名 | 宽度 | 说明 | 必填 |
|--------|------|------|------|
| 序号 | 8 | 接口序号，从1开始递增 | 是 |
| 接口地址 | 80 | 完整的接口URL，必须以/开头 | 是 |
| 接口描述 | 40 | 接口功能描述，根据URL推断或手动补充 | 是 |
| 请求方式 | 12 | GET/POST/PUT/DELETE，根据URL关键词推断 | 是 |
| 接口参数 | 30 | 接口参数说明，可后续补充 | 否 |
| 所属模块 | 20 | 接口所属业务模块 | 是 |
| 来源文件数 | 12 | 引用该接口的文件数量 | 否 |
| 是否规范化URL | 20 | 是否添加了/前缀 | 是 |

### 去重处理规则

```javascript
// 去重逻辑
const uniqueUrls = [...new Set(allUrls)];

// URL规范化后去重
function normalizeAndDeduplicate(urls) {
    const normalized = urls.map(url => {
        // 1. 去除空白
        url = url.trim();
        // 2. 添加/前缀
        if (!url.startsWith('/') && !url.startsWith('http')) {
            url = '/' + url;
        }
        // 3. 清理模板变量
        url = url.replace(/\$\{[^}]+\}/g, '');
        // 4. 清理多余斜杠
        url = url.replace(/\/+/g, '/').replace(/\/$/, '');
        return url;
    });
    
    // 使用Set去重
    return [...new Set(normalized)];
}
```

## 执行方式

### 分批处理模式

由于项目规模较大，必须采用分批处理模式：

```javascript
const BATCH_SIZE = 500;  // 每批处理500个文件
const MEMORY_CLEANUP_INTERVAL = 2000;  // 每2000个文件清理一次内存

async function processInBatches(files) {
    const results = [];
    for (let i = 0; i < files.length; i += BATCH_SIZE) {
        const batch = files.slice(i, i + BATCH_SIZE);
        const batchResults = await processBatch(batch);
        results.push(...batchResults);
        
        // 进度报告
        console.log(`进度: ${Math.min(i + BATCH_SIZE, files.length)}/${files.length} 文件已处理`);
        
        // 定期清理内存
        if (i % MEMORY_CLEANUP_INTERVAL === 0 && i > 0) {
            global.gc && global.gc();
            console.log('内存清理完成');
        }
    }
    return results;
}
```

### 长时间运行保障

```javascript
// 1. 设置超时时间为无限
process.env.UV_THREADPOOL_SIZE = 128;

// 2. 错误自动恢复
process.on('uncaughtException', (err) => {
    console.error('捕获到未处理异常:', err);
    // 记录错误但继续执行
    logError(err);
});

// 3. 进度持久化
function saveProgress(processedFiles, currentIndex) {
    const progress = {
        timestamp: new Date().toISOString(),
        processedCount: currentIndex,
        totalCount: processedFiles.length,
        status: 'in_progress'
    };
    fs.writeFileSync('.scan_progress.json', JSON.stringify(progress, null, 2));
}

// 4. 断点续传
function loadProgress() {
    if (fs.existsSync('.scan_progress.json')) {
        return JSON.parse(fs.readFileSync('.scan_progress.json', 'utf-8'));
    }
    return null;
}
```

### 无需人工确认

```javascript
// 自动执行配置
const AUTO_CONFIG = {
    skipConfirmation: true,      // 跳过所有确认步骤
    overwriteExisting: true,     // 自动覆盖已存在的文件
    continueOnError: true,       // 遇到错误继续执行
    silentMode: false,           // 非静默模式，输出进度信息
    workingDirectory: process.cwd()  // 工作目录为当前目录
};

// 执行前检查权限
function checkPermissions() {
    const cwd = process.cwd();
    try {
        fs.accessSync(cwd, fs.constants.R_OK | fs.constants.W_OK);
        console.log(`工作目录权限检查通过: ${cwd}`);
        return true;
    } catch (err) {
        console.error(`工作目录权限不足: ${cwd}`);
        return false;
    }
}
```

## 质量保障

### 全量检查流程

```javascript
async function fullQualityCheck(allFiles, extractedApis) {
    console.log('========================================');
    console.log('开始全量质量检查');
    console.log('========================================');
    
    // 1. 文件覆盖率检查
    const coverage = calculateCoverage(allFiles, extractedApis);
    console.log(`文件覆盖率: ${coverage.percentage}%`);
    console.log(`已扫描文件: ${coverage.scanned}/${coverage.total}`);
    
    // 2. 接口完整性检查
    const integrity = checkIntegrity(extractedApis);
    console.log(`接口完整性: ${integrity.valid}/${integrity.total}`);
    
    // 3. 去重验证
    const duplicates = findDuplicates(extractedApis);
    if (duplicates.length > 0) {
        console.warn(`发现 ${duplicates.length} 个重复接口`);
    } else {
        console.log('去重验证通过: 无重复接口');
    }
    
    // 4. URL格式验证
    const invalidUrls = validateUrls(extractedApis);
    if (invalidUrls.length > 0) {
        console.warn(`发现 ${invalidUrls.length} 个无效URL`);
    } else {
        console.log('URL格式验证通过');
    }
    
    // 5. 模块归属验证
    const unassignedApis = extractedApis.filter(api => api.module === '其他模块');
    console.log(`未归属模块的接口数量: ${unassignedApis.length}`);
    
    console.log('========================================');
    console.log('质量检查完成');
    console.log('========================================');
    
    return {
        coverage,
        integrity,
        duplicates,
        invalidUrls,
        unassignedApis
    };
}
```

### 逐一排查机制

```javascript
function verifyEachFile(files, apiMap) {
    const results = [];
    
    for (const file of files) {
        const content = fs.readFileSync(file, 'utf-8');
        const apisInFile = extractApis(content);
        
        // 检查是否有遗漏
        const recordedApis = apiMap.get(file) || [];
        const missing = apisInFile.filter(api => !recordedApis.includes(api));
        
        if (missing.length > 0) {
            results.push({
                file,
                status: 'incomplete',
                missingApis: missing
            });
        } else {
            results.push({
                file,
                status: 'complete',
                apiCount: apisInFile.length
            });
        }
    }
    
    return results;
}
```

## 交付物

### 1. 执行计划文档

**文件名格式**: `日期时分秒.模型名称.md`

**示例**: `20250128153045.claude-3-opus.md`

**文档内容模板**:

```markdown
# API接口扫描执行计划

## 基本信息
- 执行时间: [YYYY-MM-DD HH:mm:ss]
- 模型名称: [模型标识]
- 项目路径: [项目根目录]
- 输出路径: [Excel输出路径]

## 扫描范围
- 文件类型: [.js, .vue, .ts, ...]
- 扫描目录: [目录列表]
- 排除目录: [排除列表]

## 执行步骤
1. 项目结构分析
2. 接口模式扫描
3. URL规范化处理
4. 数据去重与整理
5. Excel文档生成
6. 全量检查验证

## 预期输出
- 接口数量预估: [数量]
- 预计耗时: [时间]
- 输出文件: [文件名]

## 质量保障
- [ ] 文件覆盖率 >= 100%
- [ ] 接口去重完成
- [ ] URL格式规范化
- [ ] 模块归属完整

## 执行状态
- 状态: [待执行/执行中/已完成]
- 进度: [0%]
```

### 2. 接口清单Excel文档

**文件名格式**: `日期时分秒.模型名称.xlsx`

**示例**: `20250128153045.claude-3-opus.xlsx`

**文档结构**:

| Sheet名称 | 说明 |
|-----------|------|
| 接口清单 | 主要接口列表 |
| 统计汇总 | 模块分布、请求方式统计 |
| 验证报告 | 质量检查结果 |

### 交付物生成代码

```javascript
function generateDeliverables(apis, modelName) {
    const timestamp = formatDate(new Date(), 'YYYYMMDDHHmmss');
    
    // 1. 生成执行计划文档
    const planPath = `${timestamp}.${modelName}.md`;
    const planContent = generatePlanDocument(apis, modelName);
    fs.writeFileSync(planPath, planContent);
    console.log(`执行计划文档已生成: ${planPath}`);
    
    // 2. 生成Excel文档
    const excelPath = `${timestamp}.${modelName}.xlsx`;
    generateExcel(apis, excelPath);
    console.log(`接口清单Excel已生成: ${excelPath}`);
    
    return {
        planPath,
        excelPath
    };
}

function formatDate(date, format) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    return format
        .replace('YYYY', year)
        .replace('MM', month)
        .replace('DD', day)
        .replace('HH', hours)
        .replace('mm', minutes)
        .replace('ss', seconds);
}
```

## 质量保障检查清单

### 扫描阶段
- [ ] 已扫描所有相关目录
- [ ] 已识别所有 url: 模式
- [ ] 已处理缺少开头/的URL
- [ ] 已进行去重处理

### 验证阶段
- [ ] 已生成Excel文档
- [ ] 已输出验证报告
- [ ] 已检查数据完整性
- [ ] 文件覆盖率达到100%
- [ ] 无重复接口记录

### 交付阶段
- [ ] 执行计划文档已生成
- [ ] Excel文档命名符合规范
- [ ] 所有字段填写完整

## 注意事项

1. **大型项目处理**: 对于包含数千个文件的项目，扫描可能需要较长时间，程序会自动分批处理，请耐心等待
2. **URL规范化**: 所有缺少开头"/"的URL都会被自动添加前缀，并在Excel中标记
3. **去重机制**: 相同URL只保留一条记录，确保数据唯一性
4. **模块识别**: 基于URL路径关键词自动识别，可能需要人工复核
5. **请求方式**: 基于URL关键词推断，建议人工确认
6. **执行中断**: 如遇中断，程序支持断点续传，可从上次进度继续
7. **权限要求**: 程序在工作目录下拥有绝对操作权限，无需人工确认

## 依赖要求

- Node.js 环境 (v14.0.0+)
- xlsx npm包（用于Excel生成）
- 文件系统访问权限
- 足够的内存空间（建议4GB+）

## 脚本文件

技能包含以下辅助脚本：

- `scripts/scan_apis.js` - 核心扫描脚本
- `scripts/verify_excel.js` - 验证脚本

详细脚本内容请参考 scripts/ 目录。
