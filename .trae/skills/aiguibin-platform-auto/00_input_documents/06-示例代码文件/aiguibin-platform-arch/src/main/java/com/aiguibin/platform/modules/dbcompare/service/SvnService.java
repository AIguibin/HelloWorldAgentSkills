package com.aiguibin.platform.modules.dbcompare.service;

import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.tmatesoft.svn.core.SVNCommitInfo;
import org.tmatesoft.svn.core.SVNDepth;
import org.tmatesoft.svn.core.SVNException;
import org.tmatesoft.svn.core.SVNURL;
import org.tmatesoft.svn.core.auth.ISVNAuthenticationManager;
import org.tmatesoft.svn.core.internal.io.dav.DAVRepositoryFactory;
import org.tmatesoft.svn.core.internal.io.fs.FSRepositoryFactory;
import org.tmatesoft.svn.core.internal.io.svn.SVNRepositoryFactoryImpl;
import org.tmatesoft.svn.core.io.SVNRepository;
import org.tmatesoft.svn.core.io.SVNRepositoryFactory;
import org.tmatesoft.svn.core.wc.*;

import javax.annotation.PostConstruct;
import java.io.File;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * SVN服务
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Slf4j
@Service
public class SvnService {

    @Value("${svn.url}")
    private String svnUrl;

    @Value("${svn.username}")
    private String username;

    @Value("${svn.password}")
    private String password;

    @Value("${svn.work-copy-path}")
    private String workCopyPath;

    private SVNClientManager clientManager;

    @PostConstruct
    public void init() {
        DAVRepositoryFactory.setup();
        SVNRepositoryFactoryImpl.setup();
        FSRepositoryFactory.setup();

        ISVNAuthenticationManager authManager = SVNWCUtil.createDefaultAuthenticationManager(username, password.toCharArray());
        clientManager = SVNClientManager.newInstance(null, authManager);

        // 确保工作副本存在
        ensureWorkCopyExists();
    }

    /**
     * 确保工作副本存在
     */
    private void ensureWorkCopyExists() {
        try {
            File wcDir = new File(workCopyPath);
            if (!wcDir.exists()) {
                wcDir.mkdirs();
                log.info("检出SVN仓库到: {}", workCopyPath);
                SVNUpdateClient updateClient = clientManager.getUpdateClient();
                updateClient.doCheckout(SVNURL.parseURIEncoded(svnUrl), wcDir, SVNRevision.HEAD, SVNRevision.HEAD, SVNDepth.INFINITY, false);
            }
        } catch (SVNException e) {
            log.error("SVN检出失败", e);
            throw new RuntimeException("SVN检出失败", e);
        }
    }

    /**
     * 更新设计文档
     */
    public void updateDoc() {
        try {
            File wcDir = new File(workCopyPath);
            SVNUpdateClient updateClient = clientManager.getUpdateClient();
            long revision = updateClient.doUpdate(wcDir, SVNRevision.HEAD, SVNDepth.INFINITY, false, false);
            log.info("SVN更新完成, 版本: {}", revision);
        } catch (SVNException e) {
            log.error("SVN更新失败", e);
            throw new RuntimeException("SVN更新失败", e);
        }
    }

    /**
     * 上传结果文件
     */
    public void uploadResult(String env, String dbName, String localFilePath) {
        try {
            File localFile = new File(localFilePath);
            if (!localFile.exists()) {
                log.warn("结果文件不存在: {}", localFilePath);
                return;
            }

            // 构建目标目录
            String envDir = workCopyPath + "/results/" + env;
            String dbDir = envDir + "/" + dbName;
            File dbDirFile = new File(dbDir);
            if (!dbDirFile.exists()) {
                dbDirFile.mkdirs();
            }

            // 复制文件
            File destFile = new File(dbDir + "/" + localFile.getName());
            FileUtils.copyFile(localFile, destFile);

            // SVN添加
            SVNWCClient wcClient = clientManager.getWCClient();
            wcClient.doAdd(destFile, false, false, false, SVNDepth.INFINITY, false, false);

            log.info("结果文件已添加到SVN: {}", destFile.getAbsolutePath());
        } catch (Exception e) {
            log.error("SVN上传失败", e);
            throw new RuntimeException("SVN上传失败", e);
        }
    }

    /**
     * 提交所有变更
     */
    public String commitAll(String message) {
        try {
            File wcDir = new File(workCopyPath);
            SVNCommitClient commitClient = clientManager.getCommitClient();
            SVNCommitInfo commitInfo = commitClient.doCommit(new File[]{wcDir}, false, message, null, null);
            log.info("SVN提交完成, 版本: {}", commitInfo.getNewRevision());
            return String.valueOf(commitInfo.getNewRevision());
        } catch (SVNException e) {
            log.error("SVN提交失败", e);
            throw new RuntimeException("SVN提交失败", e);
        }
    }
}
