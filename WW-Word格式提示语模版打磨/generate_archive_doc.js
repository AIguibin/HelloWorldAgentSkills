// 湖北农信新信贷系统数据库清理归档策略方案 - docx 生成脚本
// V3.0.0（前瞻性设计版）- 清理=分区分配，归档=文件导出，严禁历史表方案
// 严格基于《湖北农信清理归档表清单.xlsx》86张表编制
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
const PAGE_WIDTH = 12240;       // US Letter 宽度 (DXA)
const PAGE_HEIGHT = 15840;      // US Letter 高度 (DXA)
const MARGIN = 1440;            // 1 英寸边距
const CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN; // 9360 DXA

const FONT_CN = '宋体';
const FONT_EN = 'Arial';
const FONT_CODE = 'Courier New';

const COLOR_HEADER_BG = 'D5E8F0';   // 表头浅蓝
const COLOR_CODE_BG = 'F5F5F5';     // 代码块浅灰
const COLOR_BORDER = 'BFBFBF';      // 表格边框
const COLOR_BLACK = '000000';
const COLOR_DARK_BLUE = '1F3864';
const COLOR_ACCENT = '5B9BD5';
const COLOR_GRAY = '595959';
const COLOR_DARK_GRAY = '333333';

// ============ 读取清单数据 ============
const JSON_PATH = path.join(
  'e:\\WorkSpace\\HelloWorldAgentSkills\\aiguibin-common-excel',
  'cleanup_archive_list.json'
);
const TABLE_LIST = JSON.parse(fs.readFileSync(JSON_PATH, 'utf8'));
const TOTAL_TABLES = TABLE_LIST.length;

// ============ 数据库分组定义 ============
const DB_MODULE_GROUPS = [
  { db: 'NCMS_CREDIT', module: '合同管理', moduleEn: 'Contract' },
  { db: 'NCMS_CREDIT', module: '授信管理', moduleEn: 'Credit' },
  { db: 'NCMS_CREDIT', module: '放还款组', moduleEn: 'DisburseRepay' },
  { db: 'NCMS_CREDIT', module: '档案管理', moduleEn: 'Archive' },
  { db: 'NCMS_CREDIT', module: '用信管理', moduleEn: 'CreditUse' },
  { db: 'NCMS_CREDIT', module: '系统管理', moduleEn: 'System' },
  { db: 'NCMS_CREDIT', module: '线上贷款', moduleEn: 'OnlineLoan' },
  { db: 'NCMS_CREDIT', module: '营销管理', moduleEn: 'Marketing' },
  { db: 'NCMS_CREDIT', module: '风控中心', moduleEn: 'RiskControl' },
  { db: 'NCMS_RCA', module: '贷后管理', moduleEn: 'PostLoan' },
  { db: 'NCMS_RCA', module: '风险分类', moduleEn: 'RiskClass' },
  { db: 'NCMS_CLM', module: '额度中心', moduleEn: 'Limit' },
  { db: 'NCMS_RISK', module: '风控中心', moduleEn: 'RiskControl2' },
  { db: 'NCMS_AUTH', module: '统一认证', moduleEn: 'Auth' },
];

function getModuleTables(db, module) {
  return TABLE_LIST.filter(t => t['所属数据库'] === db && t['所属模块'] === module);
}

// ============ 统计数据 ============
function countBy(field) {
  const m = {};
  TABLE_LIST.forEach(t => {
    const k = t[field] || '(空)';
    m[k] = (m[k] || 0) + 1;
  });
  return m;
}

const DB_COUNT = countBy('所属数据库');
const MODULE_COUNT = countBy('所属模块');

// ============ 分区策略模式分类（V3.0.0核心：基于分区方案，严禁历史表） ============
function classifyPartitionStrategy(t) {
  const module = t['所属模块'];
  const strategy = t['清理策略'] || '';
  // 模式A：贷款状态+时间（合同/借据/放还款/用信/线上贷款）
  if (['合同管理', '放还款组', '用信管理', '线上贷款'].includes(module)) {
    return 'A';
  }
  // 模式B：任务状态+时间（贷后/风险分类）
  if (['贷后管理', '风险分类'].includes(module)) {
    return 'B';
  }
  // 模式C：失效时间（授信/额度）
  if (strategy.includes('失效超过1年')) {
    return 'C';
  }
  // 模式D：创建时间（档案/日志/营销/风控/认证）
  return 'D';
}

const STRATEGY_PATTERNS = {};
TABLE_LIST.forEach(t => {
  const p = classifyPartitionStrategy(t);
  STRATEGY_PATTERNS[p] = (STRATEGY_PATTERNS[p] || 0) + 1;
});

// 按策略模式分组的表列表
function getStrategyTables(mode) {
  return TABLE_LIST.filter(t => classifyPartitionStrategy(t) === mode);
}

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
    text: '湖北农信新信贷系统',
    font: FONT_CN, size: 52, bold: true, color: COLOR_DARK_BLUE,
  })],
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 0, after: 240 },
  children: [new TextRun({
    text: '数据库清理归档策略方案',
    font: FONT_CN, size: 52, bold: true, color: COLOR_DARK_BLUE,
  })],
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 0, after: 240 },
  children: [new TextRun({
    text: '面向新建信贷项目的前瞻性架构设计',
    font: FONT_CN, size: 28, color: COLOR_ACCENT,
  })],
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 0, after: 1200 },
  children: [new TextRun({
    text: 'Database Cleanup and Archiving Strategy — Forward-looking Architecture Design',
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
      cell('V3.0.0（前瞻性设计版）', 4000, { alignment: AlignmentType.CENTER }),
    ]}),
    new TableRow({ children: [
      cell('发布日期', 2000, { bold: true, alignment: AlignmentType.CENTER }),
      cell('2026年6月', 4000, { alignment: AlignmentType.CENTER }),
    ]}),
    new TableRow({ children: [
      cell('编制单位', 2000, { bold: true, alignment: AlignmentType.CENTER }),
      cell('信贷系统架构组', 4000, { alignment: AlignmentType.CENTER }),
    ]}),
    new TableRow({ children: [
      cell('文档密级', 2000, { bold: true, alignment: AlignmentType.CENTER }),
      cell('内部使用', 4000, { alignment: AlignmentType.CENTER }),
    ]}),
    new TableRow({ children: [
      cell('数据来源', 2000, { bold: true, alignment: AlignmentType.CENTER }),
      cell('湖北农信清理归档表清单.xlsx（86张表）', 4000, { alignment: AlignmentType.CENTER }),
    ]}),
  ],
});
children.push(coverTable);
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
children.push(P('湖北农信新信贷系统是全省农信机构的信贷业务核心平台，当前处于系统设计与架构阶段。业务数据是信贷系统的核心资产，其管理策略直接影响系统的长期运行质量和运维成本。'));
children.push(P('本方案考虑到系统上线运行3-5年后，随着业务数据持续积累，联机交易表数据量可能达到数千万甚至上亿级别，随之出现查询性能下降、备份时间延长、存储成本上升等问题，因此在系统设计阶段提前将数据清理归档作为基础能力纳入架构规划，在数据库表结构设计时即确定分区策略和清理归档规则，使系统上线后可按预设策略自动完成冷热数据分离和过期数据归档，避免后期改造带来的业务中断和成本增加。'));
children.push(P(`本次清理归档范围基于《湖北农信清理归档表清单.xlsx》编制，共覆盖 ${TOTAL_TABLES} 张表，涉及 5 个数据库、13 个业务模块。各数据库表数分布如下：`));
children.push(makeTable(
  ['数据库', '表数', '占比', '主要业务域'],
  [
    ['NCMS_CREDIT', String(DB_COUNT['NCMS_CREDIT'] || 0), ((DB_COUNT['NCMS_CREDIT'] || 0) / TOTAL_TABLES * 100).toFixed(1) + '%', '合同/授信/放还款/档案/用信/系统/线上贷款/营销/风控'],
    ['NCMS_RCA', String(DB_COUNT['NCMS_RCA'] || 0), ((DB_COUNT['NCMS_RCA'] || 0) / TOTAL_TABLES * 100).toFixed(1) + '%', '贷后管理/风险分类'],
    ['NCMS_CLM', String(DB_COUNT['NCMS_CLM'] || 0), ((DB_COUNT['NCMS_CLM'] || 0) / TOTAL_TABLES * 100).toFixed(1) + '%', '额度中心'],
    ['NCMS_RISK', String(DB_COUNT['NCMS_RISK'] || 0), ((DB_COUNT['NCMS_RISK'] || 0) / TOTAL_TABLES * 100).toFixed(1) + '%', '风控中心'],
    ['NCMS_AUTH', String(DB_COUNT['NCMS_AUTH'] || 0), ((DB_COUNT['NCMS_AUTH'] || 0) / TOTAL_TABLES * 100).toFixed(1) + '%', '统一认证'],
    ['合计', String(TOTAL_TABLES), '100.0%', '—'],
  ],
  [2000, 1200, 1200, 4960]
));

children.push(H2('1.2 技术需求'));
children.push(P('基于信贷业务数据的特点和行业实践经验，本方案需满足以下核心技术需求：'));
children.push(makeTable(
  ['需求领域', '需求描述', '技术目标'],
  [
    ['冷热数据分离', '将活跃数据与历史数据在存储层面进行物理隔离，联机交易仅访问热数据', '减少联机事务扫描的数据量，降低IO开销'],
    ['分区策略设计', '为86张表设计合理的分区键和分区方式，支持按时间和业务状态组合分区', '实现数据按生命周期自动流转，分区间数据相互独立'],
    ['冷数据迁移', '将满足冷却条件的数据行从热分区迁移至冷分区，迁移过程对业务无感知', '支持在线DDL操作，避免锁表影响业务'],
    ['文件归档导出', '对冷分区中超过保留期限的数据，导出为结构化文件并存储至对象存储或文件系统', '释放数据库存储空间，归档文件可独立查询'],
    ['数据恢复能力', '归档后的数据可通过标准接口恢复至数据库供查询，支持按条件筛选恢复', '保证历史数据可追溯、可查询、可恢复'],
    ['自动化调度', '清理和归档作业按预设周期自动执行，支持银行业务日历调度', '减少人工干预，降低运维复杂度'],
    ['监控告警', '对清理和归档作业的执行状态、数据量、存储空间进行监控，异常时触发告警', '及时发现和响应作业异常'],
  ],
  [1800, 4200, 3360]
));
children.push(P('上述技术需求的核心思路是：在表结构设计阶段预建分区，利用数据库原生分区能力实现冷热数据的物理隔离；通过分区重组操作将冷数据迁移至冷分区；对冷分区中超过保留期限的数据，以文件形式导出归档。整个过程不创建历史表，数据始终在同一张表中，通过分区边界进行管理。'));

children.push(H2('1.3 合规驱动'));
children.push(P('数据清理归档不仅是技术优化需求，更是法律法规的强制性要求。本方案在架构设计阶段即充分考虑以下法规约束：'));
children.push(makeTable(
  ['法规名称', '条款', '核心要求', '对本方案的影响'],
  [
    ['《个人信息保护法》', '第47条', '处理目的已实现或不再必要时应主动删除个人信息', '建立数据冷却→归档→销毁的完整生命周期，到期数据主动删除'],
    ['《银行业金融机构数据治理指引》', '第34条', '建立数据生命周期管理机制，覆盖产生到销毁全过程', '本方案构建完整数据生命周期管理，从架构层面保障'],
    ['《征信业管理条例》', '第16条', '个人不良信息保存期限为不良行为终止之日起5年', '征信相关记录保留5年后进入冷却流程，到期归档销毁'],
    ['《反洗钱法》', '第19条', '客户身份资料保存期限不少于10年', '客户身份资料保留≥10年，特殊标记永久保留'],
    ['《会计档案管理办法》', '—', '会计凭证保管期限10年', '合同、借据等会计档案保留10年，到期归档销毁'],
  ],
  [2400, 1000, 3360, 2600]
));

children.push(H2('1.4 总体目标'));
children.push(P('本方案旨在通过系统化的数据清理与归档策略，为清单中全部86张表建立分区清理机制，实现以下量化目标：'));
children.push(makeTable(
  ['目标维度', '架构设计目标', '实现方式', '预期效果'],
  [
    ['清理归档内建', '清理归档机制作为系统内核能力，不依赖后续改造', 'DDL阶段预建RANGE+LIST组合分区', '上线即具备完整生命周期管理能力'],
    ['冷热物理隔离', '联机交易仅访问热分区，冷数据通过分区裁剪自动隔离', '基于时间+状态的组合分区键', '联机交易RT稳定在50ms以内'],
    ['归档可追溯', '归档数据以Parquet文件存储，支持按需还原查询', 'Python归档导出引擎+归档元数据表', '归档数据完整可追溯、可查询、可恢复'],
    ['合规零缺陷', '各阶段数据保留期限严格匹配法规要求', '保留期限矩阵+合规审批流程', '合规审计零缺陷通过'],
    ['自动化运维', '清理/归档/校验全流程自动化调度', 'Crontab+XXL-Job调度', '人工干预降至最低，运维效率提升80%'],
  ],
  [1800, 3000, 2600, 1960]
));

