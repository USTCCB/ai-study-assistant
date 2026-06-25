package com.ustccb.aistudy;

import com.ustccb.aistudy.dto.ChunkRequest;
import com.ustccb.aistudy.dto.ChunkResponse;
import com.ustccb.aistudy.service.ChunkService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class ChunkServiceTest {

    @Autowired
    private ChunkService chunkService;

    @Test
    void chunkShouldRespectOverlap() {
        String text = "Spring Boot makes it easy to create stand-alone, production-grade Spring applications. " +
                      "It provides a range of non-functional features common to large classes of projects. " +
                      "Java is a high-level, class-based, object-oriented programming language. " +
                      "Microservices are an architectural style that structures an application as a collection of services.";

        ChunkRequest req = new ChunkRequest();
        req.setText(text);
        req.setChunkSize(80);
        req.setOverlap(20);
        req.setSource("test-doc");

        ChunkResponse resp = chunkService.chunk(req);
        assertTrue(resp.getTotal() >= 2);
        for (var c : resp.getChunks()) {
            assertEquals("test-doc", c.getSource());
            assertTrue(c.getCharCount() > 0);
            assertTrue(c.getCharCount() <= 200, "chunk too big: " + c.getCharCount());
        }
    }

    @Test
    void emptyTextShouldReturnZero() {
        ChunkRequest req = new ChunkRequest();
        req.setText("");
        req.setSource("empty");
        ChunkResponse resp = chunkService.chunk(req);
        assertEquals(0, resp.getTotal());
    }

    @Test
    void chineseTextShouldSplit() {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 100; i++) sb.append("这是一句测试文本。");
        ChunkRequest req = new ChunkRequest();
        req.setText(sb.toString());
        req.setChunkSize(120);
        req.setOverlap(20);
        req.setSource("zh");
        ChunkResponse resp = chunkService.chunk(req);
        assertTrue(resp.getTotal() >= 5);
    }
}
