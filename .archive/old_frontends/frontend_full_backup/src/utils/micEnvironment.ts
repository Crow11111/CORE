/**
 * Cursor / VS Code Simple Browser nutzen Electron-Webviews.
 * getUserMedia + MediaRecorder kann dort den Host-Prozess abstürzen lassen.
 * Normales Chrome/Firefox auf localhost: meist ohne "Electron" in der UA.
 */
export function isMicUnsafeInEmbeddedHost(): boolean {
  if (typeof navigator === "undefined") return true;
  if (import.meta.env.VITE_FORCE_MIC_UNSAFE === "1") return false;
  if (import.meta.env.VITE_BLOCK_EMBEDDED_MIC === "0") return false;
  const ua = navigator.userAgent || "";
  if (/Electron/i.test(ua)) return true;
  try {
    const loc = window.location?.href || "";
    if (/^vscode-webview:/i.test(loc)) return true;
  } catch {
    /* ignore */
  }
  return false;
}