children.push(H2('1.5 适用范围'));
children.push(P(`本方案仅适用于《湖北农信清理归档表清单.xlsx》中列明的 ${TOTAL_TABLES} 张表，具体覆盖范围如下：`));
children.push(bullet(`NCMS_CREDIT库（${DB_COUNT['NCMS_CREDIT'] || 0}张）：合同管理、授信管理、放还款组、档案管理、用信管理、系统管理、线上贷款、营销管理、风控中心模块表`));
children.push(bullet(`NCMS_RCA库（${DB_COUNT['NCMS_RCA'] || 0}张）：贷后管理、风险分类模块表`));
children.push(bullet(`NCMS_CLM库（${DB_COUNT['NCMS_CLM'] || 0}张）：额度中心模块表`));
children.push(bullet(`NCMS_RISK库（${DB_COUNT['NCMS_RISK'] || 0}张）：风控中心模块表`));
children.push(bullet(`NCMS_AUTH库（${DB_COUNT['NCMS_AUTH'] || 0}张）：统一认证模块表`));
children.push(P('本方案不适用于系统配置类、参数类、字典类等基础数据表。清单外的表如需纳入清理归档，需另行评估并补充至清单。'));

children.push(pageBreak());

// ==================== 第2章：信贷业务维度分析 ====================
children.push(H1('第2章 信贷业务维度分析'));

children.push(H2('2.1 基于贷款生命周期的数据划分策略'));
children.push(P('信贷业务数据具有鲜明的生命周期特征，不同阶段的数据访问频率、业务价值和法规要求差异显著。本方案基于贷款生命周期四阶段模型，为每个阶段制定差异化的数据冷热划分策略。'));

children.push(H3('2.1.1 贷前阶段（授信申请、征信查询）'));
children.push(P('贷前阶段数据以授信申请、征信查询、额度审批为主，具有临时性强、审批终态后访问频率骤降的特点。该阶段数据在审批终态确定后，其业务价值迅速衰减。'));
children.push(bullet('数据特征：临时性强，审批终态后访问频率骤降'));
children.push(bullet('冷却策略：授信审批终态后6个月进入冷分区'));
children.push(bullet('涉及表：授信申请信息表（CRLMT_CRGLN_APLY）、额度批复表（CRLMT_LMT_REPLY）等11张授信/额度类表'));
children.push(bullet('特殊处理：黑名单/失信客户关联的授信记录永久保留在热分区'));

children.push(H3('2.1.2 贷中阶段（合同签订、放款、用信）'));
children.push(P('贷中阶段是信贷业务的核心环节，合同签订、放款、用信等操作频繁，数据需保持联机活跃状态。该阶段数据在整个贷款存续期内均为热数据。'));
children.push(bullet('数据特征：业务操作频繁，需联机实时访问'));
children.push(bullet('热数据保持策略：合同存续期 + 宏观审慎期（约1年）保持热分区'));
children.push(bullet('涉及表：对私合同信息表（PRVT_CTR_INF）、借据信息表（IOU_INF）、放款明细信息（RTL_PAY_DSBR_DTL_INF）等28张合同/借据/放还款类表'));
children.push(bullet('冷却触发：合同状态为终止/废止 + 终止日期超冷却等待期'));

children.push(H3('2.1.3 贷后阶段（还款、检查、预警、分类）'));
children.push(P('贷后阶段数据以还款记录、贷后检查、风险预警、五级分类为主，还款周期内保持热，结清后进入冷却观察期。'));
children.push(bullet('数据特征：还款周期内访问频繁，结清后访问频率逐步下降'));
children.push(bullet('热数据保持：还款周期内保持热，结清后进入冷却观察期（1-3年）'));
children.push(bullet('涉及表：贷后检查任务表（R_LOAN_FTM_CHK_TSK_TBL）、风险分类记录（RTL_RISK_CL_RECORD_INF）等26张贷后/风险类表'));
children.push(bullet('冷却触发：流程状态为3/5/6（已完结）+ 超2-5年'));
children.push(bullet('特殊规则：不良贷款（次级/可疑/损失）数据永久保留在热分区'));

children.push(H3('2.1.4 结清/终止阶段'));
children.push(P('贷款结清或合同终止后，数据进入冷却观察期，完成全生命周期闭环。'));
children.push(bullet('数据特征：仅用于历史查询和审计取证，不再参与联机交易'));
children.push(bullet('冷却策略：结清后根据产品类型延迟1-3年进入冷分区'));
children.push(bullet('归档策略：冷分区保留5年后导出为Parquet文件存储至对象存储'));
children.push(bullet('销毁策略：保留期满后执行不可逆物理销毁'));

children.push(H3('2.1.5 各阶段冷热转换状态机'));
children.push(P('数据生命周期各阶段冷热转换状态机定义如下：'));
children.push(makeTable(
  ['当前阶段', '当前状态', '触发条件', '目标状态', '转换动作', '涉及表类型'],
  [
    ['贷前', '热数据', '审批终态后6个月', '冷数据', '分区重组至冷分区', '授信/额度类'],
    ['贷中', '热数据', '合同终止+超冷却等待期', '冷数据', '分区重组至冷分区', '合同/借据/放还款类'],
    ['贷后', '热数据', '流程完结+超2-5年', '冷数据', '分区重组至冷分区', '贷后/风险类'],
    ['结清/终止', '冷数据', '冷分区保留超5年', '归档文件', '文件导出+物理删除', '全部类'],
    ['归档', '归档文件', '保留期满', '已销毁', '不可逆物理销毁', '全部类'],
    ['特殊', '热数据', '不良贷款/黑名单', '永久热数据', '永不冷却', '风险分类类'],
  ],
  [1200, 1200, 2200, 1200, 2000, 1560]
));

children.push(H2('2.2 不同产品类型的数据归档要求'));
children.push(P('不同信贷产品类型在冷却等待期、归档周期和保留期限上存在显著差异，需按产品类型制定差异化策略。'));
children.push(makeTable(
  ['产品类型', '典型产品', '冷却等待期', '归档周期', '保留期限', '法规依据'],
  [
    ['个人贷款', '消费贷、经营贷', '结清后2年', '5年', '10年', '《会计档案管理办法》'],
    ['对公贷款', '流贷、固贷、项目贷', '结清后3年', '5年', '15年', '《会计档案管理办法》'],
    ['票据贴现', '银承、商承', '到期后1年', '5年', '10年', '《票据法》'],
    ['线上贷款', '秒贷、快贷', '结清后1年', '5年', '5年', '《征信业管理条例》'],
  ],
  [1600, 2000, 1400, 1200, 1200, 1960]
));

children.push(H2('2.3 监管合规视角下的数据保留期限设计'));
children.push(P('本方案严格遵循5部核心法规的数据保留要求，逐条对照如下：'));
children.push(makeTable(
  ['法规', '条款', '核心要求', '保留期限', '适用表范围'],
  [
    ['《个人信息保护法》', '第47条', '处理目的实现后主动删除', '结清后1-3年', '全部86张表'],
    ['《征信业管理条例》', '第16条', '不良信息保存5年', '5年', '征信查询/风险分类表'],
    ['《反洗钱法》', '第19条', '客户身份资料保存10年', '永久', '客户信息相关表'],
    ['《会计档案管理办法》', '—', '会计凭证保管10年', '10年', '合同/借据/还款类表'],
    ['《银行业数据治理指引》', '第34条', '建立数据生命周期管理', 'N/A', '全部86张表'],
  ],
  [2400, 1000, 2200, 1400, 2360]
));

children.push(H2('2.4 风险控制相关数据的特殊处理规则'));
children.push(P('风险控制相关数据具有特殊的业务价值，其冷热判断需综合考虑风险等级、处置状态和整改进展。'));

children.push(H3('2.4.1 风险分类数据'));
children.push(bullet('五级分类变更历史（RTL_RISK_CL_RECORD_INF等）：需长期保留，支持监管回溯和内部审计'));
children.push(bullet('不良资产处置周期内不冷却：次级/可疑/损失类贷款关联数据永久保留在热分区'));
children.push(bullet('正常/关注类贷款结清后2年方可进入冷分区'));

children.push(H3('2.4.2 贷后检查数据'));
children.push(bullet('检查结果与整改记录（R_LOAN_FTM_CHK_TSK_TBL等）：需保留至贷款结清后5年'));
children.push(bullet('存在未整改问题的记录持续保持热数据状态'));
children.push(bullet('已整改完毕且流程完结超2年方可进入冷分区'));

children.push(H3('2.4.3 预警数据'));
children.push(bullet('触发预警且未解除的记录（PSTLOAN_WARN_INFO等）：持续保持热数据'));
children.push(bullet('已解除预警且超5年方可进入冷分区'));
children.push(bullet('预警处理记录（PSTLOAN_WARN_DISPL_RCRD）随预警主表同步冷却'));

children.push(H3('2.4.4 风险数据冷热判断优先级矩阵'));
children.push(makeTable(
  ['风险等级', '当前状态', '冷热判定', '优先级', '说明'],
  [
    ['次级/可疑/损失', '处置中', '永久热数据', '最高', '不良资产处置周期内不冷却'],
    ['次级/可疑/损失', '已处置+结清', '热数据', '高', '结清后延长5年观察期'],
    ['关注', '未解除', '热数据', '中高', '关注期内保持热'],
    ['关注', '已解除+结清超2年', '可冷却', '中', '条件满足后进入冷分区'],
    ['正常', '存续中', '热数据', '中', '贷款存续期保持热'],
    ['正常', '结清超2年', '可冷却', '低', '标准冷却流程'],
  ],
  [1600, 1800, 1400, 1000, 3560]
));

children.push(H2('2.5 客户等级与数据处理优先级的关联机制'));
children.push(P('客户等级直接影响数据的冷却周期和归档策略，确保重要客户数据可获得更长的联机查询窗口。'));
children.push(makeTable(
  ['客户等级', '冷却周期倍率', '归档策略', '特殊规则'],
  [
    ['VIP/战略客户', '×2倍', '标准归档', '延长冷却等待期，确保重要客户数据联机可查'],
    ['普通客户', '×1倍', '标准归档', '标准流程，到期自动冷却'],
    ['关注客户', '×1.5倍', '标准归档', '适当延长，关注客户数据保留更久'],
    ['黑名单/失信客户', '永久不冷却', '不归档', '数据永久保留在热分区，支持持续监控'],
  ],
  [2400, 2000, 1800, 3160]
));

children.push(pageBreak());

// ==================== 第3章：数据分区与生命周期管理 ====================
children.push(H1('第3章 数据分区与生命周期管理'));

children.push(H2('3.1 冷热数据分层架构'));
children.push(P('本方案采用三级数据分层架构，实现冷热数据物理隔离和自动化流转：'));
children.push(makeTable(
  ['层级', '存储介质', '数据特征', '访问方式', '性能目标'],
  [
    ['热分区（Hot Partition）', 'SSD（高性能存储）', '活跃贷款、未达冷却条件的正常数据', '联机交易直接访问', 'RT < 50ms'],
    ['冷分区（Cold Partition）', 'HDD（低成本存储）', '已结清/已终止的历史数据，通过分区裁剪自动隔离', '联机交易不可见，历史查询可访问', 'RT < 200ms'],
    ['归档存储（Archive Storage）', '对象存储/HDFS', '已导出为文件的数据，从数据库物理删除', '通过归档查询服务按需还原', 'RT < 2s（还原后）'],
  ],
  [2000, 2400, 2400, 2400, 1600]
));
children.push(P('数据流转路径：热分区 →（冷却条件触发）→ 冷分区 →（归档条件触发）→ 文件导出 → 归档存储 →（保留期满）→ 物理销毁。'));

children.push(H2('3.2 分区键设计原则'));
children.push(P('分区键是冷热隔离的核心，本方案采用"时间+状态"的组合分区键设计，兼顾性能与可维护性。'));
children.push(bullet('时间维度：以CREATE_TIME或UPDATE_TIME的年份作为RANGE分区键，按年分区（如p2024/p2025/p2026），天然支持按时间范围裁剪'));
children.push(bullet('状态维度：以LOAN_STS/CTRT_STS_CD/TECPCS_STS_CD等状态字段作为LIST子分区键（如sp_active/sp_settled），实现冷热数据物理隔离'));
children.push(bullet('组合分区键：RANGE主分区（时间）+ LIST子分区（状态），推荐方案。兼顾时间裁剪和状态隔离，联机交易仅扫描活跃子分区'));
children.push(bullet('分区粒度：按年主分区 + 按状态子分区，单分区数据量控制在5000万行以内，支持在线DDL'));

