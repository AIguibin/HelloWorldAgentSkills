package com.aiguibin.platform.service;

import cn.hutool.core.util.IdUtil;
import com.aiguibin.platform.common.constant.Constants;
import com.aiguibin.platform.common.exception.BusinessException;
import com.aiguibin.platform.common.util.JwtUtil;
import com.aiguibin.platform.dto.LoginStep1DTO;
import com.aiguibin.platform.dto.LoginStep2DTO;
import com.aiguibin.platform.entity.SysOrg;
import com.aiguibin.platform.entity.SysUser;
import com.aiguibin.platform.mapper.SysMenuMapper;
import com.aiguibin.platform.mapper.SysOrgMapper;
import com.aiguibin.platform.mapper.SysRoleMapper;
import com.aiguibin.platform.mapper.SysUserMapper;
import com.aiguibin.platform.vo.*;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class AuthService {
    
    private final SysUserMapper sysUserMapper;
    private final SysOrgMapper sysOrgMapper;
    private final SysRoleMapper sysRoleMapper;
    private final SysMenuMapper sysMenuMapper;
    private final JwtUtil jwtUtil;
    
    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();
    
    private final Map<String, LoginStep1Cache> tempTokenCache = new ConcurrentHashMap<>();
    
    @lombok.Data
    @lombok.AllArgsConstructor
    private static class LoginStep1Cache {
        private Long userId;
        private String username;
        private String realName;
        private List<OrgVO> orgList;
        private long expireTime;
    }
    
    public LoginStep1VO loginStep1(LoginStep1DTO dto) {
        SysUser user = sysUserMapper.selectByUsername(dto.getUsername());
        if (user == null) {
            throw new BusinessException("用户名或密码错误");
        }
        
        if (user.getStatus() == Constants.STATUS_DISABLE) {
            throw new BusinessException("账号已被禁用");
        }
        
        if (user.getIsLocked() == Constants.YES) {
            throw new BusinessException("账号已被锁定：" + user.getLockReason());
        }
        
        if (!passwordEncoder.matches(dto.getPassword(), user.getPassword())) {
            throw new BusinessException("用户名或密码错误");
        }
        
        List<String> orgCodes = sysUserMapper.selectOrgCodesByUserId(user.getId());
        if (orgCodes == null || orgCodes.isEmpty()) {
            throw new BusinessException("用户未关联任何机构");
        }
        
        List<SysOrg> orgList = sysOrgMapper.selectList(
                new LambdaQueryWrapper<SysOrg>()
                        .in(SysOrg::getOrgCode, orgCodes)
                        .eq(SysOrg::getStatus, Constants.STATUS_ENABLE)
        );
        
        List<OrgVO> orgVOList = orgList.stream()
                .map(org -> OrgVO.builder()
                        .orgCode(org.getOrgCode())
                        .orgName(org.getOrgName())
                        .orgType(org.getOrgType())
                        .build())
                .collect(Collectors.toList());
        
        String tempToken = IdUtil.simpleUUID();
        long expireTime = System.currentTimeMillis() + 5 * 60 * 1000;
        tempTokenCache.put(tempToken, new LoginStep1Cache(user.getId(), user.getUsername(), user.getRealName(), orgVOList, expireTime));
        
        return LoginStep1VO.builder()
                .tempToken(tempToken)
                .realName(user.getRealName())
                .orgList(orgVOList)
                .build();
    }
    
    public LoginStep2VO loginStep2(LoginStep2DTO dto) {
        LoginStep1Cache cache = tempTokenCache.get(dto.getTempToken());
        if (cache == null) {
            throw new BusinessException("临时Token无效或已过期");
        }
        
        if (System.currentTimeMillis() > cache.getExpireTime()) {
            tempTokenCache.remove(dto.getTempToken());
            throw new BusinessException("临时Token已过期，请重新登录");
        }
        
        boolean orgValid = cache.getOrgList().stream()
                .anyMatch(org -> org.getOrgCode().equals(dto.getOrgCode()));
        if (!orgValid) {
            throw new BusinessException("无效的机构选择");
        }
        
        tempTokenCache.remove(dto.getTempToken());
        
        String accessToken = jwtUtil.generateToken(cache.getUserId(), cache.getUsername(), dto.getOrgCode());
        String refreshToken = jwtUtil.generateRefreshToken(cache.getUserId(), cache.getUsername());
        
        SysOrg selectedOrg = sysOrgMapper.selectOne(
                new LambdaQueryWrapper<SysOrg>()
                        .eq(SysOrg::getOrgCode, dto.getOrgCode())
        );
        
        SysUser user = sysUserMapper.selectById(cache.getUserId());
        
        List<String> roles = sysRoleMapper.selectRolesByUserId(cache.getUserId())
                .stream()
                .map(role -> role.getRoleCode())
                .collect(Collectors.toList());
        
        List<String> permissions = sysMenuMapper.selectPermissionsByUserId(cache.getUserId());
        
        UserInfoVO userInfo = UserInfoVO.builder()
                .userId(user.getId())
                .username(user.getUsername())
                .realName(user.getRealName())
                .avatar(user.getAvatar())
                .orgCode(dto.getOrgCode())
                .orgName(selectedOrg != null ? selectedOrg.getOrgName() : "")
                .deptCode(user.getDeptCode())
                .roles(roles)
                .permissions(permissions)
                .build();
        
        return LoginStep2VO.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .tokenType("Bearer")
                .expiresIn(1800L)
                .userInfo(userInfo)
                .build();
    }
    
    public void logout(String token) {
        log.info("用户登出");
    }
}
