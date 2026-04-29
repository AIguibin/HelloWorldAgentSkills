package com.aiguibin.platform.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("db_execute_record")
public class DbExecuteRecord {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String recordNo;

    private String env;

    private String dsKey;

    private String dbName;

    private String triggerType;

    private Long triggerBy;

    private LocalDateTime startTime;

    private LocalDateTime endTime;

    private Long durationMs;

    private String status;

    private Integer tableDiffCount;

    private Integer columnDiffCount;

    private Integer indexDiffCount;

    private Integer standardViolationCount;

    private String resultFilePath;

    private String svnRevision;

    private String errorMsg;

    private LocalDateTime createTime;
}
