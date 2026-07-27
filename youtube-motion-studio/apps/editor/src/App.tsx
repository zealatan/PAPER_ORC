/**
 * Editor shell layout (spec §11): top toolbar, left panel, center canvas, right inspector, bottom
 * timeline. Panels are thin views over the Zustand store; they own no domain state (spec §34.3).
 */
import { Canvas } from "./canvas/Canvas";
import { useKeyboardShortcuts } from "./canvas/useKeyboardShortcuts";
import { useAudioPlayback } from "./canvas/useAudioPlayback";
import { TopToolbar } from "./panels/TopToolbar";
import { LeftPanel } from "./panels/LeftPanel";
import { Inspector } from "./panels/Inspector";
import { Timeline } from "./panels/Timeline";
import { useEditor } from "./state/store";

export function App() {
  useKeyboardShortcuts();
  useAudioPlayback();
  const loadError = useEditor((s) => s.loadError);

  return (
    <div className="editor">
      <TopToolbar />
      {loadError ? <div className="editor__error">Load failed: {loadError}</div> : null}
      <div className="editor__body">
        <aside className="editor__left">
          <LeftPanel />
        </aside>
        <main className="editor__center">
          <Canvas />
        </main>
        <aside className="editor__right">
          <Inspector />
        </aside>
      </div>
      <footer className="editor__timeline">
        <Timeline />
      </footer>
    </div>
  );
}
