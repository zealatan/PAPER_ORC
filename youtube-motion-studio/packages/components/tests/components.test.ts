import { describe, expect, it } from "vitest";
import {
  captionComponent,
  circleComponent,
  groupComponent,
  imageComponent,
  rectangleComponent,
  textComponent,
  titleComponent,
} from "../src";
import { makeContext, makeElement, makeProject } from "./helpers";

const ctx = makeContext();

describe("title component", () => {
  it("emits a heavy weight and a font family when set (hero display face)", () => {
    const el = makeElement("t", "title", {
      props: { text: "70년", fontWeight: 900, fontFamily: "Black Han Sans" },
    });
    expect(titleComponent.render(el, ctx)).toMatchObject({
      kind: "text",
      fontWeight: 900,
      fontFamily: "Black Han Sans",
    });
  });

  it("omits font family when unset so the renderer default applies", () => {
    const el = makeElement("t", "title", { props: { text: "Hi" } });
    const node = titleComponent.render(el, ctx);
    expect(node).toMatchObject({ kind: "text" });
    expect(node && "fontFamily" in node ? node.fontFamily : undefined).toBeUndefined();
  });
});

describe("caption component", () => {
  it("draws a background pill by default", () => {
    const el = makeElement("c", "caption", {
      props: { text: "Hi", background: "#111111" },
    });
    expect(captionComponent.render(el, ctx)?.kind).toBe("group");
  });

  it("renders bare text (no pill) when background is empty", () => {
    const el = makeElement("c", "caption", { props: { text: "Hi", background: "" } });
    expect(captionComponent.render(el, ctx)?.kind).toBe("text");
  });
});

describe("rectangle component", () => {
  it("renders a rect using style fill/stroke/radius", () => {
    const el = makeElement("r", "rectangle", {
      transform: { width: 200, height: 100 },
      style: {
        backgroundColor: "#123456",
        borderColor: "#000",
        borderWidth: 3,
        borderRadius: 8,
      },
    });
    const node = rectangleComponent.render(el, ctx);
    expect(node).toMatchObject({
      kind: "rect",
      width: 200,
      height: 100,
      radius: 8,
      fill: { color: "#123456" },
      stroke: { color: "#000", width: 3 },
    });
  });

  it("omits the stroke when border width is zero", () => {
    const el = makeElement("r", "rectangle", { style: { backgroundColor: "#fff" } });
    const node = rectangleComponent.render(el, ctx);
    expect(node && "stroke" in node ? node.stroke : undefined).toBeUndefined();
  });
});

describe("circle component", () => {
  it("renders an ellipse centered in the box", () => {
    const el = makeElement("c", "circle", {
      transform: { width: 120, height: 120 },
      style: { backgroundColor: "#abcdef" },
    });
    expect(circleComponent.render(el, ctx)).toMatchObject({
      kind: "ellipse",
      cx: 60,
      cy: 60,
      rx: 60,
      ry: 60,
      fill: { color: "#abcdef" },
    });
  });
});

describe("text component", () => {
  it("renders a centered text node with props", () => {
    const el = makeElement("t", "text", {
      transform: { width: 600, height: 100 },
      props: { text: "Hello", fontSize: 40, textAlign: "center", color: "#fff" },
    });
    const node = textComponent.render(el, ctx);
    // Either a bare text node or a group whose last child is the text.
    const textNode =
      node?.kind === "group" ? node.children[node.children.length - 1] : node;
    expect(textNode).toMatchObject({
      kind: "text",
      text: "Hello",
      fontSize: 40,
      align: "center",
    });
  });

  it("wraps text in a background rect when style.backgroundColor is set", () => {
    const el = makeElement("t", "text", {
      props: { text: "Bar" },
      style: { backgroundColor: "#111", borderRadius: 12 },
    });
    const node = textComponent.render(el, ctx);
    expect(node?.kind).toBe("group");
  });

  it("does not throw on missing props", () => {
    const el = makeElement("t", "text");
    expect(() => textComponent.render(el, ctx)).not.toThrow();
  });
});

describe("image component", () => {
  it("renders a placeholder rect when the asset is unresolved", () => {
    const el = makeElement("i", "image", { props: { assetId: "missing" } });
    expect(imageComponent.render(el, ctx)?.kind).toBe("rect");
  });

  it("renders an image node when the asset resolves", () => {
    const project = makeProject(
      [],
      [
        {
          id: "img1",
          type: "image",
          name: "img",
          source: { kind: "data-url", value: "data:image/png;base64,AAAA" },
        },
      ],
    );
    const el = makeElement("i", "image", {
      transform: { width: 300, height: 300 },
      props: { assetId: "img1" },
    });
    const node = imageComponent.render(el, makeContext(project));
    expect(node).toMatchObject({
      kind: "image",
      width: 300,
      height: 300,
      href: "data:image/png;base64,AAAA",
    });
  });
});

describe("group component", () => {
  it("returns null when it has no background", () => {
    expect(groupComponent.render(makeElement("g", "group"), ctx)).toBeNull();
  });

  it("returns a background rect when style.backgroundColor is set", () => {
    const el = makeElement("g", "group", { style: { backgroundColor: "#222" } });
    expect(groupComponent.render(el, ctx)).toMatchObject({
      kind: "rect",
      fill: { color: "#222" },
    });
  });
});
