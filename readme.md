Multiplayer Tank Game with AI Agents
A multiplayer tank game featuring autonomous AI agents, developed in Unity with networking capabilities.
Authors

Burak TÜZEL
Talha Alper ASAV

Under the supervision of Ahmet Çağdaş SEÇKİN
Project Overview
This project implements a multiplayer tank game with AI-controlled opponents. Players can enjoy both single-player matches against AI enemies and multiplayer battles with friends over local network connections.
Key Features

Multiplayer gameplay with self-hosted networking
AI-controlled opponents trained on player data
Progressive game design in single-player mode
Competitive multiplayer environment
Real-time player interaction and combat

Technologies Used

Unity Engine
Visual Studio 2022
Python (for AI development)
Netcode for GameObjects
Unity Gaming Services
YOLOv8 (for object detection)

Technical Architecture
Networking Infrastructure
The game uses a self-hosted networking model where one player acts as both client and server. This architecture offers:
Advantages

Simple implementation
No hosting costs
Quick setup for local gameplay

Considerations

Host's connection quality affects all players
Host has minimal latency advantage
Potential security considerations

Core Components
1. Multiplayer Foundation

NetworkManager: Handles connection management and network state
NetworkTransform: Synchronizes object positions and rotations
Client/Server Architecture: Implements RPCs for game actions

2. Player Systems

Movement with tank hull rotation
Mouse-based turret aiming
Client-side and server-side projectile handling
Health system with damage management
In-game currency (coins) system

3. Game Features

Lobby system for game creation and joining
Player authentication
Custom player names
Connection approval system
Respawn mechanics
Healing zones

AI Agent Architecture
The autonomous agent system comprises several key components:
1. Data Pipeline

Game frame capture
Data labeling via Roboflow
YOLOv8 model training
Environment matrix generation

2. Core AI Components

Matrix Generation: Creates navigable space representation
Pathfinding: Implements bidirectional A* algorithm
Decision Making: Evaluates game state for action selection
Object Detection: Real-time game environment analysis

3. Key Modules

Matrix.py: Terrain analysis and distance mapping
Astar.py: Path calculation
DecisionMaker.py: Strategic action selection
MapPathfinder.py: Path optimization
YoloInference.py: Real-time object detection and action execution

Installation

Install Unity Engine via Unity Hub
Install Visual Studio 2022 with Unity development tools
Required Unity packages:

Netcode for GameObjects
Unity Services Multiplay
Cinemachine
Input System



Development Workflow

Environment Setup

Configure Unity project
Set up networking components
Implement basic player mechanics


Game Features

Add player controls
Implement combat system
Create resource management


Networking

Set up lobby system
Implement player authentication
Add connection management


AI Development

Collect gameplay data
Train detection models
Implement decision-making
Integrate autonomous agents



Technical Notes

Uses self-hosted multiplayer model for simplicity
Implements both client-side and server-side projectiles for fair play
Features sophisticated pathfinding with bidirectional A* algorithm
Includes real-time object detection for AI decision-making

Credits
Base repository and inspiration from YumingRong's Tank Project
References
Full documentation and technical resources available in project documentation. Key references include Unity's official documentation, Netcode for GameObjects documentation, and various technical tutorials.

Project completed June 2024
