package com.aiguibin.platform.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("sys_oper_log")
public class SysOperLog {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String operType;

    private String title;

    private String method;

    private String requestUrl;

    private String requestMethod;

    private String requestParams;

    private String responseData;

    private Long userId;

    private String username;

    private String orgCode;

    private String operIp;

    private String operLocation;

    private Integer status;

    private String errorMsg;

    private LocalDateTime operTime;

    private Long costTime;
}
