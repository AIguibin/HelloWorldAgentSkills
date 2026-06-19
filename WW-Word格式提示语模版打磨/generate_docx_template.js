// 技术设计文档通用模板 - docx 生成脚本
// 默认9大章，内容用示例填写，后续可根据实际内容替换
// 使用 docx-js 库生成专业 Word 文档

const fs = require('fs');
const path = require('path');

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat,
  TableOfContents, HeadingLevel, BorderStyle, WidthType, ShadingType,
  VerticalAlign, PageNumber, PageBreak,
} = require('docx');

// ============ 常量定义 ============
const PAGE_WIDTH = 12240;
const PAGE_HEIGHT = 15840;
const MARGIN = 1440;
const CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN;

const FONT_CN = '宋体';
const FONT_EN = 'Arial';
const FONT_CODE = 'Courier New';

const COLOR_HEADER_BG = 'D5E8F0';
const COLOR_CODE_BG = 'F5F5F5';
const COLOR_BORDER = 'BFBFBF';
const COLOR_BLACK = '000000';
const COLOR_DARK_BLUE = '1F3864';
const COLOR_ACCENT = '5B9BD5';
const COLOR_GRAY = '595959';
const COLOR_DARK_GRAY = '333333';

// ============ 辅助函数 ============
const border = { style: BorderStyle.SINGLE, size: 4, color: COLOR_BORDER };
const borders = { top: border, bottom: border, left: border, right: border };

function P(text, opts = {}) {
  const runOpts = { text: String(text == null ? '' : text), font: FONT_CN, size: 22 };
  if (opts.bold) runOpts.bold = true;
  if (opts.italics) runOpts.italics = true;
  if (opts.color) runOpts.color = opts.color;
  if (opts.size) runOpts.size = opts.size;
  if (opts.font) runOpts.font = opts.font;
  return new Paragraph({
    spacing: { before: opts.before || 0, after: opts.after || 120, line: 360 },
    indent: opts.noIndent ? undefined : { firstLine: 480 },
    alignment: opts.alignment || AlignmentType.LEFT,
    children: [new TextRun(runOpts)],
  });
}

function H1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 240 },
    children: [new TextRun({ text, font: FONT_CN, size: 32, bold: true, color: COLOR_BLACK })],
  });
}
function H2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 180 },
    children: [new TextRun({ text, font: FONT_CN, size: 28, bold: true, color: COLOR_BLACK })],
  });
}
function H3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 200, after: 120 },
    children: [new TextRun({ text, font: FONT_CN, size: 24, bold: true, color: COLOR_BLACK })],
  });
}

function headerCell(text, width) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: COLOR_HEADER_BG, type: ShadingType.CLEAR, color: 'auto' },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 0, after: 0 },
      children: [new TextRun({ text: String(text), font: FONT_CN, size: 22, bold: true, color: COLOR_BLACK })],
    })],
  });
}

function cell(text, width, opts = {}) {
  const children = [];
  const lines = String(text == null ? '' : text).split('\n');
  lines.forEach((line, i) => {
    children.push(new Paragraph({
      alignment: opts.alignment || AlignmentType.LEFT,
      spacing: { before: 0, after: i === lines.length - 1 ? 0 : 60 },
      children: [new TextRun({
        text: line,
        font: FONT_CN,
        size: 20,
        bold: opts.bold || false,
        color: opts.color || COLOR_BLACK,
      })],
    }));
  });
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    verticalAlign: VerticalAlign.CENTER,
    children,
  });
}

function makeTable(headers, rows, columnWidths) {
  const tableWidth = columnWidths.reduce((a, b) => a + b, 0);
  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map((h, i) => headerCell(h, columnWidths[i])),
  });
  const dataRows = rows.map(r => new TableRow({
    children: r.map((c, i) => cell(c, columnWidths[i])),
  }));
  return new Table({
    width: { size: tableWidth, type: WidthType.DXA },
    columnWidths,
    rows: [headerRow, ...dataRows],
  });
}

function codeBlock(code) {
  const lines = code.split('\n');
  return lines.map(line => new Paragraph({
    spacing: { before: 0, after: 0, line: 280 },
    shading: { fill: COLOR_CODE_BG, type: ShadingType.CLEAR, color: 'auto' },
    children: [new TextRun({
      text: line || ' ',
      font: FONT_CODE,
      size: 18,
      color: COLOR_DARK_GRAY,
    })],
  }));
}

