const fs = require("fs").promises;
const path = require("path");
const vm = require("vm");

async function findJsFiles(startPath) {
    const files = await fs.readdir(startPath, { withFileTypes: true });
    let results = [];

    for (const file of files) {
        const fullPath = path.join(startPath, file.name);

        if (file.isDirectory()) {
            // Recursively search subdirectories
            results = results.concat(await findJsFiles(fullPath));
        } else if (file.isFile() && path.extname(file.name) === ".js") {
            results.push(fullPath);
        }
    }

    return results;
}

async function extractGraphData(filePath) {
    try {
        const content = await fs.readFile(filePath, "utf8");

        // Create a sandbox context to safely evaluate the JS file
        const sandbox = {};
        const context = vm.createContext(sandbox);

        try {
            // Execute the file content in the sandbox
            vm.runInContext(content, context);

            // Check if graphData exists in the sandbox
            if ("graphData" in sandbox) {
                return sandbox.graphData;
            } else {
                console.warn(`No graphData found in ${filePath}`);
                return null;
            }
        } catch (evalError) {
            console.error(`Error evaluating ${filePath}:`, evalError.message);
            return null;
        }
    } catch (readError) {
        console.error(`Error reading ${filePath}:`, readError.message);
        return null;
    }
}

async function processFiles(startPath) {
    try {
        // Find all JS files in subfolders
        const jsFiles = await findJsFiles(startPath);

        // Process each file
        for (const filePath of jsFiles) {
            const graphData = await extractGraphData(filePath);

            if (graphData) {
                // Create JSON filename by replacing .js extension with .json
                const jsonPath = filePath.replace(".js", ".json");

                try {
                    // Save the graphData as JSON
                    await fs.writeFile(
                        jsonPath,
                        JSON.stringify(graphData, null, 4),
                        "utf8"
                    );
                    console.log(`Successfully saved ${jsonPath}`);
                } catch (writeError) {
                    console.error(
                        `Error saving ${jsonPath}:`,
                        writeError.message
                    );
                }
            }
        }
    } catch (error) {
        console.error("Error processing files:", error.message);
    }
}

// Get the start path from command line arguments, or use current directory
const startPath = process.argv[2] || process.cwd();

// Start processing files
processFiles(startPath)
    .then(() => console.log("Processing complete"))
    .catch((error) => console.error("Fatal error:", error.message));
