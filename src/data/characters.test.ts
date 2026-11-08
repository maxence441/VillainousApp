import { describe, expect, it } from "vitest";
import villains from "./characters.json";
import { CHARACTERS } from "./characters";

describe("character catalog", () => {
  it("contains unique, fully described selectable characters", () => {
    expect(villains).toHaveLength(27);
    expect(new Set(CHARACTERS).size).toBe(villains.length);
    expect(villains.every(villain => villain.description && villain.advice)).toBe(true);
    expect(CHARACTERS).toContain("Maléfique");
    expect(CHARACTERS).toContain("Sœurs Sanderson");
  });
});
