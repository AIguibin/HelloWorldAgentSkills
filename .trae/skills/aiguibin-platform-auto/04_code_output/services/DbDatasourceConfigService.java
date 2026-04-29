package com.aiguibin.platform.modules.dbcompare.service;

import com.aiguibin.platform.modules.dbcompare.entity.DbDatasourceConfig;
import com.baomidou.mybatisplus.extension.service.IService;
import java.util.List;

public interface DbDatasourceConfigService extends IService<DbDatasourceConfig> {
    
    List<DbDatasourceConfig> getByEnv(String env);
}