children.push(H2('3.3 分区策略（按表类型分组）'));
children.push(P('基于86张表的业务特征和数据访问模式，归纳为以下4种分区策略模式：'));
children.push(makeTable(
  ['表类型', '主分区键', '子分区键', '分区方式', '适用表数', '典型表'],
  [
    ['合同/借据/放还款', 'YEAR(CREATE_TIME)', 'LOAN_STS / CTRT_STS_CD', 'RANGE+LIST', String(STRATEGY_PATTERNS['A'] || 0), 'IOU_INF, PRVT_CTR_INF, DSBR_CONT_ACC_INF'],
    ['贷后/风险', 'YEAR(CREATE_TIME)', 'TECPCS_STS_CD', 'RANGE+LIST', String(STRATEGY_PATTERNS['B'] || 0), 'R_LOAN_FTM_CHK_TSK_TBL, RTL_RISK_CL_RECORD_INF'],
    ['额度/授信', 'YEAR(UPDATE_TIME)', 'STATUS', 'RANGE+LIST', String(STRATEGY_PATTERNS['C'] || 0), 'ULM_LMT_PRIM_INF, CRLMT_LMT_REPLY'],
    ['档案/日志/营销', 'YEAR(CREATE_TIME)', '—', 'RANGE', String(STRATEGY_PATTERNS['D'] || 0), 'ARCH_INFO, SYS_LOG, CMPN_NMLST_CST'],
  ],
  [2000, 2000, 1800, 1400, 1200, 2160]
));

children.push(H2('3.4 数据生命周期状态机'));
children.push(P('数据从产生到销毁经历完整的生命周期，状态机如下：'));
children.push(makeTable(
  ['阶段', '状态', '触发条件', '转换动作', '数据位置', '访问方式'],
  [
    ['1.产生', '活跃数据', '业务操作产生', 'INSERT至热分区', '热分区（SSD）', '联机交易直接访问'],
    ['2.运营中', '热数据', '贷款存续期', '保持在热分区', '热分区（SSD）', '联机交易直接访问'],
    ['3.冷却', '冷数据', '冷却条件触发（结清+超期等）', '分区重组至冷分区', '冷分区（HDD）', '历史查询UNION ALL'],
    ['4.归档', '归档文件', '归档条件触发（冷分区超5年等）', '文件导出+物理删除分区', '对象存储', '归档查询服务按需还原'],
    ['5.销毁', '已销毁', '保留期满', '不可逆物理删除', '—', '不可访问'],
  ],
  [1000, 1200, 2000, 2200, 1600, 1760]
));

children.push(pageBreak());

// ==================== 第4章：清理策略设计 ====================
children.push(H1('第4章 清理策略设计'));

children.push(H2('4.1 清理定义重申'));
children.push(P('本方案中的"清理（Cleanup）"定义为：识别并筛选符合预设条件的数据记录，将其分配至指定数据分区作为冷数据存储。清理后的数据仍在同一张表中，通过分区实现冷热隔离。'));
children.push(P('严禁采用创建历史表的方式处理！传统方案中"INSERT INTO 历史表 + DELETE FROM 原表"的模式存在以下根本缺陷：'));
children.push(bullet('破坏数据完整性：数据分散在多张表中，跨表关联查询困难'));
children.push(bullet('增加运维复杂度：需维护大量历史表，DDL变更需同步'));
children.push(bullet('无法利用分区裁剪：联机交易无法自动过滤已迁移至历史表的数据'));
children.push(bullet('回滚操作复杂：数据在原表与历史表之间迁移，回滚需双向操作'));
children.push(P('基于分区方案的清理策略，通过ALTER TABLE REORGANIZE PARTITION实现在线DDL级别的分区重组，数据始终在同一张表中，联机交易通过分区裁剪自动隔离冷数据。'));

children.push(H2('4.2 多维度冷却触发条件'));
children.push(P('冷却触发条件采用多维度综合筛选矩阵，确保精准识别可冷却数据，避免误将活跃数据分配至冷分区：'));
children.push(makeTable(
  ['维度', '条件', '适用表类型', '检查方式'],
  [
    ['贷款状态', '结清（LOAN_STS=2）/核销（8）/终止（CTRT_STS_CD=10/11）', '合同/借据/放还款', 'WHERE子句过滤'],
    ['时间范围', '结清日期距当前超过冷却等待期', '全部', 'DATE_SUB函数计算'],
    ['风险等级', '五级分类为正常/关注（非不良）', '风险分类', '子查询关联检查'],
    ['客户等级', '非VIP/非黑名单', '全部', 'CUST_LEVEL字段判断'],
    ['关联实体', '无活跃借据关联', '合同', 'NOT EXISTS子查询'],
    ['任务状态', '流程状态代码为3/5/6（已完结）', '贷后/风险', 'TECPCS_STS_CD字段判断'],
    ['整改状态', '无未整改问题', '贷后检查', '关联整改记录检查'],
    ['预警状态', '无未解除预警', '预警', '关联预警记录检查'],
  ],
  [1600, 3200, 2000, 2560]
));

children.push(H2('4.3 清理执行方式'));
children.push(P('本方案提供三种可选的清理执行方式，根据场景选择最优方案：'));
children.push(makeTable(
  ['方式', '适用场景', '优点', '缺点', 'DDL'],
  [
    ['分区重组（REORGANIZE）', '子分区中部分数据需冷却', '在线DDL，不锁表，支持INPLACE', '需MySQL 5.7+', 'ALTER TABLE ... REORGANIZE PARTITION'],
    ['分区交换（EXCHANGE）', '整个分区均为冷数据', '秒级完成，原子操作', '需预建冷分区', 'ALTER TABLE ... EXCHANGE PARTITION'],
    ['分区截断（TRUNCATE）', '日志类超期数据', '快速，释放空间', '不可恢复，需谨慎', 'ALTER TABLE ... TRUNCATE PARTITION'],
  ],
  [2200, 2400, 2400, 2000, 560]
));

children.push(H2('4.4 清理流程'));
children.push(P('清理操作严格执行五步流程，确保安全可追溯：'));
children.push(makeTable(
  ['步骤', '动作', '执行人', '产出物', '注意事项'],
  [
    ['1.条件评估', '基于多维度冷却触发条件，评估待冷却数据', '自动化引擎', '冷却候选清单', '校验所有维度条件均满足'],
    ['2.数据筛选', '生成精确的WHERE条件，锁定待冷却数据范围', '自动化引擎', '筛选SQL', '确保筛选条件精确无歧义'],
    ['3.分区重组', '执行ALTER TABLE REORGANIZE PARTITION，将数据从热子分区迁移至冷子分区', 'DBA', 'DDL执行日志', 'ALGORITHM=INPLACE, LOCK=NONE'],
    ['4.校验', '行数校验 + 抽样数据校验 + 分区状态校验', 'DBA', '校验报告', '校验不一致立即停止并回滚'],
    ['5.元数据记录', '记录清理操作元数据至ARCH_META_INFO表', '自动化引擎', '审计记录', '永久保留审计日志'],
  ],
  [1200, 3200, 1400, 1800, 1760]
));

children.push(H2('4.5 清理策略分类（基于86张表，4种模式）'));
children.push(P('根据86张表的业务特征，归纳为以下4种分区清理策略模式：'));
children.push(makeTable(
  ['策略模式', '分区键', '冷却条件', '清理方式', '适用表数', '典型表'],
  [
    ['模式A：贷款状态+时间', 'LOAN_STS/CTRT_STS_CD + CREATE_TIME', '结清/核销/终止 + 超冷却等待期', '分区重组', String(STRATEGY_PATTERNS['A'] || 0), 'IOU_INF, PRVT_CTR_INF, DSBR_CONT_ACC_INF'],
    ['模式B：任务状态+时间', 'TECPCS_STS_CD + CREATE_TIME', '流程完结（3/5/6）+ 超2-5年', '分区重组', String(STRATEGY_PATTERNS['B'] || 0), 'R_LOAN_FTM_CHK_TSK_TBL, PSTLOAN_WARN_INFO'],
    ['模式C：失效时间', 'STATUS + UPDATE_TIME', '失效超1年', '分区重组', String(STRATEGY_PATTERNS['C'] || 0), 'ULM_LMT_PRIM_INF, CRLMT_LMT_REPLY'],
    ['模式D：创建时间', 'CREATE_TIME', '超期（10年/3月/1年）', '分区截断', String(STRATEGY_PATTERNS['D'] || 0), 'ARCH_INFO, SYS_LOG, CMPN_NMLST_CST'],
  ],
  [2000, 2600, 2200, 1200, 1200, 1960]
));

children.push(pageBreak());

// ==================== 第5章：归档策略设计 ====================
children.push(H1('第5章 归档策略设计'));

children.push(H2('5.1 归档定义重申'));
children.push(P('本方案中的"归档（Archiving）"定义为：对已完成冷分区的数据，执行文件导出操作（如CSV、Parquet），从数据库分区中导出并存储至对象存储/文件系统，减少数据库存储压力。归档后数据从数据库中物理删除。'));
children.push(P('归档与清理的本质区别：清理是同一张表内的分区迁移（冷热隔离），归档是跨存储介质的数据导出（数据库→文件系统）。'));

children.push(H2('5.2 归档触发条件'));
children.push(P('归档操作需严格满足以下任一触发条件：'));
children.push(bullet('时间条件：冷分区数据保留超过5年（从进入冷分区时间起算）'));
children.push(bullet('容量条件：冷分区数据总量超过阈值（如单分区超5000万行或总冷分区容量超500GB）'));
children.push(bullet('合规条件：监管要求达到可销毁年限，需先归档后销毁'));
children.push(bullet('业务条件：年度归档计划窗口（每年6月/12月集中归档）'));

children.push(H2('5.3 归档文件规范'));
children.push(P('归档文件采用标准化命名和格式，确保可追溯、可校验、可恢复：'));
children.push(makeTable(
  ['属性', '规范', '示例'],
  [
    ['文件格式', 'Parquet（列式存储，推荐）/ CSV（通用）/ JSON Lines（半结构化）', '—'],
    ['压缩算法', 'Snappy（推荐，速度快）/ Gzip（高压缩比）', '—'],
    ['文件命名', '{表名}_{分区键范围}_{归档日期}_{SHA256前8位}.{格式}.{压缩}', 'IOU_INF_p2020_settled_20260617_a1b2c3d4.parquet.snappy'],
    ['存储路径', '/archive/{数据库}/{业务模块}/{表名}/{年份}/', '/archive/NCMS_CREDIT/放还款组/IOU_INF/2020/'],
    ['分片策略', '单文件不超过1GB，超限自动分片', 'IOU_INF_p2020_settled_part1, part2...'],
  ],
  [1600, 3600, 4160]
));

children.push(H2('5.4 归档导出流程'));
children.push(P('归档导出严格执行六步流程，确保数据完整性和可恢复性：'));
children.push(makeTable(
  ['步骤', '操作', '校验点', '异常处理'],
  [
    ['1.分区锁定', '对目标冷分区设置只读标记，防止导出期间数据变更', '确认分区为只读状态', '超时自动解锁'],
    ['2.数据导出', '使用Python脚本通过SELECT INTO OUTFILE导出分区数据', '行数校验（导出前后行数一致）', '重试3次，失败告警'],
    ['3.压缩与校验', '对导出文件执行Snappy/Gzip压缩，计算SHA256校验和', '校验和与原数据比对', '不一致则重新导出'],
    ['4.上传对象存储', '将压缩文件上传至MinIO/S3对象存储', '上传后校验文件完整性', '断点续传'],
    ['5.记录元数据', '写入ARCH_META_INFO表，记录归档批次、文件路径、校验和等', '元数据写入成功', '重试写入'],
    ['6.删除分区', '确认归档文件完整后，执行DROP PARTITION删除冷分区', '二次确认归档文件可恢复', '保留分区至下次归档'],
  ],
  [1400, 3000, 2600, 2360]
));

children.push(H2('5.5 归档元数据表DDL'));
const archMetaDDL = `CREATE TABLE ARCH_META_INFO (
  ARCH_BATCH_ID      VARCHAR(64)   NOT NULL COMMENT '归档批次ID，格式：ARCH_YYYYMMDDHHmmss',
  SRC_TABLE_NAME     VARCHAR(128)  NOT NULL COMMENT '源表名',
  SRC_PARTITION_NAME VARCHAR(128)  COMMENT '源分区名',
  ARCH_FILE_PATH     VARCHAR(512)  NOT NULL COMMENT '归档文件完整路径',
  ARCH_FILE_FORMAT   VARCHAR(16)   NOT NULL COMMENT '文件格式：PARQUET/CSV/JSON',
  ARCH_COMPRESSION   VARCHAR(16)   COMMENT '压缩算法：SNAPPY/GZIP/NONE',
  ARCH_FILE_SIZE     BIGINT        COMMENT '归档文件大小（字节）',
  ARCH_ROW_COUNT     BIGINT        COMMENT '归档行数',
  ARCH_CHECKSUM      VARCHAR(64)   NOT NULL COMMENT 'SHA256校验和',
  ARCH_OPERATOR      VARCHAR(64)   COMMENT '操作人',
  ARCH_START_TIME    DATETIME      COMMENT '归档开始时间',
  ARCH_END_TIME      DATETIME      COMMENT '归档结束时间',
  ARCH_STATUS        VARCHAR(16)   COMMENT '状态：RUNNING/SUCCESS/FAILED/VERIFIED',
  ARCH_LEVEL         VARCHAR(8)    COMMENT '存储级别：OBJECT_STORAGE/HDFS/NAS',
  RETENTION_DAYS     INT           COMMENT '保留天数',
  DESTROY_DATE       DATE          COMMENT '计划销毁日期',
  REMARK             VARCHAR(512)  COMMENT '备注',
  CREATE_TIME        DATETIME      DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (ARCH_BATCH_ID),
  INDEX idx_src_table (SRC_TABLE_NAME),
  INDEX idx_status (ARCH_STATUS),
  INDEX idx_destroy_date (DESTROY_DATE)
) COMMENT '归档元数据表';`;
codeBlock(archMetaDDL).forEach(p => children.push(p));

