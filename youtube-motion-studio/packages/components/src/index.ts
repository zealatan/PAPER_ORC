/**
 * @motion-studio/components — the built-in component pack (text, shapes, media, layout, social,
 * charts) and the registries that wire them into the renderer.
 */
import { DefaultRenderRegistry, type RenderRegistry } from "@motion-studio/renderer-core";
import { DefaultComponentRegistry, installRenderers } from "./registry";
import type { ComponentDefinition, ComponentRegistry } from "./types";
import { rectangleComponent } from "./shapes/rectangle";
import { circleComponent } from "./shapes/circle";
import { textComponent } from "./text/text";
import { titleComponent } from "./text/title";
import { captionComponent } from "./text/caption";
import { subtitleComponent } from "./text/subtitle";
import { imageComponent } from "./media/image";
import { imageCardComponent } from "./media/imageCard";
import { groupComponent } from "./layout/group";
import { profileCardComponent } from "./social/profileCard";
import { characterComponent } from "./social/character";
import { speechBubbleComponent } from "./social/speechBubble";
import { topicCircleComponent } from "./social/topicCircle";
import { youtubeCommentComponent } from "./social/youtubeComment";
import { phoneFrameComponent } from "./social/phoneFrame";
import { notificationComponent } from "./social/notification";
import { barChartComponent } from "./chart/barChart";
import { lineChartComponent } from "./chart/lineChart";
import { tableComponent } from "./chart/table";

export * from "./types";
export { DefaultComponentRegistry, installRenderers } from "./registry";
export { rectangleComponent } from "./shapes/rectangle";
export { circleComponent } from "./shapes/circle";
export { textComponent } from "./text/text";
export { titleComponent } from "./text/title";
export { captionComponent } from "./text/caption";
export { subtitleComponent } from "./text/subtitle";
export { imageComponent } from "./media/image";
export { imageCardComponent } from "./media/imageCard";
export { groupComponent } from "./layout/group";
export { profileCardComponent } from "./social/profileCard";
export { characterComponent } from "./social/character";
export { speechBubbleComponent } from "./social/speechBubble";
export { topicCircleComponent } from "./social/topicCircle";
export { youtubeCommentComponent } from "./social/youtubeComment";
export { phoneFrameComponent } from "./social/phoneFrame";
export { notificationComponent } from "./social/notification";
export { barChartComponent } from "./chart/barChart";
export { lineChartComponent } from "./chart/lineChart";
export { tableComponent } from "./chart/table";

/** Every built-in component definition, in registration order. */
export const BUILTIN_COMPONENTS: ComponentDefinition<unknown>[] = [
  // primitives
  rectangleComponent,
  circleComponent,
  textComponent,
  imageComponent,
  groupComponent,
  // text
  titleComponent,
  captionComponent,
  subtitleComponent,
  // media
  imageCardComponent,
  // social
  profileCardComponent,
  characterComponent,
  speechBubbleComponent,
  topicCircleComponent,
  youtubeCommentComponent,
  phoneFrameComponent,
  notificationComponent,
  // charts
  barChartComponent,
  lineChartComponent,
  tableComponent,
];

/** A component registry pre-populated with the built-in components. */
export function createDefaultComponentRegistry(): ComponentRegistry {
  const registry = new DefaultComponentRegistry();
  for (const component of BUILTIN_COMPONENTS) {
    registry.register(component);
  }
  return registry;
}

/** A renderer-core RenderRegistry with the built-in components installed as element renderers. */
export function createDefaultRenderRegistry(): RenderRegistry {
  const renderers = new DefaultRenderRegistry();
  installRenderers(createDefaultComponentRegistry(), renderers);
  return renderers;
}
