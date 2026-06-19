# 信贷数据库清理归档策略方案 Spec（V3.0.0 前瞻性设计版）

## Why
针对新建信贷项目，在系统设计与架构阶段进行前瞻性规划，确保数据清理与归档功能在项目初期即以内置能力实现，避免上线后再进行大规模逻辑修改。当前不存在实际运行问题，作为顶级信贷业务专家及架构师，需进行未雨绸缪的系统设计规划，将冷热数据分离、分区管理、归档导出等能力作为系统内核能力预先设计，而非事后补救。

## What Changes（V3.0.0 全量修订）
- **BREAKING**：清理语义重新定义——清理不再创建历史表，而是识别符合条件的数据记录，将其分配至指定数据分区作为冷数据存储。**严禁采用创建历史表的方式处理**
- **BREAKING**：归档语义重新定义——归档是对已完成分区的冷数据执行文件导出操作并进行规范归档存储，而非将数据迁移至历史库
- 新增：信贷业务领域五维度专业分析（贷款生命周期/产品类型/监管合规/风险控制/客户等级）
- 新增：基于分区策略的冷热数据分离方案，清理与分区深度协同
- 新增：冷数据分区存储方案（分区键选择、分区策略、存储介质要求）
- 新增：归档文件导出功能设计（文件格式规范、命名规则、压缩方式、存储路径）
- 新增：可执行代码及操作脚本（数据筛选SQL、分区管理命令、文件导出程序、自动化调度配置）
- 新增：数据恢复方案（归档数据可追溯、可查询、可恢复）
- **移除**：责任人分布相关章节
- **移除**：历史表创建相关方案（替换为分区方案）
- 数据源：严格且仅基于 `湖北农信清理归档表清单.xlsx`（86张表）

## 核心概念重新定义

### 清理（Cleanup）
识别并筛选符合预设条件的数据记录，将其**分配至指定数据分区**作为冷数据存储。**严禁采用创建历史表的方式处理**。清理后的数据仍在同一张表中，通过分区实现冷热隔离。

### 归档（Archiving）
对已完成冷分区识别的数据，执行**文件导出操作**（如CSV、Parquet、JSON Lines），从数据库分区中导出并存储至对象存储/文件系统/HDFS，减少数据库存储压力。归档后数据从数据库中物理删除，通过文件系统对外提供查询。

### 冷热分层
- **热数据**：当前活跃分区，联机交易直接读写
- **冷数据**：已清理分区，联机交易不可见，通过分区裁剪自动隔离
- **归档数据**：已导出为文件，脱离数据库，按需通过文件查询接口访问

## Impact
- 受影响能力：联机交易性能、冷数据查询、监管报送、数据备份恢复、数据生命周期管理
- 受影响代码/系统：
  - 信贷核心数据库 DDL（所有表需预建分区）
  - 数据清理调度模块（新增）
  - 文件导出/归档模块（新增）
  - 归档数据查询接口（新增）
  - 运维监控平台（新增指标）
- 参考文件：
  - `DD-湖北农信基础配置检核\湖北农信清理归档表清单.xlsx`（86张表，唯一权威清单）
  - `CC-新信贷基础知识\*.txt`（信贷业务知识库）
  - `.trae/specs/db-partition-strategy-doc/spec.md`（分区策略，清理与分区需协同设计）

## 文档输出规范

### 格式要求
- 输出格式：.docx
- 语言：中文
- 风格：专业、严谨，业务视角、技术视角、合规视角三融合，面向新建项目架构设计
- 必须包含：目录、页眉页脚、表格、分区架构图、DDL/脚本示例、分区策略图

### 内容要求（10章 + 附录）