children.push(H2('5.6 存储介质选型对比'));
children.push(makeTable(
  ['存储介质', '适用场景', '访问延迟', '成本', '扩展性', '推荐'],
  [
    ['对象存储（MinIO/S3）', '长期归档，海量文件', '秒级', '低', '无限扩展', '★★★★★ 推荐'],
    ['HDFS', '大数据分析场景，Spark查询', '秒级', '中', 'PB级', '★★★★☆'],
    ['NAS', '小规模归档，快速恢复', '毫秒级', '高', 'TB级', '★★★☆☆'],
    ['磁带库', '超长期合规保存', '分钟级', '极低', 'EB级', '★★☆☆☆ 特殊场景'],
  ],
  [2400, 2400, 1400, 1000, 1200, 1960]
));
children.push(P('推荐方案：优先采用MinIO/S3对象存储作为归档存储介质，成本低、扩展性强、支持S3协议标准，便于与Python归档脚本集成。'));

children.push(pageBreak());

// ==================== 第6章：技术实现方案 ====================
children.push(H1('第6章 技术实现方案'));

children.push(H2('6.1 技术架构'));

children.push(P('清理归档技术架构分为项目组负责（数据源层、调度层）和运维负责（存储层、查询层、监控层）两个部分，职责边界清晰：'));
children.push(makeTable(
  ['层级', '组件', '技术选型', '负责方', '职责'],
  [
    ['数据源层', '生产库', 'OceanBase / GoldenDB（分区模式，不分片）', '项目组', '业务数据产生与联机读写，热分区+冷分区共存于同一张表'],
    ['调度层', '清理调度', 'XXL-Job + Java批处理', '项目组', '定时触发冷却条件评估，执行分区重组DDL，记录清理元数据'],
    ['调度层', '归档调度', 'XXL-Job + Java批处理', '项目组', '定时触发归档条件评估，通过JDBC导出冷分区数据为CSV文件，压缩后移交运维'],
    ['存储层', '对象存储', 'MinIO / S3', '运维', '归档文件持久化存储，多副本冗余，生命周期管理'],
    ['查询层', '归档查询服务', '运维自建', '运维', '三级查询路由：热分区→冷分区→归档文件'],
    ['监控层', '监控告警', 'Prometheus + Grafana + 企业微信', '运维', '清理成功率、归档成功率、存储容量、校验和一致性'],
  ],
  [1400, 1600, 2600, 1200, 2560]
));
children.push(P('项目组交付范围：数据源层的分区表DDL设计 + 调度层的Java批处理程序（清理作业、归档导出作业）+ XXL-Job任务配置。运维负责后续的存储、查询和监控平台搭建。'));

children.push(H2('6.2 总体实施步骤'));
children.push(P('清理归档方案的实施分为4个阶段，按顺序推进：'));
children.push(makeTable(
  ['阶段', '工作内容', '主要产出', '负责方'],
  [
    ['第一阶段：分区表设计', '分析86张表的数据特征，为每张表设计分区键和分区方式，在DDL中预建分区', '含分区定义的表结构DDL', '项目组'],
    ['第二阶段：清理批处理开发', '开发Java批处理程序，实现冷却条件评估、分区重组DDL执行、元数据记录', '清理作业Java程序 + XXL-Job配置', '项目组'],
    ['第三阶段：归档批处理开发', '开发Java批处理程序，实现冷分区数据导出为CSV文件、压缩、校验、移交运维', '归档导出作业Java程序 + XXL-Job配置', '项目组'],
    ['第四阶段：运维平台对接', '运维搭建对象存储、归档查询服务、监控告警平台，项目组提供接口对接', '运维平台上线', '项目组+运维'],
  ],
  [2000, 3200, 2600, 1560]
));

children.push(H2('6.3 分区DDL设计'));

children.push(H3('6.3.1 数据库兼容性说明'));
children.push(P('本方案同时兼容OceanBase和GoldenDB两种云数据库，两者均支持MySQL兼容的RANGE分区和LIST子分区语法，且均运行在分区模式（不分片）下。分区DDL在两个数据库上均可直接执行，无需修改。'));
children.push(P('分区表设计的核心原则：在CREATE TABLE时即定义分区策略，系统上线后数据自动按分区规则写入对应分区，后续清理操作仅需重组分区边界，无需移动数据。'));

children.push(H3('6.3.2 借据信息表分区DDL（IOU_INF）'));
children.push(P('以下为借据信息表（IOU_INF）的完整分区DDL，采用RANGE主分区（按年）+ LIST子分区（按贷款状态）的组合分区方案：'));
const partitionDDL = `CREATE TABLE IOU_INF (
    IOU_ID              BIGINT       NOT NULL COMMENT '借据ID',
    LNISG_APLY_NO       VARCHAR(64)  NOT NULL COMMENT '贷款发放申请编号',
    LN_ACCT_NO          VARCHAR(64)  COMMENT '贷款账号',
    CTRT_NO             VARCHAR(64)  COMMENT '合同编号',
    DUBL_NO             VARCHAR(64)  COMMENT '借据编号',
    LOAN_STS            VARCHAR(8)   NOT NULL COMMENT '贷款状态：1-正常，2-结清，8-核销',
    SETTLE_DT           DATE         COMMENT '结清日期',
    LOAN_PRIN_AMT       DECIMAL(18,2) COMMENT '贷款本金金额',
    CUST_NO             VARCHAR(64)  COMMENT '客户编号',
    CUST_LEVEL          VARCHAR(16)  COMMENT '客户等级：VIP/NORMAL/CONCERN/BLACKLIST',
    RISK_CLASS          VARCHAR(16)  COMMENT '五级分类：NORMAL/CONCERN/SUB/DOUBT/LOSS',
    CREATE_TIME         DATETIME     NOT NULL COMMENT '创建时间',
    UPDATE_TIME         DATETIME     COMMENT '更新时间',
    PRIMARY KEY (IOU_ID, CREATE_TIME)
) COMMENT '借据信息表'
PARTITION BY RANGE (YEAR(CREATE_TIME))
SUBPARTITION BY LIST (LOAN_STS)
SUBPARTITION TEMPLATE (
    SUBPARTITION sp_active VALUES IN ('1') COMMENT '热数据-正常',
    SUBPARTITION sp_settled VALUES IN ('2') COMMENT '冷数据-结清',
    SUBPARTITION sp_written_off VALUES IN ('8') COMMENT '冷数据-核销'
) (
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p2026 VALUES LESS THAN (2027),
    PARTITION p2027 VALUES LESS THAN (2028),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);`;
codeBlock(partitionDDL).forEach(p => children.push(p));

children.push(H3('6.3.3 其他核心表分区方案'));
children.push(P('基于86张表的数据特征，按业务类型分组设计分区策略：'));
children.push(makeTable(
  ['表类型', '主分区键', '子分区键', '分区方式', '表数', '分区DDL模板'],
  [
    ['借据/放还款', 'YEAR(CREATE_TIME)', 'LOAN_STS', 'RANGE+LIST', '19', '参照IOU_INF'],
    ['合同', 'YEAR(CREATE_TIME)', 'CTRT_STS_CD', 'RANGE+LIST', '7', '参照PRVT_CTR_INF模板'],
    ['贷后/风险', 'YEAR(CREATE_TIME)', 'TECPCS_STS_CD', 'RANGE+LIST', '26', '参照R_LOAN_FTM_CHK_TSK_TBL模板'],
    ['额度/授信', 'YEAR(UPDATE_TIME)', 'STATUS', 'RANGE+LIST', '11', '参照ULM_LMT_PRIM_INF模板'],
    ['档案', 'YEAR(CREATE_TIME)', '—', 'RANGE', '5', '单分区键RANGE'],
    ['日志', 'YEAR(CREATE_TIME)', '—', 'RANGE', '5', '单分区键RANGE'],
    ['其他', 'YEAR(CREATE_TIME)', '—', 'RANGE', '13', '单分区键RANGE'],
  ],
  [1400, 1800, 1800, 1600, 800, 1760]
));

children.push(H2('6.4 清理作业实现（Java批处理 + XXL-Job）'));

children.push(H3('6.4.1 清理作业流程'));
children.push(P('清理作业是一个Java批处理程序，由XXL-Job定时调度。每次执行时，对满足冷却条件的表逐表执行分区重组。具体步骤：'));

children.push(P('步骤1：冷却条件评估'));
children.push(P('读取86张表的清理策略配置（冷却条件），逐表查询当前热分区中满足冷却条件的数据量。如果数据量为0，跳过该表；如果数据量超过阈值（如500万行），则分批处理。'));

children.push(P('步骤2：执行分区重组DDL'));
children.push(P('对满足冷却条件的表，生成并执行分区重组SQL。以借据表为例，将2024年热分区中已结清/核销的数据重组为冷分区：'));
const cleanupSQL = `-- 清理操作：将2024年已结清借据从热分区重组至冷分区
-- 执行前提：已通过步骤1确认p2024分区中sp_active子分区有满足冷却条件的数据

-- 在线DDL方式执行，不锁表，联机交易无感知
ALTER TABLE IOU_INF
REORGANIZE PARTITION p2024 INTO (
    PARTITION p2024_hot VALUES LESS THAN (2025) (
        SUBPARTITION sp_active VALUES IN ('1')
    ),
    PARTITION p2024_cold VALUES LESS THAN (2025) (
        SUBPARTITION sp_settled VALUES IN ('2'),
        SUBPARTITION sp_written_off VALUES IN ('8')
    )
);`;
codeBlock(cleanupSQL).forEach(p => children.push(p));

children.push(P('步骤3：校验分区重组结果'));
children.push(P('执行完成后，查询INFORMATION_SCHEMA.PARTITIONS确认分区重组结果，对比重组前后的数据量是否一致。'));
const verifySQL = `-- 校验分区重组结果
SELECT PARTITION_NAME, SUBPARTITION_NAME, TABLE_ROWS
FROM INFORMATION_SCHEMA.PARTITIONS
WHERE TABLE_SCHEMA = 'NCMS_CREDIT'
  AND TABLE_NAME = 'IOU_INF'
  AND PARTITION_NAME LIKE 'p2024%'
ORDER BY PARTITION_NAME, SUBPARTITION_NAME;`;
codeBlock(verifySQL).forEach(p => children.push(p));

children.push(P('步骤4：记录清理元数据'));
children.push(P('将本次清理操作的关键信息写入ARCH_META_INFO表，包括：表名、分区名、操作类型（CLEANUP）、清理行数、执行时间、执行结果。'));

children.push(H3('6.4.2 清理作业Java代码框架'));
children.push(P('清理作业主类 CleanupJobHandler，通过XXL-Job的@XxlJob注解注册为定时任务：'));
const cleanupJava = `package com.hbnx.credit.archive.job;

import com.xxl.job.core.handler.annotation.XxlJob;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;
import javax.annotation.Resource;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

@Component
public class CleanupJobHandler {

    @Resource
    private JdbcTemplate jdbcTemplate;

    /**
     * 月度清理作业：按分区重组方式将满足冷却条件的数据迁移至冷分区
     * XXL-Job配置：cron表达式 0 0 3 1 * ?（每月1日凌晨3点）
     */
    @XxlJob("cleanupMonthlyJob")
    public void execute() {
        LocalDate bizDate = LocalDate.now();
        // 1. 加载清理策略配置（86张表的冷却条件）
        List<CleanupConfig> configs = loadCleanupConfigs();
        for (CleanupConfig config : configs) {
            // 2. 评估待冷却数据量
            long coldRowCount = evaluateColdData(config, bizDate);
            if (coldRowCount == 0) {
                continue;  // 无待冷却数据，跳过
            }
            // 3. 分批执行分区重组（每批500万行，避免大事务）
            int batchSize = 5_000_000;
            for (int offset = 0; offset < coldRowCount; offset += batchSize) {
                // 4. 生成并执行分区重组DDL
                String reorganizeSQL = buildReorganizeSQL(config);
                jdbcTemplate.execute(reorganizeSQL);
                // 5. 校验结果
                long actualRows = verifyPartitionRows(config);
                // 6. 记录元数据
                insertMetaInfo(config, actualRows, "SUCCESS");
            }
        }
    }

    private long evaluateColdData(CleanupConfig config, LocalDate bizDate) {
        String sql = config.getCountSQL()
            .replace("${'$'}{coolDate}", bizDate.minusYears(config.getCoolYears()).toString());
        return jdbcTemplate.queryForObject(sql, Long.class);
    }

    private String buildReorganizeSQL(CleanupConfig config) {
        // 根据表的分区配置生成分区重组DDL
        // 示例：ALTER TABLE IOU_INF REORGANIZE PARTITION p2024 INTO (...)
        return config.getReorganizeSQL();
    }
}`;
codeBlock(cleanupJava).forEach(p => children.push(p));

