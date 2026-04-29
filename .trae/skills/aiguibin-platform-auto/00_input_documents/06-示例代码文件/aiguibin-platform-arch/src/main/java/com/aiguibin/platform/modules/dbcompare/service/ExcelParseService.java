package com.aiguibin.platform.modules.dbcompare.service;

import com.aiguibin.platform.modules.dbcompare.model.dto.*;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.ss.usermodel.WorkbookFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.FileInputStream;
import java.util.*;

/**
 * Excel解析服务
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Slf4j
@Service
public class ExcelParseService {

    @Value("${svn.work-copy-path}")
    private String workCopyPath;

    @Value("${svn.doc-relative-path:docs}")
    private String docRelativePath;

    /**
     * 解析设计文档
     */
    public DocData parseDoc() {
        DocData docData = new DocData();

        // 查找文档文件
        File docDir = new File(workCopyPath + "/" + docRelativePath);
        File[] docFiles = docDir.listFiles((dir, name) -> name.endsWith(".xlsx") || name.endsWith(".xls"));

        if (docFiles == null || docFiles.length == 0) {
            throw new RuntimeException("未找到设计文档");
        }

        File docFile = docFiles[0];
        docData.setFileName(docFile.getName());
        docData.setFilePath(docFile.getAbsolutePath());

        log.info("开始解析设计文档: {}", docFile.getName());

        try (FileInputStream fis = new FileInputStream(docFile);
             Workbook workbook = WorkbookFactory.create(fis)) {

            // 1. 解析目录Sheet
            Sheet menuSheet = findSheet(workbook, "目录");
            if (menuSheet == null) {
                throw new RuntimeException("未找到目录Sheet");
            }
            List<MenuItem> menuList = parseMenuSheet(menuSheet);
            docData.setMenuList(menuList);
            log.info("解析到{}张表", menuList.size());

            // 2. 解析字段Sheet
            Map<String, List<ColumnItem>> columnMap = parseColumnSheets(workbook, menuList);
            docData.setColumnMap(columnMap);

            // 3. 解析索引Sheet
            Sheet indexSheet = findSheet(workbook, "索引");
            if (indexSheet == null) {
                indexSheet = findSheet(workbook, "索引目录");
            }
            if (indexSheet != null) {
                Map<String, List<IndexItem>> indexMap = parseIndexSheet(indexSheet);
                docData.setIndexMap(indexMap);
                log.info("解析到{}张表的索引", indexMap.size());
            } else {
                docData.setIndexMap(new HashMap<>());
            }

        } catch (Exception e) {
            throw new RuntimeException("解析设计文档失败", e);
        }

        return docData;
    }

    /**
     * 解析目录Sheet
     * 起始行: 第15行 (索引14)
     */
    private List<MenuItem> parseMenuSheet(Sheet sheet) {
        List<MenuItem> list = new ArrayList<>();
        int startRow = 14; // 第15行

        for (int i = startRow; i <= sheet.getLastRowNum(); i++) {
            Row row = sheet.getRow(i);
            if (row == null) continue;

            String tableName = getCellValue(row.getCell(4)); // 表名（英文）
            if (StringUtils.isBlank(tableName)) continue;

            MenuItem item = new MenuItem();
            item.setSeq(getCellValue(row.getCell(0)));
            item.setDatabaseName(getCellValue(row.getCell(1)));
            item.setModule(getCellValue(row.getCell(2)));
            item.setOwner(getCellValue(row.getCell(3)));
            item.setTableName(tableName.trim());
            item.setTableComment(getCellValue(row.getCell(5)));
            item.setIsShard(getCellValue(row.getCell(6)));
            item.setShardKey(getCellValue(row.getCell(7)));
            item.setIsInit(getCellValue(row.getCell(8)));
            item.setInitCount(getCellValue(row.getCell(9)));
            item.setIsMigrate(getCellValue(row.getCell(10)));
            item.setIsSync(getCellValue(row.getCell(11)));
            item.setIsStandard(getCellValue(row.getCell(12))); // 是否贯标
            item.setIsClean(getCellValue(row.getCell(13)));
            item.setCleanPolicy(getCellValue(row.getCell(14)));
            item.setArchivePolicy(getCellValue(row.getCell(15)));
            item.setRemark(getCellValue(row.getCell(16)));

            // 新增字段
            item.setIsPartition(getCellValue(row.getCell(17)));
            item.setPartitionKey(getCellValue(row.getCell(18)));
            item.setOldDataCount(getCellValue(row.getCell(19)));
            item.setFutureDataEstimate(getCellValue(row.getCell(20)));

            list.add(item);
        }

        return list;
    }

    /**
     * 解析字段Sheet
     */
    private Map<String, List<ColumnItem>> parseColumnSheets(Workbook workbook, List<MenuItem> menuList) {
        Map<String, List<ColumnItem>> result = new HashMap<>();

        for (MenuItem menu : menuList) {
            String sheetName = findSheetName(workbook, menu.getTableComment());
            if (sheetName == null) continue;

            Sheet sheet = workbook.getSheet(sheetName);
            if (sheet == null) continue;

            List<ColumnItem> columns = parseColumnSheet(sheet, menu.getTableName());
            result.put(menu.getTableName().toUpperCase(), columns);
        }

        return result;
    }

    /**
     * 解析单个字段Sheet
     */
    private List<ColumnItem> parseColumnSheet(Sheet sheet, String defaultTableName) {
        List<ColumnItem> list = new ArrayList<>();
        int startRow = 1; // 跳过表头

        for (int i = startRow; i <= sheet.getLastRowNum(); i++) {
            Row row = sheet.getRow(i);
            if (row == null) continue;

            String columnName = getCellValue(row.getCell(3)); // 字段英文名
            if (StringUtils.isBlank(columnName)) continue;

            ColumnItem item = new ColumnItem();
            item.setSeq(getCellValue(row.getCell(0)));
            item.setTableName(StringUtils.defaultIfBlank(getCellValue(row.getCell(1)), defaultTableName).toUpperCase());
            item.setTableComment(getCellValue(row.getCell(2)));
            item.setColumnName(columnName.trim().toUpperCase());
            item.setColumnType(getCellValue(row.getCell(4)));
            item.setColumnComment(getCellValue(row.getCell(5)));
            item.setIsNullable(getCellValue(row.getCell(6)));
            item.setIsPk(getCellValue(row.getCell(7)));
            item.setDictCode(getCellValue(row.getCell(8)));
            item.setIsBusPk(getCellValue(row.getCell(9)));
            item.setIsBusRequired(getCellValue(row.getCell(10)));
            item.setChangeDate(getCellValue(row.getCell(11)));
            item.setRemark(getCellValue(row.getCell(12)));

            list.add(item);
        }

        return list;
    }

    /**
     * 解析索引Sheet
     */
    private Map<String, List<IndexItem>> parseIndexSheet(Sheet sheet) {
        Map<String, List<IndexItem>> result = new HashMap<>();
        int startRow = 1;

        for (int i = startRow; i <= sheet.getLastRowNum(); i++) {
            Row row = sheet.getRow(i);
            if (row == null) continue;

            String tableName = getCellValue(row.getCell(0));
            if (StringUtils.isBlank(tableName)) continue;

            IndexItem item = new IndexItem();
            item.setTableName(tableName.trim().toUpperCase());
            item.setTableComment(getCellValue(row.getCell(1)));
            item.setIndexName(getCellValue(row.getCell(2)));
            item.setIndexType(getCellValue(row.getCell(3)));
            item.setIndexColumn(getCellValue(row.getCell(4)));
            item.setRemark(getCellValue(row.getCell(5)));

            result.computeIfAbsent(item.getTableName(), k -> new ArrayList<>()).add(item);
        }

        return result;
    }

    /**
     * 查找Sheet
     */
    private Sheet findSheet(Workbook workbook, String name) {
        for (int i = 0; i < workbook.getNumberOfSheets(); i++) {
            if (workbook.getSheetName(i).equals(name)) {
                return workbook.getSheetAt(i);
            }
        }
        return null;
    }

    /**
     * 根据表中文名查找Sheet名称
     */
    private String findSheetName(Workbook workbook, String tableComment) {
        if (StringUtils.isBlank(tableComment)) return null;

        // 精确匹配
        Sheet exactSheet = workbook.getSheet(tableComment);
        if (exactSheet != null) return tableComment;

        // 模糊匹配
        for (int i = 0; i < workbook.getNumberOfSheets(); i++) {
            String sheetName = workbook.getSheetName(i);
            if (sheetName.contains(tableComment) || tableComment.contains(sheetName)) {
                return sheetName;
            }
        }

        return null;
    }

    /**
     * 获取单元格值
     */
    private String getCellValue(Cell cell) {
        if (cell == null) return "";

        try {
            cell.setCellType(CellType.STRING);
            return StringUtils.trim(cell.getStringCellValue());
        } catch (Exception e) {
            return "";
        }
    }
}