#### 第1章：背景与目标
- 1.1 业务背景：新建信贷项目，系统设计与架构阶段进行前瞻性数据管理规划，将清理归档作为系统内核能力内置
- 1.2 前瞻性规划必要性：避免后期上线后历史数据膨胀导致性能退化、存储成本攀升、逻辑修改困难
- 1.3 合规驱动：《个人信息保护法》《银行业金融机构数据治理指引》《征信业管理条例》《反洗钱法》《会计档案管理办法》对数据保留与销毁的要求
- 1.4 总体目标：
  - 清理归档内建于系统架构，不依赖后续改造
  - 冷热数据通过分区物理隔离，联机交易仅访问热数据
  - 归档数据可追溯、可查询、可恢复
  - 合规审计零缺陷
- 1.5 适用范围：仅适用于《湖北农信清理归档表清单.xlsx》中列明的86张表，覆盖5个数据库、13个业务模块

#### 第2章：信贷业务维度分析（核心新增章节）
从信贷业务专业视角，进行五维度深度分析，为清理归档策略提供业务依据：

- 2.1 基于贷款生命周期的数据划分策略
  - 贷前阶段（授信申请、征信查询）：数据临时性强，审批终态后速冷
  - 贷中阶段（合同签订、放款、用信）：数据需联机活跃，贷款存续期保持热
  - 贷后阶段（还款、检查、预警、分类）：还款周期内热，结清后阶段性冷却
  - 结清/终止阶段：进入冷数据分区，完成全生命周期闭环
  - 各阶段数据冷热转换时间节点定义（含状态机）

- 2.2 不同产品类型的数据归档要求
  - 个人贷款（消费贷、经营贷）：结清后2年冷却，5年归档
  - 对公贷款（流贷、固贷、项目贷）：结清后3年冷却，10年归档
  - 票据贴现：到期后1年冷却，5年归档
  - 线上贷款：结清后1年冷却，5年归档
  - 产品类型与归档周期的映射矩阵

- 2.3 监管合规视角下的数据保留期限设计
  - 《征信业管理条例》第16条：不良信息保存5年
  - 《反洗钱法》第19条：客户身份资料保存10年
  - 《会计档案管理办法》：会计凭证保管10年
  - 《个人信息保护法》第47条：处理目的实现后主动删除
  - 逐表对照法规的保留期限矩阵（基于86张表清单）

- 2.4 风险控制相关数据的特殊处理规则
  - 风险分类数据：五级分类变更历史需长期保留（不良资产处置周期）
  - 贷后检查数据：检查结果与整改记录需保留至贷款结清后5年
  - 预警数据：触发预警且未解除的记录需持续热数据
  - 风险数据冷热判断的优先级矩阵

- 2.5 客户等级与数据处理优先级的关联机制
  - VIP客户/战略客户：数据冷却周期延长（热数据期×2）
  - 普通客户：标准冷却周期
  - 黑名单/失信客户：数据永久保留，不进入归档
  - 客户等级与数据保留优先级的映射表

#### 第3章：数据分区与生命周期管理
- 3.1 冷热数据分层架构：
  - 热分区：联机交易直接访问，保留在SSD存储
  - 冷分区：联机交易不可见，可通过分区裁剪查询，保留在HDD存储
  - 归档存储：对象存储/HDFS
- 3.2 分区键设计原则：
  - 时间维度分区键（如按年份、按季度）
  - 状态维度分区键（如贷款状态）
  - 组合分区键（时间+状态）
- 3.3 分区策略（基于86张表）：
  - RANGE分区：按时间范围（如按年RANGE分区）
  - LIST分区：按状态列值（如CTRT_STS_CD）
  - RANGE+LIST子分区：时间+状态组合
  - 每张表的分区方案建议
- 3.4 数据生命周期状态机：产生 → 热数据 → 冷却条件触发 → 冷分区 → 归档条件触发 → 文件导出 → 归档存储 → 销毁

