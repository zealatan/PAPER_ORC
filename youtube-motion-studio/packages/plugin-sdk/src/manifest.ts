/**
 * Plugin manifest + version helpers (spec §19.2). The manifest is data; the engine validates its
 * version compatibility and gates capabilities behind declared permissions.
 */

export type PluginPermission =
  | "register-components"
  | "register-inspector-controls"
  | "register-themes"
  | "register-templates"
  | "register-animation-presets"
  | "register-commands";

export interface PluginManifest {
  id: string;
  name: string;
  version: string;
  engine: { minimumVersion: string };
  entry?: string;
  permissions: PluginPermission[];
}

function parseVersion(version: string): [number, number, number] {
  const parts = version.split(".").map((p) => Number.parseInt(p, 10));
  return [parts[0] ?? 0, parts[1] ?? 0, parts[2] ?? 0];
}

/** Compare two semver strings: -1 if a<b, 0 if equal, 1 if a>b. */
export function compareVersions(a: string, b: string): -1 | 0 | 1 {
  const va = parseVersion(a);
  const vb = parseVersion(b);
  for (let i = 0; i < 3; i += 1) {
    if (va[i]! < vb[i]!) return -1;
    if (va[i]! > vb[i]!) return 1;
  }
  return 0;
}

/** True when `engineVersion` satisfies the plugin's minimum engine requirement. */
export function satisfiesEngine(engineVersion: string, minimumVersion: string): boolean {
  return compareVersions(engineVersion, minimumVersion) >= 0;
}
