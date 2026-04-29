package com.aiguibin.platform.modules.dbcompare.service;

import com.aiguibin.platform.modules.dbcompare.model.dto.*;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;

/**
 * SQL生成服务
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Service
public class SqlGenService {

    /**
     * 生成创建表SQL
     */
    public String genCreateTable(DocData docData, String tableName) {
        StringBuilder sql = new StringBuilder();
        sql.append("-- 请根据文档创建表: ").append(tableName).append("\n");
        sql.append("-- 参考文档中的字段定义\n");
        sql.append("CREATE TABLE ").append(tableName).append(" (\n");
        sql.append("  -- 请补充字段定义\n");
        sql.append(");");
        return sql.toString();
    }

    /**
     * 生成添加字段SQL
     */
    public String genAddColumn(String tableName, ColumnItem column) {
        StringBuilder sql = new StringBuilder();
        sql.append("ALTER TABLE ").append(tableName)
                .append(" ADD COLUMN ").append(column.getColumnName())
                .append(" ").append(column.getColumnType());

        if ("NO".equalsIgnoreCase(column.getIsNullable())) {
            sql.append(" NOT NULL");
        }

        if (StringUtils.isNotBlank(column.getColumnComment())) {
            sql.append(" COMMENT '").append(column.getColumnComment()).append("'");
        }

        sql.append(";");
        return sql.toString();
    }

    /**
     * 生成修改字段SQL
     */
    public String genModifyColumn(String tableName, ColumnItem column) {
        StringBuilder sql = new StringBuilder();
        sql.append("ALTER TABLE ").append(tableName)
                .append(" MODIFY COLUMN ").append(column.getColumnName())
                .append(" ").append(column.getColumnType());

        if ("NO".equalsIgnoreCase(column.getIsNullable())) {
            sql.append(" NOT NULL");
        }

        if (StringUtils.isNotBlank(column.getColumnComment())) {
            sql.append(" COMMENT '").append(column.getColumnComment()).append("'");
        }

        sql.append(";");
        return sql.toString();
    }

    /**
     * 生成创建索引SQL
     */
    public String genCreateIndex(String tableName, IndexItem index) {
        StringBuilder sql = new StringBuilder();

        if ("UNIQUE".equalsIgnoreCase(index.getIndexType())) {
            sql.append("CREATE UNIQUE INDEX ");
        } else {
            sql.append("CREATE INDEX ");
        }

        sql.append(index.getIndexName())
                .append(" ON ").append(tableName)
                .append("(").append(index.getIndexColumn()).append(");");

        return sql.toString();
    }

    /**
     * 生成重建索引SQL
     */
    public String genRecreateIndex(String tableName, IndexItem index) {
        StringBuilder sql = new StringBuilder();
        sql.append("-- 先删除旧索引\n");
        sql.append("DROP INDEX ").append(index.getIndexName()).append(" ON ").append(tableName).append(";\n");
        sql.append("-- 再创建新索引\n");
        sql.append(genCreateIndex(tableName, index));
        return sql.toString();
    }
}
