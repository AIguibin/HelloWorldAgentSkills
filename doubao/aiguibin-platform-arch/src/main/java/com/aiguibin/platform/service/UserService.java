package com.aiguibin.platform.service;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.StrUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.aiguibin.platform.common.exception.BusinessException;
import com.aiguibin.platform.dto.UserCreateDTO;
import com.aiguibin.platform.dto.UserQueryDTO;
import com.aiguibin.platform.dto.UserUpdateDTO;
import com.aiguibin.platform.entity.SysUser;
import com.aiguibin.platform.mapper.SysUserMapper;
import com.aiguibin.platform.vo.UserVO;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class UserService extends ServiceImpl<SysUserMapper, SysUser> {

    private final PasswordEncoder passwordEncoder;

    public Page<UserVO> queryUserPage(UserQueryDTO queryDTO) {
        Page<SysUser> page = new Page<>(queryDTO.getPageNum(), queryDTO.getPageSize());
        
        LambdaQueryWrapper<SysUser> wrapper = new LambdaQueryWrapper<>();
        if (StrUtil.isNotBlank(queryDTO.getUsername())) {
            wrapper.like(SysUser::getUsername, queryDTO.getUsername());
        }
        if (StrUtil.isNotBlank(queryDTO.getRealName())) {
            wrapper.like(SysUser::getRealName, queryDTO.getRealName());
        }
        if (StrUtil.isNotBlank(queryDTO.getOrgCode())) {
            wrapper.eq(SysUser::getOrgCode, queryDTO.getOrgCode());
        }
        if (queryDTO.getStatus() != null) {
            wrapper.eq(SysUser::getStatus, queryDTO.getStatus());
        }
        wrapper.orderByDesc(SysUser::getCreateTime);
        
        Page<SysUser> userPage = this.page(page, wrapper);
        
        Page<UserVO> resultPage = new Page<>(userPage.getCurrent(), userPage.getSize(), userPage.getTotal());
        List<UserVO> userVOList = userPage.getRecords().stream()
                .map(this::convertToUserVO)
                .collect(Collectors.toList());
        resultPage.setRecords(userVOList);
        
        return resultPage;
    }

    public UserVO getUserDetail(Long userId) {
        SysUser user = this.getById(userId);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        return convertToUserVO(user);
    }

    @Transactional(rollbackFor = Exception.class)
    public void createUser(UserCreateDTO createDTO) {
        LambdaQueryWrapper<SysUser> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(SysUser::getUsername, createDTO.getUsername());
        if (this.count(wrapper) > 0) {
            throw new BusinessException("用户名已存在");
        }
        
        wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(SysUser::getUserNo, createDTO.getUserNo());
        if (this.count(wrapper) > 0) {
            throw new BusinessException("用户编号已存在");
        }
        
        SysUser user = new SysUser();
        BeanUtil.copyProperties(createDTO, user);
        user.setPassword(passwordEncoder.encode(createDTO.getPassword()));
        user.setIsLocked(0);
        user.setStatus(1);
        this.save(user);
    }

    @Transactional(rollbackFor = Exception.class)
    public void updateUser(UserUpdateDTO updateDTO) {
        SysUser user = this.getById(updateDTO.getId());
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        
        if (StrUtil.isNotBlank(updateDTO.getUserNo()) && !updateDTO.getUserNo().equals(user.getUserNo())) {
            LambdaQueryWrapper<SysUser> wrapper = new LambdaQueryWrapper<>();
            wrapper.eq(SysUser::getUserNo, updateDTO.getUserNo())
                    .ne(SysUser::getId, updateDTO.getId());
            if (this.count(wrapper) > 0) {
                throw new BusinessException("用户编号已存在");
            }
        }
        
        BeanUtil.copyProperties(updateDTO, user, "password");
        this.updateById(user);
    }

    @Transactional(rollbackFor = Exception.class)
    public void deleteUser(Long userId) {
        SysUser user = this.getById(userId);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        this.removeById(userId);
    }

    @Transactional(rollbackFor = Exception.class)
    public void resetPassword(Long userId, String newPassword) {
        SysUser user = this.getById(userId);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        user.setPassword(passwordEncoder.encode(newPassword));
        this.updateById(user);
    }

    @Transactional(rollbackFor = Exception.class)
    public void toggleLock(Long userId, Integer isLocked, String lockReason) {
        SysUser user = this.getById(userId);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        user.setIsLocked(isLocked);
        user.setLockReason(lockReason);
        this.updateById(user);
    }

    private UserVO convertToUserVO(SysUser user) {
        UserVO userVO = new UserVO();
        BeanUtil.copyProperties(user, userVO);
        return userVO;
    }
}
