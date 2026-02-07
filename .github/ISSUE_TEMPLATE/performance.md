---
name: Performance Issue
about: Report slow execution, high resource usage, or optimization opportunities
title: '[PERF] '
labels: performance
assignees: ''
---

## Performance Issue

**What's slow or resource-intensive?**

A clear description of the performance problem.

## Performance Metrics

**Execution time:**
- Expected: [e.g., < 2 seconds]
- Actual: [e.g., 15 seconds]

**Resource usage:**
- CPU: [e.g., 80% sustained]
- Memory: [e.g., 2GB RAM]
- Disk I/O: [High/Normal/Low]
- Network: [High/Normal/Low]

## Affected Component

**Which part of JARVIS is slow?**

- [ ] Backend server (Flask/SocketIO)
- [ ] Planner model (Gemini API calls)
- [ ] Local client execution
- [ ] Vision pipeline (FastSAM/Vision Mapper)
- [ ] File operations
- [ ] Shell command execution
- [ ] Mobile app (React Native)
- [ ] WebSocket communication
- [ ] Other: ___________

**Specific execution plane:**
- [ ] Shell commands
- [ ] File operations
- [ ] Keyboard actions
- [ ] Vision pipeline
- [ ] All planes

## Steps to Reproduce

1. Start JARVIS components
2. Execute command: "..."
3. Measure time/resources
4. Observe slowness

**Test command:**
```
[Paste the command that's slow]
```

## Profiling Data

**Debug logs:**
```
[Paste relevant timing information from execution_log.txt]
```

**Bottleneck identified:**
- [ ] API call latency
- [ ] Image processing (FastSAM)
- [ ] Vision model inference
- [ ] File I/O operations
- [ ] Network communication
- [ ] Screenshot capture
- [ ] Unknown

**Timing breakdown (if available):**
```
Step 1: 0.5s
Step 2: 12.3s  ← Bottleneck
Step 3: 0.8s
Total: 13.6s
```

## System Information

**Hardware:**
- CPU: [e.g., Intel i7-9700K]
- RAM: [e.g., 16GB]
- GPU: [e.g., NVIDIA GTX 1660 / None]
- Storage: [e.g., SSD / HDD]

**Software:**
- Windows version: [e.g., Windows 11 22H2]
- Python version: [e.g., 3.10.5]
- PyTorch version: [e.g., 2.0.1]
- CUDA available: [Yes/No]

**Network:**
- Internet speed: [e.g., 100 Mbps]
- Latency to Gemini API: [e.g., 50ms]

## Expected Performance

**What would be acceptable?**

- Target execution time: [e.g., < 3 seconds]
- Target resource usage: [e.g., < 30% CPU]

**Comparison:**
- Similar tasks in other tools: [e.g., "Windows automation takes 1s"]
- Previous JARVIS versions: [e.g., "Used to be faster"]

## Optimization Ideas

**Have you identified potential optimizations?**

- [ ] Cache API responses
- [ ] Reduce image resolution
- [ ] Optimize FastSAM parameters
- [ ] Use faster execution plane
- [ ] Batch operations
- [ ] Parallel processing
- [ ] Reduce logging
- [ ] Other: ___________

**Specific suggestions:**
```
[Describe your optimization ideas]
```

## Workarounds

**Have you found any workarounds?**

- [ ] Using different commands
- [ ] Adjusting configuration
- [ ] Reducing image quality
- [ ] Other: ___________

## Frequency

**How often does this occur?**

- [ ] Always (every execution)
- [ ] Often (most executions)
- [ ] Sometimes (intermittent)
- [ ] Rare (specific conditions)

**Conditions that make it worse:**
- [ ] Large screenshots
- [ ] Multiple UI elements
- [ ] Complex commands
- [ ] Slow internet
- [ ] High system load
- [ ] Other: ___________

## Related Issues

Are there related performance issues?

## Willing to Contribute?

- [ ] I can profile the code to identify bottlenecks
- [ ] I can test optimization patches
- [ ] I can implement optimizations
- [ ] I can provide more performance data
- [ ] I prefer someone else to investigate

---

**Checklist before submitting:**
- [ ] I've measured actual performance metrics
- [ ] I've identified the slow component
- [ ] I've provided system information
- [ ] I've included debug logs with timing data
- [ ] I've described expected vs actual performance
