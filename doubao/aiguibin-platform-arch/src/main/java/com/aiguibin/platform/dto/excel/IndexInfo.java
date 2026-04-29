package com.aiguibin.platform.dto.excel;

import lombok.Data;

import java.util.List;

@Data
public class IndexInfo {

    private String indexName;

    private String indexType;

    private List<String> columnNames;

    private Boolean unique;
}
