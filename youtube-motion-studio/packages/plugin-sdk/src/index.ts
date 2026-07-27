/**
 * @motion-studio/plugin-sdk — manifest, permission-gated API, and a reversible plugin host.
 */
export const ENGINE_VERSION = "0.1.0";

export {
  type PluginManifest,
  type PluginPermission,
  compareVersions,
  satisfiesEngine,
} from "./manifest";
export {
  PluginHost,
  type PluginAPI,
  type MotionStudioPlugin,
  type LoadablePlugin,
  type PluginHostTargets,
} from "./host";
export { exampleManifest, examplePlugin, exampleLoadable } from "./examplePlugin";
