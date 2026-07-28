// @ts-check
import js from "@eslint/js";
import tseslint from "typescript-eslint";
import globals from "globals";

export default tseslint.config(
  {
    ignores: [
      "**/dist/**",
      "**/node_modules/**",
      "**/coverage/**",
      "**/*.d.ts",
      "examples/[0-9]*/**",
      "examples/gallery/**",
      "showcase/[0-9]*/**",
      "showcase/gallery/**",
      "scenarios/[0-9]*/**",
      "scenarios/gallery/**",
      "ultimate/[0-9]*/**",
      "ultimate/gallery/**",
      "ultimate/ultimate-90/**",
      "journey/[0-9]*/**",
      "journey/gallery/**",
      "journey/journey-time/**",
    ],
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      globals: { ...globals.browser, ...globals.node },
    },
    rules: {
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
      "@typescript-eslint/consistent-type-imports": [
        "error",
        { prefer: "type-imports", fixStyle: "inline-type-imports" },
      ],
    },
  },
  {
    // Config and test files may use devDependencies / node globals freely.
    files: ["**/*.config.{js,ts}", "**/*.test.ts", "**/tests/**"],
    languageOptions: { globals: { ...globals.node } },
  },
);