children.push(H3('6.4.3 清理策略配置表'));
children.push(P('清理策略配置存储在数据库表中，Java批处理运行时读取，避免硬编码：'));
const configDDL = `CREATE TABLE ARCH_CLEANUP_CONFIG (
    ID            BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
    TABLE_NAME    VARCHAR(128) NOT NULL COMMENT '表名',
    DB_NAME       VARCHAR(64)  NOT NULL COMMENT '所属数据库',
    PARTITION_KEY VARCHAR(128) COMMENT '分区键列名',
    STATUS_COLUMN VARCHAR(128) COMMENT '状态列名（如LOAN_STS/CTRT_STS_CD）',
    COLD_STATUS   VARCHAR(256) COMMENT '冷却状态值（如1,2,8表示结清/核销）',
    COOL_YEARS    INT          COMMENT '冷却等待年数',
    CLEANUP_MODE  VARCHAR(16)  COMMENT '清理模式：REORGANIZE/TRUNCATE',
    ENABLED       TINYINT      DEFAULT 1 COMMENT '是否启用：1-启用，0-停用',
    CREATE_TIME   DATETIME     DEFAULT CURRENT_TIMESTAMP,
    UPDATE_TIME   DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (ID),
    UNIQUE KEY UK_TABLE (TABLE_NAME)
) COMMENT '清理策略配置表';`;
codeBlock(configDDL).forEach(p => children.push(p));

children.push(H3('6.4.4 多维度数据筛选SQL'));
children.push(P('冷却条件评估时，需综合多个维度判断数据是否可冷却。以下为合同表（PRVT_CTR_INF）的筛选SQL：'));
const filterSQL = `-- 合同表冷却筛选：多维度条件综合判断
-- 仅筛选满足全部条件的、真正可冷却的数据

SELECT c.CTRT_NO, c.CTRT_STS_CD, c.TMT_DT,
       c.CUST_LEVEL, c.RISK_CLASS, c.CREATE_TIME
FROM PRVT_CTR_INF c
WHERE c.CTRT_STS_CD IN ('10', '11')          -- 维度1：合同状态为已终止或已废止
  AND c.TMT_DT < DATE_SUB(CURDATE(), INTERVAL 1 YEAR)  -- 维度2：终止日期超1年
  AND NOT EXISTS (                            -- 维度3：无活跃借据关联
    SELECT 1 FROM IOU_INF i
    WHERE i.CTRT_NO = c.CTRT_NO
      AND i.LOAN_STS = '1'                    -- 存在活跃借据则不冷却
  )
  AND c.CUST_LEVEL NOT IN ('VIP', 'BLACKLIST') -- 维度4：非VIP/非黑名单
  AND c.RISK_CLASS IN ('NORMAL', 'CONCERN')    -- 维度5：非不良贷款（正常/关注）
  AND NOT EXISTS (                             -- 维度6：无未解除预警
    SELECT 1 FROM PSTLOAN_WARN_INFO w
    WHERE w.CTRT_NO = c.CTRT_NO
      AND w.WARN_STS = 'ACTIVE'
  );`;
codeBlock(filterSQL).forEach(p => children.push(p));

children.push(H2('6.5 归档导出作业实现（Java批处理 + XXL-Job）'));

children.push(H3('6.5.1 归档导出流程'));
children.push(P('归档导出作业同样是Java批处理程序，由XXL-Job定时调度。项目组负责将冷分区数据导出为CSV文件并压缩，然后移交运维存储至对象存储。具体步骤：'));

children.push(P('步骤1：归档条件评估'));
children.push(P('读取ARCH_CLEANUP_CONFIG配置，筛选冷分区保留时间超过5年的表。逐表查询冷分区数据量，确认可归档。'));

children.push(P('步骤2：JDBC流式导出CSV'));
children.push(P('通过JDBC流式读取冷分区数据，边读边写CSV文件，避免内存溢出。文件写入本地临时目录。'));

children.push(P('步骤3：Gzip压缩与校验'));
children.push(P('对CSV文件进行Gzip压缩，计算SHA256校验和。'));

children.push(P('步骤4：文件命名与移交'));
children.push(P('按命名规范生成文件名，将文件移动至运维指定的NAS共享目录，记录归档元数据。'));

children.push(P('步骤5：删除已归档分区'));
children.push(P('确认文件已成功移交且校验通过后，删除数据库中已归档的冷分区，释放存储空间。'));

children.push(H3('6.5.2 归档导出作业Java代码框架'));
const archiveJava = `package com.hbnx.credit.archive.job;

import com.xxl.job.core.handler.annotation.XxlJob;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;
import javax.annotation.Resource;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.zip.GZIPOutputStream;

@Component
public class ArchiveJobHandler {

    @Resource
    private JdbcTemplate jdbcTemplate;

    private static final String OUTPUT_DIR = "/nfs/archive/";  // 运维指定的NAS挂载路径
    private static final int FETCH_SIZE = 10000;  // JDBC流式读取，每次fetch 10000行

    /**
     * 季度归档导出作业
     * XXL-Job配置：cron表达式 0 0 3 5 1,4,7,10 ?（每季度第一个月5日凌晨3点）
     */
    @XxlJob("archiveQuarterlyJob")
    public void execute() {
        LocalDate bizDate = LocalDate.now();
        List<ArchiveConfig> configs = loadArchiveConfigs();
        for (ArchiveConfig config : configs) {
            // 1. 查询冷分区数据量
            long coldRowCount = jdbcTemplate.queryForObject(
                config.getCountSQL(), Long.class);
            if (coldRowCount == 0) continue;

            // 2. 流式导出CSV文件
            String timestamp = bizDate.format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
            String csvFile = OUTPUT_DIR + "temp/" + config.getTableName() + "_" + timestamp + ".csv";
            exportToCSV(config, csvFile);

            // 3. 压缩并计算校验和
            String gzFile = OUTPUT_DIR + "temp/" + config.getTableName() + "_" + timestamp + ".csv.gz";
            String checksum = compressAndChecksum(csvFile, gzFile);
            new File(csvFile).delete();  // 删除未压缩的CSV

            // 4. 按命名规范移动至最终目录
            String finalName = String.format("%s_%s_%s_%s.csv.gz",
                config.getTableName(), config.getPartitionName(),
                timestamp, checksum.substring(0, 8));
            String finalPath = OUTPUT_DIR + config.getTableName() + "/" + finalName;
            new File(finalPath).getParentFile().mkdirs();
            new File(gzFile).renameTo(new File(finalPath));

            // 5. 记录元数据
            insertMetaInfo(config, finalPath, coldRowCount, checksum);

            // 6. 删除已归档分区
            jdbcTemplate.execute("ALTER TABLE " + config.getTableName()
                + " DROP PARTITION " + config.getPartitionName());
        }
    }

    private void exportToCSV(ArchiveConfig config, String filePath) {
        String sql = config.getExportSQL();
        try (BufferedWriter writer = new BufferedWriter(
                new OutputStreamWriter(new FileOutputStream(filePath), StandardCharsets.UTF_8))) {
            // 写入BOM头，确保Excel正确识别UTF-8
            writer.write('\\uFEFF');
            // JDBC流式查询，边读边写
            jdbcTemplate.query(sql, rs -> {
                try {
                    int colCount = rs.getMetaData().getColumnCount();
                    for (int i = 1; i <= colCount; i++) {
                        if (i > 1) writer.write(',');
                        String val = rs.getString(i);
                        if (val != null) {
                            writer.write('"');
                            writer.write(val.replace("\\"", "\\"\\""));
                            writer.write('"');
                        }
                    }
                    writer.newLine();
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
            });
        } catch (IOException e) {
            throw new RuntimeException("CSV导出失败", e);
        }
    }

    private String compressAndChecksum(String inputFile, String outputFile) {
        try (FileInputStream fis = new FileInputStream(inputFile);
             FileOutputStream fos = new FileOutputStream(outputFile);
             GZIPOutputStream gzos = new GZIPOutputStream(fos)) {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] buffer = new byte[8192];
            int len;
            while ((len = fis.read(buffer)) > 0) {
                gzos.write(buffer, 0, len);
                md.update(buffer, 0, len);
            }
            // 转十六进制字符串
            StringBuilder sb = new StringBuilder();
            for (byte b : md.digest()) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            throw new RuntimeException("压缩/校验失败", e);
        }
    }
}`;
codeBlock(archiveJava).forEach(p => children.push(p));

children.push(H3('6.5.3 归档文件命名规范'));
children.push(P('归档文件统一命名，便于运维识别和管理：'));
children.push(makeTable(
  ['字段', '说明', '示例'],
  [
    ['表名', '源表英文名', 'IOU_INF'],
    ['分区名', '被归档的冷分区名称', 'p2024_cold'],
    ['归档时间', '格式yyyyMMddHHmmss', '20260617030000'],
    ['校验和', 'SHA256前8位', 'a1b2c3d4'],
    ['格式', 'csv.gz（CSV+Gzip压缩）', 'csv.gz'],
  ],
  [1400, 3000, 4960]
));
children.push(P('完整文件名示例：IOU_INF_p2024_cold_20260617030000_a1b2c3d4.csv.gz'));

children.push(H2('6.6 XXL-Job调度配置'));

children.push(P('本方案中所有定时作业均通过XXL-Job进行统一调度，避免使用操作系统crontab，便于统一管理、监控和日志追踪。'));
children.push(P('XXL-Job任务配置清单：'));
children.push(makeTable(
  ['任务名称', 'JobHandler', 'Cron表达式', '执行频率', '说明'],
  [
    ['月度清理', 'cleanupMonthlyJob', '0 0 3 1 * ?', '每月1日凌晨3点', '对满足冷却条件的表执行分区重组'],
    ['季度归档', 'archiveQuarterlyJob', '0 0 3 5 1,4,7,10 ?', '每季度第一个月5日凌晨3点', '导出冷分区数据为CSV文件，移交运维'],
    ['日志清理', 'cleanupLogsJob', '0 0 2 * * ?', '每日凌晨2点', '日志类表直接截断过期分区'],
  ],
  [1600, 2000, 2400, 1600, 1760]
));
children.push(P('调度原则：避开年终决算（12月31日）、结息日（3/6/9/12月20日）、季度末最后一周等关键业务节点，如遇冲突则顺延至下一工作日。'));

children.push(H2('6.7 数据恢复方案'));

children.push(P('归档数据恢复分为两个场景：'));
children.push(makeTable(
  ['恢复场景', '触发条件', '恢复方式', '预计耗时', '负责方'],
  [
    ['冷分区查询', '业务需要查询冷分区数据', '直接在冷分区上执行SELECT，无需恢复', '实时', '项目组（数据库已支持）'],
    ['归档文件恢复', '监管检查、审计取证需查询5年以上数据', '运维从对象存储下载归档文件，项目组通过LOAD DATA INFILE导入临时表', 'T+1', '运维+项目组协同'],
  ],
  [1600, 2400, 3200, 1200, 960]
));

children.push(P('归档文件恢复至临时表的SQL脚本：'));
const restoreSQL = `-- 归档数据恢复：从归档文件还原至临时表供查询
-- 前序步骤：运维已将归档文件从对象存储下载至数据库服务器指定目录

-- 1. 创建恢复临时表（与源表结构一致）
CREATE TABLE IOU_INF_RESTORE_2024 LIKE IOU_INF;

-- 2. 从归档文件加载数据
LOAD DATA INFILE '/data/restore/IOU_INF_p2024_cold_20260617030000_a1b2c3d4.csv.gz'
INTO TABLE IOU_INF_RESTORE_2024
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\\n';

-- 3. 验证恢复数据量
SELECT COUNT(*) AS restored_rows FROM IOU_INF_RESTORE_2024;

-- 4. 查询完成后清理临时表
DROP TABLE IF EXISTS IOU_INF_RESTORE_2024;`;
codeBlock(restoreSQL).forEach(p => children.push(p));

children.push(H2('6.8 运维对接接口规格'));

children.push(P('项目组与运维的交接点位于"归档文件移交"环节。项目组将压缩后的CSV文件写入运维指定的NAS共享目录，同时将归档元数据写入ARCH_META_INFO表，运维后续从该目录读取文件并上传至对象存储。'));

