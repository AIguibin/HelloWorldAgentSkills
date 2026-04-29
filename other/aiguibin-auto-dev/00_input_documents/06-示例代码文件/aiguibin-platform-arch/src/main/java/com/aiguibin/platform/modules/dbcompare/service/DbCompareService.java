package com.aiguibin.platform.modules.dbcompare.service;

import com.aiguibin.platform.modules.dbcompare.excel.*;
import com.aiguibin.platform.modules.dbcompare.model.dto.*;
import com.aiguibin.platform.modules.dbcompare.model.vo.*;
import com.baomidou.dynamic.datasource.toolkit.DynamicDataSourceContextHolder;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;

import java.io.File;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * 数据库比对服务
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class DbCompareService {

    private final ExcelParseService excelParseService;
    private final ExcelWriteService excelWriteService;
    private final SvnService svnService;
    private final NotifyService notifyService;
    private final DbMetaService dbMetaService;
    private final SqlGenService sqlGenService;

    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyyMMdd");
    private static final DateTimeFormatter DATE_TIME_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    /**
     * 环境数据源映射
     */
    private static final Map<String, List<String>> ENV_DATASOURCES = new HashMap<>();

    static {
        // DEV环境 - 7个数据库
        ENV_DATASOURCES.put("DEV", Arrays.asList(
                "dev-ncms-credit", "dev-ncms-rule", "dev-ncms-collateral",
                "dev-ncms-customer", "dev-ncms-product", "dev-ncms-account", "dev-ncms-batch"
        ));
        // SIT环境 - 7个数据库
        ENV_DATASOURCES.put("SIT", Arrays.asList(
                "sit-ncms-credit", "sit-ncms-rule", "sit-ncms-collateral",
                "sit-ncms-customer", "sit-ncms-product", "sit-ncms-account", "sit-ncms-batch"
        ));
        // UAT环境 - 12个数据库
        ENV_DATASOURCES.put("UAT", Arrays.asList(
                "uat-ncms-credit", "uat-ncms-rule", "uat-ncms-collateral",
                "uat-ncms-customer", "uat-ncms-product", "uat-ncms-account", "uat-ncms-batch",
                "uat-ncms-report", "uat-ncms-history", "uat-ncms-archive",
                "uat-ncms-log", "uat-ncms-config"
        ));
    }

    /**
     * 执行环境比对（该环境所有数据库）
     */
    public CompareResultVo compareEnv(String env, String triggerType) {
        log.info("开始{}环境比对, 触发类型: {}", env, triggerType);
        long startTime = System.currentTimeMillis();

        // 1. SVN更新设计文档
        svnService.updateDoc();

        // 2. 解析Excel文档
        DocData docData = excelParseService.parseDoc();

        // 3. 检查目录字段完整性
        List<MenuFieldCheckResult> menuCheckResults = checkMenuFields(docData);

        // 4. 获取该环境所有数据源
        List<String> dataSources = ENV_DATASOURCES.getOrDefault(env, Collections.emptyList());
        log.info("{}环境共有{}个数据库需要比对", env, dataSources.size());

        // 5. 循环执行各数据库比对
        List<DbCompareDetail> dbResults = new ArrayList<>();
        int totalTableDiff = 0;
        int totalColumnDiff = 0;
        int totalIndexDiff = 0;

        for (String dsKey : dataSources) {
            try {
                DbCompareDetail detail = compareSingleDbInternal(env, dsKey, docData);
                dbResults.add(detail);
                totalTableDiff += detail.getTableDiffCount();
                totalColumnDiff += detail.getColumnDiffCount();
                totalIndexDiff += detail.getIndexDiffCount();

                // 发送单个数据库完成通知
                notifyService.sendDbCompleteNotify(env, dsKey, detail);
            } catch (Exception e) {
                log.error("{}环境{}数据库比对失败", env, dsKey, e);
                dbResults.add(DbCompareDetail.fail(dsKey, e.getMessage()));
            }
        }

        long duration = System.currentTimeMillis() - startTime;

        // 6. 构建结果
        CompareResultVo result = new CompareResultVo();
        result.setEnv(env);
        result.setTriggerType(triggerType);
        result.setStartTime(LocalDateTime.now().format(DATE_TIME_FORMATTER));
        result.setDurationMs(duration);
        result.setStatus("SUCCESS");
        result.setTotalDbCount(dataSources.size());
        result.setSuccessCount((int) dbResults.stream().filter(DbCompareDetail::isSuccess).count());
        result.setDbResults(dbResults);
        result.setTotalTableDiff(totalTableDiff);
        result.setTotalColumnDiff(totalColumnDiff);
        result.setTotalIndexDiff(totalIndexDiff);
        result.setMenuCheckResults(menuCheckResults);

        log.info("{}环境比对完成, 成功: {}/{}", env, result.getSuccessCount(), result.getTotalDbCount());

        return result;
    }

    /**
     * 执行单个数据库比对（对外接口）
     */
    public CompareResultVo compareSingleDb(String env, String dbKey, String triggerType) {
        // SVN更新
        svnService.updateDoc();

        // 解析文档
        DocData docData = excelParseService.parseDoc();

        // 执行比对
        DbCompareDetail detail = compareSingleDbInternal(env, dbKey, docData);

        // 构建结果
        CompareResultVo result = new CompareResultVo();
        result.setEnv(env);
        result.setTriggerType(triggerType);
        result.setStartTime(LocalDateTime.now().format(DATE_TIME_FORMATTER));
        result.setStatus(detail.isSuccess() ? "SUCCESS" : "FAILED");
        result.setTotalDbCount(1);
        result.setSuccessCount(detail.isSuccess() ? 1 : 0);
        result.setDbResults(Collections.singletonList(detail));
        result.setTotalTableDiff(detail.getTableDiffCount());
        result.setTotalColumnDiff(detail.getColumnDiffCount());
        result.setTotalIndexDiff(detail.getIndexDiffCount());

        return result;
    }

    /**
     * 执行单个数据库比对（内部方法）
     */
    private DbCompareDetail compareSingleDbInternal(String env, String dsKey, DocData docData) {
        String dbName = extractDbName(dsKey);
        log.info("开始比对数据库: {} ({})", dsKey, dbName);
        long startTime = System.currentTimeMillis();

        // 切换数据源
        DynamicDataSourceContextHolder.push(dsKey);

        try {
            String dateStr = LocalDateTime.now().format(DATE_FORMATTER);
            String checkDate = LocalDateTime.now().format(DATE_TIME_FORMATTER);

            // 1. 表比对
            List<TableDiff> tableDiffs = compareTables(dbName, docData, checkDate);

            // 2. 字段比对
            ColumnCompareResult columnResult = compareColumns(dbName, docData, checkDate);

            // 3. 索引比对
            List<IndexDiff> indexDiffs = compareIndexes(dbName, docData, checkDate);

            // 4. 贯标检查
            List<StandardViolation> standardViolations = checkStandard(dbName, docData, checkDate);

            // 5. 生成结果文件
            String outputDir = System.getProperty("user.home") + "/platform-output/" + env + "/" + dbName;
            new File(outputDir).mkdirs();

            // 字段差异Excel
            String columnDiffPath = outputDir + "/" + dateStr + "_" + dbName + "_字段差异汇总.xlsx";
            excelWriteService.writeColumnDiff(columnDiffPath, dbName, checkDate,
                    columnResult.getDocMoreList(), columnResult.getDbMoreList(), columnResult.getTypeMismatchList());

            // 表差异Excel
            String tableDiffPath = outputDir + "/" + dateStr + "_" + dbName + "_表差异汇总.xlsx";
            excelWriteService.writeTableDiff(tableDiffPath, dbName, checkDate, tableDiffs);

            // 索引差异Excel
            String indexDiffPath = outputDir + "/" + dateStr + "_" + dbName + "_索引差异汇总.xlsx";
            excelWriteService.writeIndexDiff(indexDiffPath, dbName, checkDate, indexDiffs);

            // 贯标检查Excel
            if (!standardViolations.isEmpty()) {
                String standardPath = outputDir + "/" + dateStr + "_" + dbName + "_贯标检查结果.xlsx";
                excelWriteService.writeStandardCheck(standardPath, dbName, checkDate, standardViolations);
            }

            // 6. SVN上传
            svnService.uploadResult(env, dbName, columnDiffPath);
            svnService.uploadResult(env, dbName, tableDiffPath);
            svnService.uploadResult(env, dbName, indexDiffPath);

            long duration = System.currentTimeMillis() - startTime;

            return DbCompareDetail.success(dsKey, dbName, duration,
                    tableDiffs.size(), columnResult.getTotalCount(), indexDiffs.size());

        } finally {
            DynamicDataSourceContextHolder.poll();
        }
    }

    /**
     * 执行全环境比对
     */
    public List<CompareResultVo> compareAllEnv(String triggerType) {
        log.info("开始全环境比对");
        List<CompareResultVo> results = new ArrayList<>();

        // 顺序执行: DEV -> SIT -> UAT
        results.add(compareEnv("DEV", triggerType));
        results.add(compareEnv("SIT", triggerType));
        results.add(compareEnv("UAT", triggerType));

        // 发送汇总通知
        notifyService.sendAllEnvCompleteNotify(results);

        return results;
    }

    /**
     * 检查目录字段完整性
     */
    private List<MenuFieldCheckResult> checkMenuFields(DocData docData) {
        List<MenuFieldCheckResult> results = new ArrayList<>();

        for (MenuItem item : docData.getMenuList()) {
            // 检查必填字段
            checkField(results, item, "是否表分区", item.getIsPartition(), true);
            checkField(results, item, "贯标要求", item.getIsStandard(), true);
            checkField(results, item, "是否上线初始化", item.getIsInit(), true);
            checkField(results, item, "是否同步查询库", item.getIsSync(), true);
            checkField(results, item, "是否迁移", item.getIsMigrate(), true);
            checkField(results, item, "是否数据清理", item.getIsClean(), true);

            // 条件必填字段
            if ("是".equals(item.getIsPartition()) && StringUtils.isBlank(item.getPartitionKey())) {
                results.add(new MenuFieldCheckResult(item.getTableName(), item.getTableComment(),
                        "分区键", "是否表分区=是时必填", true, ""));
            }
            if ("是".equals(item.getIsClean()) && StringUtils.isBlank(item.getCleanPolicy())) {
                results.add(new MenuFieldCheckResult(item.getTableName(), item.getTableComment(),
                        "表数据清理策略", "是否数据清理=是时必填", true, ""));
            }
        }

        return results;
    }

    private void checkField(List<MenuFieldCheckResult> results, MenuItem item,
                            String fieldName, String fieldValue, boolean required) {
        if (required && StringUtils.isBlank(fieldValue)) {
            results.add(new MenuFieldCheckResult(item.getTableName(), item.getTableComment(),
                    fieldName, "必填字段", true, ""));
        }
    }

    /**
     * 表比对
     */
    private List<TableDiff> compareTables(String dbName, DocData docData, String checkDate) {
        List<TableDiff> diffs = new ArrayList<>();

        // 获取文档表名集合
        Set<String> docTables = docData.getMenuList().stream()
                .map(MenuItem::getTableName)
                .filter(StringUtils::isNotBlank)
                .map(String::toUpperCase)
                .collect(java.util.stream.Collectors.toSet());

        // 获取数据库表名集合
        List<TableInfo> dbTableList = dbMetaService.getTables(dbName);
        Set<String> dbTables = dbTableList.stream()
                .map(TableInfo::getTableName)
                .map(String::toUpperCase)
                .collect(java.util.stream.Collectors.toSet());

        int seq = 1;

        // 1. 文档比数据库多的表
        for (String tableName : docTables) {
            if (!dbTables.contains(tableName)) {
                MenuItem menu = findMenuByName(docData.getMenuList(), tableName);
                TableDiff diff = new TableDiff();
                diff.setSeq(String.valueOf(seq++));
                diff.setFileName(docData.getFileName());
                diff.setCheckDate(checkDate);
                diff.setDbName(dbName);
                diff.setTableName(tableName);
                diff.setTableComment(menu != null ? menu.getTableComment() : "");
                diff.setDiffType("1-文档比数据库多");
                diff.setDiffNote("文档比数据库多的表，需要创建");
                diff.setProcessScript(sqlGenService.genCreateTable(docData, tableName));
                diff.setBackupScript("");
                diff.setRemark("");
                diffs.add(diff);
            }
        }

        // 2. 数据库比文档多的表
        for (String tableName : dbTables) {
            if (!docTables.contains(tableName)) {
                TableInfo dbTable = findDbTableByName(dbTableList, tableName);
                TableDiff diff = new TableDiff();
                diff.setSeq(String.valueOf(seq++));
                diff.setFileName(docData.getFileName());
                diff.setCheckDate(checkDate);
                diff.setDbName(dbName);
                diff.setTableName(tableName);
                diff.setTableComment(dbTable != null ? dbTable.getTableComment() : "");
                diff.setDiffType("2-数据库比文档多");
                diff.setDiffNote("数据库比文档多的表，需要确认后删除");
                diff.setBackupScript("ALTER TABLE " + tableName + " RENAME TO " + tableName + "_BAK_" + DATE_FORMATTER.format(LocalDateTime.now()) + ";");
                diff.setProcessScript("DROP TABLE " + tableName + ";");
                diff.setRemark("请先备份再删除");
                diffs.add(diff);
            }
        }

        return diffs;
    }

    /**
     * 字段比对
     */
    private ColumnCompareResult compareColumns(String dbName, DocData docData, String checkDate) {
        ColumnCompareResult result = new ColumnCompareResult();
        List<ColumnDiff> docMoreList = new ArrayList<>();
        List<ColumnDiff> dbMoreList = new ArrayList<>();
        List<ColumnDiff> typeMismatchList = new ArrayList<>();

        int docMoreSeq = 1;
        int dbMoreSeq = 1;
        int typeSeq = 1;

        for (MenuItem menu : docData.getMenuList()) {
            String tableName = menu.getTableName();
            if (StringUtils.isBlank(tableName)) continue;

            // 获取文档字段
            List<ColumnItem> docColumns = docData.getColumnMap().get(tableName.toUpperCase());
            if (docColumns == null) continue;

            Map<String, ColumnItem> docColumnMap = docColumns.stream()
                    .collect(java.util.stream.Collectors.toMap(
                            c -> c.getColumnName().toUpperCase(), c -> c, (a, b) -> a));

            // 获取数据库字段
            List<ColumnInfo> dbColumns = dbMetaService.getColumns(dbName, tableName);
            Map<String, ColumnInfo> dbColumnMap = dbColumns.stream()
                    .collect(java.util.stream.Collectors.toMap(
                            c -> c.getColumnName().toUpperCase(), c -> c, (a, b) -> a));

            Set<String> docColNames = docColumnMap.keySet();
            Set<String> dbColNames = dbColumnMap.keySet();

            // 1. 文档字段多余数据库
            for (String colName : docColNames) {
                if (!dbColNames.contains(colName)) {
                    ColumnItem docCol = docColumnMap.get(colName);
                    ColumnDiff diff = createColumnDiff(docMoreSeq++, docData.getFileName(), checkDate,
                            dbName, tableName, menu.getTableComment(), docCol, null, null,
                            "1-文档字段多余数据库", "文档字段多余数据库字段",
                            sqlGenService.genAddColumn(tableName, docCol));
                    docMoreList.add(diff);
                }
            }

            // 2. 数据库字段多余文档
            for (String colName : dbColNames) {
                if (!docColNames.contains(colName)) {
                    ColumnInfo dbCol = dbColumnMap.get(colName);
                    ColumnDiff diff = createColumnDiff(dbMoreSeq++, docData.getFileName(), checkDate,
                            dbName, tableName, menu.getTableComment(), null, dbCol, null,
                            "2-数据库字段多余文档", "数据库字段多余文档字段",
                            "ALTER TABLE " + tableName + " DROP COLUMN " + colName + ";");
                    dbMoreList.add(diff);
                }
            }

            // 3. 字段类型不一致
            for (String colName : docColNames) {
                if (dbColNames.contains(colName)) {
                    ColumnItem docCol = docColumnMap.get(colName);
                    ColumnInfo dbCol = dbColumnMap.get(colName);

                    String docType = normalizeType(docCol.getColumnType());
                    String dbType = normalizeType(dbCol.getColumnType());

                    if (!docType.equalsIgnoreCase(dbType)) {
                        ColumnDiff diff = createColumnDiff(typeSeq++, docData.getFileName(), checkDate,
                                dbName, tableName, menu.getTableComment(), docCol, dbCol, null,
                                "3-字段类型不一致", "字段类型不一致",
                                sqlGenService.genModifyColumn(tableName, docCol));
                        typeMismatchList.add(diff);
                    }
                }
            }
        }

        result.setDocMoreList(docMoreList);
        result.setDbMoreList(dbMoreList);
        result.setTypeMismatchList(typeMismatchList);
        return result;
    }

    /**
     * 索引比对
     */
    private List<IndexDiff> compareIndexes(String dbName, DocData docData, String checkDate) {
        List<IndexDiff> diffs = new ArrayList<>();
        int seq = 1;

        for (MenuItem menu : docData.getMenuList()) {
            String tableName = menu.getTableName();
            if (StringUtils.isBlank(tableName)) continue;

            // 获取文档索引
            List<IndexItem> docIndexes = docData.getIndexMap().getOrDefault(tableName.toUpperCase(), Collections.emptyList());
            Map<String, IndexItem> docIndexMap = docIndexes.stream()
                    .collect(java.util.stream.Collectors.toMap(
                            i -> i.getIndexName().toUpperCase(), i -> i, (a, b) -> a));

            // 获取数据库索引
            List<IndexInfo> dbIndexes = dbMetaService.getIndexes(dbName, tableName);
            Map<String, IndexInfo> dbIndexMap = dbIndexes.stream()
                    .collect(java.util.stream.Collectors.toMap(
                            i -> i.getIndexName().toUpperCase(), i -> i, (a, b) -> a));

            Set<String> docIndexNames = docIndexMap.keySet();
            Set<String> dbIndexNames = dbIndexMap.keySet();

            // 1. 文档索引多余数据库
            for (String idxName : docIndexNames) {
                if (!dbIndexNames.contains(idxName)) {
                    IndexItem docIdx = docIndexMap.get(idxName);
                    IndexDiff diff = new IndexDiff();
                    diff.setSeq(String.valueOf(seq++));
                    diff.setFileName(docData.getFileName());
                    diff.setCheckDate(checkDate);
                    diff.setDbName(dbName);
                    diff.setTableName(tableName);
                    diff.setIndexName(idxName);
                    diff.setIndexType(docIdx.getIndexType());
                    diff.setDocIndexColumn(docIdx.getIndexColumn());
                    diff.setDbIndexColumn("");
                    diff.setDiffType("1-文档索引多余数据库");
                    diff.setDiffNote("文档索引多余数据库索引");
                    diff.setProcessScript(sqlGenService.genCreateIndex(tableName, docIdx));
                    diff.setRemark("");
                    diffs.add(diff);
                }
            }

            // 2. 数据库索引多余文档
            for (String idxName : dbIndexNames) {
                if (!docIndexNames.contains(idxName)) {
                    IndexInfo dbIdx = dbIndexMap.get(idxName);
                    IndexDiff diff = new IndexDiff();
                    diff.setSeq(String.valueOf(seq++));
                    diff.setFileName(docData.getFileName());
                    diff.setCheckDate(checkDate);
                    diff.setDbName(dbName);
                    diff.setTableName(tableName);
                    diff.setIndexName(idxName);
                    diff.setIndexType(dbIdx.getIndexType());
                    diff.setDocIndexColumn("");
                    diff.setDbIndexColumn(dbIdx.getIndexColumn());
                    diff.setDiffType("2-数据库索引多余文档");
                    diff.setDiffNote("数据库索引多余文档索引");
                    diff.setProcessScript("DROP INDEX " + idxName + " ON " + tableName + ";");
                    diff.setRemark("");
                    diffs.add(diff);
                }
            }

            // 3. 索引字段不一致
            for (String idxName : docIndexNames) {
                if (dbIndexNames.contains(idxName)) {
                    IndexItem docIdx = docIndexMap.get(idxName);
                    IndexInfo dbIdx = dbIndexMap.get(idxName);

                    String docCols = normalizeIndexColumn(docIdx.getIndexColumn());
                    String dbCols = normalizeIndexColumn(dbIdx.getIndexColumn());

                    if (!docCols.equalsIgnoreCase(dbCols)) {
                        IndexDiff diff = new IndexDiff();
                        diff.setSeq(String.valueOf(seq++));
                        diff.setFileName(docData.getFileName());
                        diff.setCheckDate(checkDate);
                        diff.setDbName(dbName);
                        diff.setTableName(tableName);
                        diff.setIndexName(idxName);
                        diff.setIndexType(docIdx.getIndexType());
                        diff.setDocIndexColumn(docIdx.getIndexColumn());
                        diff.setDbIndexColumn(dbIdx.getIndexColumn());
                        diff.setDiffType("3-索引字段不一致");
                        diff.setDiffNote("索引字段不一致");
                        diff.setProcessScript(sqlGenService.genRecreateIndex(tableName, docIdx));
                        diff.setRemark("");
                        diffs.add(diff);
                    }
                }
            }
        }

        return diffs;
    }

    /**
     * 贯标检查
     */
    private List<StandardViolation> checkStandard(String dbName, DocData docData, String checkDate) {
        List<StandardViolation> violations = new ArrayList<>();

        // 筛选出需要贯标检查的表
        List<MenuItem> standardTables = docData.getMenuList().stream()
                .filter(m -> "Y".equalsIgnoreCase(m.getIsStandard()) || "是".equals(m.getIsStandard()))
                .collect(java.util.stream.Collectors.toList());

        if (standardTables.isEmpty()) {
            return violations;
        }

        // 构建贯标字段映射
        Map<String, List<ColumnItem>> zhNameMap = new HashMap<>();
        Map<String, List<ColumnItem>> enNameMap = new HashMap<>();

        for (MenuItem menu : standardTables) {
            List<ColumnItem> columns = docData.getColumnMap().get(menu.getTableName().toUpperCase());
            if (columns == null) continue;

            for (ColumnItem col : columns) {
                if (StringUtils.isNotBlank(col.getColumnComment())) {
                    zhNameMap.computeIfAbsent(col.getColumnComment(), k -> new ArrayList<>()).add(col);
                }
                if (StringUtils.isNotBlank(col.getColumnName())) {
                    enNameMap.computeIfAbsent(col.getColumnName().toUpperCase(), k -> new ArrayList<>()).add(col);
                }
            }
        }

        int seq = 1;

        // 检查同中文名不同英文名
        for (Map.Entry<String, List<ColumnItem>> entry : zhNameMap.entrySet()) {
            List<ColumnItem> fields = entry.getValue();
            if (fields.size() < 2) continue;

            Set<String> enNames = fields.stream()
                    .map(ColumnItem::getColumnName)
                    .map(String::toUpperCase)
                    .collect(java.util.stream.Collectors.toSet());

            if (enNames.size() > 1) {
                for (ColumnItem field : fields) {
                    StandardViolation v = new StandardViolation();
                    v.setSeq(String.valueOf(seq++));
                    v.setFileName(docData.getFileName());
                    v.setCheckDate(checkDate);
                    v.setDbName(dbName);
                    v.setTableName(field.getTableName());
                    v.setColumnName(field.getColumnName());
                    v.setViolationType("同中文名不同英文名");
                    v.setViolationNote("字段中文名[" + entry.getKey() + "]对应多个英文名: " + enNames);
                    violations.add(v);
                }
            }
        }

        // 检查同英文名不同中文名、不同类型
        for (Map.Entry<String, List<ColumnItem>> entry : enNameMap.entrySet()) {
            List<ColumnItem> fields = entry.getValue();
            if (fields.size() < 2) continue;

            Set<String> zhNames = fields.stream()
                    .map(ColumnItem::getColumnComment)
                    .collect(java.util.stream.Collectors.toSet());
            Set<String> types = fields.stream()
                    .map(ColumnItem::getColumnType)
                    .map(this::normalizeType)
                    .collect(java.util.stream.Collectors.toSet());

            if (zhNames.size() > 1) {
                for (ColumnItem field : fields) {
                    StandardViolation v = new StandardViolation();
                    v.setSeq(String.valueOf(seq++));
                    v.setFileName(docData.getFileName());
                    v.setCheckDate(checkDate);
                    v.setDbName(dbName);
                    v.setTableName(field.getTableName());
                    v.setColumnName(field.getColumnName());
                    v.setViolationType("同英文名不同中文名");
                    v.setViolationNote("字段英文名[" + entry.getKey() + "]对应多个中文名: " + zhNames);
                    violations.add(v);
                }
            }

            if (types.size() > 1) {
                for (ColumnItem field : fields) {
                    StandardViolation v = new StandardViolation();
                    v.setSeq(String.valueOf(seq++));
                    v.setFileName(docData.getFileName());
                    v.setCheckDate(checkDate);
                    v.setDbName(dbName);
                    v.setTableName(field.getTableName());
                    v.setColumnName(field.getColumnName());
                    v.setViolationType("同英文名同中文名但类型不同");
                    v.setViolationNote("字段英文名[" + entry.getKey() + "]对应多个类型: " + types);
                    violations.add(v);
                }
            }
        }

        return violations;
    }

    private ColumnDiff createColumnDiff(int seq, String fileName, String checkDate, String dbName,
                                        String tableName, String tableComment, ColumnItem docCol,
                                        ColumnInfo dbCol, StandardField standardField,
                                        String diffType, String diffNote, String processScript) {
        ColumnDiff diff = new ColumnDiff();
        diff.setSeq(String.valueOf(seq));
        diff.setFileName(fileName);
        diff.setCheckDate(checkDate);
        diff.setDbName(dbName);
        diff.setTableName(tableName);
        diff.setTableComment(tableComment);
        diff.setDocColumnName(docCol != null ? docCol.getColumnName() : "");
        diff.setDbColumnName(dbCol != null ? dbCol.getColumnName() : "");
        diff.setStandardColumnName(standardField != null ? standardField.getColumnName() : "");
        diff.setDocColumnComment(docCol != null ? docCol.getColumnComment() : "");
        diff.setDbColumnComment(dbCol != null ? dbCol.getColumnComment() : "");
        diff.setStandardColumnComment(standardField != null ? standardField.getColumnComment() : "");
        diff.setDocColumnType(docCol != null ? docCol.getColumnType() : "");
        diff.setDbColumnType(dbCol != null ? dbCol.getColumnType() : "");
        diff.setStandardColumnType(standardField != null ? standardField.getColumnType() : "");
        diff.setDiffType(diffType);
        diff.setDiffNote(diffNote);
        diff.setProcessScript(processScript);
        diff.setRemark("");
        return diff;
    }

    private String normalizeType(String type) {
        if (StringUtils.isBlank(type)) return "";
        return type.toUpperCase().replaceAll("\\s+", "").replace("(", "").replace(")", "");
    }

    private String normalizeIndexColumn(String columns) {
        if (StringUtils.isBlank(columns)) return "";
        return columns.toUpperCase().replaceAll("\\s+", "");
    }

    private String extractDbName(String dsKey) {
        return dsKey.substring(dsKey.lastIndexOf("-") + 1);
    }

    private MenuItem findMenuByName(List<MenuItem> menuList, String tableName) {
        return menuList.stream()
                .filter(m -> tableName.equalsIgnoreCase(m.getTableName()))
                .findFirst()
                .orElse(null);
    }

    private TableInfo findDbTableByName(List<TableInfo> dbTableList, String tableName) {
        return dbTableList.stream()
                .filter(t -> tableName.equalsIgnoreCase(t.getTableName()))
                .findFirst()
                .orElse(null);
    }

    public List<ExecuteRecordVo> getRecords(String env, String status) {
        // TODO: 实现查询
        return Collections.emptyList();
    }

    public CompareResultVo getResult(String recordId) {
        // TODO: 实现查询
        return null;
    }
}
