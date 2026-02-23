import { spawn } from "child_process";

console.log("Starting Python Flask application...");

const pythonProcess = spawn("python", ["main.py"], { 
  stdio: "inherit",
  env: { ...process.env }
});

pythonProcess.on("close", (code) => {
  console.log(`Python process exited with code ${code}`);
  process.exit(code || 0);
});

// Handle graceful shutdown
process.on("SIGTERM", () => {
  pythonProcess.kill("SIGTERM");
});
process.on("SIGINT", () => {
  pythonProcess.kill("SIGINT");
});
