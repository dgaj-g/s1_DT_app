const DEFAULT_TIMEOUT_MS = 15000;

export async function withTimeout<T>(
  promise: PromiseLike<T>,
  label: string,
  timeoutMs = DEFAULT_TIMEOUT_MS
): Promise<T> {
  let timeoutId: number | undefined;

  try {
    return await Promise.race([
      Promise.resolve(promise),
      new Promise<never>((_, reject) => {
        timeoutId = window.setTimeout(() => {
          reject(new Error(`${label} is taking too long. Please check your connection and try again.`));
        }, timeoutMs);
      })
    ]);
  } finally {
    if (timeoutId !== undefined) {
      window.clearTimeout(timeoutId);
    }
  }
}

export function getErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof Error && error.message.trim()) {
    return error.message;
  }

  if (typeof error === "string" && error.trim()) {
    return error;
  }

  if (error && typeof error === "object") {
    const record = error as { message?: unknown; details?: unknown; hint?: unknown; code?: unknown };
    const parts = [record.message, record.details, record.hint, record.code]
      .filter((part): part is string => typeof part === "string" && part.trim().length > 0)
      .map((part) => part.trim());

    if (parts.length > 0) {
      return parts.join(" ");
    }
  }

  return fallback;
}
