package com.ustccb.aistudy.controller;

import com.ustccb.aistudy.dto.ApiResponse;
import com.ustccb.aistudy.dto.ChunkRequest;
import com.ustccb.aistudy.dto.ChunkResponse;
import com.ustccb.aistudy.service.ChunkService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class ChunkController {

    private final ChunkService chunkService;

    /** Python 端调这个接口：POST /api/chunk，body 是 ChunkRequest JSON */
    @PostMapping("/chunk")
    public ApiResponse<ChunkResponse> chunk(@Valid @RequestBody ChunkRequest req) {
        return ApiResponse.ok(chunkService.chunk(req));
    }

    @GetMapping("/health")
    public ApiResponse<Map<String,Object>> health() {
        return ApiResponse.ok(Map.of("status", "UP", "service", "ai-study-java-tools"));
    }
}
