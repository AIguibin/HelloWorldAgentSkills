package com.aiguibin.platform.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "数据源更新请求")
public class DatasourceUpdateDTO {

    @Schema(description = "数据源ID", required = true)
    private Long id;

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

    @Schema(description = "密码")
    private String password;

    @Schema(description = "连接参数")
    private String connectionParams;

    @Schema(description = "是否启用")
    private Integer enabled;
}
