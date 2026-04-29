package com.aiguibin.platform.modules.dbcompare.mapper;

import com.aiguibin.platform.modules.dbcompare.entity.DbDatasourceConfig;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

@Mapper
public interface DbDatasourceConfigMapper extends BaseMapper<DbDatasourceConfig> {
    
    List<DbDatasourceConfig> selectByEnv(@Param("env") String env);
}