function bullet(text, level = 0) {
  return new Paragraph({
    numbering: { reference: 'bullets', level },
    spacing: { before: 0, after: 80, line: 360 },
    children: [new TextRun({ text, font: FONT_CN, size: 22 })],
  });
}

function emptyP() {
  return new Paragraph({ children: [new TextRun({ text: ' ', font: FONT_CN, size: 22 })] });
}

function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

// ============ 文档内容构建 ============
const children = [];

// ==================== 封面 ====================
children.push(new Paragraph({ spacing: { before: 2400 }, children: [new TextRun({ text: ' ' })] }));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 0, after: 240 },
  children: [new TextRun({
    text: '【项目名称】',
    font: FONT_CN, size: 52, bold: true, color: COLOR_DARK_BLUE,
  })],
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 0, after: 240 },
  children: [new TextRun({
    text: '【文档标题】',
    font: FONT_CN, size: 52, bold: true, color: COLOR_DARK_BLUE,
  })],
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 0, after: 240 },
  children: [new TextRun({
    text: '【文档副标题（可选）】',
    font: FONT_CN, size: 28, color: COLOR_ACCENT,
  })],
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 0, after: 1200 },
  children: [new TextRun({
    text: 'English Subtitle (Optional)',
    font: FONT_EN, size: 24, italics: true, color: COLOR_ACCENT,
  })],
}));

const coverTable = new Table({
  width: { size: 6000, type: WidthType.DXA },
  columnWidths: [2000, 4000],
  alignment: AlignmentType.CENTER,
  rows: [
    new TableRow({ children: [
      cell('文档版本', 2000, { bold: true, alignment: AlignmentType.CENTER }),
      cell('V1.0.0', 4000, { alignment: AlignmentType.CENTER }),
    ]}),
    new TableRow({ children: [
      cell('发布日期', 2000, { bold: true, alignment: AlignmentType.CENTER }),
      cell('YYYY年MM月', 4000, { alignment: AlignmentType.CENTER }),
    ]}),
    new TableRow({ children: [
      cell('编制单位', 2000, { bold: true, alignment: AlignmentType.CENTER }),
      cell('【编制单位名称】', 4000, { alignment: AlignmentType.CENTER }),
    ]}),
    new TableRow({ children: [
      cell('文档密级', 2000, { bold: true, alignment: AlignmentType.CENTER }),
      cell('内部使用', 4000, { alignment: AlignmentType.CENTER }),
    ]}),
    new TableRow({ children: [
      cell('文档状态', 2000, { bold: true, alignment: AlignmentType.CENTER }),
      cell('草稿 / 评审中 / 已定稿', 4000, { alignment: AlignmentType.CENTER }),
    ]}),
  ],
});
children.push(coverTable);
children.push(pageBreak());

// ==================== 修订记录 ====================
children.push(H1('修订记录'));
children.push(makeTable(
  ['版本', '日期', '修订人', '修订内容', '审核人'],
  [
    ['V1.0.0', 'YYYY-MM-DD', '【姓名】', '初始版本', '【姓名】'],
  ],
  [1200, 1800, 1400, 3360, 1600]
));
children.push(pageBreak());

// ==================== 目录 ====================
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 0, after: 360 },
  children: [new TextRun({ text: '目  录', font: FONT_CN, size: 36, bold: true, color: COLOR_BLACK })],
}));
children.push(new TableOfContents('Table of Contents', {
  hyperlink: true,
  headingStyleRange: '1-3',
}));
children.push(pageBreak());

// ==================== 第1章：背景与目标 ====================
children.push(H1('第1章 背景与目标'));

children.push(H2('1.1 业务背景'));
children.push(P('【请在此处填写项目背景信息。说明项目的业务定位、当前阶段、核心目标，以及编写本文档的出发点。】'));
children.push(P('示例：XX系统是公司XX业务的核心平台，当前处于系统设计与架构阶段。本方案立足于XX业务特点，在架构设计阶段将XX能力作为基础模块纳入规划，确保系统上线后具备XX能力，避免后期改造带来的业务中断和成本增加。'));
children.push(P('【请在此处补充业务数据范围、覆盖模块等量化信息。】'));

