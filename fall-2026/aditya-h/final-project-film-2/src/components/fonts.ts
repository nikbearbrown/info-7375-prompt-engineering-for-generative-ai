import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";

// Inter for everything readable; JetBrains Mono for labels, prompt contracts and data. Both SIL Open Font License.
export const SANS = loadInter("normal", { weights: ["400", "500", "600", "700", "800"], subsets: ["latin"] }).fontFamily;
export const MONO = loadMono("normal", { weights: ["400", "500", "700"], subsets: ["latin"] }).fontFamily;
