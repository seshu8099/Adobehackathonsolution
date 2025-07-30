#Adobe Hackathon: Persona-Driven Document Intelligence
This project provides an intelligent system to extract and rank relevant sections from PDF documents based on a specified persona and their job requirements.

#Features
PDF Processing: Extracts text and formatting.

Section Detection: Identifies headings and sections.

Semantic Relevance: Ranks content using AI for relevance.

Offline Operation: Runs without internet connection.

Fast Processing: Processes 3-5 documents within 60 seconds.

#Setup & Run
Prerequisites
Docker installed (AMD64 architecture)

#Build Docker Image
```

docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .
```
Run the Solution
Create Directories:

```

mkdir -p input output
```
Add PDFs: Place your PDF files (3-10 related documents) into the input directory.
#Run Container:

```

docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none mysolutionname:somerandomidentifier
```
Output
A file named output.json will be generated in the output directory. It contains:

Metadata (input, persona, job-to-be-done)

Top 20 relevant sections

Top 30 relevant subsections

Configuration
Modify config.json to change the persona and job-to-be-done:

JSON

{
  "persona": "Research Analyst",
  "job_to_be_done": "Analyze key findings and methodologies from research documents"
}

Testing
To validate the solution, run the tests:

```

python run_tests.py
```