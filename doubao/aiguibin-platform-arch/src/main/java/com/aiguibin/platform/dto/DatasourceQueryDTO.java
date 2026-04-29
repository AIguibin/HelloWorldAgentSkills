package com.aiguibin.platform.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "数据源查询请求")
public class DatasourceQueryDTO {

    @Schema(description = "页码", defaultValue = "1")
    private Integer pageNum = 1;

    @Schema(description = "每页条数", defaultValue = "10")
    private Integer pageSize = 10;

    @Schema(description = "环境：DEV/SIT/UAT")
    private String env;

    @Schema(description = "数据源名称")
    private String dsName;

    @Schema(description = "是否启用")
    private Integer enabled;
}