#### 第4章：清理策略设计（基于分区方案）
- 4.1 清理定义（重申）：将符合条件的数据从热分区迁移至冷分区，严禁创建历史表
- 4.2 清理触发条件（多维度）：
  - 贷款状态维度：贷款状态=结清/终止/废止
  - 时间维度：结清日期距当前日期超过N年（N取决于产品类型）
  - 风险等级维度：非不良贷款（五级分类=正常/关注）
  - 客户等级维度：非VIP客户
  - 综合筛选条件组合矩阵
- 4.3 清理执行方式：
  - 分区重组（REORGANIZE PARTITION）：将热分区中的冷数据重组至冷分区
  - 分区交换（EXCHANGE PARTITION）：将冷分区整体交换（适用于已按结清年份预分区场景）
  - 在线DDL（ALGORITHM=INPLACE）：避免锁表
- 4.4 清理流程：条件评估 → 数据筛选 → 分区重组 → 校验 → 元数据记录
- 4.5 清理策略分类（基于86张表清单）：
  | 策略模式 | 适用表数 | 分区键 | 冷却条件 |
  | 按贷款状态+结清时间 | 合同/借据/放还款类 | CTRT_STS_CD + TMT_DT | 已终止/结清且超1年 |
  | 按任务状态+时间 | 贷后/风险分类类 | TECPCS_STS_CD + CREATE_TIME | 流程完结且超2-5年 |
  | 按失效时间 | 额度/授信类 | STATUS + UPDATE_TIME | 失效超1年 |
  | 按创建时间 | 档案/日志类 | CREATE_TIME | 超10年/3月/1年 |

#### 第5章：归档策略设计
- 5.1 归档定义（重申）：对已完成冷分区的数据执行文件导出，从数据库物理删除
- 5.2 归档触发条件：
  - 冷分区数据保留时间超过阈值（如冷分区>5年）
  - 冷分区数据总量超过存储阈值
  - 按监管要求达到可销毁年限
- 5.3 归档文件规范：
  - 文件格式：Parquet（列式存储，压缩率高）/ CSV（通用可读）/ JSON Lines（半结构化）
  - 压缩方式：Snappy（推荐）/ Gzip
  - 命名规则：`{表名}_{分区键范围}_{归档日期}_{校验和}.{格式}.{压缩}`
  - 示例：`IOU_INF_p2020_p2021_20260617_a1b2c3d4.parquet.snappy`
  - 存储路径：`/archive/{数据库}/{模块}/{表名}/{年份}/`
- 5.4 归档导出流程：
  - 分区锁定 → 数据导出（SELECT INTO OUTFILE / mysqldump / 自定义导出工具）→ 压缩 → 上传对象存储 → 校验 → 删除分区 → 元数据记录
- 5.5 归档元数据表设计：
  ```sql
  CREATE TABLE ARCH_META_INFO (
    ARCH_BATCH_ID VARCHAR(64) NOT NULL COMMENT '归档批次ID',
    SRC_TABLE_NAME VARCHAR(128) NOT NULL COMMENT '源表名',
    SRC_PARTITION_NAME VARCHAR(128) COMMENT '源分区名',
    ARCH_FILE_PATH VARCHAR(512) COMMENT '归档文件路径',
    ARCH_FILE_FORMAT VARCHAR(16) COMMENT '文件格式:PARQUET/CSV/JSONL',
    ARCH_COMPRESSION VARCHAR(16) COMMENT '压缩方式:SNAPPY/GZIP/NONE',
    ARCH_FILE_SIZE BIGINT COMMENT '归档文件大小(字节)',
    ARCH_ROW_COUNT BIGINT COMMENT '归档行数',
    ARCH_CHECKSUM VARCHAR(64) COMMENT '文件校验和(SHA256)',
    ARCH_KEY_RANGE_START VARCHAR(64) COMMENT '分区键范围起始',
    ARCH_KEY_RANGE_END VARCHAR(64) COMMENT '分区键范围结束',
    ARCH_OPERATOR VARCHAR(64) COMMENT '操作人',
    ARCH_START_TIME DATETIME COMMENT '归档开始时间',
    ARCH_END_TIME DATETIME COMMENT '归档结束时间',
    ARCH_STATUS VARCHAR(16) COMMENT '状态:PENDING/RUNNING/SUCCESS/FAILED/RESTORED',
    PRIMARY KEY (ARCH_BATCH_ID),
    INDEX IDX_ARCH_TABLE (SRC_TABLE_NAME),
    INDEX IDX_ARCH_TIME (ARCH_START_TIME)
  ) COMMENT '归档元数据表';
  ```