children.push(H2('1.2 技术需求'));
children.push(P('基于业务特点和技术架构要求，本方案需满足以下核心技术需求：'));
children.push(makeTable(
  ['需求领域', '需求描述', '技术目标'],
  [
    ['需求一', '【请描述具体需求内容】', '【请描述期望达到的技术目标】'],
    ['需求二', '【请描述具体需求内容】', '【请描述期望达到的技术目标】'],
    ['需求三', '【请描述具体需求内容】', '【请描述期望达到的技术目标】'],
    ['需求四', '【请描述具体需求内容】', '【请描述期望达到的技术目标】'],
  ],
  [2000, 4200, 3160]
));

children.push(H2('1.3 总体目标'));
children.push(P('本方案旨在实现以下目标：'));
children.push(makeTable(
  ['目标维度', '目标描述', '实现方式', '预期效果'],
  [
    ['目标一', '【请描述目标】', '【请描述实现方式】', '【请描述预期效果】'],
    ['目标二', '【请描述目标】', '【请描述实现方式】', '【请描述预期效果】'],
    ['目标三', '【请描述目标】', '【请描述实现方式】', '【请描述预期效果】'],
  ],
  [1800, 2600, 2600, 2360]
));

children.push(H2('1.4 适用范围'));
children.push(P('本方案适用于以下范围：'));
children.push(bullet('【适用范围一】'));
children.push(bullet('【适用范围二】'));
children.push(bullet('【适用范围三】'));
children.push(P('本方案不适用于以下场景：【请说明不适用范围】。'));

children.push(pageBreak());

// ==================== 第2章：需求分析 ====================
children.push(H1('第2章 需求分析'));

children.push(H2('2.1 功能需求'));
children.push(P('【请在本节详细描述功能需求，可包含功能列表、用例描述等。】'));
children.push(H3('2.1.1 核心功能一'));
children.push(P('【请描述核心功能一的具体需求。包括功能描述、输入输出、处理逻辑等。】'));
children.push(bullet('需求要点一'));
children.push(bullet('需求要点二'));
children.push(bullet('需求要点三'));

children.push(H3('2.1.2 核心功能二'));
children.push(P('【请描述核心功能二的具体需求。】'));
children.push(bullet('需求要点一'));
children.push(bullet('需求要点二'));

children.push(H2('2.2 非功能需求'));
children.push(P('本方案需满足以下非功能性需求：'));
children.push(makeTable(
  ['需求类别', '具体指标', '量化标准', '验证方法'],
  [
    ['性能', '【请描述性能指标】', '【请填写量化标准】', '【请填写验证方法】'],
    ['可用性', '【请描述可用性指标】', '【请填写量化标准】', '【请填写验证方法】'],
    ['安全性', '【请描述安全性指标】', '【请填写量化标准】', '【请填写验证方法】'],
    ['可扩展性', '【请描述可扩展性指标】', '【请填写量化标准】', '【请填写验证方法】'],
    ['可维护性', '【请描述可维护性指标】', '【请填写量化标准】', '【请填写验证方法】'],
  ],
  [1800, 2200, 2600, 2760]
));

children.push(H2('2.3 约束条件'));
children.push(P('本方案设计需考虑以下约束条件：'));
children.push(bullet('技术约束：【请描述技术栈、框架、数据库等约束】'));
children.push(bullet('业务约束：【请描述业务流程、合规要求等约束】'));
children.push(bullet('资源约束：【请描述人力、时间、预算等约束】'));
children.push(bullet('法规约束：【请描述法律法规、行业标准等约束】'));

children.push(pageBreak());

// ==================== 第3章：总体方案设计 ====================
children.push(H1('第3章 总体方案设计'));

children.push(H2('3.1 设计原则'));
children.push(P('本方案遵循以下设计原则：'));
children.push(makeTable(
  ['原则', '说明', '设计体现'],
  [
    ['原则一', '【请说明原则含义】', '【请说明在本方案中的体现】'],
    ['原则二', '【请说明原则含义】', '【请说明在本方案中的体现】'],
    ['原则三', '【请说明原则含义】', '【请说明在本方案中的体现】'],
    ['原则四', '【请说明原则含义】', '【请说明在本方案中的体现】'],
  ],
  [1600, 3200, 4560]
));

