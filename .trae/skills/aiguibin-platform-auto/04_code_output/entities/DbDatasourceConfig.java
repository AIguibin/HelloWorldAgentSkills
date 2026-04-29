package com.aiguibin.platform.modules.dbcompare.entity;

import com.baomidou.mybatisplus.annotation.*;
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
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
}
