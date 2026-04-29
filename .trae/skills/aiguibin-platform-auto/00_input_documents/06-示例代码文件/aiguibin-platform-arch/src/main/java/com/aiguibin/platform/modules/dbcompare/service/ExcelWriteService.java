package com.aiguibin.platform.modules.dbcompare.service;

import com.aiguibin.platform.modules.dbcompare.model.dto.*;
import com.alibaba.excel.EasyExcel;
import com.alibaba.excel.ExcelWriter;
import com.alibaba.excel.write.metadata.WriteSheet;
import com.alibaba.excel.annotation.ExcelProperty;
import com.alibaba.excel.annotation.write.style.ColumnWidth;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Excel写入服务
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Slf4j
@Service
public class ExcelWriteService {

    /**
     * 写入字段差异Excel
     */
    public void writeColumnDiff(String outputPath, String dbName, String checkDate,
                                List<ColumnDiff> docMoreList,
                                List<ColumnDiff> dbMoreList,
                                List<ColumnDiff> typeMismatchList) {
        ExcelWriter writer = EasyExcel.write(outputPath).build();

        // Sheet1: 文档字段多余数据库字段
        WriteSheet sheet1 = EasyExcel.writerSheet(0, "文档字段多余数据库字段")
                .head(ColumnDiffDocMoreVo.class)
                .build();
        writer.write(convertDocMoreList(docMoreList), sheet1);

        // Sheet2: 数据库字段多余文档字段
        WriteSheet sheet2 = EasyExcel.writerSheet(1, "数据库字段多余文档字段")
                .head(ColumnDiffDbMoreVo.class)
                .build();
        writer.write(convertDbMoreList(dbMoreList), sheet2);

        // Sheet3: 字段类型不一致
        WriteSheet sheet3 = EasyExcel.writerSheet(2, "字段类型不一致")
                .head(ColumnDiffTypeMismatchVo.class)
                .build();
        writer.write(convertTypeMismatchList(typeMismatchList), sheet3);

        writer.finish();
        log.info("字段差异Excel已生成: {}", outputPath);
    }

    /**
     * 写入表差异Excel
     */
    public void writeTableDiff(String outputPath, String dbName, String checkDate, List<TableDiff> diffs) {
        List<TableDiffVo> voList = diffs.stream()
                .map(this::convertTableDiff)
                .collect(Collectors.toList());

        EasyExcel.write(outputPath, TableDiffVo.class)
                .sheet("表差异")
                .doWrite(voList);

        log.info("表差异Excel已生成: {}", outputPath);
    }

    /**
     * 写入索引差异Excel
     */
    public void writeIndexDiff(String outputPath, String dbName, String checkDate, List<IndexDiff> diffs) {
        List<IndexDiffVo> voList = diffs.stream()
                .map(this::convertIndexDiff)
                .collect(Collectors.toList());

        EasyExcel.write(outputPath, IndexDiffVo.class)
                .sheet("索引差异")
                .doWrite(voList);

        log.info("索引差异Excel已生成: {}", outputPath);
    }

    /**
     * 写入贯标检查结果Excel
     */
    public void writeStandardCheck(String outputPath, String dbName, String checkDate, List<StandardViolation> violations) {
        List<StandardViolationVo> voList = violations.stream()
                .map(this::convertStandardViolation)
                .collect(Collectors.toList());

        EasyExcel.write(outputPath, StandardViolationVo.class)
                .sheet("贯标异常")
                .doWrite(voList);

        log.info("贯标检查Excel已生成: {}", outputPath);
    }

    // ============== VO转换方法 ==============

    private List<ColumnDiffDocMoreVo> convertDocMoreList(List<ColumnDiff> list) {
        return list.stream().map(diff -> {
            ColumnDiffDocMoreVo vo = new ColumnDiffDocMoreVo();
            vo.setSeq(diff.getSeq());
            vo.setFileName(diff.getFileName());
            vo.setCheckDate(diff.getCheckDate());
            vo.setDbName(diff.getDbName());
            vo.setTableName(diff.getTableName());
            vo.setTableComment(diff.getTableComment());
            vo.setDocColumnName(diff.getDocColumnName());
            vo.setDbColumnName(diff.getDbColumnName());
            vo.setStandardColumnName(diff.getStandardColumnName());
            vo.setDocColumnComment(diff.getDocColumnComment());
            vo.setDbColumnComment(diff.getDbColumnComment());
            vo.setStandardColumnComment(diff.getStandardColumnComment());
            vo.setDocColumnType(diff.getDocColumnType());
            vo.setDbColumnType(diff.getDbColumnType());
            vo.setStandardColumnType(diff.getStandardColumnType());
            vo.setDiffType(diff.getDiffType());
            vo.setDiffNote(diff.getDiffNote());
            vo.setProcessScript(diff.getProcessScript());
            vo.setRemark(diff.getRemark());
            return vo;
        }).collect(Collectors.toList());
    }