children.push(H2('3.2 总体架构'));
children.push(P('本方案采用分层架构设计，各层职责如下：'));
children.push(makeTable(
  ['层次', '名称', '职责描述', '关键技术'],
  [
    ['L1', '【层名称】', '【请描述该层职责】', '【请填写关键技术】'],
    ['L2', '【层名称】', '【请描述该层职责】', '【请填写关键技术】'],
    ['L3', '【层名称】', '【请描述该层职责】', '【请填写关键技术】'],
    ['L4', '【层名称】', '【请描述该层职责】', '【请填写关键技术】'],
  ],
  [1000, 2000, 3800, 2560]
));

children.push(H2('3.3 核心流程'));
children.push(P('核心业务流程如下：'));
children.push(bullet('步骤一：【请描述步骤一的具体操作】'));
children.push(bullet('步骤二：【请描述步骤二的具体操作】'));
children.push(bullet('步骤三：【请描述步骤三的具体操作】'));
children.push(bullet('步骤四：【请描述步骤四的具体操作】'));

children.push(H2('3.4 关键决策'));
children.push(P('本方案涉及以下关键技术决策：'));
children.push(makeTable(
  ['决策点', '方案A', '方案B', '选择', '理由'],
  [
    ['决策一', '【方案A描述】', '【方案B描述】', '【A/B】', '【选择理由】'],
    ['决策二', '【方案A描述】', '【方案B描述】', '【A/B】', '【选择理由】'],
    ['决策三', '【方案A描述】', '【方案B描述】', '【A/B】', '【选择理由】'],
  ],
  [1400, 2000, 2000, 800, 3160]
));

children.push(pageBreak());

// ==================== 第4章：详细设计 ====================
children.push(H1('第4章 详细设计'));

children.push(H2('4.1 数据模型设计'));
children.push(P('【请在本节详细描述数据模型设计，包括表结构、字段定义、索引设计、分区策略等。】'));
children.push(H3('4.1.1 核心表结构'));
children.push(P('【请描述核心表结构，可使用表格形式展示字段定义。】'));
children.push(makeTable(
  ['字段名', '字段类型', '是否必填', '默认值', '字段说明'],
  [
    ['id', 'BIGINT', '是', '—', '主键ID'],
    ['create_time', 'DATETIME', '是', 'CURRENT_TIMESTAMP', '创建时间'],
    ['update_time', 'DATETIME', '是', 'CURRENT_TIMESTAMP', '修改时间'],
    ['【字段名】', '【类型】', '【是/否】', '【默认值】', '【说明】'],
  ],
  [1800, 1800, 1200, 2000, 2560]
));

children.push(H3('4.1.2 分区设计'));
children.push(P('表分区采用以下策略：'));
children.push(bullet('分区方式：【请描述分区方式，如RANGE分区、LIST分区、组合分区等】'));
children.push(bullet('分区键：【请描述分区键的选择依据】'));
children.push(bullet('分区粒度：【请描述分区粒度，如按日、按月、按年等】'));

children.push(H2('4.2 接口设计'));
children.push(P('【请在本节详细描述接口设计，包括API定义、请求/响应格式、错误码等。】'));
children.push(H3('4.2.1 接口一'));
children.push(P('【请描述接口一的定义。】'));
children.push(makeTable(
  ['项目', '说明'],
  [
    ['接口名称', '【接口名称】'],
    ['请求方式', '【GET/POST/PUT/DELETE】'],
    ['请求路径', '【/api/xxx】'],
    ['请求参数', '【请描述请求参数】'],
    ['响应格式', '【请描述响应格式】'],
    ['错误码', '【请描述错误码】'],
  ],
  [2000, 7360]
));

children.push(H2('4.3 调度策略设计'));
children.push(P('【请描述定时任务调度策略，包括执行频率、触发条件、依赖关系等。】'));
children.push(makeTable(
  ['任务名称', '执行频率', '触发条件', '依赖任务', '超时时间'],
  [
    ['任务一', '【频率】', '【条件】', '【依赖】', '【超时】'],
    ['任务二', '【频率】', '【条件】', '【依赖】', '【超时】'],
    ['任务三', '【频率】', '【条件】', '【依赖】', '【超时】'],
  ],
  [1800, 1600, 2200, 1800, 1960]
));

