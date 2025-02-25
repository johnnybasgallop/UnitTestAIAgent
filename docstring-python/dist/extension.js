"use strict";
var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// src/extension.ts
var extension_exports = {};
__export(extension_exports, {
  activate: () => activate,
  deactivate: () => deactivate
});
module.exports = __toCommonJS(extension_exports);
var import_child_process = require("child_process");
var path = __toESM(require("path"));
var vscode = __toESM(require("vscode"));
function activate(context) {
  let disposable = vscode.commands.registerCommand("docstring-python.generateDocstrings", async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showErrorMessage("No active editor found!");
      return;
    }
    const document = editor.document;
    if (document.languageId !== "python") {
      vscode.window.showErrorMessage("Current file is not a Python file.");
      return;
    }
    const fileContent = document.getText();
    const fileName = path.basename(document.fileName);
    const pythonScriptPath = path.join(context.extensionPath, "python", "main.py");
    const config = vscode.workspace.getConfiguration("docstring-python");
    const apiKey = config.get("geminiApiKey");
    if (!apiKey) {
      vscode.window.showErrorMessage("Please set your Gemini API key in the extension settings.");
      return;
    }
    vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      // Show in notification area
      title: "Generating Docstrings...",
      cancellable: false
      // Set to true if you want to allow users to cancel
    }, async (progress) => {
      progress.report({ increment: 0 });
      const pythonProcess = (0, import_child_process.spawn)("python3", [pythonScriptPath]);
      let output = "";
      let errorOutput = "";
      pythonProcess.stdout.on("data", (data) => {
        output += data.toString();
      });
      pythonProcess.stderr.on("data", (data) => {
        errorOutput += data.toString();
      });
      pythonProcess.on("close", async (code) => {
        if (code !== 0) {
          console.error(`Python script exited with code ${code}:
${errorOutput}`);
          vscode.window.showErrorMessage(`Python script failed (code ${code}). See console for details.`);
          return;
        }
        const jsonRegex = /{[\s\S]*}/;
        const jsonMatch = output.match(jsonRegex);
        if (!jsonMatch) {
          console.error("No valid JSON found in Python output:", output);
          vscode.window.showErrorMessage("Python script did not return valid JSON.");
          return;
        }
        let cleaned_json;
        try {
          cleaned_json = JSON.parse(jsonMatch[0]);
          if (!cleaned_json || typeof cleaned_json.code !== "string") {
            throw new Error("Invalid JSON structure or missing 'code' property.");
          }
        } catch (error) {
          console.error("Error parsing JSON:", error.message, "\nOriginal Output:", output);
          vscode.window.showErrorMessage("Failed to parse JSON from Python script: " + error.message);
          return;
        }
        try {
          await editor.edit((editBuilder) => {
            const fullRange = new vscode.Range(
              document.positionAt(0),
              document.positionAt(fileContent.length)
            );
            editBuilder.replace(fullRange, cleaned_json.code);
          });
          vscode.window.showInformationMessage("Docstrings generated and applied!");
        } catch (error) {
          console.error("Error writing to file:", error);
          vscode.window.showErrorMessage("Failed to update file: " + error);
        }
      });
      pythonProcess.stdin.write(apiKey + "\n");
      pythonProcess.stdin.write(fileName + "\n");
      pythonProcess.stdin.end(fileContent);
      return new Promise((resolve) => {
        pythonProcess.on("close", () => {
          progress.report({ increment: 100 });
          resolve();
        });
      });
    });
  });
  context.subscriptions.push(disposable);
}
function deactivate() {
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  activate,
  deactivate
});
//# sourceMappingURL=extension.js.map