    private List<ColumnDiffDbMoreVo> convertDbMoreList(List<ColumnDiff> list) {
        return list.stream().map(diff -> {
            ColumnDiffDbMoreVo vo = new ColumnDiffDbMoreVo();
            vo.setSeq(diff.getSeq());
            vo.setFileName(diff.getFileName());
            vo.setCheckDate(diff.getCheckDate());
            vo.setDbName(diff.getDbName());
            vo.setTableName(diff.getTableName());
            vo.setTableComment(diff.getTableComment());
            vo.setDocColumnName(diff.getDocColumnName());
            vo.setDbColumnName(diff.getDbColumnName());
            vo.setStandardColumnName(diff.getStandardColumnName());
            vo.setDocColumnComment(diff.getDocColumnComment());
            vo.setDbColumnComment(diff.getDbColumnComment());
            vo.setStandardColumnComment(diff.getStandardColumnComment());
            vo.setDocColumnType(diff.getDocColumnType());
            vo.setDbColumnType(diff.getDbColumnType());
            vo.setStandardColumnType(diff.getStandardColumnType());
            vo.setDiffType(diff.getDiffType());
            vo.setDiffNote(diff.getDiffNote());
            vo.setProcessScript(diff.getProcessScript());
            vo.setRemark(diff.getRemark());
            return vo;
        }).collect(Collectors.toList());
    }

    private List<ColumnDiffTypeMismatchVo> convertTypeMismatchList(List<ColumnDiff> list) {
        return list.stream().map(diff -> {
            ColumnDiffTypeMismatchVo vo = new ColumnDiffTypeMismatchVo();
            vo.setSeq(diff.getSeq());
            vo.setFileName(diff.getFileName());
            vo.setCheckDate(diff.getCheckDate());
            vo.setDbName(diff.getDbName());
            vo.setTableName(diff.getTableName());
            vo.setTableComment(diff.getTableComment());
            vo.setDocColumnName(diff.getDocColumnName());
            vo.setDbColumnName(diff.getDbColumnName());
            vo.setStandardColumnName(diff.getStandardColumnName());
            vo.setDocColumnComment(diff.getDocColumnComment());
            vo.setDbColumnComment(diff.getDbColumnComment());
            vo.setStandardColumnComment(diff.getStandardColumnComment());
            vo.setDocColumnType(diff.getDocColumnType());
            vo.setDbColumnType(diff.getDbColumnType());
            vo.setStandardColumnType(diff.getStandardColumnType());
            vo.setDiffType(diff.getDiffType());
            vo.setDiffNote(diff.getDiffNote());
            vo.setProcessScript(diff.getProcessScript());
            vo.setRemark(diff.getRemark());
            return vo;
        }).collect(Collectors.toList());
    }

    private TableDiffVo convertTableDiff(TableDiff diff) {
        TableDiffVo vo = new TableDiffVo();
        vo.setSeq(diff.getSeq());
        vo.setFileName(diff.getFileName());
        vo.setCheckDate(diff.getCheckDate());
        vo.setDbName(diff.getDbName());
        vo.setTableName(diff.getTableName());
        vo.setTableComment(diff.getTableComment());
        vo.setDiffType(diff.getDiffType());
        vo.setDiffNote(diff.getDiffNote());
        vo.setProcessScript(diff.getProcessScript());
        vo.setBackupScript(diff.getBackupScript());
        vo.setRemark(diff.getRemark());
        return vo;
    }

    private IndexDiffVo convertIndexDiff(IndexDiff diff) {
        IndexDiffVo vo = new IndexDiffVo();
        vo.setSeq(diff.getSeq());
        vo.setFileName(diff.getFileName());
        vo.setCheckDate(diff.getCheckDate());
        vo.setDbName(diff.getDbName());
        vo.setTableName(diff.getTableName());
        vo.setIndexName(diff.getIndexName());
        vo.setIndexType(diff.getIndexType());
        vo.setDocIndexColumn(diff.getDocIndexColumn());
        vo.setDbIndexColumn(diff.getDbIndexColumn());
        vo.setDiffType(diff.getDiffType());
        vo.setDiffNote(diff.getDiffNote());
        vo.setProcessScript(diff.getProcessScript());
        vo.setRemark(diff.getRemark());
        return vo;
    }