- 5.6 归档存储介质选型：对象存储(MinIO/S3) / HDFS / NAS / 磁带库

#### 第6章：技术实现方案（核心章节）
- 6.1 技术架构图：生产库(热分区+冷分区) → 清理调度引擎 → 分区重组 → 归档调度引擎 → 文件导出 → 对象存储 → 归档查询服务
- 6.2 分区DDL设计（以IOU_INF为例）：
  ```sql
  -- 创建分区表（新建项目预建分区）
  CREATE TABLE IOU_INF (
    IOU_ID BIGINT NOT NULL,
    LNISG_APLY_NO VARCHAR(64) NOT NULL,
    LN_ACCT_NO VARCHAR(64),
    CTRT_NO VARCHAR(64),
    LOAN_STS VARCHAR(8) COMMENT '贷款状态:1-正常,2-结清,8-核销',
    SETTLE_DT DATE COMMENT '结清日期',
    CREATE_TIME DATETIME,
    -- ... 其他字段
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
    PARTITION p_future VALUES LESS THAN MAXVALUE
  );
  ```

- 6.3 清理执行脚本（分区重组方式）：
  ```sql
  -- 场景：将2024年已结清的借据从热分区分裂至冷分区
  -- 1. 重组分区：将p2024的sp_active子分区中结清数据分离
  ALTER TABLE IOU_INF
  REORGANIZE PARTITION p2024 INTO (
    PARTITION p2024 VALUES LESS THAN (2025)
    SUBPARTITION sp_active VALUES IN ('1'),
    PARTITION p2024_cold VALUES LESS THAN (2025)
    SUBPARTITION sp_settled VALUES IN ('2'),
    SUBPARTITION sp_written_off VALUES IN ('8')
  );
  -- 2. 记录清理元数据
  INSERT INTO ARCH_META_INFO(ARCH_BATCH_ID, SRC_TABLE_NAME, SRC_PARTITION_NAME, ...)
  VALUES(...);
  ```

- 6.4 数据筛选SQL（多维度冷却条件）：
  ```sql
  -- 合同表冷却筛选：已终止/废止且超1年，且关联借据已结清
  SELECT * FROM PRVT_CTR_INF
  WHERE CTRT_STS_CD IN ('10', '11')  -- 已终止或已废止
    AND TMT_DT < DATE_SUB(CURDATE(), INTERVAL 1 YEAR)  -- 终止日期超1年
    AND CTRT_NO NOT IN (
      SELECT DISTINCT CTRT_NO FROM IOU_INF
      WHERE LOAN_STS NOT IN ('2', '8')  -- 排除仍有活跃借据的合同
    );
  ```

- 6.5 归档文件导出脚本（Python实现）：
  ```python
  #!/usr/bin/env python3
  """冷数据分区归档导出工具"""
  import subprocess, hashlib, os, shutil
  from datetime import datetime

  def export_partition(table_name, partition_name, output_path, format='parquet'):
      """导出指定分区数据为归档文件"""
      timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
      temp_file = f"/tmp/arch_{table_name}_{partition_name}_{timestamp}.csv"
      # 1. 导出分区数据
      subprocess.run([
          "mysql", "-e",
          f"SELECT * FROM {table_name} PARTITION({partition_name}) INTO OUTFILE '{temp_file}'"
      ])
      # 2. 压缩
      compressed = f"{temp_file}.gz"
      subprocess.run(["gzip", temp_file])
      # 3. 计算校验和
      sha256 = hashlib.sha256()
      with open(compressed, 'rb') as f:
          sha256.update(f.read())
      checksum = sha256.hexdigest()
      # 4. 目标文件名
      dest = f"{output_path}/{table_name}_{partition_name}_{timestamp}_{checksum[:8]}.csv.gz"
      shutil.move(compressed, dest)
      # 5. 记录元数据
      file_size = os.path.getsize(dest)
      return {"path": dest, "checksum": checksum, "size": file_size}

  # 示例调用
  result = export_partition("IOU_INF", "p2024_cold", "/archive/NCMS_CREDIT/放还款/IOU_INF/2024/")
  print(f"归档完成: {result}")
  ```

