package com.aiguibin.platform.core.org.mapper;

import com.aiguibin.platform.core.org.entity.SysOrg;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface SysOrgMapper extends BaseMapper<SysOrg> {
    
    SysOrg selectByOrgCode(@Param("orgCode") String orgCode);
}
