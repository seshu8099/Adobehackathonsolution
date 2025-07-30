Adobe India Hackathon 2025 - Solution
This repository contains the complete solution for Challenges 1a and 1b. The solution is packaged as a single, efficient, and offline-capable Docker container.


Team Information

Team Name: Codingwarriors77

Team Leader: cheekati saman

Member: seshu kumar,rishiprasad

Architecture Overview
The solution is designed as a modular Python application with two main components:


Challenge 1a (challenge_1a/): 
A high-performance PDF-to-JSON processor. It uses the PyMuPDF library for fast text and structure extraction, ensuring it meets the strict 10-second performance constraint.

Challenge 1b (challenge_1b/): 
A persona-based document analysis engine. It leverages a lightweight, offline Sentence Transformer model (all-MiniLM-L6-v2) to find semantically relevant content across multiple documents based on a user's task. The model is pre-packaged within the Docker image to ensure zero network dependency.