children.push(pageBreak());

// ==================== 第5章：技术实现方案 ====================
children.push(H1('第5章 技术实现方案'));

children.push(H2('5.1 技术栈'));
children.push(P('本方案采用的技术栈如下：'));
children.push(makeTable(
  ['技术领域', '技术选型', '版本', '选型理由'],
  [
    ['后端框架', '【技术名称】', '【版本号】', '【选型理由】'],
    ['数据库', '【技术名称】', '【版本号】', '【选型理由】'],
    ['缓存', '【技术名称】', '【版本号】', '【选型理由】'],
    ['消息队列', '【技术名称】', '【版本号】', '【选型理由】'],
    ['调度框架', '【技术名称】', '【版本号】', '【选型理由】'],
  ],
  [1800, 2200, 1400, 3960]
));

children.push(H2('5.2 核心代码实现'));
children.push(P('【请在本节提供核心代码实现，包括关键逻辑的代码片段。】'));

children.push(H3('5.2.1 核心逻辑一'));
children.push(P('【请描述核心逻辑一的实现思路。】'));
children.push(...codeBlock(
`-- 示例SQL代码
-- 请根据需要替换为实际的SQL语句
SELECT column1, column2
FROM table_name
WHERE condition1 = ?
  AND condition2 = ?
ORDER BY create_time DESC
LIMIT 100;`
));

children.push(H3('5.2.2 核心逻辑二'));
children.push(P('【请描述核心逻辑二的实现思路。】'));
children.push(...codeBlock(
`// 示例Java代码
// 请根据需要替换为实际的Java代码
public class DemoHandler {
    
    @XxlJob("demoJobHandler")
    public void execute() {
        // 1. 参数校验
        // 2. 数据查询
        // 3. 业务处理
        // 4. 结果写入
        XxlJobHelper.log("任务执行完成");
    }
}`
));

children.push(H2('5.3 部署方案'));
children.push(P('【请描述部署方案，包括部署架构、环境配置、启动流程等。】'));
children.push(bullet('部署环境：【请描述部署环境要求】'));
children.push(bullet('部署步骤：【请描述部署步骤】'));
children.push(bullet('配置项：【请描述关键配置项】'));

children.push(pageBreak());

// ==================== 第6章：部署方案 ====================
children.push(H1('第6章 部署方案'));

children.push(H2('6.1 部署架构'));
children.push(P('【请描述部署架构，包括服务器拓扑、网络架构、负载均衡等。】'));

children.push(H2('6.2 环境要求'));
children.push(P('各环境配置要求如下：'));
children.push(makeTable(
  ['环境', 'CPU', '内存', '磁盘', '操作系统', '依赖软件'],
  [
    ['开发环境', '【配置】', '【配置】', '【配置】', '【OS】', '【依赖】'],
    ['测试环境', '【配置】', '【配置】', '【配置】', '【OS】', '【依赖】'],
    ['生产环境', '【配置】', '【配置】', '【配置】', '【OS】', '【依赖】'],
  ],
  [1400, 1400, 1400, 1400, 1800, 1960]
));

children.push(H2('6.3 部署步骤'));
children.push(P('具体部署步骤如下：'));
children.push(bullet('1. 环境准备：【请描述环境准备步骤】'));
children.push(bullet('2. 数据库初始化：【请描述数据库初始化步骤】'));
children.push(bullet('3. 应用部署：【请描述应用部署步骤】'));
children.push(bullet('4. 配置更新：【请描述配置更新步骤】'));
children.push(bullet('5. 服务启动：【请描述服务启动步骤】'));
children.push(bullet('6. 验证测试：【请描述验证测试步骤】'));

children.push(H2('6.4 回滚方案'));
children.push(P('部署失败时按以下步骤回滚：'));
children.push(bullet('步骤一：【请描述回滚步骤一】'));
children.push(bullet('步骤二：【请描述回滚步骤二】'));
children.push(bullet('步骤三：【请描述回滚步骤三】'));

children.push(pageBreak());

// ==================== 第7章：运维管理 ====================
children.push(H1('第7章 运维管理'));

