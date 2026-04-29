package com.aiguibin.platform.modules.dbcompare.service;

import com.aiguibin.platform.modules.dbcompare.model.dto.ColumnInfo;
import com.aiguibin.platform.modules.dbcompare.model.dto.IndexInfo;
import com.aiguibin.platform.modules.dbcompare.model.dto.TableInfo;
import com.aiguibin.platform.modules.dbcompare.mapper.DbMetaMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 数据库元数据服务
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class DbMetaService {

    private final DbMetaMapper dbMetaMapper;

    /**
     * 获取数据库中的所有表
     */
    public List<TableInfo> getTables(String schema) {
        return dbMetaMapper.selectTables(schema);
    }

    /**
     * 获取表的所有字段
     */
    public List<ColumnInfo> getColumns(String schema, String tableName) {
        return dbMetaMapper.selectColumns(schema, tableName);
    }

    /**
     * 获取表的所有索引
     */
    public List<IndexInfo> getIndexes(String schema, String tableName) {
        return dbMetaMapper.selectIndexes(schema, tableName);
    }
}
