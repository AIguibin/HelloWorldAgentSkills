package com.aiguibin.platform.modules.dbcompare.mapper;

import com.aiguibin.platform.modules.dbcompare.model.dto.ColumnInfo;
import com.aiguibin.platform.modules.dbcompare.model.dto.IndexInfo;
import com.aiguibin.platform.modules.dbcompare.model.dto.TableInfo;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 数据库元数据Mapper
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Mapper
public interface DbMetaMapper {

    /**
     * 查询数据库中的所有表
     */
    @Select("SELECT " +
            "  TABLE_NAME as tableName, " +
            "  TABLE_COMMENT as tableComment, " +
            "  TABLE_SCHEMA as tableSchema " +
            "FROM INFORMATION_SCHEMA.TABLES " +
            "WHERE TABLE_SCHEMA = #{schema} " +
            "AND TABLE_TYPE = 'BASE TABLE' " +
            "ORDER BY TABLE_NAME")
    List<TableInfo> selectTables(@Param("schema") String schema);

    /**
     * 查询表的所有字段
     */
    @Select("SELECT " +
            "  COLUMN_NAME as columnName, " +
            "  COLUMN_COMMENT as columnComment, " +
            "  COLUMN_TYPE as columnType, " +
            "  DATA_TYPE as dataType, " +
            "  IS_NULLABLE as isNullable, " +
            "  COLUMN_DEFAULT as columnDefault, " +
            "  COLUMN_KEY as columnKey, " +
            "  EXTRA as extra " +
            "FROM INFORMATION_SCHEMA.COLUMNS " +
            "WHERE TABLE_SCHEMA = #{schema} " +
            "AND TABLE_NAME = #{tableName} " +
            "ORDER BY ORDINAL_POSITION")
    List<ColumnInfo> selectColumns(@Param("schema") String schema, @Param("tableName") String tableName);

    /**
     * 查询表的所有索引
     */
    @Select("SELECT " +
            "  INDEX_NAME as indexName, " +
            "  INDEX_TYPE as indexType, " +
            "  NON_UNIQUE as nonUnique, " +
            "  GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) as indexColumn " +
            "FROM INFORMATION_SCHEMA.STATISTICS " +
            "WHERE TABLE_SCHEMA = #{schema} " +
            "AND TABLE_NAME = #{tableName} " +
            "GROUP BY INDEX_NAME, INDEX_TYPE, NON_UNIQUE " +
            "ORDER BY INDEX_NAME")
    List<IndexInfo> selectIndexes(@Param("schema") String schema, @Param("tableName") String tableName);
}