    private StandardViolationVo convertStandardViolation(StandardViolation v) {
        StandardViolationVo vo = new StandardViolationVo();
        vo.setSeq(v.getSeq());
        vo.setFileName(v.getFileName());
        vo.setCheckDate(v.getCheckDate());
        vo.setDbName(v.getDbName());
        vo.setTableName(v.getTableName());
        vo.setColumnName(v.getColumnName());
        vo.setViolationType(v.getViolationType());
        vo.setViolationNote(v.getViolationNote());
        return vo;
    }

    // ============== VO类定义 ==============

    @Data
    public static class ColumnDiffDocMoreVo {
        @ExcelProperty("序号") @ColumnWidth(6) private String seq;
        @ExcelProperty("文件名") @ColumnWidth(30) private String fileName;
        @ExcelProperty("检查日期") @ColumnWidth(15) private String checkDate;
        @ExcelProperty("数据库名称") @ColumnWidth(20) private String dbName;
        @ExcelProperty("表名称") @ColumnWidth(30) private String tableName;
        @ExcelProperty("表名称中文") @ColumnWidth(30) private String tableComment;
        @ExcelProperty("文档字段名称") @ColumnWidth(25) private String docColumnName;
        @ExcelProperty("数据库字段名称") @ColumnWidth(25) private String dbColumnName;
        @ExcelProperty("贯标字段名称") @ColumnWidth(25) private String standardColumnName;
        @ExcelProperty("文档字段名称中文") @ColumnWidth(25) private String docColumnComment;
        @ExcelProperty("数据库字段名称中文") @ColumnWidth(25) private String dbColumnComment;
        @ExcelProperty("贯标字段名称中文") @ColumnWidth(25) private String standardColumnComment;
        @ExcelProperty("文档字段类型") @ColumnWidth(20) private String docColumnType;
        @ExcelProperty("数据库字段类型") @ColumnWidth(20) private String dbColumnType;
        @ExcelProperty("贯标字段类型") @ColumnWidth(20) private String standardColumnType;
        @ExcelProperty("差异类型") @ColumnWidth(30) private String diffType;
        @ExcelProperty("差异说明") @ColumnWidth(40) private String diffNote;
        @ExcelProperty("处理脚本") @ColumnWidth(80) private String processScript;
        @ExcelProperty("备注说明") @ColumnWidth(30) private String remark;
    }

    @Data
    public static class ColumnDiffDbMoreVo {
        @ExcelProperty("序号") @ColumnWidth(6) private String seq;
        @ExcelProperty("文件名") @ColumnWidth(30) private String fileName;
        @ExcelProperty("检查日期") @ColumnWidth(15) private String checkDate;
        @ExcelProperty("数据库名称") @ColumnWidth(20) private String dbName;
        @ExcelProperty("表名称") @ColumnWidth(30) private String tableName;
        @ExcelProperty("表名称中文") @ColumnWidth(30) private String tableComment;
        @ExcelProperty("文档字段名称") @ColumnWidth(25) private String docColumnName;
        @ExcelProperty("数据库字段名称") @ColumnWidth(25) private String dbColumnName;
        @ExcelProperty("贯标字段名称") @ColumnWidth(25) private String standardColumnName;
        @ExcelProperty("文档字段名称中文") @ColumnWidth(25) private String docColumnComment;
        @ExcelProperty("数据库字段名称中文") @ColumnWidth(25) private String dbColumnComment;
        @ExcelProperty("贯标字段名称中文") @ColumnWidth(25) private String standardColumnComment;
        @ExcelProperty("文档字段类型") @ColumnWidth(20) private String docColumnType;
        @ExcelProperty("数据库字段类型") @ColumnWidth(20) private String dbColumnType;
        @ExcelProperty("贯标字段类型") @ColumnWidth(20) private String standardColumnType;
        @ExcelProperty("差异类型") @ColumnWidth(30) private String diffType;
        @ExcelProperty("差异说明") @ColumnWidth(40) private String diffNote;
        @ExcelProperty("处理脚本") @ColumnWidth(80) private String processScript;
        @ExcelProperty("备注说明") @ColumnWidth(30) private String remark;
    }

