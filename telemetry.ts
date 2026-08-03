// telemetry.ts
import { diag, DiagConsoleLogger, DiagLogLevel } from '@opentelemetry/api';

// Set up diagnostics to catch tracing or initialization issues
diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.INFO);

export function trackEvent(eventName: string, attributes?: Record<string, any>) {
  console.log(`[Telemetry Event]: ${eventName}`, attributes || {});
}