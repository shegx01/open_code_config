# TypeScript debugging tools

```yaml
language_support:
  typescript:
    file_patterns: ["*.ts", "*.tsx", "*.js", "*.jsx"]
    debugging_tools: ["debugger", "console", "profiler", "testing"]
    build_commands: ["npm test", "yarn test"]
    safety_level: "development_focused"
```

## TypeScript Debugging Techniques

### Core Debugging Tools

**Browser DevTools Integration:**

```typescript
// Source map debugging
console.log('Debug checkpoint:', data);
console.trace('Call stack trace');
debugger; // Breakpoint in browser

// Advanced logging with structured data
console.group('API Call Debug');
console.log('Request:', request);
console.log('Response:', response);
console.groupEnd();
```

**Node.js Debugging:**

```typescript
// Built-in debugger
import { debuglog } from 'util';
const debug = debuglog('myapp');

debug('Debug message: %o', complexObject);

// Inspector debugging
// Run with: node --inspect-brk app.js
// Connect Chrome DevTools to debug
```

**TypeScript-Specific Debugging:**

```typescript
// Type-safe debugging utilities
function debugAssert<T>(condition: T, message: string): asserts condition {
    if (!condition) {
        console.error('Debug assertion failed:', message);
        debugger;
    }
}

// Runtime type checking for debugging
function isString(value: unknown): value is string {
    const result = typeof value === 'string';
    if (!result) {
        console.warn('Type check failed: expected string, got', typeof value);
    }
    return result;
}
```

### Production Debugging Strategies

**Structured Logging:**

```typescript
interface LogEntry {
    level: 'debug' | 'info' | 'warn' | 'error';
    message: string;
    timestamp: string;
    context?: Record<string, unknown>;
    error?: Error;
}

class Logger {
    private isDevelopment = process.env.NODE_ENV === 'development';

    log(entry: LogEntry): void {
        if (this.isDevelopment) {
            console.log(JSON.stringify(entry, null, 2));
        } else {
            // Send to logging service (e.g., Winston, Pino)
            this.sendToLoggingService(entry);
        }
    }

    private sendToLoggingService(entry: LogEntry): void {
        // Production logging implementation
    }
}
```

**Error Boundary Pattern:**

```typescript
// React Error Boundary for debugging
class ErrorBoundary extends React.Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.error('Error caught by boundary:', error, errorInfo);
        // Send to error reporting service
        this.reportError(error, errorInfo);
    }
}

// Generic error handling
function withErrorHandling<T extends (...args: any[]) => any>(
    fn: T
): T {
    return ((...args: Parameters<T>) => {
        try {
            return fn(...args);
        } catch (error) {
            console.error('Function error:', error);
            throw error;
        }
    }) as T;
}
```

### Performance Debugging

**Performance Monitoring:**

```typescript
// Performance measurement utilities
class PerformanceTracker {
    private marks = new Map<string, number>();

    mark(name: string): void {
        this.marks.set(name, performance.now());
    }

    measure(name: string, startMark: string): number {
        const start = this.marks.get(startMark);
        if (!start) {
            console.warn(`Start mark "${startMark}" not found`);
            return 0;
        }

        const duration = performance.now() - start;
        console.log(`${name}: ${duration.toFixed(2)}ms`);
        return duration;
    }
}

// Memory usage tracking
function trackMemoryUsage(label: string): void {
    if ('memory' in performance) {
        const memory = (performance as any).memory;
        console.log(`${label} - Memory:`, {
            used: `${(memory.usedJSHeapSize / 1024 / 1024).toFixed(2)} MB`,
            total: `${(memory.totalJSHeapSize / 1024 / 1024).toFixed(2)} MB`,
            limit: `${(memory.jsHeapSizeLimit / 1024 / 1024).toFixed(2)} MB`
        });
    }
}
```
