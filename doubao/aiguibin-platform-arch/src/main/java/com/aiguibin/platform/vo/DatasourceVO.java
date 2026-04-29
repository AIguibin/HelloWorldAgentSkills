package com.aiguibin.platform.vo;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@Schema(description = "数据源信息响应")
public class DatasourceVO {

    @Schema(description = "数据源ID")
    private Long id;

    @Schema(description = "环境：DEV/SIT/UAT")
    private String env;

    @Schema(description = "数据源标识")
    private String dsKey;

    @Schema(description = "数据源名称")
    private String dsName;

    @Schema(description = "数据库名")
    private String dbName;

    @Schema(description = "数据库类型")
    private String dbType;

    @Schema(description = "主机")
    private String host;

    @Schema(description = "端口")
    private Integer port;

    @Schema(description = "用户名")
    private String username;

    @Schema(description = "连接参数")
    private String connectionParams;

    @Schema(description = "是否启用")
    private Integer enabled;

    @Schema(description = "创建时间")
    private LocalDateTime createTime;

    @Schema(description = "更新时间")
    private LocalDateTime updateTime;
}
