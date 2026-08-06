/**
 * Audio preview sync (spec §16.1). Keeps one HTMLAudioElement per audio track and drives its
 * position + play/pause from the timeline so audio stays synchronized with the preview during
 * playback and scrubbing. No-op when a project has no audio tracks or unresolved assets.
 */
import { useEffect, useRef } from "react";
import { createRenderContext } from "@motion-studio/renderer-core";
import { useEditor } from "../state/store";

export function useAudioPlayback() {
  const project = useEditor((s) => s.project);
  const time = useEditor((s) => s.time);
  const playing = useEditor((s) => s.playing);
  const elementsRef = useRef<Map<string, HTMLAudioElement>>(new Map());

  // Create/update an <audio> per track; drop stale ones.
  useEffect(() => {
    const map = elementsRef.current;
    const ctx = createRenderContext(project);
    const seen = new Set<string>();
    for (const track of project.audioTracks) {
      seen.add(track.id);
      const url = ctx.resolveAssetUrl(track.assetId);
      if (!url) continue;
      let audio = map.get(track.id);
      if (!audio) {
        audio = new Audio();
        map.set(track.id, audio);
      }
      if (audio.src !== url) audio.src = url;
      audio.volume = track.muted ? 0 : (track.volume ?? 1);
    }
    for (const [id, audio] of map) {
      if (!seen.has(id)) {
        audio.pause();
        map.delete(id);
      }
    }
  }, [project]);

  // Drive position + play/pause from the timeline.
  useEffect(() => {
    const map = elementsRef.current;
    for (const track of project.audioTracks) {
      const audio = map.get(track.id);
      if (!audio) continue;
      const trimStart = track.trimStart ?? 0;
      const local = time - track.start + trimStart;
      const within = local >= trimStart && local <= trimStart + track.duration;
      if (playing && within) {
        if (Math.abs(audio.currentTime - local) > 0.25) {
          audio.currentTime = Math.max(0, local);
        }
        void audio.play().catch(() => {});
      } else {
        audio.pause();
      }
    }
  }, [project, time, playing]);

  useEffect(() => {
    const map = elementsRef.current;
    return () => {
      for (const audio of map.values()) audio.pause();
      map.clear();
    };
  }, []);
}
