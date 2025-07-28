Persona-Based Document Analyser
This tool acts like a smart research assistant. You tell it who you are (e.g., a "Marketing Manager") and what you need to find, and it automatically scans a folder of PDFs to pull out the most relevant sections for you. It works completely offline and is designed to be fast.

🚀 How to Use It (4 Simple Steps)
You'll need Docker installed on your computer to run this tool.

Step 1: Define Your Goal
First, tell the tool what to look for. Open the config.json file and edit the persona and job_to_be_done.

For example:

JSON

{
  "persona": "Research Analyst",
  "job_to_be_done": "Analyze key findings and methodologies from research documents"
}
Step 2: Add Your PDFs
Create an input folder and place all the PDF files you want to analyze inside it. The tool works best when you give it a set of related documents (3-10 is ideal).

Step 3: Build the Tool
Open your terminal and run the command below. You only need to do this once. This command packages the tool into a reusable Docker image.

Bash

docker build -t doc-analyzer .
Step 4: Run the Analysis
Now, run the tool with this command. It will read your PDFs, find the relevant sections, and create an output file.

Bash

docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output doc-analyzer
Note: Make sure you have an output folder created before running.

📄 Checking Your Results
After the tool finishes, look inside your output folder for a file named output.json.

This file contains:

Top 20 most relevant sections from all the documents.

Top 30 most relevant subsections.

✅ Optional: Run a Test
If you want to make sure everything is set up correctly, you can run the built-in tests with this command:

Bash

python run_tests.py