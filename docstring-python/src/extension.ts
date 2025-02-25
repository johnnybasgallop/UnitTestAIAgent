// docstring-python/src/extension.ts
import { spawn } from 'child_process';
import * as path from 'path';
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    let disposable = vscode.commands.registerCommand('docstring-python.generateDocstrings', async () => { //Changed to async
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor found!');
            return;
        }

        const document = editor.document;

        // Check if the active file is a Python file
        if (document.languageId !== 'python') {
            vscode.window.showErrorMessage('Current file is not a Python file.');
            return;
        }

        const fileContent = document.getText();
        const fileName = path.basename(document.fileName); // Get just the filename (e.g., "test.py")

        const pythonScriptPath = path.join(context.extensionPath, 'python', 'main.py');

        // --- Spawn the Python Process ---
        const python = spawn('python3', [pythonScriptPath]);

        let output = '';
        let errorOutput = ''; // Capture stderr separately

        python.stdout.on('data', (data) => {
            output += data.toString();
        });

        python.stderr.on('data', (data) => {
            errorOutput += data.toString();
        });

        python.on('close', async (code) => { // Changed to async
            if (code !== 0) {
                console.error(`Python script exited with code ${code}:\n${errorOutput}`);
                vscode.window.showErrorMessage(`Python script failed (code ${code}). See console for details.`);
                return;
            }

            //Regex to extract the JSON
            const jsonRegex = /{[\s\S]*}/;
            const jsonMatch = output.match(jsonRegex);

            if (!jsonMatch) {
                console.error("No valid JSON found in Python output:", output);
                vscode.window.showErrorMessage("Python script did not return valid JSON.");
                return;
            }

            let cleaned_json;
            try {
                //Corrected JSON parsing
                cleaned_json = JSON.parse(jsonMatch[0]);

                if (!cleaned_json || typeof cleaned_json.code !== 'string') {
                    throw new Error("Invalid JSON structure or missing 'code' property.");
                }

            } catch (error: any) {
                console.error("Error parsing JSON:", error.message, "\nOriginal Output:", output);
                vscode.window.showErrorMessage("Failed to parse JSON from Python script: " + error.message);
                return;
            }


            // --- Replace the Document Content ---
			// All of this is now inside the 'python.on('close')' handler
			// and is also async
			try{
				await editor.edit((editBuilder) => {
					const fullRange = new vscode.Range(
						document.positionAt(0),
						document.positionAt(fileContent.length)
					);
					editBuilder.replace(fullRange, cleaned_json.code);
				});
				vscode.window.showInformationMessage('Docstrings generated and applied!');

            }catch (error : any){
                console.error("Error writing to file:", error);
                vscode.window.showErrorMessage("Failed to update file:  "+ error);
            }
        });


        // --- Send the filename and file content to Python's stdin ---
        python.stdin.write(fileName + "\n"); // Send filename first, followed by a newline
        python.stdin.end(fileContent);  // Then send the file content and close stdin
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}