children.push(H2('7.1 日常运维'));
children.push(P('日常运维工作包括以下内容：'));
children.push(makeTable(
  ['运维项', '频率', '执行人', '操作说明', '预期耗时'],
  [
    ['运维项一', '【频率】', '【角色】', '【操作说明】', '【耗时】'],
    ['运维项二', '【频率】', '【角色】', '【操作说明】', '【耗时】'],
    ['运维项三', '【频率】', '【角色】', '【操作说明】', '【耗时】'],
    ['运维项四', '【频率】', '【角色】', '【操作说明】', '【耗时】'],
  ],
  [1800, 1400, 1400, 3400, 1360]
));

children.push(H2('7.2 监控指标'));
children.push(P('核心监控指标如下：'));
children.push(makeTable(
  ['指标类别', '指标名称', '采集方式', '告警阈值', '通知方式'],
  [
    ['系统指标', '【指标名】', '【采集方式】', '【阈值】', '【通知方式】'],
    ['业务指标', '【指标名】', '【采集方式】', '【阈值】', '【通知方式】'],
    ['性能指标', '【指标名】', '【采集方式】', '【阈值】', '【通知方式】'],
    ['安全指标', '【指标名】', '【采集方式】', '【阈值】', '【通知方式】'],
  ],
  [1600, 1800, 1800, 1800, 2360]
));

children.push(H2('7.3 应急预案'));
children.push(P('针对以下异常场景的应急预案：'));
children.push(H3('7.3.1 场景一：数据库故障'));
children.push(P('【请描述数据库故障场景的应急处理流程。】'));
children.push(bullet('现象：主库不可用'));
children.push(bullet('影响：联机交易中断'));
children.push(bullet('处置：切换至备库，确认数据一致性后恢复业务'));
children.push(bullet('恢复时间目标：RTO ≤ 30分钟'));

children.push(H3('7.3.2 场景二：应用故障'));
children.push(P('【请描述应用故障场景的应急处理流程。】'));
children.push(bullet('现象：应用服务不可用'));
children.push(bullet('影响：部分功能不可用'));
children.push(bullet('处置：重启应用服务，检查日志定位原因'));
children.push(bullet('恢复时间目标：RTO ≤ 10分钟'));

children.push(pageBreak());

// ==================== 第8章：风险与应对 ====================
children.push(H1('第8章 风险与应对'));

children.push(H2('8.1 风险识别'));
children.push(P('本方案识别的风险及应对措施如下：'));
children.push(makeTable(
  ['风险编号', '风险类别', '风险描述', '影响程度', '发生概率', '应对措施'],
  [
    ['R001', '技术风险', '【请描述技术风险】', '高/中/低', '高/中/低', '【请描述应对措施】'],
    ['R002', '业务风险', '【请描述业务风险】', '高/中/低', '高/中/低', '【请描述应对措施】'],
    ['R003', '合规风险', '【请描述合规风险】', '高/中/低', '高/中/低', '【请描述应对措施】'],
    ['R004', '安全风险', '【请描述安全风险】', '高/中/低', '高/中/低', '【请描述应对措施】'],
    ['R005', '运维风险', '【请描述运维风险】', '高/中/低', '高/中/低', '【请描述应对措施】'],
  ],
  [1000, 1400, 2400, 1200, 1200, 2160]
));

children.push(H2('8.2 风险应对策略'));
children.push(P('风险应对策略分为以下四种：'));
children.push(bullet('规避：通过调整方案设计，从源头消除风险'));
children.push(bullet('转移：通过保险、外包等方式将风险转移给第三方'));
children.push(bullet('缓解：采取技术或管理措施，降低风险发生概率或影响程度'));
children.push(bullet('接受：对于低风险，制定应急预案，发生时按预案执行'));

children.push(H2('8.3 回滚方案'));
children.push(P('方案上线后如出现严重问题，按以下步骤回滚：'));
children.push(bullet('步骤一：停止相关定时任务'));
children.push(bullet('步骤二：回滚数据库变更'));
children.push(bullet('步骤三：回滚应用版本'));
children.push(bullet('步骤四：验证回滚结果'));
children.push(bullet('步骤五：通知相关方'));

children.push(pageBreak());

// ==================== 第9章：附录 ====================
children.push(H1('第9章 附录'));

