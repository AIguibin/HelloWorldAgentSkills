package com.aiguibin.platform.modules.dbcompare.service.impl;

import com.aiguibin.platform.modules.dbcompare.entity.DbDatasourceConfig;
import com.aiguibin.platform.modules.dbcompare.mapper.DbDatasourceConfigMapper;
import com.aiguibin.platform.modules.dbcompare.service.DbDatasourceConfigService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class DbDatasourceConfigServiceImpl extends ServiceImpl<DbDatasourceConfigMapper, DbDatasourceConfig> implements DbDatasourceConfigService {
    
    @Autowired
    private DbDatasourceConfigMapper datasourceConfigMapper;
    
    @Override
    public List<DbDatasourceConfig> getByEnv(String env) {
        return datasourceConfigMapper.selectByEnv(env);
    }
}