children.push(P('交接文件目录结构：'));
const dirStructure = `/nfs/archive/                     -- 运维指定的NAS挂载路径（运维提供）
  ├── IOU_INF/                     -- 按表名分目录
  │   ├── IOU_INF_p2024_cold_20260617030000_a1b2c3d4.csv.gz
  │   └── IOU_INF_p2023_cold_20260305030000_b2c3d4e5.csv.gz
  ├── PRVT_CTR_INF/
  │   └── PRVT_CTR_INF_p2023_cold_20260305030000_c3d4e5f6.csv.gz
  └── ...`;
codeBlock(dirStructure).forEach(p => children.push(p));

children.push(P('运维侧需提供的接口：'));
children.push(bullet('提供NAS共享目录路径，确保项目组批处理服务器有写入权限'));
children.push(bullet('搭建对象存储（MinIO/S3），将NAS目录中的归档文件上传至对象存储'));
children.push(bullet('搭建归档查询服务，实现三级路由查询（热分区→冷分区→归档文件）'));
children.push(bullet('搭建监控告警平台，监控清理成功率、归档成功率、存储容量、校验和一致性'));

children.push(H2('6.9 监控指标'));
children.push(P('以下监控指标由运维侧Prometheus+Grafana实现，项目组在ARCH_META_INFO表中提供数据源：'));
children.push(makeTable(
  ['监控项', '数据来源', '阈值', '告警级别'],
  [
    ['分区清理成功率', 'ARCH_META_INFO表，ARCH_TYPE=CLEANUP', '< 100%', '严重'],
    ['归档导出成功率', 'ARCH_META_INFO表，ARCH_TYPE=ARCHIVE', '< 100%', '严重'],
    ['冷分区数据量', 'INFORMATION_SCHEMA.PARTITIONS', '> 单分区5000万行', '警告'],
    ['归档文件存储容量', 'NAS/对象存储容量监控', '> 80%', '警告'],
    ['校验和不一致', '归档文件SHA256与ARCH_META_INFO对比', '任意不一致', '严重'],
  ],
  [2200, 3200, 2000, 1960]
));

// ==================== 第7章：业务影响分析 ====================
children.push(H1('第7章 业务影响分析'));

children.push(H2('7.1 对联机交易的影响'));
children.push(P('基于分区裁剪的清理方案对联机交易的影响极小，且能显著提升性能：'));
children.push(makeTable(
  ['影响维度', '清理前', '清理后', '提升幅度', '原理'],
  [
    ['查询IO', '全表扫描（含冷数据）', '仅扫描热分区', 'IO减少60%-80%', '分区裁剪自动过滤冷分区'],
    ['联机交易RT', '500ms+', '50ms以内', 'RT降低90%+', '数据量减少+索引更高效'],
    ['锁争用', '大事务可能锁表', '分区重组在线DDL', '锁争用降至零', 'ALGORITHM=INPLACE, LOCK=NONE'],
    ['连接数', '正常', '正常', '无影响', '清理作业使用独立连接池'],
  ],
  [1600, 2000, 2000, 1600, 2160]
));

children.push(H2('7.2 对历史查询的影响'));
children.push(P('历史查询通过三级路由实现，延迟梯度可控：'));
children.push(makeTable(
  ['查询场景', '数据来源', '查询方式', '预期RT', '用户体验'],
  [
    ['近3个月查询', '热分区', '直查生产库', '50ms', '无感知'],
    ['3个月-1年查询', '热分区+冷分区', 'UNION ALL', '100ms', '无感知'],
    ['1-5年查询', '冷分区', 'UNION ALL冷分区', '200ms', '轻微延迟'],
    ['5年以上查询', '归档文件', 'API还原查询', '2s', '需等待，可接受'],
  ],
  [1800, 1600, 2000, 1400, 2560]
));

children.push(H2('7.3 对报表/统计的影响'));
children.push(bullet('冷热分区聚合：报表数据源通过UNION ALL合并热分区和冷分区，实现全量数据聚合'));
children.push(bullet('归档文件查询：5年以上数据通过Spark/Impala离线查询归档文件（Parquet格式）'));
children.push(bullet('预聚合加速：对跨年统计预计算并缓存，降低实时聚合压力'));
children.push(bullet('报表时效调整：跨年报表由实时改为T+1，避开清理作业窗口'));

children.push(H2('7.4 对监管报送的影响'));
children.push(bullet('1104/EAST报送：报送窗口期间不执行清理/归档操作，避免数据切换'));
children.push(bullet('历史回溯报送：通过归档查询服务的三级路由，自动路由至归档文件'));
children.push(bullet('T+1还原机制：归档数据T+1还原至临时表供报送，确保数据完整性'));

children.push(H2('7.5 对数据备份的影响'));
children.push(bullet('冷分区跳过日常备份：冷分区数据不再变化，无需每日全量备份，仅保留初始备份'));
children.push(bullet('备份窗口减少60%+：仅备份热分区数据，备份集大幅缩小'));
children.push(bullet('归档文件独立备份：归档文件在对象存储层面配置多副本和跨区域复制'));

children.push(pageBreak());

// ==================== 第8章：运维管理 ====================
children.push(H1('第8章 运维管理'));

children.push(H2('8.1 作业调度'));
children.push(P('清理归档作业调度遵循银行业务日历，严格避开年终决算（12/31）、结息日（3/6/9/12月20日）和季度末等关键节点：'));
children.push(makeTable(
  ['调度类型', '清理对象', '执行频率', '执行时间', '避开窗口'],
  [
    ['每日清理', '日志类（模式D）', '每日1次', '凌晨2:00', '—'],
    ['月度清理', '全部模式A/B/C/D', '每月1次', '每月1日凌晨3:00', '避开结息日'],
    ['季度归档', '冷分区满5年数据', '每季度1次', '1/4/7/10月5日凌晨3:00', '避开季度末最后一周'],
    ['年度复盘', '全部策略回顾', '每年1次', '每年3月', '避开年终决算和开门红'],
    ['校验和验证', '全部归档文件', '每周1次', '周日凌晨4:00', '—'],
  ],
  [1400, 2000, 1400, 2400, 2160]
));

children.push(H2('8.2 监控指标'));
children.push(makeTable(
  ['指标类别', '指标名', '说明', '健康阈值', '采集方式'],
  [
    ['作业', '清理成功率', '每次清理作业的成功率', '100%', 'ARCH_META_INFO统计'],
    ['作业', '归档成功率', '每次归档作业的成功率', '100%', 'ARCH_META_INFO统计'],
    ['容量', '冷分区数据量', '各冷子分区的数据行数', '> 5000万行触发告警', 'INFORMATION_SCHEMA.PARTITIONS'],
    ['容量', '归档存储容量', '对象存储总使用量', '> 80%触发告警', 'df -h /archive'],
    ['一致性', '校验和一致率', '归档文件SHA256校验', '100%一致', '定时校验脚本'],
    ['性能', '归档还原RT', '归档文件还原为临时表的耗时', '> 5s触发告警', 'API监控'],
  ],
  [1200, 2000, 2600, 2000, 1360]
));

children.push(H2('8.3 告警机制'));
children.push(makeTable(
  ['告警类型', '触发条件', '通知方式', '响应时效', '处理动作'],
  [
    ['清理失败', 'ARCH_META_INFO.ARCH_STATUS = FAILED', '短信+电话+企业微信', '15分钟', '立即介入排查'],
    ['归档失败', 'ARCH_META_INFO.ARCH_STATUS = FAILED', '短信+电话+企业微信', '15分钟', '重试归档+人工介入'],
    ['校验和不一致', '定时校验发现不一致', '短信+电话+企业微信', '立即', '标记为异常+从备份恢复'],
    ['存储容量预警', '磁盘使用率 > 80%', '企业微信+邮件', '1小时', '扩容或加速归档'],
    ['分区重组锁等待', '锁等待 > 60s', '企业微信', '30分钟', '暂停清理作业'],
  ],
  [2000, 2800, 2400, 1200, 1360]
));

children.push(H2('8.4 应急预案'));
children.push(makeTable(
  ['异常场景', '应急动作', '恢复时间', '预防措施'],
  [
    ['分区清理失败', '自动回滚+保留原分区+人工介入', '< 30分钟', '执行前快照原分区'],
    ['归档文件损坏', '从对象存储多副本恢复', '< 1小时', '对象存储3副本+跨区域复制'],
    ['校验和不一致', '停止归档+从备份还原+重新导出', '< 2小时', '归档时双重校验'],
    ['误将活跃数据分配至冷分区', '执行反向分区重组+回滚', '< 1小时', '多维度条件校验+审批'],
    ['存储故障', '切换备节点+扩容', '< 1小时', '存储集群冗余'],
  ],
  [2400, 3200, 1600, 2160]
));

children.push(H2('8.5 运维操作手册'));
children.push(H3('8.5.1 日常巡检（每日）'));
children.push(bullet('检查前一日清理作业执行状态与日志'));
children.push(bullet('检查归档文件存储容量与对象存储健康状态'));
children.push(bullet('检查核心表分区裁剪是否正常（EXPLAIN验证）'));
children.push(bullet('检查ARCH_META_INFO表是否有异常记录'));

children.push(H3('8.5.2 月度清理（每月）'));
children.push(bullet('执行月度清理作业（分区重组/截断）'));
children.push(bullet('生成月度清理报告（清理量、成功率、耗时）'));
children.push(bullet('校验冷分区与热分区数据一致性'));
children.push(bullet('评估存储容量，规划扩容'));

children.push(H3('8.5.3 季度归档（每季度）'));
children.push(bullet('执行季度归档作业（冷分区文件导出+物理删除）'));
children.push(bullet('归档文件校验和全量验证'));
children.push(bullet('归档数据抽样还原测试'));

children.push(H3('8.5.4 年度复盘（每年）'));
children.push(bullet('回顾年度清理归档执行情况，优化策略参数'));
children.push(bullet('合规自评，形成年度合规报告'));
children.push(bullet('评估分区策略是否需要调整（新增表/分区键变更）'));

children.push(pageBreak());

// ==================== 第9章：风险与回滚 ====================
children.push(H1('第9章 风险与回滚'));

children.push(H2('9.1 技术风险'));
children.push(makeTable(
  ['风险点', '风险描述', '概率', '影响', '缓解措施'],
  [
    ['分区重组锁表', 'REORGANIZE PARTITION在不支持INPLACE的版本上可能锁表', '低', '高', '使用MySQL 8.0+，ALGORITHM=INPLACE, LOCK=NONE'],
    ['分区键设计不当', '分区键选择不合理导致数据倾斜或裁剪失效', '中', '高', '架构阶段评审分区键设计，确保均衡分布'],
    ['归档文件损坏', '对象存储故障或传输错误导致归档文件损坏', '低', '高', 'SHA256校验和+多副本冗余+定期校验'],
    ['清理条件遗漏', '冷却筛选条件不完整，遗漏部分可冷却数据', '中', '中', '多维度综合筛选矩阵+定期回顾优化'],
  ],
  [2000, 3400, 800, 800, 2960]
));

children.push(H2('9.2 业务风险'));
children.push(makeTable(
  ['风险点', '风险描述', '概率', '影响', '缓解措施'],
  [
    ['误将活跃数据分配至冷分区', '冷却条件判断有误，将仍在使用的数据迁移至冷分区', '低', '高', '多维度条件校验+审批+回滚机制'],
    ['归档文件查询超时', '查询归档文件时下载和解析耗时过长', '中', '中', '预建索引+分片存储+异步还原'],
    ['监管报送数据缺失', '归档期间监管报送需访问历史数据但尚未还原', '低', '高', 'T+1还原机制+报送窗口避开清理'],
  ],
  [2400, 3200, 800, 800, 2960]
));

children.push(H2('9.3 合规风险'));
children.push(makeTable(
  ['风险点', '风险描述', '概率', '影响', '缓解措施'],
  [
    ['未达保留期误归档', '在法定保留期内执行归档操作，违反法规要求', '低', '高', '保留期限矩阵校验+合规审批+自动化拦截'],
    ['归档数据泄露', '归档文件未加密或访问控制不当导致数据泄露', '低', '高', 'AES-256加密+RBAC访问控制+敏感字段脱敏'],
    ['销毁不可证明', '无法提供数据已不可逆销毁的证明', '低', '高', '销毁证明+SHA256校验记录+第三方见证'],
  ],
  [2400, 3200, 800, 800, 2960]
));

children.push(H2('9.4 回滚方案'));
children.push(P('清理操作设计为可逆，支持分级回滚：'));
children.push(H3('9.4.1 分区重组回滚'));
children.push(bullet('保留原分区至下次清理操作执行前，期间可随时执行反向REORGANIZE'));
children.push(bullet('反向REORGANIZE SQL：将冷子分区数据重新合并回热子分区'));
children.push(bullet('回滚时效：分钟级，INPLACE在线DDL'));

children.push(H3('9.4.2 归档文件恢复'));
children.push(bullet('从对象存储下载归档文件至本地'));
children.push(bullet('通过LOAD DATA INFILE还原至临时表'));
children.push(bullet('通过INSERT INTO SELECT将临时表数据回灌至生产库冷分区'));
children.push(bullet('恢复时效：视归档文件大小，通常2-4小时'));

