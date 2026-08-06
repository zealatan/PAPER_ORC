/**
 * Plugin host (spec §19). Loads a plugin behind three guards:
 *  - **version**: the plugin's `engine.minimumVersion` must be satisfied by the engine version,
 *  - **permissions**: a capability call is denied unless the manifest declares its permission,
 *  - **isolation**: an error in `activate` rolls back partial registrations and surfaces a typed
 *    {@link PluginActivationError} instead of crashing the host.
 *
 * Every registration returns a disposer, so unloading a plugin exactly reverses it (spec §19.4:
 * "Plugin registration must be reversible").
 */
import { PluginActivationError } from "@motion-studio/core";
import type { Theme, MotionTemplate } from "@motion-studio/core";
import type { ComponentDefinition, ComponentRegistry } from "@motion-studio/components";
import type { PluginManifest, PluginPermission } from "./manifest";
import { satisfiesEngine } from "./manifest";

/** Capability surface handed to a plugin's `activate` (spec §19.1). */
export interface PluginAPI {
  registerComponent(definition: ComponentDefinition<unknown>): void;
  registerTheme(theme: Theme): void;
  registerTemplate(template: MotionTemplate): void;
  log(message: string): void;
}

export interface MotionStudioPlugin {
  activate(api: PluginAPI): void | Promise<void>;
  deactivate?(): void | Promise<void>;
}

export interface LoadablePlugin {
  manifest: PluginManifest;
  plugin: MotionStudioPlugin;
}

export interface PluginHostTargets {
  engineVersion: string;
  components: ComponentRegistry;
  themes: Theme[];
  templates: MotionTemplate[];
  onLog?: (pluginId: string, message: string) => void;
}

interface LoadedEntry {
  manifest: PluginManifest;
  plugin: MotionStudioPlugin;
  disposers: Array<() => void>;
}

export class PluginHost {
  private readonly loaded = new Map<string, LoadedEntry>();

  constructor(private readonly targets: PluginHostTargets) {}

  isLoaded(pluginId: string): boolean {
    return this.loaded.has(pluginId);
  }

  listLoaded(): string[] {
    return [...this.loaded.keys()];
  }

  async load({ manifest, plugin }: LoadablePlugin): Promise<void> {
    if (this.loaded.has(manifest.id)) {
      throw new PluginActivationError(manifest.id, "Plugin is already loaded.");
    }
    if (!satisfiesEngine(this.targets.engineVersion, manifest.engine.minimumVersion)) {
      throw new PluginActivationError(
        manifest.id,
        `Requires engine >= ${manifest.engine.minimumVersion}, but this engine is ${this.targets.engineVersion}.`,
        "Update the engine or lower the plugin's minimumVersion.",
      );
    }

    const disposers: Array<() => void> = [];
    const targets = this.targets;
    const requirePermission = (permission: PluginPermission): void => {
      if (!manifest.permissions.includes(permission)) {
        throw new PluginActivationError(
          manifest.id,
          `Missing permission "${permission}".`,
          `Add "${permission}" to the plugin manifest's permissions.`,
        );
      }
    };

    const api: PluginAPI = {
      registerComponent(definition) {
        requirePermission("register-components");
        targets.components.register(definition);
        disposers.push(() => targets.components.unregister(definition.type));
      },
      registerTheme(theme) {
        requirePermission("register-themes");
        targets.themes.push(theme);
        disposers.push(() => {
          const index = targets.themes.indexOf(theme);
          if (index >= 0) targets.themes.splice(index, 1);
        });
      },
      registerTemplate(template) {
        requirePermission("register-templates");
        targets.templates.push(template);
        disposers.push(() => {
          const index = targets.templates.indexOf(template);
          if (index >= 0) targets.templates.splice(index, 1);
        });
      },
      log(message) {
        targets.onLog?.(manifest.id, message);
      },
    };

    try {
      await plugin.activate(api);
    } catch (error) {
      // Roll back any partial registrations so a failed plugin leaves no trace.
      for (const dispose of disposers.reverse()) {
        try {
          dispose();
        } catch {
          /* keep rolling back */
        }
      }
      throw new PluginActivationError(
        manifest.id,
        error instanceof Error ? error.message : String(error),
      );
    }

    this.loaded.set(manifest.id, { manifest, plugin, disposers });
  }

  async unload(pluginId: string): Promise<void> {
    const entry = this.loaded.get(pluginId);
    if (!entry) return;
    try {
      await entry.plugin.deactivate?.();
    } catch {
      /* deactivation errors must not block unregistration */
    }
    for (const dispose of entry.disposers.reverse()) {
      try {
        dispose();
      } catch {
        /* continue */
      }
    }
    this.loaded.delete(pluginId);
  }
}
