package com.aiguibin.platform.service;

import com.aiguibin.platform.dto.excel.TableInfo;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class DbCompareService {

    public String executeCompare(Long datasourceId) {
        log.info("开始执行数据库比对，数据源ID: {}", datasourceId);
        
        String recordNo = "REC" + System.currentTimeMillis();
        
        log.info("数据库比对任务已创建，记录编号: {}", recordNo);
        return recordNo;
    }

    public List<TableInfo> parseExcel(String filePath) {
        log.info("开始解析Excel文件: {}", filePath);
        return new ArrayList<>();
    }

    public List<TableInfo> readDatabaseMetadata(Long datasourceId) {
        log.info("开始读取数据库元数据，数据源ID: {}", datasourceId);
        return new ArrayList<>();
    }
}