children.push(H2('9.5 风险评估矩阵'));
children.push(makeTable(
  ['风险点', '类别', '概率', '影响', '风险等级', '缓解措施', '是否可接受'],
  [
    ['分区重组锁表', '技术', '低', '高', '中', 'ALGORITHM=INPLACE', '是'],
    ['分区键设计不当', '技术', '中', '高', '高', '架构阶段评审', '是（需控制）'],
    ['误将活跃数据分配至冷分区', '业务', '低', '高', '中', '多维度条件校验', '是'],
    ['未达保留期误归档', '合规', '低', '高', '中', '保留期限矩阵校验', '是'],
    ['归档文件损坏', '技术', '低', '高', '中', '多副本+校验和', '是'],
    ['归档文件查询超时', '业务', '中', '中', '中', '预建索引+分片', '是'],
  ],
  [2400, 1000, 800, 800, 1000, 2400, 1360]
));

children.push(pageBreak());

// ==================== 第10章：合规与审计 ====================
children.push(H1('第10章 合规与审计'));

children.push(H2('10.1 法规符合性对照表'));
children.push(P('本方案与5部核心法规的逐条符合性对照：'));
children.push(makeTable(
  ['法规', '条款', '核心要求', '方案对应措施', '证明材料'],
  [
    ['《个人信息保护法》', '第47条', '处理目的实现后主动删除', '冷却→归档→销毁的完整生命周期', '销毁审批单+操作日志'],
    ['《银行业数据治理指引》', '第34条', '建立数据生命周期管理', '本方案构建完整生命周期管理', '本方案文档'],
    ['《征信业管理条例》', '第16条', '不良信息保存5年', '不良贷款数据冷却期5年+归档期5年', 'ARCH_META_INFO元数据'],
    ['《反洗钱法》', '第19条', '客户身份资料保存10年', '客户信息表标记为永久保留', '保留期限矩阵'],
    ['《会计档案管理办法》', '—', '会计凭证保管10年', '合同/借据/还款类保留10年', 'ARCH_META_INFO元数据'],
  ],
  [2000, 1000, 2200, 2400, 1760]
));

children.push(H2('10.2 数据安全'));
children.push(H3('10.2.1 加密存储'));
children.push(bullet('热分区：MySQL表空间透明加密（TDE）'));
children.push(bullet('冷分区：MySQL表空间透明加密（TDE），与热分区一致'));
children.push(bullet('归档文件：AES-256-CBC加密，密钥由KMS管理'));
children.push(bullet('传输通道：TLS 1.2+加密传输'));

children.push(H3('10.2.2 访问控制'));
children.push(makeTable(
  ['角色', '热分区权限', '冷分区权限', '归档文件权限', '审计要求'],
  [
    ['DBA', '管理', '管理', '只读', '全操作审计'],
    ['业务查询', '只读', '只读（经审批）', '无', '查询日志'],
    ['运维', '只读', '只读', '只读', '全操作审计'],
    ['合规官', '只读元数据', '只读元数据', '只读元数据', '审计日志'],
    ['审计员', '只读', '只读', '只读', '独立审计'],
  ],
  [1400, 1600, 2000, 2000, 2360]
));

children.push(H2('10.3 审计追踪'));
children.push(P('清理/归档全流程操作日志完整记录，审计追踪永久保留：'));
children.push(makeTable(
  ['审计要素', '记录内容', '记录位置', '保留期限'],
  [
    ['操作人', '执行清理/归档的DBA或系统账号', 'ARCH_META_INFO.ARCH_OPERATOR', '永久'],
    ['操作时间', '清理/归档开始时间和结束时间', 'ARCH_META_INFO.ARCH_START/END_TIME', '永久'],
    ['操作范围', '源表名、分区名、筛选条件、行数', 'ARCH_META_INFO', '永久'],
    ['操作结果', '成功/失败/回滚状态', 'ARCH_META_INFO.ARCH_STATUS', '永久'],
    ['校验记录', 'SHA256校验和、行数校验结果', 'ARCH_META_INFO.ARCH_CHECKSUM', '永久'],
    ['审批流程', '审批人、审批时间、审批意见', '审批系统', '永久'],
  ],
  [1400, 3200, 3200, 1560]
));

children.push(H2('10.4 销毁证明'));
children.push(P('归档文件物理销毁时，生成不可逆的销毁证明：'));
children.push(bullet('销毁证明内容：文件路径、SHA256校验和、销毁时间、销毁方式、见证人'));
children.push(bullet('销毁方式：使用shred命令多次覆写后删除（Linux），或使用安全删除工具'));
children.push(bullet('销毁证明与ARCH_META_INFO关联，形成完整的可追溯链'));

children.push(H2('10.5 定期合规审查'));
children.push(H3('10.5.1 年度合规自评'));
children.push(bullet('每年3月对上年度清理归档执行情况进行合规自评'));
children.push(bullet('自评报告涵盖：清理量、归档量、销毁量、合规性、审计追踪完整性'));
children.push(bullet('自评报告经合规官审核后归档保留'));

children.push(H3('10.5.2 监管检查应对'));
children.push(bullet('监管检查时提供：本方案、清理归档清单、ARCH_META_INFO元数据、销毁证明'));
children.push(bullet('建立监管检查快速响应机制，24小时内提供所需材料'));
children.push(bullet('定期演练监管检查应对流程'));

children.push(pageBreak());

// ==================== 附录A：86张表清理归档方案 ====================
children.push(H1('附录'));
children.push(H2(`附录A：86张表清理归档方案（按分区策略模式分组）`));
children.push(P(`本附录完整列出《湖北农信清理归档表清单.xlsx》中全部 ${TOTAL_TABLES} 张表，按分区策略模式（A/B/C/D）分组，每张表含：表名、中文名、所属模块、分区键、清理方式、归档周期。`));

// 策略模式A：贷款状态+时间 → 合同/借据/放还款/用信/线上贷款
const modeATables = getStrategyTables('A');
const modeBTables = getStrategyTables('B');
const modeCTables = getStrategyTables('C');
const modeDTables = getStrategyTables('D');

const APP_HDRS = ['序号', '表名（英文）', '表名（中文）', '所属模块', '所属数据库', '分区键', '清理方式', '归档周期'];
const APP_W = [500, 1800, 1600, 1200, 1400, 1400, 1200, 760];

function buildAppendixRows(tables) {
  let idx = 0;
  return tables.map(t => {
    idx++;
    const mode = classifyPartitionStrategy(t);
    let partKey = '', cleanupMethod = '', archiveCycle = '';
    if (mode === 'A') {
      partKey = 'LOAN_STS/CTRT_STS_CD + YEAR(CREATE_TIME)';
      cleanupMethod = '分区重组';
      archiveCycle = '5年';
    } else if (mode === 'B') {
      partKey = 'TECPCS_STS_CD + YEAR(CREATE_TIME)';
      cleanupMethod = '分区重组';
      archiveCycle = '5年';
    } else if (mode === 'C') {
      partKey = 'STATUS + YEAR(UPDATE_TIME)';
      cleanupMethod = '分区重组';
      archiveCycle = '不归档';
    } else {
      partKey = 'YEAR(CREATE_TIME)';
      cleanupMethod = '分区截断';
      archiveCycle = '不归档';
    }
    return [String(idx), t['表名_英文'] || '', t['表名_中文'] || '',
            t['所属模块'] || '', t['所属数据库'] || '',
            partKey, cleanupMethod, archiveCycle];
  });
}

children.push(H3(`A.1 模式A：贷款状态+时间（${modeATables.length}张）——合同/借据/放还款/用信/线上贷款`));
children.push(P('分区键：LOAN_STS/CTRT_STS_CD + YEAR(CREATE_TIME)，清理方式：分区重组，归档周期：冷分区保留5年后归档'));
children.push(makeTable(APP_HDRS, buildAppendixRows(modeATables), APP_W));

children.push(H3(`A.2 模式B：任务状态+时间（${modeBTables.length}张）——贷后管理/风险分类`));
children.push(P('分区键：TECPCS_STS_CD + YEAR(CREATE_TIME)，清理方式：分区重组，归档周期：冷分区保留5年后归档'));
children.push(makeTable(APP_HDRS, buildAppendixRows(modeBTables), APP_W));

children.push(H3(`A.3 模式C：失效时间（${modeCTables.length}张）——授信管理/额度中心`));
children.push(P('分区键：STATUS + YEAR(UPDATE_TIME)，清理方式：分区重组，归档周期：不归档（失效数据直接清理）'));
children.push(makeTable(APP_HDRS, buildAppendixRows(modeCTables), APP_W));

children.push(H3(`A.4 模式D：创建时间（${modeDTables.length}张）——档案/日志/营销/风控/认证`));
children.push(P('分区键：YEAR(CREATE_TIME)，清理方式：分区截断，归档周期：不归档（超期直接删除）'));
children.push(makeTable(APP_HDRS, buildAppendixRows(modeDTables), APP_W));

children.push(pageBreak());

// ==================== 附录B：分区DDL模板 ====================
children.push(H2('附录B：核心表分区DDL模板'));

children.push(H3('B.1 借据信息表（IOU_INF）——模式A'));
children.push(P('详见第6章6.2节，此处不再重复。'));

children.push(H3('B.2 对私合同信息表（PRVT_CTR_INF）——模式A'));
const privtDDL = `CREATE TABLE PRVT_CTR_INF (
    CTRT_NO             VARCHAR(64)  NOT NULL COMMENT '合同编号',
    CTRT_STS_CD         VARCHAR(8)   NOT NULL COMMENT '合同状态：10-已终止，11-已废止',
    TMT_DT              DATE         COMMENT '终止日期',
    CUST_NO             VARCHAR(64)  COMMENT '客户编号',
    CUST_LEVEL          VARCHAR(16)  COMMENT '客户等级',
    RISK_CLASS          VARCHAR(16)  COMMENT '五级分类',
    CREATE_TIME         DATETIME     NOT NULL,
    UPDATE_TIME         DATETIME,
    PRIMARY KEY (CTRT_NO, CREATE_TIME)
) COMMENT '对私合同信息表'
PARTITION BY RANGE (YEAR(CREATE_TIME))
SUBPARTITION BY LIST (CTRT_STS_CD)
SUBPARTITION TEMPLATE (
    SUBPARTITION sp_active VALUES IN ('1','2','3','4','5','6','7','8','9') COMMENT '热数据',
    SUBPARTITION sp_terminated VALUES IN ('10','11') COMMENT '冷数据-已终止/已废止'
) (
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p2026 VALUES LESS THAN (2027),
    PARTITION p2027 VALUES LESS THAN (2028),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);`;
codeBlock(privtDDL).forEach(p => children.push(p));

children.push(H3('B.3 贷后检查任务表（R_LOAN_FTM_CHK_TSK_TBL）——模式B'));
const chkDDL = `CREATE TABLE R_LOAN_FTM_CHK_TSK_TBL (
    TSK_NO              VARCHAR(64)  NOT NULL COMMENT '任务编号',
    TECPCS_STS_CD       VARCHAR(8)   NOT NULL COMMENT '流程状态：3-已完成，5-已关闭，6-已作废',
    CTRT_NO             VARCHAR(64)  COMMENT '合同编号',
    CREATE_TIME         DATETIME     NOT NULL,
    UPDATE_TIME         DATETIME,
    PRIMARY KEY (TSK_NO, CREATE_TIME)
) COMMENT '贷后检查任务表'
PARTITION BY RANGE (YEAR(CREATE_TIME))
SUBPARTITION BY LIST (TECPCS_STS_CD)
SUBPARTITION TEMPLATE (
    SUBPARTITION sp_active VALUES IN ('1','2','4') COMMENT '热数据-进行中',
    SUBPARTITION sp_completed VALUES IN ('3','5','6') COMMENT '冷数据-已完结'
) (
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p2026 VALUES LESS THAN (2027),
    PARTITION p2027 VALUES LESS THAN (2028),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);`;
codeBlock(chkDDL).forEach(p => children.push(p));

children.push(pageBreak());

// ==================== 附录C：完整自动化脚本 ====================
children.push(H2('附录C：完整自动化脚本'));

children.push(H3('C.1 Python归档导出脚本完整版'));
children.push(P('详见第6章6.5节，已包含完整可执行代码。'));

