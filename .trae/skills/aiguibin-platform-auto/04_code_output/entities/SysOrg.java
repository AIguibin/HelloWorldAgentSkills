package com.aiguibin.platform.core.org.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("sys_org")
public class SysOrg {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private String orgCode;
    
    private String orgName;
    
    private String orgType;
    
    private String parentCode;
    
    private String parentCodes;
    
    private Integer level;
    
    private Integer sortOrder;
    
    private Integer status;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
    
    @TableField(fill = FieldFill.INSERT)
    private Long createBy;
    
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private Long updateBy;
    
    @TableLogic
    private Integer deleted;
}
