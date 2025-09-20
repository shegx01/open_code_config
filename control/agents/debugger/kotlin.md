# Kotlin Multiplatform debugging tools

```yaml
language_support:
  kmp:
    file_patterns: ["*.kt", "*.kts", "build.gradle.kts"]
    debugging_tools: ["debugger", "profiler", "logging"]
    build_commands: ["./gradlew build", "./gradlew test"]
    safety_level: "development_focused"
```

## Kotlin Multiplatform (KMP) Debugging Techniques

### Core Debugging Approach

**Platform-Specific Debugging:**

```kotlin
// Common code debugging with expect/actual
expect fun debugLog(message: String)

// Android actual implementation
actual fun debugLog(message: String) {
    Log.d("KMP_DEBUG", message)
}

// iOS actual implementation
actual fun debugLog(message: String) {
    println("KMP_DEBUG: $message")
}
```

**Cross-Platform Logging:**

```kotlin
// Using Napier for unified logging
Napier.d("Debug message across platforms")
Napier.e("Error occurred", throwable)

// Platform-specific configuration
// Android
Napier.base(DebugAntilog())

// iOS
Napier.base(DebugAntilog())
```

### IDE-Based Debugging

**IntelliJ IDEA / Android Studio:**

```kotlin
// Set breakpoints in common code
fun processData(input: String): Result {
    val processed = input.trim() // <- Breakpoint here
    return validateInput(processed)
}

// Debug expect/actual implementations
expect fun platformSpecificOperation(): String

// Debug actual Android implementation
actual fun platformSpecificOperation(): String {
    return "Android result" // <- Breakpoint works here
}
```

**Cross-Language Debugging (iOS):**

- Set breakpoints in Kotlin code from Android Studio
- Debug Swift and Kotlin simultaneously
- Navigate between Kotlin and Swift code
- Use Android Studio debugger for iOS targets

### Production Debugging Strategies

**Safe Logging Implementation:**

```kotlin
object KMPLogger {
    private var isDebugMode = false

    fun initialize(debug: Boolean) {
        isDebugMode = debug
        if (debug) {
            Napier.base(DebugAntilog())
        } else {
            Napier.base(CrashlyticsAntilog())
        }
    }

    fun logError(message: String, throwable: Throwable? = null) {
        if (isDebugMode) {
            Napier.e(message, throwable)
        } else {
            // Send to crash reporting only in production
            Napier.e(message, throwable, tag = "PRODUCTION")
        }
    }
}
```

**Platform-Specific Error Handling:**

```kotlin
// Common error handling interface
expect class PlatformException(message: String, cause: Throwable?) : Exception

// Android actual implementation
actual class PlatformException actual constructor(
    message: String,
    cause: Throwable?
) : Exception(message, cause)

// iOS actual implementation
actual class PlatformException actual constructor(
    message: String,
    cause: Throwable?
) : Exception(message, cause)
```

### Memory and Performance Debugging

**Memory Leak Detection:**

```kotlin
// Common memory tracking
expect class MemoryTracker() {
    fun trackAllocation(size: Long)
    fun trackDeallocation(size: Long)
    fun getCurrentUsage(): Long
}

// Platform-specific implementations with native tools
// Android: Use LeakCanary integration
// iOS: Use Xcode Instruments integration
```

**Performance Profiling:**

```kotlin
// Cross-platform performance measurement
expect fun measureTime(block: () -> Unit): Long

// Android actual - uses System.nanoTime()
actual fun measureTime(block: () -> Unit): Long {
    val start = System.nanoTime()
    block()
    return System.nanoTime() - start
}

// iOS actual - uses platform.posix
actual fun measureTime(block: () -> Unit): Long {
    // Implementation using iOS native timing
}
```

### Debugging Workflows

**Development Debugging:**

1. **IDE Setup**: Use IntelliJ IDEA or Android Studio with KMP plugin
2. **Breakpoint Strategy**: Set breakpoints in common code and platform-specific implementations
3. **Cross-Platform Testing**: Debug on multiple platforms simultaneously
4. **Expect/Actual Validation**: Verify all expected declarations have actual implementations

**Production Debugging:**

1. **Centralized Logging**: Use Napier or Kermit with platform-specific backends
2. **Crash Reporting**: Integrate with Firebase Crashlytics or similar
3. **Remote Debugging**: Implement remote log collection
4. **Platform Isolation**: Debug platform-specific issues in isolation

### Common KMP Debugging Patterns

**Expect/Actual Debugging:**

```kotlin
// Debug missing actual implementations
expect fun getCurrentPlatform(): String

// Compiler will error if actual is missing
// Use IDE navigation to jump between expect/actual
```

**Coroutines Debugging:**

```kotlin
// Debug coroutines across platforms
suspend fun fetchData(): Result<Data> {
    return withContext(Dispatchers.IO) {
        try {
            debugLog("Starting data fetch")
            val result = apiCall()
            debugLog("Data fetch successful")
            Result.success(result)
        } catch (e: Exception) {
            debugLog("Data fetch failed: ${e.message}")
            Result.failure(e)
        }
    }
}
```

### Safety Guidelines

**KMP Production Debugging Rules:**

- Use platform-appropriate logging libraries (Napier, Kermit)
- Implement proper error boundaries for each platform
- Test debugging tools on all target platforms
- Use conditional compilation for debug-only code
- Implement platform-specific crash reporting

**Never Do in KMP:**

```kotlin
// DANGEROUS - Platform-specific code in common module
fun debugFunction() {
    println("Debug") // Works on JVM/Android, may fail on Native
    System.out.println("Debug") // JVM-only, will crash on Native
}

// DANGEROUS - Unhandled platform differences
expect fun platformFunction(): String
// Missing actual implementations will cause compilation errors
```
