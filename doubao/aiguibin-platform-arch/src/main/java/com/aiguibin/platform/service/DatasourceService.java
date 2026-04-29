package com.aiguibin.platform.service;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.StrUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.aiguibin.platform.common.exception.BusinessException;
import com.aiguibin.platform.dto.DatasourceCreateDTO;
import com.aiguibin.platform.dto.DatasourceQueryDTO;
import com.aiguibin.platform.dto.DatasourceUpdateDTO;
import com.aiguibin.platform.entity.DbDatasourceConfig;
import com.aiguibin.platform.mapper.DbDatasourceConfigMapper;
import com.aiguibin.platform.vo.DatasourceVO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class DatasourceService extends ServiceImpl<DbDatasourceConfigMapper, DbDatasourceConfig> {

    public Page<DatasourceVO> queryDatasourcePage(DatasourceQueryDTO queryDTO) {
        Page<DbDatasourceConfig> page = new Page<>(queryDTO.getPageNum(), queryDTO.getPageSize());
        
        LambdaQueryWrapper<DbDatasourceConfig> wrapper = new LambdaQueryWrapper<>();
        if (StrUtil.isNotBlank(queryDTO.getEnv())) {
            wrapper.eq(DbDatasourceConfig::getEnv, queryDTO.getEnv());
        }
        if (StrUtil.isNotBlank(queryDTO.getDsName())) {
            wrapper.like(DbDatasourceConfig::getDsName, queryDTO.getDsName());
        }
        if (queryDTO.getEnabled() != null) {
            wrapper.eq(DbDatasourceConfig::getEnabled, queryDTO.getEnabled());
        }
        wrapper.orderByDesc(DbDatasourceConfig::getCreateTime);
        
        Page<DbDatasourceConfig> dsPage = this.page(page, wrapper);
        
        Page<DatasourceVO> resultPage = new Page<>(dsPage.getCurrent(), dsPage.getSize(), dsPage.getTotal());
        List<DatasourceVO> dsVOList = dsPage.getRecords().stream()
                .map(this::convertToVO)
                .collect(Collectors.toList());
        resultPage.setRecords(dsVOList);
        
        return resultPage;
    }

    public List<DatasourceVO> getAllEnabledDatasources() {
        LambdaQueryWrapper<DbDatasourceConfig> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(DbDatasourceConfig::getEnabled, 1);
        wrapper.orderByAsc(DbDatasourceConfig::getId);
        List<DbDatasourceConfig> dsList = this.list(wrapper);
        return dsList.stream()
                .map(this::convertToVO)
                .collect(Collectors.toList());
    }

    public DatasourceVO getDatasourceDetail(Long dsId) {
        DbDatasourceConfig ds = this.getById(dsId);
        if (ds == null) {
            throw new BusinessException("数据源不存在");
        }
        return convertToVO(ds);
    }

    @Transactional(rollbackFor = Exception.class)
    public void createDatasource(DatasourceCreateDTO createDTO) {
        LambdaQueryWrapper<DbDatasourceConfig> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(DbDatasourceConfig::getDsKey, createDTO.getDsKey());
        if (this.count(wrapper) > 0) {
            throw new BusinessException("数据源标识已存在");
        }
        
        DbDatasourceConfig ds = new DbDatasourceConfig();
        BeanUtil.copyProperties(createDTO, ds);
        ds.setEnabled(1);
        ds.setCreateTime(LocalDateTime.now());
        ds.setUpdateTime(LocalDateTime.now());
        this.save(ds);
    }

    @Transactional(rollbackFor = Exception.class)
    public void updateDatasource(DatasourceUpdateDTO updateDTO) {
        DbDatasourceConfig ds = this.getById(updateDTO.getId());
        if (ds == null) {
            throw new BusinessException("数据源不存在");
        }
        
        BeanUtil.copyProperties(updateDTO, ds);
        ds.setUpdateTime(LocalDateTime.now());
        this.updateById(ds);
    }

    @Transactional(rollbackFor = Exception.class)
    public void deleteDatasource(Long dsId) {
        DbDatasourceConfig ds = this.getById(dsId);
        if (ds == null) {
            throw new BusinessException("数据源不存在");
        }
        this.removeById(dsId);
    }

    public boolean testConnection(Long dsId) {
        DbDatasourceConfig ds = this.getById(dsId);
        if (ds == null) {
            throw new BusinessException("数据源不存在");
        }
        return testConnectionInternal(ds);
    }

    public boolean testConnectionByConfig(DatasourceCreateDTO config) {
        DbDatasourceConfig ds = new DbDatasourceConfig();
        BeanUtil.copyProperties(config, ds);
        return testConnectionInternal(ds);
    }

    private boolean testConnectionInternal(DbDatasourceConfig ds) {
        String jdbcUrl = buildJdbcUrl(ds);
        Connection conn = null;
        try {
            Class.forName(getDriverClassName(ds.getDbType()));
            conn = DriverManager.getConnection(jdbcUrl, ds.getUsername(), ds.getPassword());
            return conn.isValid(5);
        } catch (Exception e) {
            throw new BusinessException("数据库连接失败：" + e.getMessage());
        } finally {
            if (conn != null) {
                try {
                    conn.close();
                } catch (SQLException e) {
                    // ignore
                }
            }
        }
    }

    private String buildJdbcUrl(DbDatasourceConfig ds) {
        StringBuilder url = new StringBuilder();
        if ("mysql".equalsIgnoreCase(ds.getDbType())) {
            url.append("jdbc:mysql://")
               .append(ds.getHost())
               .append(":")
               .append(ds.getPort())
               .append("/")
               .append(ds.getDbName())
               .append("?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=Asia/Shanghai");
            if (StrUtil.isNotBlank(ds.getConnectionParams())) {
                url.append("&").append(ds.getConnectionParams());
            }
        } else if ("oracle".equalsIgnoreCase(ds.getDbType())) {
            url.append("jdbc:oracle:thin:@")
               .append(ds.getHost())
               .append(":")
               .append(ds.getPort())
               .append(":")
               .append(ds.getDbName());
        } else {
            throw new BusinessException("不支持的数据库类型：" + ds.getDbType());
        }
        return url.toString();
    }

    private String getDriverClassName(String dbType) {
        if ("mysql".equalsIgnoreCase(dbType)) {
            return "com.mysql.cj.jdbc.Driver";
        } else if ("oracle".equalsIgnoreCase(dbType)) {
            return "oracle.jdbc.OracleDriver";
        }
        throw new BusinessException("不支持的数据库类型：" + dbType);
    }

    private DatasourceVO convertToVO(DbDatasourceConfig ds) {
        DatasourceVO vo = new DatasourceVO();
        BeanUtil.copyProperties(ds, vo);
        return vo;
    }
}
