package com.aiguibin.platform.service;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.StrUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.aiguibin.platform.dto.OperLogQueryDTO;
import com.aiguibin.platform.entity.SysOperLog;
import com.aiguibin.platform.mapper.SysOperLogMapper;
import com.aiguibin.platform.vo.OperLogVO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class OperLogService extends ServiceImpl<SysOperLogMapper, SysOperLog> {

    private static final DateTimeFormatter FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    public Page<OperLogVO> queryOperLogPage(OperLogQueryDTO queryDTO) {
        Page<SysOperLog> page = new Page<>(queryDTO.getPageNum(), queryDTO.getPageSize());
        
        LambdaQueryWrapper<SysOperLog> wrapper = new LambdaQueryWrapper<>();
        if (StrUtil.isNotBlank(queryDTO.getOperType())) {
            wrapper.eq(SysOperLog::getOperType, queryDTO.getOperType());
        }
        if (StrUtil.isNotBlank(queryDTO.getTitle())) {
            wrapper.like(SysOperLog::getTitle, queryDTO.getTitle());
        }
        if (StrUtil.isNotBlank(queryDTO.getUsername())) {
            wrapper.like(SysOperLog::getUsername, queryDTO.getUsername());
        }
        if (queryDTO.getStatus() != null) {
            wrapper.eq(SysOperLog::getStatus, queryDTO.getStatus());
        }
        if (StrUtil.isNotBlank(queryDTO.getStartTime())) {
            wrapper.ge(SysOperLog::getOperTime, LocalDateTime.parse(queryDTO.getStartTime(), FORMATTER));
        }
        if (StrUtil.isNotBlank(queryDTO.getEndTime())) {
            wrapper.le(SysOperLog::getOperTime, LocalDateTime.parse(queryDTO.getEndTime(), FORMATTER));
        }
        wrapper.orderByDesc(SysOperLog::getOperTime);
        
        Page<SysOperLog> logPage = this.page(page, wrapper);
        
        Page<OperLogVO> resultPage = new Page<>(logPage.getCurrent(), logPage.getSize(), logPage.getTotal());
        List<OperLogVO> logVOList = logPage.getRecords().stream()
                .map(this::convertToOperLogVO)
                .collect(Collectors.toList());
        resultPage.setRecords(logVOList);
        
        return resultPage;
    }

    public OperLogVO getOperLogDetail(Long logId) {
        SysOperLog log = this.getById(logId);
        if (log == null) {
            return null;
        }
        return convertToOperLogVO(log);
    }

    @org.springframework.transaction.annotation.Transactional(rollbackFor = Exception.class)
    public void saveOperLog(SysOperLog operLog) {
        if (operLog.getOperTime() == null) {
            operLog.setOperTime(LocalDateTime.now());
        }
        this.save(operLog);
    }

    @org.springframework.transaction.annotation.Transactional(rollbackFor = Exception.class)
    public void deleteOperLog(Long logId) {
        this.removeById(logId);
    }

    @org.springframework.transaction.annotation.Transactional(rollbackFor = Exception.class)
    public void clearOperLog() {
        this.remove(new LambdaQueryWrapper<>());
    }

    private OperLogVO convertToOperLogVO(SysOperLog log) {
        OperLogVO logVO = new OperLogVO();
        BeanUtil.copyProperties(log, logVO);
        return logVO;
    }
}
