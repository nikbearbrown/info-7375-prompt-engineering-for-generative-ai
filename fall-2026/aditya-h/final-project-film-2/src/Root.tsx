import React from "react";
import { Composition } from "remotion";
import { VIDEO } from "./config/theme";
import { totalFrames } from "./config/timeline";
import { Film } from "./Film";
import { StyleFrame } from "./scenes/StyleFrame";
import { ComponentDemo } from "./scenes/ComponentDemo";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="ProductLensFilm" component={Film} durationInFrames={totalFrames()} fps={VIDEO.fps} width={VIDEO.width} height={VIDEO.height} />
    <Composition id="StyleFrame" component={StyleFrame} durationInFrames={90} fps={VIDEO.fps} width={VIDEO.width} height={VIDEO.height} />
    <Composition id="ComponentDemo" component={ComponentDemo} durationInFrames={120} fps={VIDEO.fps} width={VIDEO.width} height={VIDEO.height} />
  </>
);