children.push(H2('附录A 术语表'));
children.push(P('本文档使用的术语定义如下：'));
children.push(makeTable(
  ['术语', '英文', '说明'],
  [
    ['【术语一】', '【English】', '【说明】'],
    ['【术语二】', '【English】', '【说明】'],
    ['【术语三】', '【English】', '【说明】'],
  ],
  [2000, 2400, 4960]
));

children.push(H2('附录B 参考文档'));
children.push(P('本文档编写过程中参考了以下资料：'));
children.push(bullet('【参考文档一】'));
children.push(bullet('【参考文档二】'));
children.push(bullet('【参考文档三】'));

children.push(H2('附录C 配置项清单'));
children.push(P('关键配置项清单如下：'));
children.push(makeTable(
  ['配置项', '默认值', '说明', '是否可动态修改'],
  [
    ['【配置项一】', '【默认值】', '【说明】', '是/否'],
    ['【配置项二】', '【默认值】', '【说明】', '是/否'],
    ['【配置项三】', '【默认值】', '【说明】', '是/否'],
  ],
  [2400, 2000, 3200, 1760]
));

children.push(H2('附录D 相关方联系方式'));
children.push(P('项目相关方联系方式：'));
children.push(makeTable(
  ['角色', '姓名', '邮箱', '联系电话'],
  [
    ['项目经理', '【姓名】', '【邮箱】', '【电话】'],
    ['技术负责人', '【姓名】', '【邮箱】', '【电话】'],
    ['业务负责人', '【姓名】', '【邮箱】', '【电话】'],
    ['运维负责人', '【姓名】', '【邮箱】', '【电话】'],
  ],
  [2000, 1800, 3000, 2560]
));

// ============ 生成 docx 文件 ============
const doc = new Document({
  styles: {
    default: {
      heading1: {
        run: { font: FONT_CN, size: 32, bold: true, color: COLOR_BLACK },
        paragraph: { spacing: { before: 360, after: 240 } },
      },
      heading2: {
        run: { font: FONT_CN, size: 28, bold: true, color: COLOR_BLACK },
        paragraph: { spacing: { before: 280, after: 180 } },
      },
      heading3: {
        run: { font: FONT_CN, size: 24, bold: true, color: COLOR_BLACK },
        paragraph: { spacing: { before: 200, after: 120 } },
      },
    },
    paragraphStyles: [{
      id: 'bulletStyle',
      name: 'Bullet List',
      paragraph: {
        spacing: { before: 0, after: 80, line: 360 },
      },
    }],
  },
  numbering: {
    config: [{
      reference: 'bullets',
      levels: [{
        level: 0,
        format: LevelFormat.BULLET,
        text: '\u2022',
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } },
      }, {
        level: 1,
        format: LevelFormat.BULLET,
        text: '\u25E6',
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 1080, hanging: 360 } } },
      }],
    }],
  },
  sections: [{
    properties: {
      page: {
        size: { width: PAGE_WIDTH, height: PAGE_HEIGHT },
        margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({
            text: '【文档标题】',
            font: FONT_CN, size: 18, color: COLOR_GRAY,
          })],
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: '第 ', font: FONT_CN, size: 18, color: COLOR_GRAY }),
            new TextRun({ children: [PageNumber.CURRENT], font: FONT_CN, size: 18, color: COLOR_GRAY }),
            new TextRun({ text: ' 页 / 共 ', font: FONT_CN, size: 18, color: COLOR_GRAY }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], font: FONT_CN, size: 18, color: COLOR_GRAY }),
            new TextRun({ text: ' 页', font: FONT_CN, size: 18, color: COLOR_GRAY }),
          ],
        })],
      }),
    },
    children,
  }],
});

// ============ 输出文件 ============
const OUTPUT_DIR = path.join(
  'e:\\WorkSpace\\HelloWorldAgentSkills\\aiguibin-common-excel',
  'FF--湖北农信新信贷数据库设计策略'
);
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

const OUTPUT_PATH = path.join(OUTPUT_DIR, '技术设计文档模板.docx');
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(OUTPUT_PATH, buffer);
  console.log(`文档模板已生成: ${OUTPUT_PATH}`);
  console.log(`文件大小: ${(buffer.length / 1024).toFixed(2)} KB`);
}).catch(err => {
  console.error('生成失败:', err.message);
  process.exit(1);
});