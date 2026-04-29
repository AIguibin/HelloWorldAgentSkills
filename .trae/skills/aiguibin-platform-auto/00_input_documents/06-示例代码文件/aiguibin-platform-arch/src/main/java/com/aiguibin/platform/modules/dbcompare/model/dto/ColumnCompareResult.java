package com.aiguibin.platform.modules.dbcompare.model.dto;

import lombok.Data;

import java.util.List;

/**
 * 字段比对结果
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Data
public class ColumnCompareResult {

    private List<ColumnDiff> docMoreList;
    private List<ColumnDiff> dbMoreList;
    private List<ColumnDiff> typeMismatchList;

    public int getTotalCount() {
        int count = 0;
        if (docMoreList != null) count += docMoreList.size();
        if (dbMoreList != null) count += dbMoreList.size();
        if (typeMismatchList != null) count += typeMismatchList.size();
        return count;
    }
}
