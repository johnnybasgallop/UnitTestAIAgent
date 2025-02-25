// docstring-python/src/extension.ts
import { spawn } from 'child_process';
import * as path from 'path';
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    let disposable = vscode.commands.registerCommand('docstring-python.generateDocstrings', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor found!');
            return;
        }

        const document = editor.document;

        if (document.languageId !== 'python') {
            vscode.window.showErrorMessage('Current file is not a Python file.');
            return;
        }

        const fileContent = document.getText();
        const fileName = path.basename(document.fileName);
        const pythonScriptPath = path.join(context.extensionPath, 'python', 'main.py');

        // --- Get the API key from settings ---
        const config = vscode.workspace.getConfiguration('docstring-python');
        const apiKey = config.get<string>('geminiApiKey');

        if (!apiKey) {
            vscode.window.showErrorMessage('Please set your Gemini API key in the extension settings.');
            return; // Stop execution if no API key is set
        }


        // --- Show Progress Indicator ---
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification, // Show in notification area
            title: "Generating Docstrings...",
            cancellable: false // Set to true if you want to allow users to cancel
        }, async (progress) => { // Use async here

            // Start the progress at 0 (optional, for visual clarity)
            progress.report({ increment: 0 });

            const pythonProcess = spawn('python3', [pythonScriptPath]);

            let output = '';
            let errorOutput = '';

            pythonProcess.stdout.on('data', (data) => {
                output += data.toString();
            });

            pythonProcess.stderr.on('data', (data) => {
                errorOutput += data.toString();
            });

            pythonProcess.on('close', async (code) => {
                if (code !== 0) {
                    console.error(`Python script exited with code ${code}:\n${errorOutput}`);
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
                    if (!cleaned_json || typeof cleaned_json.code !== 'string') {
                        throw new Error("Invalid JSON structure or missing 'code' property.");
                    }
                } catch (error: any) {
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
                    // Now show success message *after* the edit
                    vscode.window.showInformationMessage('Docstrings generated and applied!');

                } catch (error: any) {
                    console.error("Error writing to file:", error);
                    vscode.window.showErrorMessage("Failed to update file: " + error);
                }
                // Progress is implicitly completed when the promise resolves
            });

            // --- Send the API key, filename, and file content to Python's stdin ---
            pythonProcess.stdin.write(apiKey + "\n"); // Send API key FIRST
            pythonProcess.stdin.write(fileName + "\n");
            pythonProcess.stdin.end(fileContent);

            // Return a promise that resolves when the Python process is done.
            // This is important for withProgress to work correctly.
            return new Promise<void>(resolve => {
                pythonProcess.on('close', () => {
                    progress.report({ increment: 100 }); // Optional: Set to 100% explicitly
                    resolve(); // Resolve the promise when the process is done
                });
            });
        }); // End of withProgress
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}
