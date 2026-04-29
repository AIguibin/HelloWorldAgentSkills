package com.aiguibin.platform.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
@Schema(description = "数据源创建请求")
public class DatasourceCreateDTO {

    @Schema(description = "环境：DEV/SIT/UAT", required = true)
    @NotBlank(message = "环境不能为空")
    private String env;

    @Schema(description = "数据源标识", required = true)
    @NotBlank(message = "数据源标识不能为空")
    private String dsKey;

    @Schema(description = "数据源名称", required = true)
    @NotBlank(message = "数据源名称不能为空")
    private String dsName;

    @Schema(description = "数据库名", required = true)
    @NotBlank(message = "数据库名不能为空")
    private String dbName;

    @Schema(description = "数据库类型：mysql/oracle", defaultValue = "mysql")
    private String dbType = "mysql";

    @Schema(description = "主机", required = true)
    @NotBlank(message = "主机不能为空")
    private String host;

    @Schema(description = "端口", defaultValue = "3306")
    private Integer port = 3306;

    @Schema(description = "用户名", required = true)
    @NotBlank(message = "用户名不能为空")
    private String username;

    @Schema(description = "密码", required = true)
    @NotBlank(message = "密码不能为空")
    private String password;

    @Schema(description = "连接参数")
    private String connectionParams;
}