children.push(H3('C.2 Shell调度脚本'));
const shellScript = '#!/bin/bash\n' +
'# cleanup_monthly.sh - 月度清理调度脚本\n' +
'# 功能：执行月度分区清理操作，生成清理报告\n' +
'set -euo pipefail\n' +
'\n' +
'LOG_DIR="/var/log/cleanup"\n' +
'REPORT_DIR="/var/log/cleanup/reports"\n' +
'TIMESTAMP=$(date +%Y%m%d_%H%M%S)\n' +
'LOG_FILE="$LOG_DIR/cleanup_monthly_${TIMESTAMP}.log"\n' +
'\n' +
'# 初始化日志\n' +
'exec 2>&1 | tee -a "$LOG_FILE"\n' +
'echo "=== 月度清理开始 $(date \'+%Y-%m-%d %H:%M:%S\') ==="\n' +
'\n' +
'# 1. 检查是否避开结息日\n' +
'CURRENT_DAY=$(date +%d)\n' +
'if [ "$CURRENT_DAY" = "20" ]; then\n' +
'    echo "今日为结息日，跳过清理作业"\n' +
'    exit 0\n' +
'fi\n' +
'\n' +
'# 2. 检查是否有正在运行的清理作业\n' +
'if pgrep -f "cleanup" > /dev/null; then\n' +
'    echo "已有清理作业正在运行，退出"\n' +
'    exit 1\n' +
'fi\n' +
'\n' +
'# 3. 执行清理作业\n' +
'echo "执行模式A/B/C分区重组..."\n' +
'mysql -h localhost -u arch_user -p"***" <<EOF\n' +
'  -- 清理已结清借据\n' +
'  ALTER TABLE NCMS_CREDIT.IOU_INF\n' +
'  REORGANIZE PARTITION p2024 INTO (\n' +
'      PARTITION p2024_hot VALUES LESS THAN (2025) (\n' +
'          SUBPARTITION sp_active VALUES IN (\'1\')\n' +
'      ),\n' +
'      PARTITION p2024_cold VALUES LESS THAN (2025) (\n' +
'          SUBPARTITION sp_settled VALUES IN (\'2\'),\n' +
'          SUBPARTITION sp_written_off VALUES IN (\'8\')\n' +
'      )\n' +
'  ), ALGORITHM=INPLACE, LOCK=NONE;\n' +
'EOF\n' +
'\n' +
'# 4. 生成清理报告\n' +
'echo "生成月度清理报告..."\n' +
'mysql -h localhost -u arch_user -p"***" -e "\n' +
'  SELECT SRC_TABLE_NAME, COUNT(*) AS batch_count,\n' +
'         SUM(ARCH_ROW_COUNT) AS total_rows,\n' +
'         MAX(ARCH_END_TIME) AS last_cleanup_time\n' +
'  FROM ARCH_META.ARCH_META_INFO\n' +
'  WHERE ARCH_STATUS = \'SUCCESS\'\n' +
'    AND ARCH_END_TIME >= DATE_SUB(NOW(), INTERVAL 1 MONTH)\n' +
'  GROUP BY SRC_TABLE_NAME;\n' +
'" > "$REPORT_DIR/report_${TIMESTAMP}.txt"\n' +
'\n' +
'echo "=== 月度清理完成 $(date \'+%Y-%m-%d %H:%M:%S\') ==="';
codeBlock(shellScript).forEach(p => children.push(p));

children.push(H3('C.3 归档校验和验证脚本'));
const verifyScript = '#!/bin/bash\n' +
'# verify_archive_checksum.sh - 归档校验和验证脚本\n' +
'set -euo pipefail\n' +
'\n' +
'echo "=== 归档校验和验证开始 $(date \'+%Y-%m-%d %H:%M:%S\') ==="\n' +
'\n' +
'# 从元数据表获取所有归档文件列表\n' +
'mysql -h localhost -u arch_user -p"***" -N -e "\n' +
'  SELECT ARCH_BATCH_ID, ARCH_FILE_PATH, ARCH_CHECKSUM\n' +
'  FROM ARCH_META.ARCH_META_INFO\n' +
'  WHERE ARCH_STATUS = \'SUCCESS\'\n' +
'    AND ARCH_LEVEL = \'OBJECT_STORAGE\'\n' +
'  ORDER BY CREATE_TIME DESC LIMIT 100;\n' +
'" | while read -r BATCH_ID FILE_PATH STORED_CHECKSUM; do\n' +
'    echo "验证: $BATCH_ID - $FILE_PATH"\n' +
'\n' +
'    # 从对象存储下载文件并计算校验和\n' +
'    LOCAL_FILE="/tmp/verify_${BATCH_ID}.tmp"\n' +
'    mc cp "minio/archive-bucket/${FILE_PATH}" "$LOCAL_FILE" 2>/dev/null\n' +
'\n' +
'    if [ -f "$LOCAL_FILE" ]; then\n' +
'        CALC_CHECKSUM=$(sha256sum "$LOCAL_FILE" | awk \'{print $1}\')\n' +
'        if [ "$CALC_CHECKSUM" = "$STORED_CHECKSUM" ]; then\n' +
'            echo "  校验通过: $CALC_CHECKSUM"\n' +
'            mysql -h localhost -u arch_user -p"***" -e "\n' +
'              UPDATE ARCH_META.ARCH_META_INFO\n' +
'              SET ARCH_STATUS = \'VERIFIED\'\n' +
'              WHERE ARCH_BATCH_ID = \'$BATCH_ID\';\n' +
'            "\n' +
'        else\n' +
'            echo "  [严重] 校验失败！存储值:$STORED_CHECKSUM 计算值:$CALC_CHECKSUM"\n' +
'            # 触发告警\n' +
'            curl -X POST "https://alert.example.com/api/alert" \\\n' +
'              -d \'{"level":"CRITICAL","msg":"归档校验和失败:\'$BATCH_ID\'"}\'\n' +
'        fi\n' +
'        rm -f "$LOCAL_FILE"\n' +
'    else\n' +
'        echo "  [警告] 无法下载归档文件"\n' +
'    fi\n' +
'done\n' +
'\n' +
'echo "=== 归档校验和验证完成 $(date \'+%Y-%m-%d %H:%M:%S\') ==="';
codeBlock(verifyScript).forEach(p => children.push(p));

children.push(pageBreak());

// ==================== 附录D：信贷业务五维度分析矩阵 ====================
children.push(H2('附录D：信贷业务五维度分析矩阵'));

children.push(P('本附录提供完整的五维度分析矩阵，覆盖贷款生命周期、产品类型、风险等级、客户等级和监管合规五个维度，为清理归档策略提供全面的业务依据。'));

children.push(H3('D.1 维度一：贷款生命周期 × 冷却策略'));
children.push(makeTable(
  ['生命周期阶段', '数据特征', '冷却触发条件', '冷却等待期', '涉及表数', '清理模式'],
  [
    ['贷前（授信申请）', '临时性强，审批终态后访问频率骤降', '审批终态后6个月', '6个月', '11', '模式C'],
    ['贷中（合同签订/放款）', '业务操作频繁，需联机实时访问', '合同终止+超等待期', '1-3年', '28', '模式A'],
    ['贷后（还款/检查）', '还款周期内访问频繁，结清后逐步下降', '流程完结+超2-5年', '2-5年', '26', '模式B'],
    ['结清/终止', '仅用于历史查询和审计', '结清后延迟冷却', '1-3年', '—', '模式A/B'],
    ['全生命周期', '日志/档案/营销类', '创建时间超期', '3月-10年', '21', '模式D'],
  ],
  [2200, 2400, 2400, 1400, 1200, 1200]
));

children.push(H3('D.2 维度二：产品类型 × 保留期限'));
children.push(makeTable(
  ['产品类型', '冷却等待期', '归档周期', '保留期限', '法规依据', '涉及表'],
  [
    ['个人贷款', '结清后2年', '5年', '10年', '《会计档案管理办法》', 'PRVT_CTR_INF, IOU_INF等'],
    ['对公贷款', '结清后3年', '5年', '15年', '《会计档案管理办法》', 'PRVT_CTR_INF, IOU_INF等'],
    ['票据贴现', '到期后1年', '5年', '10年', '《票据法》', 'DSBR_RLTV_BILL_INF等'],
    ['线上贷款', '结清后1年', '5年', '5年', '《征信业管理条例》', 'OL_APL_MGT_MNPLT_REC等'],
  ],
  [1600, 1400, 1200, 1200, 2400, 2560]
));

children.push(H3('D.3 维度三：风险等级 × 冷热判定'));
children.push(makeTable(
  ['风险等级', '冷却策略', '特殊规则', '涉及表'],
  [
    ['正常', '结清后标准冷却', '无特殊规则', '全部表'],
    ['关注', '结清后延长冷却（×1.5倍）', '关注期内保持热', '合同/借据/风险分类'],
    ['次级', '永久不冷却', '不良资产处置周期内全热', 'RTL_RISK_CL_RECORD_INF等'],
    ['可疑', '永久不冷却', '不良资产处置周期内全热', 'RTL_RISK_CL_RECORD_INF等'],
    ['损失', '永久不冷却', '不良资产处置周期内全热，核销后也保持热', 'RTL_RISK_CL_RECORD_INF等'],
  ],
  [1400, 2400, 3200, 2760]
));

children.push(H3('D.4 维度四：客户等级 × 数据处理'));
children.push(makeTable(
  ['客户等级', '冷却周期倍率', '归档策略', '特殊规则'],
  [
    ['VIP/战略客户', '×2倍', '标准归档', '延长冷却等待期，确保重要客户数据联机可查'],
    ['普通客户', '×1倍', '标准归档', '标准流程，到期自动冷却'],
    ['关注客户', '×1.5倍', '标准归档', '适当延长保留'],
    ['黑名单/失信客户', '永久不冷却', '不归档', '数据永久保留在热分区'],
  ],
  [2400, 2000, 1800, 3160]
));

children.push(H3('D.5 维度五：监管合规 × 保留策略'));
children.push(makeTable(
  ['法规', '条款', '核心要求', '保留策略', '到期处置'],
  [
    ['《个人信息保护法》', '第47条', '处理目的实现后主动删除', '结清后1-3年冷却', '归档后到期销毁'],
    ['《征信业管理条例》', '第16条', '不良信息保存5年', '不良贷款数据冷却5年', '归档后到期销毁'],
    ['《反洗钱法》', '第19条', '客户身份资料保存10年', '客户信息永久保留', '不归档不销毁'],
    ['《会计档案管理办法》', '—', '会计凭证保管10年', '合同/借据保留10年', '归档后到期销毁'],
    ['《银行业数据治理指引》', '第34条', '数据生命周期管理', '全生命周期覆盖', '按矩阵执行'],
  ],
  [2400, 1000, 2200, 2000, 1760]
));

children.push(emptyP());
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 480, after: 0 },
  children: [new TextRun({
    text: '— 文档结束 —',
    font: FONT_CN, size: 22, bold: true, color: COLOR_GRAY,
  })],
}));

// ==================== 文档组装 ====================
const doc = new Document({
  creator: '信贷系统架构组',
  title: '湖北农信新信贷系统数据库清理归档策略方案',
  description: 'Database Cleanup and Archiving Strategy V3.0.0 (Forward-looking Architecture Design)',
  styles: {
    default: {
      document: {
        run: { font: FONT_CN, size: 22 },
        paragraph: { spacing: { line: 360 } },
      },
    },
    paragraphStyles: [
      {
        id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 32, bold: true, font: FONT_CN, color: COLOR_BLACK },
        paragraph: { spacing: { before: 360, after: 240 }, outlineLevel: 0 },
      },
      {
        id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 28, bold: true, font: FONT_CN, color: COLOR_BLACK },
        paragraph: { spacing: { before: 280, after: 180 }, outlineLevel: 1 },
      },
      {
        id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 24, bold: true, font: FONT_CN, color: COLOR_BLACK },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 },
      },
    ],
  },
  numbering: {
    config: [
      {
        reference: 'bullets',
        levels: [
          { level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
          { level: 1, format: LevelFormat.BULLET, text: '◦', alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 1440, hanging: 360 } } } },
        ],
      },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: PAGE_WIDTH, height: PAGE_HEIGHT },
        margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: '2E75B6', space: 1 } },
          children: [new TextRun({
            text: '湖北农信新信贷系统数据库清理归档策略方案 V3.0.0（前瞻性设计版）',
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
            new TextRun({ text: ' 页', font: FONT_CN, size: 18, color: COLOR_GRAY }),
          ],
        })],
      }),
    },
    children,
  }],
});

// ==================== 输出文件 ====================
const outputPath = path.join(
  'e:\\WorkSpace\\HelloWorldAgentSkills\\aiguibin-common-excel\\FF--湖北农信新信贷数据库设计策略',
  '湖北农信新信贷数据库清理归档策略方案.docx'
);

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(outputPath, buffer);
  console.log('文档生成成功: ' + outputPath);
  console.log('文件大小: ' + (buffer.length / 1024).toFixed(2) + ' KB');
  console.log(`基于清单表数: ${TOTAL_TABLES} 张`);
  console.log('策略模式分布:');
  console.log(`  模式A（贷款状态+时间）: ${STRATEGY_PATTERNS['A'] || 0} 张`);
  console.log(`  模式B（任务状态+时间）: ${STRATEGY_PATTERNS['B'] || 0} 张`);
  console.log(`  模式C（失效时间）: ${STRATEGY_PATTERNS['C'] || 0} 张`);
  console.log(`  模式D（创建时间）: ${STRATEGY_PATTERNS['D'] || 0} 张`);
}).catch(err => {
  console.error('文档生成失败:', err);
  process.exit(1);
});