- 6.6 归档数据恢复脚本：
  ```sql
  -- 从归档文件恢复数据至临时表
  CREATE TABLE IOU_INF_RESTORE_2024 LIKE IOU_INF;
  LOAD DATA INFILE '/archive/NCMS_CREDIT/放还款/IOU_INF/2024/IOU_INF_p2024_cold_20260617_a1b2c3d4.csv.gz'
  INTO TABLE IOU_INF_RESTORE_2024
  FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"';
  -- 校验恢复数据
  SELECT COUNT(*) FROM IOU_INF_RESTORE_2024;
  ```

- 6.7 自动化调度配置（Linux crontab示例）：
  ```bash
  # 每日凌晨2点：日志类清理
  0 2 * * * /usr/local/bin/cleanup_logs.sh >> /var/log/cleanup.log 2>&1
  # 每月1日凌晨3点：月度清理
  0 3 1 * * /usr/local/bin/cleanup_monthly.sh >> /var/log/cleanup.log 2>&1
  # 每季度第一个月5日凌晨3点：归档导出
  0 3 5 1,4,7,10 * /usr/local/bin/archive_quarterly.sh >> /var/log/archive.log 2>&1
  ```

- 6.8 归档数据查询接口设计：
  ```python
  # 归档数据查询API
  @app.route('/api/archive/query', methods=['POST'])
  def query_archive():
      """查询归档数据: 先查热分区，再查冷分区，最后查归档文件"""
      params = request.json
      # 1. 查热分区
      result = query_hot_partition(params['table'], params['filters'])
      if result: return result
      # 2. 查冷分区
      result = query_cold_partition(params['table'], params['filters'])
      if result: return result
      # 3. 查归档文件（读取Parquet/CSV）
      return query_archive_files(params['table'], params['filters'])
  ```

- 6.9 监控告警配置：
  | 监控项 | 采集方式 | 阈值 | 告警级别 |
  | 分区清理成功率 | 元数据表统计 | <100% | 严重 |
  | 归档导出成功率 | 元数据表统计 | <100% | 严重 |
  | 冷分区数据量 | 分区统计 | >单分区5000万行 | 警告 |
  | 归档文件存储 | 文件系统监控 | >80% | 警告 |
  | 校验和不一致 | 自动校验 | 任意不一致 | 严重 |

#### 第7章：业务影响分析
- 7.1 对联机交易的影响：分区裁剪使联机交易仅扫描热分区，性能提升预估
- 7.2 对历史查询的影响：三级查询路由（热分区→冷分区→归档文件），延迟梯度
- 7.3 对报表/统计的影响：冷热分区UNION ALL聚合，归档文件Spark/Impala查询
- 7.4 对监管报送的影响：归档数据T+1还原至临时表供报送
- 7.5 对数据备份的影响：冷分区跳过日常备份，减少备份窗口

#### 第8章：运维管理
- 8.1 清理归档作业调度：银行业务日历，避开年终决算、结息日
- 8.2 监控指标：清理成功率、归档成功率、冷分区数据量、归档存储容量、还原响应时间
- 8.3 告警机制：清理失败、校验不一致、存储容量预警
- 8.4 应急预案：分区清理失败回滚、归档文件损坏恢复
- 8.5 运维操作手册：日常巡检、月度清理、季度归档、年度复盘