    @Data
    public static class ColumnDiffTypeMismatchVo {
        @ExcelProperty("序号") @ColumnWidth(6) private String seq;
        @ExcelProperty("文件名") @ColumnWidth(30) private String fileName;
        @ExcelProperty("检查日期") @ColumnWidth(15) private String checkDate;
        @ExcelProperty("数据库名称") @ColumnWidth(20) private String dbName;
        @ExcelProperty("表名称") @ColumnWidth(30) private String tableName;
        @ExcelProperty("表名称中文") @ColumnWidth(30) private String tableComment;
        @ExcelProperty("文档字段名称") @ColumnWidth(25) private String docColumnName;
        @ExcelProperty("数据库字段名称") @ColumnWidth(25) private String dbColumnName;
        @ExcelProperty("贯标字段名称") @ColumnWidth(25) private String standardColumnName;
        @ExcelProperty("文档字段名称中文") @ColumnWidth(25) private String docColumnComment;
        @ExcelProperty("数据库字段名称中文") @ColumnWidth(25) private String dbColumnComment;
        @ExcelProperty("贯标字段名称中文") @ColumnWidth(25) private String standardColumnComment;
        @ExcelProperty("文档字段类型") @ColumnWidth(20) private String docColumnType;
        @ExcelProperty("数据库字段类型") @ColumnWidth(20) private String dbColumnType;
        @ExcelProperty("贯标字段类型") @ColumnWidth(20) private String standardColumnType;
        @ExcelProperty("差异类型") @ColumnWidth(30) private String diffType;
        @ExcelProperty("差异说明") @ColumnWidth(40) private String diffNote;
        @ExcelProperty("处理脚本") @ColumnWidth(80) private String processScript;
        @ExcelProperty("备注说明") @ColumnWidth(30) private String remark;
    }

    @Data
    public static class TableDiffVo {
        @ExcelProperty("序号") @ColumnWidth(6) private String seq;
        @ExcelProperty("文件名") @ColumnWidth(30) private String fileName;
        @ExcelProperty("检查日期") @ColumnWidth(15) private String checkDate;
        @ExcelProperty("数据库名称") @ColumnWidth(20) private String dbName;
        @ExcelProperty("表名称") @ColumnWidth(30) private String tableName;
        @ExcelProperty("表名称中文") @ColumnWidth(30) private String tableComment;
        @ExcelProperty("差异类型") @ColumnWidth(30) private String diffType;
        @ExcelProperty("差异说明") @ColumnWidth(40) private String diffNote;
        @ExcelProperty("处理脚本") @ColumnWidth(80) private String processScript;
        @ExcelProperty("备份脚本") @ColumnWidth(80) private String backupScript;
        @ExcelProperty("备注说明") @ColumnWidth(30) private String remark;
    }

    @Data
    public static class IndexDiffVo {
        @ExcelProperty("序号") @ColumnWidth(6) private String seq;
        @ExcelProperty("文件名") @ColumnWidth(30) private String fileName;
        @ExcelProperty("检查日期") @ColumnWidth(15) private String checkDate;
        @ExcelProperty("数据库名称") @ColumnWidth(20) private String dbName;
        @ExcelProperty("表名称") @ColumnWidth(30) private String tableName;
        @ExcelProperty("索引名称") @ColumnWidth(30) private String indexName;
        @ExcelProperty("索引类型") @ColumnWidth(15) private String indexType;
        @ExcelProperty("文档索引字段") @ColumnWidth(40) private String docIndexColumn;
        @ExcelProperty("数据库索引字段") @ColumnWidth(40) private String dbIndexColumn;
        @ExcelProperty("差异类型") @ColumnWidth(30) private String diffType;
        @ExcelProperty("差异说明") @ColumnWidth(40) private String diffNote;
        @ExcelProperty("处理脚本") @ColumnWidth(80) private String processScript;
        @ExcelProperty("备注说明") @ColumnWidth(30) private String remark;
    }

    @Data
    public static class StandardViolationVo {
        @ExcelProperty("序号") @ColumnWidth(6) private String seq;
        @ExcelProperty("文件名") @ColumnWidth(30) private String fileName;
        @ExcelProperty("检查日期") @ColumnWidth(15) private String checkDate;
        @ExcelProperty("数据库名称") @ColumnWidth(20) private String dbName;
        @ExcelProperty("表名称") @ColumnWidth(30) private String tableName;
        @ExcelProperty("字段名称") @ColumnWidth(25) private String columnName;
        @ExcelProperty("异常类型") @ColumnWidth(30) private String violationType;
        @ExcelProperty("异常说明") @ColumnWidth(60) private String violationNote;
    }
}
