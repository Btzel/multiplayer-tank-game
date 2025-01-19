# Multiplayer Tank Game

A comprehensive multiplayer tank game with AI-powered autonomous agents, built using Unity Engine and modern networking architecture.

![Unity](https://img.shields.io/badge/Unity-2022.3.11f1-blue)
![C#](https://img.shields.io/badge/C%23-latest-green)
![Python](https://img.shields.io/badge/Python-3.8+-yellow)
![YOLOv8](https://img.shields.io/badge/YOLOv8-latest-red)

## 🎯 Overview

This project implements a multiplayer tank game with both player-vs-player and player-vs-AI gameplay modes. The game features:
1. Multiplayer functionality using Unity's Netcode for GameObjects
2. AI-powered autonomous agents for single-player mode
3. Advanced pathfinding and decision-making systems
4. Real-time object detection using YOLOv8

## 🔧 Technical Components

### Multiplayer Implementation

#### Core Networking Features
- Self-hosted multiplayer model
- Network transform synchronization
- Client-side prediction
- Server-side validation

#### Connection Management
- Unity Gaming Services integration
- Relay service for connection handling
- Lobby system implementation
- Player authentication
- Connection approval system

### Gameplay Systems

#### Player Mechanics
- Tank movement and rotation
- Turret aiming system
- Projectile firing mechanics
- Health and damage system
- Coin collection mechanics

#### Game Features
- Interactive healing zones
- Player respawn system
- Resource management
- Score tracking

### AI Implementation

#### Autonomous Agent Components
1. **Data Collection & Training**
   - Game frame capture system
   - Data labeling workflow
   - YOLOv8 model training

2. **Pathfinding System**
   - Bidirectional A* implementation
   - Distance mapping
   - Path smoothing algorithms

3. **Decision Making**
   - State analysis
   - Dynamic behavior selection
   - Resource prioritization

## 🛠️ Dependencies

- Unity Engine 2022.3.11f1
- Visual Studio 2022
- Python development environment
- Required Unity packages:
  - Netcode for GameObjects
  - Unity Gaming Services
  - Cinemachine
  - Input System

## 🚀 Usage

1. Install Unity Hub and Unity Editor 2022.3.11f1
2. Clone the repository
3. Open project in Unity Editor
4. Install required packages through Package Manager
5. Build and run the game

## 📊 Features

### Multiplayer Capabilities
- Real-time multiplayer battles
- Lobby system for game creation
- Player name customization
- Resource sharing mechanics

### AI Agent Capabilities
- Real-time object detection
- Dynamic pathfinding
- Intelligent decision making
- Adaptive behavior patterns

## 🔄 Future Improvements

1. **Networking**
   - Dedicated server implementation
   - Enhanced client prediction
   - Improved lag compensation

2. **AI Systems**
   - Advanced behavior trees
   - Improved decision making
   - Enhanced object detection
   - Better path optimization

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- Burak TÜZEL
- Talha Alper ASAV

## 🏫 Academic Context

Senior Design Project (2023/2024)  
Supervisor: Ahmet Çağdaş SEÇKİN  
Computer Engineering Department  
Aydin Adnan Menderes University
