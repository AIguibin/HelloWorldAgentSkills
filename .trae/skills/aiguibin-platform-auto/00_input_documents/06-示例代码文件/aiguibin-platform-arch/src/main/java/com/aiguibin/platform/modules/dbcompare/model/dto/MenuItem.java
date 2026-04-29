package com.aiguibin.platform.modules.dbcompare.model.dto;

import lombok.Data;

/**
 * 目录项
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Data
public class MenuItem {

    private String seq;
    private String databaseName;
    private String module;
    private String owner;
    private String tableName;
    private String tableComment;
    private String isShard;
    private String shardKey;
    private String isInit;
    private String initCount;
    private String isMigrate;
    private String isSync;
    private String isStandard;
    private String isClean;
    private String cleanPolicy;
    private String archivePolicy;
    private String remark;

    // 新增字段
    private String isPartition;
    private String partitionKey;
    private String oldDataCount;
    private String futureDataEstimate;
}
