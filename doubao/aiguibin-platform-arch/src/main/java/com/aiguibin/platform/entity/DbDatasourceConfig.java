package com.aiguibin.platform.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("db_datasource_config")
public class DbDatasourceConfig {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String env;

    private String dsKey;

    private String dsName;

    private String dbName;

    private String dbType;

    private String host;

    private Integer port;

    private String username;

    private String password;

    private String connectionParams;

    private Integer enabled;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;
}
