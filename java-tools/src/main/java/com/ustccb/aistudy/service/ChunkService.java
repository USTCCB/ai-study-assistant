package com.ustccb.aistudy.service;

import com.ustccb.aistudy.dto.Chunk;
import com.ustccb.aistudy.dto.ChunkRequest;
import com.ustccb.aistudy.dto.ChunkResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

/**
 * 文档滑动窗口切片 —— 给 Python 端调用。
 *
 * 设计：
 * - chunkSize 字符数（含中文），overlap 重叠字符数
 * - 优先在句号/换行/空白处切，避免把一个句子腰斩
 * - 跳过空 chunk；末尾不足一个 chunkSize 也算一段（避免丢内容）
 */
@Service
public class ChunkService {

    @Value("${chunking.defaultChunkSize:500}")
    private int defaultChunkSize;

    @Value("${chunking.defaultOverlap:80}")
    private int defaultOverlap;

    @Value("${chunking.maxChunkSize:2000}")
    private int maxChunkSize;

    public ChunkResponse chunk(ChunkRequest req) {
        long t0 = System.currentTimeMillis();
        int size = clamp(req.getChunkSize() == null ? defaultChunkSize : req.getChunkSize(), 50, maxChunkSize);
        int overlap = req.getOverlap() == null ? defaultOverlap : Math.max(0, Math.min(req.getOverlap(), size / 2));
        String text = req.getText() == null ? "" : req.getText();
        String source = req.getSource() == null ? "unknown" : req.getSource();

        List<Chunk> out = new ArrayList<>();
        if (text.isEmpty()) {
            return new ChunkResponse(0, System.currentTimeMillis() - t0, out);
        }

        int idx = 0;
        int n = text.length();
        int start = 0;
        while (start < n) {
            int end = Math.min(start + size, n);
            if (end < n) {
                int cut = findSoftBreak(text, end, start + size / 2);
                if (cut > start) end = cut;
            }
            String piece = text.substring(start, end).trim();
            if (!piece.isEmpty()) {
                out.add(new Chunk(idx++, piece, piece.length(), source));
            }
            if (end == n) break;
            start = Math.max(end - overlap, start + 1);
        }
        return new ChunkResponse(out.size(), System.currentTimeMillis() - t0, out);
    }

    /** 从 end 往前找最近的句末/换行/空白 */
    private int findSoftBreak(String s, int end, int minPos) {
        for (int i = end; i > minPos; i--) {
            char c = s.charAt(i);
            if (c == '。' || c == '！' || c == '？' || c == '.' || c == '!' || c == '?'
                || c == '\n' || c == '\r') {
                return i + 1;
            }
        }
        for (int i = end; i > minPos; i--) {
            if (Character.isWhitespace(s.charAt(i))) return i + 1;
        }
        return end;
    }

    private int clamp(int v, int lo, int hi) { return Math.max(lo, Math.min(hi, v)); }
}
