package com.aiguibin.platform.modules.dbcompare.service;

import com.aiguibin.platform.modules.dbcompare.model.vo.CompareResultVo;
import com.aiguibin.platform.modules.dbcompare.model.dto.DbCompareDetail;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 通知服务
 *
 * @author aiguibin
 * @date 2025-01-15
 */
@Slf4j
@Service
public class NotifyService {

    @Value("${feiQ.server-url}")
    private String feiQServerUrl;

    @Value("${feiQ.server-port:8080}")
    private int feiQServerPort;

    @Value("${feiQ.receivers}")
    private String receivers;

    private final RestTemplate restTemplate = new RestTemplate();

    /**
     * 发送单个数据库完成通知
     */
    public void sendDbCompleteNotify(String env, String dbKey, DbCompareDetail detail) {
        String dbName = extractDbName(dbKey);

        StringBuilder message = new StringBuilder();
        message.append("【数据库比对结果】\n");
        message.append("━━━━━━━━━━━━━━━━━━━━\n");
        message.append("环境: ").append(env).append("\n");
        message.append("数据库: ").append(dbName).append("\n");
        message.append("执行时间: ").append(LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))).append("\n");
        message.append("执行时长: ").append(detail.getDurationMs() / 1000).append("秒\n");
        message.append("━━━━━━━━━━━━━━━━━━━━\n");
        message.append("表差异: ").append(detail.getTableDiffCount()).append(" 条\n");
        message.append("字段差异: ").append(detail.getColumnDiffCount()).append(" 条\n");
        message.append("索引差异: ").append(detail.getIndexDiffCount()).append(" 条\n");
        message.append("━━━━━━━━━━━━━━━━━━━━\n");
        message.append("结果路径: /results/").append(env).append("/").append(dbName).append("/\n");

        sendFeiQ(message.toString());
    }

    /**
     * 发送全环境完成通知
     */
    public void sendAllEnvCompleteNotify(List<CompareResultVo> results) {
        StringBuilder message = new StringBuilder();
        message.append("【全环境比对完成】\n");
        message.append("━━━━━━━━━━━━━━━━━━━━\n");
        message.append("执行时间: ").append(LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))).append("\n");
        message.append("━━━━━━━━━━━━━━━━━━━━\n");

        for (CompareResultVo result : results) {
            message.append(result.getEnv()).append("环境: ");
            message.append("成功").append(result.getSuccessCount()).append("/").append(result.getTotalDbCount()).append(" ");
            message.append("(表差异:").append(result.getTotalTableDiff()).append(" ");
            message.append("字段差异:").append(result.getTotalColumnDiff()).append(" ");
            message.append("索引差异:").append(result.getTotalIndexDiff()).append(")\n");
        }

        message.append("━━━━━━━━━━━━━━━━━━━━\n");
        message.append("结果路径: /results/\n");

        sendFeiQ(message.toString());
    }

    /**
     * 发送飞秋通知
     */
    private void sendFeiQ(String message) {
        try {
            String url = feiQServerUrl + ":" + feiQServerPort + "/send";

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            Map<String, String> body = new HashMap<>();
            body.put("receivers", receivers);
            body.put("message", message);

            HttpEntity<Map<String, String>> request = new HttpEntity<>(body, headers);
            restTemplate.postForObject(url, request, String.class);

            log.info("飞秋通知已发送");
        } catch (Exception e) {
            log.error("飞秋通知发送失败", e);
        }
    }

    private String extractDbName(String dsKey) {
        return dsKey.substring(dsKey.lastIndexOf("-") + 1);
    }
}
