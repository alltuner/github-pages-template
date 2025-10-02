#!/usr/bin/env bun

import { readdirSync, readFileSync, writeFileSync, unlinkSync, existsSync } from "fs";
import { join } from "path";

interface BundleFiles {
  js: string | null;
  css: string | null;
}

function cleanupOldBundles(docsDir: string): void {
  const jsDir = join(docsDir, "statics", "js");
  const cssDir = join(docsDir, "statics", "css");

  const oldFiles = [
    join(jsDir, "bundle.js"),
    join(jsDir, "bundle.js.map"),
    join(cssDir, "bundle.css"),
  ];

  for (const file of oldFiles) {
    if (existsSync(file)) {
      unlinkSync(file);
      console.log(`🗑️  Removed old bundle: ${file}`);
    }
  }
}

function findBundleFiles(docsDir: string): BundleFiles {
  const jsDir = join(docsDir, "statics", "js");
  const cssDir = join(docsDir, "statics", "css");

  const jsFiles = readdirSync(jsDir).filter(
    f => f.startsWith("bundle.") && f.endsWith(".js") && !f.endsWith(".map") && f !== "bundle.js"
  );
  const cssFiles = readdirSync(cssDir).filter(
    f => f.startsWith("bundle.") && f.endsWith(".css") && f !== "bundle.css"
  );

  return {
    js: jsFiles.length > 0 ? jsFiles[0] : null,
    css: cssFiles.length > 0 ? cssFiles[0] : null,
  };
}

function updateHtmlFiles(docsDir: string, bundles: BundleFiles): void {
  const htmlFiles = readdirSync(docsDir).filter(f => f.endsWith(".html"));

  for (const htmlFile of htmlFiles) {
    const filePath = join(docsDir, htmlFile);
    let content = readFileSync(filePath, "utf-8");

    let updated = false;

    if (bundles.js) {
      const jsPattern = /\/statics\/js\/bundle(?:\.[a-z0-9]+)?\.js/g;
      if (jsPattern.test(content)) {
        content = content.replace(jsPattern, `/statics/js/${bundles.js}`);
        updated = true;
      }
    }

    if (bundles.css) {
      const cssPattern = /\/statics\/css\/bundle(?:\.[a-z0-9]+)?\.css/g;
      if (cssPattern.test(content)) {
        content = content.replace(cssPattern, `/statics/css/${bundles.css}`);
        updated = true;
      }
    }

    if (updated) {
      writeFileSync(filePath, content, "utf-8");
      console.log(`✓ Updated ${htmlFile}`);
    }
  }
}

const docsDir = process.argv[2] || join(import.meta.dir, "..", "docs");
console.log(`Versioning static files in ${docsDir}...`);

cleanupOldBundles(docsDir);

const bundles = findBundleFiles(docsDir);
console.log(`Found bundles:`, bundles);

if (!bundles.js || !bundles.css) {
  console.error("❌ Missing bundle files!");
  process.exit(1);
}

updateHtmlFiles(docsDir, bundles);
console.log("✓ Versioning completed");