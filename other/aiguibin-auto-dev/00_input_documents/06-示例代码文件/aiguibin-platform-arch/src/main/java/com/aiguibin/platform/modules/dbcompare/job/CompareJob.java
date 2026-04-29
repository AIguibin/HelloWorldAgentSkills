package com.aiguibin.platform.modules.dbcompare.job;

import com.aiguibin.platform.modules.dbcompare.service.DbCompareService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

/**
 * 比对定时任务
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class CompareJob {

    private final DbCompareService compareService;

    /**
     * DEV环境定时任务 - 每天2点
     */
    @Scheduled(cron = "${schedule.dev.cron:0 0 2 * * ?}")
    public void devJob() {
        log.info("DEV环境定时任务开始");
        compareService.compareEnv("DEV", "SCHEDULE");
    }

    /**
     * SIT环境定时任务 - 每天4点
     */
    @Scheduled(cron = "${schedule.sit.cron:0 0 4 * * ?}")
    public void sitJob() {
        log.info("SIT环境定时任务开始");
        compareService.compareEnv("SIT", "SCHEDULE");
    }

    /**
     * UAT环境定时任务 - 每天6点
     */
    @Scheduled(cron = "${schedule.uat.cron:0 0 6 * * ?}")
    public void uatJob() {
        log.info("UAT环境定时任务开始");
        compareService.compareEnv("UAT", "SCHEDULE");
    }
}