#### 第9章：风险与回滚
- 9.1 技术风险：分区重组锁表、分区键设计不当、归档文件损坏
- 9.2 业务风险：误将活跃数据分配至冷分区、归档文件查询超时
- 9.3 合规风险：未达保留期误归档
- 9.4 回滚方案：分区重组回滚、归档文件恢复至临时表
- 9.5 风险评估矩阵：风险点×概率×影响×缓解措施

#### 第10章：合规与审计
- 10.1 法规符合性对照表：逐条对照法规
- 10.2 数据安全：归档文件AES-256加密、访问控制、脱敏
- 10.3 审计追踪：清理/归档操作日志、审批流、元数据完整可追溯
- 10.4 销毁证明：归档文件物理销毁的不可逆证明
- 10.5 定期合规审查：年度合规自评

### 附录
- 附录A：86张表清理归档方案（从cleanup_archive_list.json读取，按分区策略重新编排）
- 附录B：分区DDL模板（核心表分区建表语句）
- 附录C：完整自动化脚本
- 附录D：信贷业务五维度分析矩阵（完整版）

## ADDED Requirements

### Requirement 1: 分区优先的清理方案
系统 SHALL 基于表分区实现冷热数据分离，通过分区重组或分区交换将冷数据隔离至冷分区。**严禁创建历史表。**

#### Scenario: 合同结清后冷却
- **WHEN** 合同状态为已终止/废止，终止日期超过1年，且无活跃借据
- **THEN** 对应数据行通过分区重组分配至冷分区，联机交易通过分区裁剪自动跳过

### Requirement 2: 文件导出归档
系统 SHALL 对冷分区数据执行文件导出，支持Parquet/CSV/JSON Lines格式，包含Snappy/Gzip压缩，文件命名含校验和。

#### Scenario: 年度归档
- **WHEN** 冷分区数据保留超过5年
- **THEN** 导出为Parquet文件，压缩后上传对象存储，源分区数据物理删除

### Requirement 3: 信贷业务五维度分析
系统 SHALL 在第2章提供完整信贷业务领域分析，覆盖贷款生命周期、产品类型、监管合规、风险控制、客户等级五个维度。

#### Scenario: 产品类型差异化
- **WHEN** 不同产品类型的贷款结清
- **THEN** 依据产品类型差异应用不同的冷却周期（个人贷款2年/对公贷款3年/票据1年/线上1年）

### Requirement 4: 多维度冷却条件筛选
系统 SHALL 设计多维度数据筛选规则，至少包含：贷款状态、时间范围、风险等级、客户等级、关联实体状态。

#### Scenario: 高风险客户数据保留
- **WHEN** 客户等级为黑名单/失信
- **THEN** 对应数据不进入冷却流程，永久保留在热分区

### Requirement 5: 可执行脚本
系统 SHALL 提供完整可执行脚本：分区DDL、数据筛选SQL、分区重组SQL、文件导出Python脚本、恢复脚本、调度配置。

### Requirement 6: 数据可恢复
系统 SHALL 确保归档数据可追溯、可查询、可恢复，提供归档查询API和恢复脚本。

## MODIFIED Requirements

### Requirement: 清理语义重新定义（V3.0.0）
**原定义**：清理=创建历史表+迁移数据+删除原表数据
**新定义**：清理=识别冷数据+分配至冷分区存储，严禁创建历史表

### Requirement: 归档语义重新定义（V3.0.0）
**原定义**：归档=在线历史库→离线归档文件
**新定义**：归档=冷分区数据→文件导出→对象存储，源数据物理删除

## REMOVED Requirements

### Requirement: 责任人分布
**Reason**: 新建项目架构设计阶段，不涉及运维责任人分配，聚焦方案设计本身

### Requirement: 历史表创建方案
**Reason**: 严禁创建历史表，统一使用分区方案实现冷热分离