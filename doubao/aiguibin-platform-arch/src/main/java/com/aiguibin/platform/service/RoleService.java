package com.aiguibin.platform.service;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.StrUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.aiguibin.platform.common.exception.BusinessException;
import com.aiguibin.platform.dto.RoleCreateDTO;
import com.aiguibin.platform.dto.RoleQueryDTO;
import com.aiguibin.platform.dto.RoleUpdateDTO;
import com.aiguibin.platform.entity.SysRole;
import com.aiguibin.platform.mapper.SysRoleMapper;
import com.aiguibin.platform.vo.RoleVO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class RoleService extends ServiceImpl<SysRoleMapper, SysRole> {

    public Page<RoleVO> queryRolePage(RoleQueryDTO queryDTO) {
        Page<SysRole> page = new Page<>(queryDTO.getPageNum(), queryDTO.getPageSize());
        
        LambdaQueryWrapper<SysRole> wrapper = new LambdaQueryWrapper<>();
        if (StrUtil.isNotBlank(queryDTO.getRoleName())) {
            wrapper.like(SysRole::getRoleName, queryDTO.getRoleName());
        }
        if (StrUtil.isNotBlank(queryDTO.getRoleCode())) {
            wrapper.like(SysRole::getRoleCode, queryDTO.getRoleCode());
        }
        if (queryDTO.getStatus() != null) {
            wrapper.eq(SysRole::getStatus, queryDTO.getStatus());
        }
        wrapper.orderByDesc(SysRole::getCreateTime);
        
        Page<SysRole> rolePage = this.page(page, wrapper);
        
        Page<RoleVO> resultPage = new Page<>(rolePage.getCurrent(), rolePage.getSize(), rolePage.getTotal());
        List<RoleVO> roleVOList = rolePage.getRecords().stream()
                .map(this::convertToRoleVO)
                .collect(Collectors.toList());
        resultPage.setRecords(roleVOList);
        
        return resultPage;
    }

    public List<RoleVO> getAllRoles() {
        LambdaQueryWrapper<SysRole> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(SysRole::getStatus, 1);
        wrapper.orderByAsc(SysRole::getId);
        List<SysRole> roleList = this.list(wrapper);
        return roleList.stream()
                .map(this::convertToRoleVO)
                .collect(Collectors.toList());
    }

    public RoleVO getRoleDetail(Long roleId) {
        SysRole role = this.getById(roleId);
        if (role == null) {
            throw new BusinessException("角色不存在");
        }
        return convertToRoleVO(role);
    }

    @Transactional(rollbackFor = Exception.class)
    public void createRole(RoleCreateDTO createDTO) {
        LambdaQueryWrapper<SysRole> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(SysRole::getRoleCode, createDTO.getRoleCode());
        if (this.count(wrapper) > 0) {
            throw new BusinessException("角色编码已存在");
        }
        
        SysRole role = new SysRole();
        BeanUtil.copyProperties(createDTO, role);
        role.setStatus(1);
        this.save(role);
    }

    @Transactional(rollbackFor = Exception.class)
    public void updateRole(RoleUpdateDTO updateDTO) {
        SysRole role = this.getById(updateDTO.getId());
        if (role == null) {
            throw new BusinessException("角色不存在");
        }
        
        BeanUtil.copyProperties(updateDTO, role);
        this.updateById(role);
    }

    @Transactional(rollbackFor = Exception.class)
    public void deleteRole(Long roleId) {
        SysRole role = this.getById(roleId);
        if (role == null) {
            throw new BusinessException("角色不存在");
        }
        this.removeById(roleId);
    }

    private RoleVO convertToRoleVO(SysRole role) {
        RoleVO roleVO = new RoleVO();
        BeanUtil.copyProperties(role, roleVO);
        return roleVO;
    }
}
