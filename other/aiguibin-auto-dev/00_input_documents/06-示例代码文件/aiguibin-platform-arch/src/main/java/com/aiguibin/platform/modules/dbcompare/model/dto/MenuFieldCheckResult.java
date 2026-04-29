package com.aiguibin.platform.modules.dbcompare.model.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

/**
 * 目录字段检查结果
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Data
@AllArgsConstructor
public class MenuFieldCheckResult {

    private String tableName;
    private String tableComment;
    private String fieldName;
    private String fieldDescription;
    private boolean required;
    private String suggestValue;
}
